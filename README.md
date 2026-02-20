# ClawFunASR

FunASR WebSocket 客户端 - 连接本地 FunASR 服务器进行语音转文字

## 功能特性

- 🔊 **多种音频格式支持**：WAV、MP3、FLAC、OGG（通过 ffmpeg 自动转换）
- 🎯 **多种转写模式**：offline、online、2pass
- 🔌 **WebSocket 宏协议**：与 FunASR 官方服务器完全兼容
- 📝 **SenseVoice 清理**：自动去除 SenseVoice 模型的特殊标记
- 🐍 **双接口**：命令行工具 + Python API
- 🛠️ **OpenCode Skill**：可直接作为 AI 助手技能使用

## 快速开始

### 前置要求

1. **FunASR 服务器**

   ```bash
   # 克隆 FunASR
   git clone https://github.com/alibaba/FunASR.git
   cd FunASR/runtime/python/websocket
   
   # 启动服务器（无 SSL）
   python funasr_wss_server.py --port 10096 \
     --asr_model iic/SenseVoiceSmall \
     --ngpu 0
   ```

2. **Python 依赖**

   ```bash
   pip install websockets numpy
   ```

3. **ffmpeg（可选）**
   
   用于支持非 WAV 格式音频：
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt install ffmpeg
   ```

### 命令行使用

```bash
# 转写音频文件
python scripts/funasr_ws_client.py \
  --host localhost \
  --port 10096 \
  --audio-file /path/to/audio.wav \
  --ssl 0

# 指定转写模式
python scripts/funasr_ws_client.py \
  --host localhost \
  --port 10096 \
  --audio-file /path/to/audio.mp3 \
  --mode offline \
  --ssl 0

# 保存结果到文件
python scripts/funasr_ws_client.py \
  --host localhost \
  --port 10096 \
  --audio-file /path/to/audio.wav \
  --ssl 0 \
  --output result.json
```

### Python API

```python
import asyncio
import sys
sys.path.insert(0, 'scripts')
from funasr_ws_client import FunASRClient

async def transcribe():
    # 创建客户端
    client = FunASRClient(
        host="localhost",
        port=10096,
        ssl_enabled=False,
        mode="offline"
    )
    
    # 转写音频文件
    result = await client.transcribe_file("/path/to/audio.wav")
    
    print(f"转写结果: {result['text']}")
    print(f"分段数: {len(result['segments'])}")

asyncio.run(transcribe())
```

## 参数说明

### 命令行参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--host` | localhost | FunASR 服务器地址 |
| `--port` | 10095 | FunASR 服务器端口 |
| `--audio-file` | - | 音频文件路径（必需） |
| `--mode` | offline | 转写模式：offline/online/2pass |
| `--ssl` | 1 | 是否使用 SSL（1=是，0=否） |
| `--chunk-size` | 5,10,5 | 流式处理的块大小 |
| `--use-itn` | 1 | 是否使用逆文本正规化 |
| `--final-wait` | 3.0 | 最终结果等待时间（秒） |
| `--output` | - | 输出文件路径（JSON 格式） |

### 转写模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| **offline** | 离线处理，准确度最高 | 已录制的音频文件 |
| **online** | 实时流式，延迟最低 | 实时语音输入 |
| **2pass** | 结合两者优势 | 需要平衡准确度和延迟 |

## 项目结构

```
clawfunasr/
├── README.md                    # 项目说明文档
├── SKILL.md                     # OpenCode Skill 定义
├── scripts/
│   ├── funasr_ws_client.py     # WebSocket 客户端
│   └── test_client.py          # 单元测试
├── references/
│   └── websocket-api.md        # API 参考文档
├── docs/
│   └── plans/                  # 开发计划
└── logs/                       # 日志目录
```

## OpenCode Skill 使用

本项目可直接作为 OpenCode skill 使用：

1. 将项目放置在 `.opencode/skills/funasr-asr/` 目录
2. OpenCode 会自动加载 `SKILL.md` 中定义的技能
3. AI 助手即可调用此技能进行语音转文字

详细使用说明请参考 [SKILL.md](./SKILL.md)。

## 音频格式支持

### 原生支持
- **WAV**（推荐）：PCM 16-bit, 16000 Hz, 单声道
- **PCM**：原始音频数据

### 通过 ffmpeg 转换支持
- MP3
- FLAC
- OGG
- 其他 ffmpeg 支持的格式

转换参数：
- 采样率：16000 Hz
- 声道：单声道
- 编码：PCM 16-bit

## 故障排除

### 连接被拒绝

```
检查服务器状态：
- 确认 FunASR 服务器正在运行
- 验证端口配置（默认 10095 或 10096）
- 检查防火墙设置
```

### SSL 错误

```
如果服务器未配置 SSL：
- 使用 --ssl 0 参数
- 或设置 ssl_enabled=False
```

### 无转写输出

```
检查音频文件：
- 确认文件格式正确
- 验证音频未损坏
- 检查采样率（推荐 16000 Hz）
```

### 高延迟

```
优化建议：
- 使用较小的模型
- 本地运行服务器减少网络延迟
- 选择合适的转写模式
```

## 开发

### 运行测试

```bash
python scripts/test_client.py
```

### 开发计划

查看 [docs/plans/](./docs/plans/) 了解详细开发计划。

## 相关链接

- [FunASR 官方仓库](https://github.com/alibaba/FunASR)
- [WebSocket API 参考](./references/websocket-api.md)
- [SenseVoice 模型](https://www.modelscope.cn/models/iic/SenseVoiceSmall)

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

---

**作者**: ClawFunASR  
**版本**: 1.0.0  
**更新日期**: 2026-02-20
