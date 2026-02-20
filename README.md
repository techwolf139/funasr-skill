# ClawFunASR

FunASR WebSocket 客户端 - 为 OpenCode AI 助手打造的语音转文字技能

> ⚡ **一句话说明**：安装此 Skill 后，只需告诉 AI 助手"帮我转写这个音频"，即可自动完成语音转文字。

---

## 🚀 快速开始（OpenCode 用户）

### 步骤 1：安装 Skill

```bash
# 方式 A：创建软链接（推荐，便于更新）
ln -s /Users/mac/git/clawfunasr ~/.config/opencode/skills/funasr-asr

# 方式 B：直接复制
cp -r /Users/mac/git/clawfunasr ~/.config/opencode/skills/funasr-asr
```

### 步骤 2：启动 FunASR 服务器（仅首次需要）

```bash
# 在终端启动服务器（保持运行）
conda activate asr
python /Users/mac/git/FunASR/runtime/python/websocket/funasr_wss_server.py \
  --port 10096 \
  --asr_model iic/SenseVoiceSmall \
  --ngpu 0
```

### 步骤 3：开始使用

安装完成后，直接对 OpenCode AI 助手说：

| 你可以说 | AI 会做什么 |
|---------|-------------|
| "帮我转写这个音频 /path/to/meeting.wav" | 连接 FunASR 服务器，转写音频 |
| "从这段录音提取文字" | 自动识别音频并转写 |
| "处理所有 wav 文件" | 批量转写目录下所有音频 |

---

## 📖 完整使用指南

### 安装方法详解

#### 方法 1：全局安装（所有 OpenCode 项目可用）

```bash
ln -s /Users/mac/git/clawfunasr ~/.config/opencode/skills/funasr-asr
```

#### 方法 2：项目内安装（仅当前项目可用）

```bash
# 在您的项目根目录执行
ln -s /Users/mac/git/clawfunasr .opencode/skills/funasr-asr
```

### Skill 触发方式

AI 助手会自动识别以下意图并调用此 Skill：

- 🎤 **语音转文字**："转写音频"、"语音转文字"
- 📝 **提取内容**："提取音频中的文字"、"录音说的是什么"
- 📄 **生成文稿**："生成文字稿"、"整理会议录音"
- 🎯 **自动触发**：提及 .wav/.mp3/.flac 等音频文件并要求处理

### 与 AI 协作示例

<details>
<summary><b>示例 1：单文件转写</b></summary>

```
👤 用户: 帮我转写 /Users/mac/Desktop/interview.wav

🤖 AI: 正在使用 FunASR 技能转写音频...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
转写结果：
你好，欢迎参加今天的面试。首先请介绍一下你自己...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 转写完成！需要我保存到文件吗？
```

</details>

<details>
<summary><b>示例 2：批量处理 + 要点提取</b></summary>

```
👤 用户: 我有三个会议录音在 /Users/mac/recordings/ 目录，帮我转写并提取关键信息

🤖 AI: 好的，正在批量处理 3 个音频文件...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 meeting-01.wav (45分钟)
   转写: 3,245 字
   要点: 项目进度、预算讨论、下周计划

📁 meeting-02.wav (30分钟)
   转写: 2,108 字
   要点: 技术方案评审、风险评估

📁 meeting-03.wav (60分钟)
   转写: 5,672 字
   要点: 客户反馈、产品路线图、团队分工
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 全部完成！已生成 3 个文字稿文件和 1 个汇总文件。
```

</details>

<details>
<summary><b>示例 3：不同格式音频</b></summary>

```
👤 用户: 把这个 mp3 转成文字

🤖 AI: 收到！正在处理 /Users/mac/Downloads/lecture.mp3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[自动检测] 格式: MP3 → 转换为 WAV
[正在转写] 使用 offline 模式（离线，准确度最高）
[完成] 转写结果: 今天我们来讲讲机器学习的基础概念...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

</details>

### 配置选项

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `host` | localhost | FunASR 服务器地址 |
| `port` | 10096 | 服务器端口（无 SSL） |
| `mode` | offline | 转写模式 |
| `ssl_enabled` | false | 是否启用 SSL |

如需修改默认值，编辑 `SKILL.md` 中的配置。

---

## 🛠️ 高级用法（可选）

### 命令行直接调用

```bash
# 转写音频文件
python scripts/funasr_ws_client.py \
  --host localhost \
  --port 10096 \
  --audio-file /path/to/audio.wav \
  --ssl 0

# 指定模式
python scripts/funasr_ws_client.py \
  --host localhost \
  --port 10096 \
  --audio-file /path/to/audio.mp3 \
  --mode 2pass \
  --ssl 0
```

### Python API

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
    print(result['text'])

asyncio.run(transcribe())
```

### 支持的音频格式

| 类型 | 格式 | 说明 |
|------|------|------|
| 原生 | WAV, PCM | 推荐，PCM 16-bit, 16000Hz, Mono |
| 转换 | MP3, FLAC, OGG | 需安装 ffmpeg |

---

## ❓ 常见问题

### Q: 提示 "Connection refused"？
**A**: 确保 FunASR 服务器正在运行，检查端口是否为 10096

### Q: 提示 SSL 错误？
**A**: 使用 `--ssl 0` 参数或确认服务器配置

### Q: 转写结果为空？
**A**: 检查音频文件是否损坏，采样率是否为 16000Hz

### Q: 需要 GPU 吗？
**A**: 不需要，已配置 `--ngpu 0` 使用 CPU 模式

---

## 📁 项目结构

```
clawfunasr/
├── README.md                      # 本文件
├── SKILL.md                       # Skill 定义（OpenCode 加载用）
├── scripts/
│   ├── funasr_ws_client.py       # WebSocket 客户端
│   └── test_client.py            # 单元测试
└── references/
    └── websocket-api.md          # API 参考文档
```

---

## 🔗 相关链接

- [FunASR 官方仓库](https://github.com/alibaba/FunASR)
- [SenseVoice 模型](https://www.modelscope.cn/models/iic/SenseVoiceSmall)
- [WebSocket API 参考](./references/websocket-api.md)

---

**许可证**: MIT  
**版本**: 1.0.0  
**更新**: 2026-02-20
