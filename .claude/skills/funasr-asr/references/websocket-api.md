# FunASR WebSocket API Reference

## Server Configuration

### Starting the Server

```bash
cd /path/to/FunASR/runtime/python/websocket
python funasr_wss_server.py --port 10095 --asr_model iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch
```

### Server Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| --host | 0.0.0.0 | Server host |
| --port | 10095 | WebSocket port |
| --asr_model | iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch | ASR model |
| --ngpu | 1 | GPU usage (0 for CPU) |
| --ncpu | 4 | CPU cores |
| --ssl | 1 | Enable SSL |

## Client Protocol

### Connection

- URI: `wss://localhost:10095` (SSL) or `ws://localhost:10095` (no SSL)
- Protocol: WebSocket with binary frames

### Message Format

#### 1. Initial Configuration Message (JSON)

```json
{
  "mode": "2pass",
  "chunk_size": [5, 10, 5],
  "chunk_interval": 10,
  "encoder_chunk_look_back": 4,
  "decoder_chunk_look_back": 0,
  "audio_fs": 16000,
  "wav_name": "demo",
  "wav_format": "pcm",
  "is_speaking": true,
  "itn": true
}
```

#### 2. Audio Data (Binary)

Send raw PCM audio data in chunks.

#### 3. End of Speech (JSON)

```json
{
  "is_speaking": false
}
```

### Response Format (JSON)

```json
{
  "wav_name": "demo",
  "text": "转写文本内容",
  "timestamp": [[0, 1000, "你好"], [1000, 2000, "世界"]],
  "is_final": true,
  "mode": "2pass"
}
```

## Modes

| Mode | Description |
|------|-------------|
| offline | Full audio processing after recording ends |
| online | Real-time streaming with lower latency |
| 2pass | Combines online speed with offline accuracy |

## Audio Requirements

- Sample Rate: 16000 Hz (recommended)
- Format: PCM 16-bit mono
- Channels: Mono

## Error Codes

| Code | Description |
|------|-------------|
| 1006 | Abnormal closure |
| 1011 | Server error |
