---
name: funasr-asr
description: Connect to local FunASR WebSocket server for real-time speech-to-text transcription. Supports audio file processing and streaming transcription.
license: MIT
allowed-tools:
  - read
  - write
  - bash
  - glob
metadata:
  version: "1.0.0"
  author: "ClawFunASR"
  repository: "https://github.com/alibaba/FunASR"
---

# FunASR ASR Skill

This skill provides instructions for connecting to a local FunASR WebSocket server to perform speech-to-text transcription.

## Prerequisites

1. **FunASR WebSocket Server Running**
   
   Start the FunASR server on your local machine:
   ```bash
   cd /path/to/FunASR/runtime/python/websocket
   python funasr_wss_server.py --port 10095
   ```

2. **Python Dependencies**
   ```bash
   pip install websockets numpy soundfile
   ```

## Usage Instructions

### Option 1: Process Audio File

Use the provided Python client script to transcribe an audio file:

```bash
python .opencode/skills/funasr-asr/scripts/funasr_ws_client.py \
  --host localhost \
  --port 10096 \
  --audio-file /path/to/your/audio.wav \
  --ssl 0
```

Note: Use `--ssl 0` if connecting to a non-SSL server. Port 10096 runs without SSL.

### Option 2: Real-time Streaming (Microphone)

For real-time transcription from microphone input:

```bash
python .opencode/skills/funasr-asr/scripts/funasr_ws_client.py \
  --host localhost \
  --port 10095 \
  --mode stream
```

### Option 3: Use as Python Module

Import and use in your own Python code:

```python
import asyncio
import sys
sys.path.insert(0, '.opencode/skills/funasr-asr/scripts')
from funasr_ws_client import FunASRClient

async def transcribe():
    client = FunASRClient(host="localhost", port=10095)
    result = await client.transcribe_file("/path/to/audio.wav")
    print(result)

asyncio.run(transcribe())
```

## Supported Audio Formats

- WAV (recommended)
- MP3
- FLAC
- OGG

## Configuration

The skill supports the following configuration options:

### Config File (config.json)

Create a `config.json` in the project root:

```json
{
  "host": "localhost",
  "port": 10096,
  "ssl_enabled": false,
  "mode": "2pass",
  "chunk_size": "5,10,5",
  "chunk_interval": 10,
  "use_itn": true,
  "final_wait": 3.0
}
```

### Command Line Arguments

| Parameter | Default | Description |
|-----------|---------|-------------|
| host | localhost | FunASR server host |
| port | 10096 | FunASR server port |
| mode | 2pass | Processing mode: offline, online, 2pass |
| ssl_enabled | false | Enable SSL |
| --config | config.json | Path to config file |

**Priority**: command line args > config file > defaults

## Troubleshooting

### Connection Refused
- Ensure FunASR server is running: `python funasr_wss_server.py --port 10095`
- Check firewall settings
- Try different port (10095, 10096)

### SSL Error
- Use `--ssl 0` flag to disable SSL

### No Transcription Output
- Verify audio file format is supported
- Check audio file is not corrupted
- Ensure audio sample rate matches model requirements (typically 16000 Hz)

### High Latency
- Use smaller models on the server
- Reduce network latency by running server locally

## References

- FunASR Documentation: https://github.com/modelscope/FunASR
- WebSocket API: See `references/websocket-api.md`
