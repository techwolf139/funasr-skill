# FunASR WebSocket ASR OpenCode Skill 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 开发一个 OpenCode skill，连接本地 FunASR WebSocket 服务器进行语音转文字

**Architecture:** 基于 FunASR 官方 WebSocket 客户端实现，创建独立的 Python 客户端类和 CLI 工具，支持 offline/online/2pass 多种模式

**Tech Stack:** Python, websockets, FunASR, WebSocket

---

## 当前状态

本 skill 已在 `.opencode/skills/funasr-asr/` 目录下实现完成：

```
.opencode/skills/funasr-asr/
├── SKILL.md                      # Skill 定义和文档
├── scripts/
│   ├── funasr_ws_client.py      # WebSocket 客户端
│   └── sample.wav               # 示例音频文件
└── references/
    └── websocket-api.md          # API 参考文档
```

---

## Task 1: 验证 Skill 基础功能

**Files:**
- Test: `.opencode/skills/funasr-asr/scripts/funasr_ws_client.py`

**Step 1: 启动 FunASR 服务器**

在终端运行：
```bash
conda activate asr
cd /Users/mac/git/FunASR/runtime/python/websocket
python funasr_wss_server.py --port 10096 \
  --asr_model iic/SenseVoiceSmall \
  --asr_model_online iic/SenseVoiceSmall \
  --ngpu 0
```

**Step 2: 测试转写功能**

```bash
conda run -n asr python .opencode/skills/funasr-asr/scripts/funasr_ws_client.py \
  --host localhost \
  --port 10096 \
  --audio-file /Users/mac/git/funasr-sample/audio/asr_example.wav \
  --ssl 0
```

**Step 3: 验证输出**

预期输出：
```
==================================================
Transcription Result:
==================================================
欢迎大家来体验打摩院推出的语音识别模型
==================================================
```

---

## Task 2: 完善 Skill 文档

**Files:**
- Modify: `.opencode/skills/funasr-asr/SKILL.md`
- Modify: `.opencode/skills/funasr-asr/references/websocket-api.md`

**Step 1: 更新 SKILL.md**

确保包含以下内容：
- 清晰的 prerequisites 说明
- 多种使用方式的示例
- 参数配置表
- 故障排除指南

**Step 2: 验证 Skill 可被 OpenCode 加载**

OpenCode 会自动发现 `.opencode/skills/*/SKILL.md` 文件

---

## Task 3: 添加单元测试（可选）

**Files:**
- Create: `.opencode/skills/funasr-asr/scripts/test_client.py`

**Step 1: 创建测试文件**

```python
import asyncio
import sys
sys.path.insert(0, '.opencode/skills/funasr-asr/scripts')
from funasr_ws_client import FunASRClient, clean_sensevoice_text

def test_clean_sensevoice_text():
    text = "<|zh|><|NEUTRAL|><|Speech|>欢迎大家"
    result = clean_sensevoice_text(text)
    assert result == "欢迎大家"

def test_client_init():
    client = FunASRClient(host="localhost", port=10096, ssl_enabled=False)
    assert client.host == "localhost"
    assert client.port == 10096
    assert client.ssl_enabled == False

if __name__ == "__main__":
    test_clean_sensevoice_text()
    test_client_init()
    print("All tests passed!")
```

**Step 2: 运行测试**

```bash
conda run -n asr python .opencode/skills/funasr-asr/scripts/test_client.py
```

---

## Task 4: 添加麦克风实时转写功能（可选）

**Files:**
- Modify: `.opencode/skills/funasr-asr/scripts/funasr_ws_client.py`

**Step 1: 添加麦克风输入支持**

参考 FunASR 官方客户端的 `record_microphone()` 函数实现

**Step 2: 测试麦克风输入**

```bash
conda run -n asr python .opencode/skills/funasr-asr/scripts/funasr_ws_client.py \
  --host localhost \
  --port 10096 \
  --mode stream \
  --ssl 0
```

---

## Task 5: 添加 Web UI（可选）

**Files:**
- Create: `.opencode/skills/funasr-asr/scripts/web_app.py`

**Step 1: 创建 Streamlit Web 应用**

```python
import streamlit as st
import asyncio
import sys
sys.path.insert(0, '.opencode/skills/funasr-asr/scripts')
from funasr_ws_client import FunASRClient

st.title("FunASR 语音转文字")

host = st.text_input("服务器地址", "localhost")
port = st.number_input("端口", value=10096)
audio_file = st.file_uploader("上传音频文件", type=["wav", "mp3", "flac"])

if st.button("开始转写"):
    if audio_file:
        # 保存上传的文件
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_file.read())
        
        # 转写
        client = FunASRClient(host=host, port=port, ssl_enabled=False)
        result = asyncio.run(client.transcribe_file("temp_audio.wav"))
        
        st.success("转写完成!")
        st.write(result["text"])
```

**Step 2: 运行 Web 应用**

```bash
pip install streamlit
streamlit run .opencode/skills/funasr-asr/scripts/web_app.py
```

---

## 验收标准

- [x] Skill 目录结构符合 OpenCode 规范
- [x] SKILL.md 包含正确的 YAML frontmatter
- [x] Python 客户端可以连接 FunASR 服务器
- [x] 能够转写 WAV 音频文件
- [x] 输出结果正确去除特殊标记

---

## 执行选项

**Plan complete and saved to `docs/plans/2026-02-20-funasr-asr-skill.md`. Two execution options:**

1. **Subagent-Driven (this session)** - 继续完善现有功能
2. **Parallel Session (separate)** - 在新 session 中继续开发

**当前状态:** Skill 基础功能已完成并测试通过，可直接使用

**建议:** 如果只需要基础转写功能，当前实现已满足需求。如需添加麦克风输入或 Web UI，可继续执行 Task 4/5

---

## 使用示例

### 快速开始

```bash
# 1. 启动 FunASR 服务器
conda activate asr
python /Users/mac/git/FunASR/runtime/python/websocket/funasr_wss_server.py \
  --port 10096 \
  --asr_model iic/SenseVoiceSmall \
  --ngpu 0

# 2. 转写音频
conda run -n asr python .opencode/skills/funasr-asr/scripts/funasr_ws_client.py \
  --host localhost \
  --port 10096 \
  --audio-file /path/to/audio.wav \
  --ssl 0
```

### Python API

```python
import asyncio
import sys
sys.path.insert(0, '.opencode/skills/funasr-asr/scripts')
from funasr_ws_client import FunASRClient

async def transcribe():
    client = FunASRClient(host="localhost", port=10096, ssl_enabled=False)
    result = await client.transcribe_file("/path/to/audio.wav")
    print(result["text"])

asyncio.run(transcribe())
```
