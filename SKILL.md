---
name: funasr-asr
description: Connect to local FunASR WebSocket server for real-time speech-to-text transcription with emotion and language detection. Supports audio file processing, streaming transcription, and SenseVoice emotion recognition.
license: MIT
allowed-tools:
  - read
  - write
  - bash
  - glob
metadata:
  version: "1.1.0"
  author: "ClawFunASR"
  repository: "https://github.com/alibaba/FunASR"
---

# FunASR ASR Skill

This skill provides instructions for connecting to a local FunASR WebSocket server to perform speech-to-text transcription with emotion and language detection.

## Prerequisites

1. **FunASR WebSocket Server Running**
   
   Start the FunASR server on your local machine:
   ```bash
   cd /path/to/FunASR/runtime/python/websocket
   python funasr_wss_server.py --port 10096 \
     --asr_model iic/SenseVoiceSmall \
     --ngpu 0
   ```

2. **Python Dependencies**
   ```bash
   pip install websockets numpy
   ```

3. **ffmpeg (optional)**
   
   Required for non-WAV formats:
   ```bash
   # macOS
   brew install ffmpeg
   # Ubuntu/Debian
   sudo apt install ffmpeg
   ```

## Usage Instructions

### Option 1: Process Audio File

Use the provided Python client script to transcribe an audio file:

```bash
python scripts/funasr_ws_client.py \
  --host localhost \
  --port 10096 \
  --audio-file /path/to/your/audio.wav \
  --ssl 0
```

Note: Default port is 10096 with SSL disabled.

### Option 2: Use as Python Module

Import and use in your own Python code:

```python
import asyncio
import sys
sys.path.insert(0, 'scripts')
from funasr_ws_client import FunASRClient

async def transcribe():
    client = FunASRClient(
        host="localhost",
        port=10096,
        ssl_enabled=False,
        mode="offline"
    )
    result = await client.transcribe_file("/path/to/audio.wav")
    
    print(f"Text: {result['text']}")
    print(f"Emotion: {result.get('emotion_text')}")
    print(f"Language: {result.get('language_text')}")

asyncio.run(transcribe())
```

## Emotion & Language Detection

When using SenseVoice model, the transcription result includes emotion and language information:

### Supported Emotions

| Emotion | Emoji | Description |
|---------|-------|-------------|
| NEUTRAL | 😐 | Neutral |
| HAPPY | 😊 | Happy |
| SAD | 😢 | Sad |
| ANGRY | 😠 | Angry |
| FEARFUL | 😨 | Fearful |
| DISGUSTED | 🤢 | Disgusted |

### Supported Languages

| Code | Language |
|------|----------|
| zh | Chinese |
| en | English |
| yue | Cantonese |
| ja | Japanese |
| ko | Korean |

### Result Format

```python
{
    "text": "Transcribed text content",
    "clean_text": "Text without tags",
    "emotion": "HAPPY",
    "emotion_text": "😊 Happy",
    "language": "zh",
    "language_text": "Chinese",
    "segments": [...]
}
```

## Supported Audio Formats

- **Native**: WAV, PCM (recommended: PCM 16-bit, 16000Hz, Mono)
- **Via ffmpeg**: MP3, FLAC, OGG

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| host | localhost | FunASR server host |
| port | 10096 | FunASR server port |
| mode | offline | Processing mode: offline, online, 2pass |
| ssl_enabled | false | Enable SSL (true/false) |
| use_itn | true | Enable inverse text normalization |
| final_wait | 3.0 | Seconds to wait for final result |

## Troubleshooting

### Connection Refused
- Ensure FunASR server is running
- Check port is 10096 (default)
- Verify firewall settings

### SSL Error
- Use `--ssl 0` flag or `ssl_enabled=False`

### No Transcription Output
- Verify audio file format is supported
- Check audio file is not corrupted
- Ensure audio sample rate is 16000 Hz

### High Latency
- Use smaller models (e.g., SenseVoiceSmall)
- Run server locally

## References

- FunASR Documentation: https://github.com/modelscope/FunASR
- SenseVoice Model: https://www.modelscope.cn/models/iic/SenseVoiceSmall
- WebSocket API: See `references/websocket-api.md`
