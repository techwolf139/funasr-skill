#!/usr/bin/env python3

import os
import sys
import asyncio
import argparse
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

import websockets
import ssl
import wave

import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def clean_sensevoice_text(text: str) -> str:
    return re.sub(r'<\|[^|]+\|>', '', text).strip()


class FunASRClient:
    """FunASR WebSocket client for speech-to-text transcription."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 10095,
        ssl_enabled: bool = True,
        mode: str = "2pass",
        chunk_size: str = "5,10,5",
        chunk_interval: int = 10,
        use_itn: bool = True,
        final_wait: float = 3.0
    ):
        self.host = host
        self.port = port
        self.ssl_enabled = ssl_enabled
        self.mode = mode
        self.chunk_size = [int(x) for x in chunk_size.split(",")]
        self.chunk_interval = chunk_interval
        self.use_itn = use_itn
        self.encoder_chunk_look_back = 4
        self.decoder_chunk_look_back = 0
        self.final_wait = final_wait
        
    def _get_ws_uri(self) -> str:
        """Get WebSocket URI."""
        if self.ssl_enabled:
            return f"wss://{self.host}:{self.port}"
        return f"ws://{self.host}:{self.port}"
    
    def _get_ssl_context(self) -> Optional[ssl.SSLContext]:
        if self.ssl_enabled:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            return ssl_context
        return None
    
    def _check_ffmpeg(self) -> bool:
        import shutil
        return shutil.which("ffmpeg") is not None
    
    def _convert_audio(self, audio_path: Path) -> tuple:
        import subprocess
        import tempfile
        
        temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_wav.close()
        
        cmd = [
            "ffmpeg", "-y", "-i", str(audio_path),
            "-ar", "16000", "-ac", "1",
            "-acodec", "pcm_s16le", temp_wav.name
        ]
        
        logger.info(f"Converting audio with ffmpeg: {' '.join(cmd[:6])}...")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg conversion failed: {result.stderr}")
        
        with wave.open(temp_wav.name, "rb") as wav_file:
            sample_rate = wav_file.getframerate()
            frames = wav_file.readframes(wav_file.getnframes())
        
        import os
        os.unlink(temp_wav.name)
        
        logger.info(f"ffmpeg conversion complete: {len(frames)} bytes, {sample_rate}Hz")
        return bytes(frames), sample_rate, "pcm"
    
    def _read_audio_file(self, audio_path: Union[str, Path]) -> tuple:
        path = Path(audio_path)
        suffix = path.suffix.lower()
        
        supported_suffixes = {".wav", ".pcm"}
        
        if suffix == ".wav":
            with wave.open(str(path), "rb") as wav_file:
                sample_rate = wav_file.getframerate()
                frames = wav_file.readframes(wav_file.getnframes())
                return bytes(frames), sample_rate, "pcm"
        elif suffix == ".pcm":
            with open(str(path), "rb") as f:
                return f.read(), 16000, "pcm"
        elif self._check_ffmpeg():
            return self._convert_audio(path)
        else:
            with open(str(path), "rb") as f:
                return f.read(), 16000, "others"
    
    async def _send_audio_chunks(self, websocket, audio_bytes: bytes, sample_rate: int, wav_format: str):
        """Send audio data in chunks to WebSocket server."""
        stride = int(60 * self.chunk_size[1] / self.chunk_interval / 1000 * sample_rate * 2)
        chunk_num = (len(audio_bytes) - 1) // stride + 1
        
        logger.info(f"Sending {chunk_num} audio chunks to server...")
        
        # Send first chunk with metadata
        message = json.dumps({
            "mode": self.mode,
            "chunk_size": self.chunk_size,
            "chunk_interval": self.chunk_interval,
            "encoder_chunk_look_back": self.encoder_chunk_look_back,
            "decoder_chunk_look_back": self.decoder_chunk_look_back,
            "audio_fs": sample_rate,
            "wav_name": Path(self.audio_path).stem if hasattr(self, 'audio_path') else "demo",
            "wav_format": wav_format,
            "is_speaking": True,
            "itn": self.use_itn
        })
        await websocket.send(message)
        
        # Send audio chunks
        for i in range(chunk_num):
            beg = i * stride
            data = audio_bytes[beg:beg + stride]
            
            is_speaking = i < chunk_num - 1
            if i == chunk_num - 1:
                # Send final chunk with is_speaking=False
                await websocket.send(data)
                end_message = json.dumps({"is_speaking": False})
                await websocket.send(end_message)
            else:
                await websocket.send(data)
            
            # Sleep for offline mode
            sleep_duration = 0.001 if self.mode == "offline" else 60 * self.chunk_size[1] / self.chunk_interval / 1000
            await asyncio.sleep(sleep_duration)
    
    async def _receive_results(self, websocket) -> List[Dict[str, Any]]:
        """Receive transcription results from server."""
        results = []
        
        try:
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                
                # Skip messages without text
                if "text" not in data:
                    continue
                
                result = {
                    "text": data.get("text", ""),
                    "wav_name": data.get("wav_name", "demo"),
                    "timestamp": data.get("timestamp", ""),
                    "is_final": data.get("is_final", False),
                    "mode": data.get("mode", self.mode)
                }
                results.append(result)
                
                logger.info(f"Received: {result['text'][:100]}...")
                
                if self.mode == "offline" and result["text"]:
                    break
                    
                if self.mode != "offline" and result["is_final"]:
                    await asyncio.sleep(self.final_wait)
                    break
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        
        return results
    
    async def transcribe_file(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribe an audio file.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dict containing transcription results
        """
        self.audio_path = audio_path
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"Reading audio file: {audio_path}")
        audio_bytes, sample_rate, wav_format = self._read_audio_file(audio_path)
        logger.info(f"Audio loaded: {len(audio_bytes)} bytes, sample rate: {sample_rate}Hz")
        
        uri = self._get_ws_uri()
        ssl_context = self._get_ssl_context()
        
        logger.info(f"Connecting to {uri}...")
        
        try:
            async with websockets.connect(uri, ping_interval=None, ssl=ssl_context) as websocket:
                await self._send_audio_chunks(websocket, audio_bytes, sample_rate, wav_format)
                
                await asyncio.sleep(0.5)
                try:
                    results = await asyncio.wait_for(self._receive_results(websocket), timeout=30)
                except asyncio.TimeoutError:
                    logger.warning("Timeout waiting for results")
                    results = []
                
                full_text = " ".join([clean_sensevoice_text(r["text"]) for r in results])
                
                return {
                    "text": full_text,
                    "segments": results,
                    "audio_file": audio_path
                }
                
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            raise
    
    async def transcribe_stream(self, audio_chunks: List[bytes], sample_rate: int = 16000):
        """
        Transcribe streaming audio chunks.
        
        Args:
            audio_chunks: List of audio chunks (bytes)
            sample_rate: Audio sample rate (default 16000)
            
        Returns:
            Dict containing transcription results
        """
        uri = self._get_ws_uri()
        ssl_context = self._get_ssl_context()
        
        logger.info(f"Connecting to {uri} for streaming...")
        
        try:
            async with websockets.connect(uri, ping_interval=None, ssl=ssl_context) as websocket:
                # Send initial metadata
                message = json.dumps({
                    "mode": self.mode,
                    "chunk_size": self.chunk_size,
                    "chunk_interval": self.chunk_interval,
                    "encoder_chunk_look_back": self.encoder_chunk_look_back,
                    "decoder_chunk_look_back": self.decoder_chunk_look_back,
                    "wav_name": "stream",
                    "is_speaking": True,
                    "itn": self.use_itn
                })
                await websocket.send(message)
                
                # Send audio chunks
                for i, chunk in enumerate(audio_chunks):
                    await websocket.send(chunk)
                    await asyncio.sleep(0.005)
                
                # Send end signal
                end_message = json.dumps({"is_speaking": False})
                await websocket.send(end_message)
                
                # Wait for results
                await asyncio.sleep(1)
                results = await self._receive_results(websocket)
                
                full_text = " ".join([r["text"] for r in results])
                
                return {
                    "text": full_text,
                    "segments": results
                }
                
        except Exception as e:
            logger.error(f"Error during streaming transcription: {e}")
            raise


async def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description="FunASR WebSocket Client for speech-to-text transcription"
    )
    parser.add_argument(
        "--host", 
        type=str, 
        default="localhost", 
        help="FunASR server host"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=10095, 
        help="FunASR server port"
    )
    parser.add_argument(
        "--audio-file",
        type=str,
        help="Path to audio file for transcription"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="offline",
        choices=["offline", "online", "2pass"],
        help="ASR mode: offline, online, or 2pass"
    )
    parser.add_argument(
        "--ssl",
        type=int,
        default=1,
        help="1 for SSL, 0 for no SSL"
    )
    parser.add_argument(
        "--chunk-size",
        type=str,
        default="5,10,5",
        help="Chunk size for streaming"
    )
    parser.add_argument(
        "--use-itn",
        type=int,
        default=1,
        help="1 for using ITN (inverse text normalization), 0 for not"
    )
    parser.add_argument(
        "--final-wait",
        type=float,
        default=3.0,
        help="Seconds to wait after final result before disconnecting"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file for transcription results"
    )
    
    args = parser.parse_args()
    
    if not args.audio_file:
        parser.error("--audio-file is required")
    
    # Create client
    client = FunASRClient(
        host=args.host,
        port=args.port,
        ssl_enabled=args.ssl == 1,
        mode=args.mode,
        chunk_size=args.chunk_size,
        use_itn=args.use_itn == 1,
        final_wait=args.final_wait
    )
    
    # Transcribe
    try:
        result = await client.transcribe_file(args.audio_file)
        
        print("\n" + "="*50)
        print("Transcription Result:")
        print("="*50)
        print(result["text"])
        print("="*50)
        
        # Save to file if specified
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\nResults saved to: {args.output}")
            
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
