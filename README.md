# 利用AI生成第一个小工具，欢迎使用
# VideoAudio Batch Converter

🎬 **视频转音频批量处理工具** - 一个高效、易用的命令行视频转音频转换器

## ✨ 功能特性

- 🔄 **批量转换**: 自动遍历目录下所有视频文件，支持递归扫描
- 📁 **智能文件命名**: 根据原视频文件路径自动生成对应音频文件名
- 🔍 **重复文件检测**: 自动识别并跳过内容相同的视频文件（通过MD5哈希值判断）
- 🎵 **多格式支持**: 支持主流视频和音频格式
- ⚡ **实时进度**: 使用进度条显示转换进度和状态
- 🛠️ **灵活配置**: 支持命令行参数和配置文件
- 📝 **详细日志**: 完整的转换日志和错误记录
- 🚫 **错误处理**: 完善的异常处理机制，单个文件失败不影响整体处理

## 📋 支持格式

### 输入视频格式
MP4, AVI, MOV, WMV, FLV, MKV, WEBM, MP4V, M4V, 3GP, MPG, MPEG, M2V, VOB, ASF

### 输出音频格式  
MP3, WAV, AAC, M4A, OGG, FLAC

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- FFmpeg (必须安装并添加到PATH)

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. FFmpeg安装

#### Windows
```bash
# 使用Chocolatey
choco install ffmpeg

# 或从官网下载: https://ffmpeg.org/download.html
```

#### macOS  
```bash
brew install ffmpeg
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

### 4. 基本使用

```bash
# 转换目录下所有视频为MP3
python video_audio_converter.py /path/to/videos

# 使用配置文件中的默认目录
python video_audio_converter.py

# 指定输出目录和格式
python video_audio_converter.py /path/to/videos -o /path/to/output -f wav

# 设置音频质量
python video_audio_converter.py /path/to/videos -q 320k

# 覆盖已存在文件
python video_audio_converter.py /path/to/videos --overwrite

# 不递归扫描子目录
python video_audio_converter.py /path/to/videos --no-recursive
```

## 📖 详细用法

### 命令行参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `input_dir` | - | 输入视频目录（可选，可在配置文件中设置） | 配置文件中的值 |
| `--output-dir` | `-o` | 输出音频目录 | 配置文件中的值或与输入同目录 |
| `--format` | `-f` | 输出音频格式 | mp3 |
| `--quality` | `-q` | 音频比特率 | 192k |
| `--overwrite` | - | 覆盖已存在文件 | false |
| `--no-recursive` | - | 不递归扫描子目录 | false |
| `--config` | - | 配置文件路径 | config.ini |
| `--version` | - | 显示版本信息 | - |

### 配置文件

可以通过 `config.ini` 文件设置默认参数:

```ini
[DEFAULT]
# 默认目录设置
default_input_directory = C:\Videos
default_output_directory = C:\Audio

# 音频设置
output_format = mp3
audio_bitrate = 192k
audio_sample_rate = 44100
ffmpeg_path = ffmpeg
overwrite_existing = false
preserve_directory_structure = true
```

配置好默认目录后，可以直接运行命令而不需要指定输入目录：
```bash
python video_audio_converter.py  # 使用配置文件中的默认目录
```

### 使用示例

#### 示例1: 基本转换
```bash
python video_audio_converter.py C:\Videos
```
- 转换 `C:\Videos` 目录下所有视频为MP3格式
- 输出到原视频同目录
- 递归处理子目录

#### 示例2: 高质量WAV转换
```bash
python video_audio_converter.py /home/user/videos -f wav -q 320k -o /home/user/audio
```
- 转换为WAV格式
- 320kbps高质量
- 输出到指定目录

#### 示例3: 使用配置文件默认设置
```bash
# 在 config.ini 中设置:
# default_input_directory = C:\Learning\Videos
# default_output_directory = C:\Learning\Audio

python video_audio_converter.py
```
- 自动使用配置文件中设置的默认目录
- 无需每次都指定输入和输出路径
- 适合经常处理特定目录的情况

#### 示例4: 仅处理当前目录
```bash
python video_audio_converter.py ./videos --no-recursive --overwrite
```
- 只处理当前目录，不包含子目录
- 覆盖已存在的音频文件

## 📊 输出信息

程序会显示详细的处理信息:

```
📂 输入目录: /path/to/videos
📁 输出目录: /path/to/output  
🎵 输出格式: MP3
🔊 音频质量: 192k
📊 递归扫描: 是
🔄 覆盖文件: 否
============================================================
🎬 开始处理 15 个视频文件...
转换进度: 100%|████████████| 15/15 [02:34<00:00]
============================================================
🎉 转换完成！
📊 处理统计:
   总文件数: 15
   ✅ 成功: 14  
   ❌ 失败: 1
   🔄 重复跳过: 3
   📈 成功率: 93.3%
   ⏱️  总耗时: 154.32 秒
   ⚡ 平均每文件: 11.02 秒
```

## 📝 日志记录

程序会自动创建 `logs/conversion.log` 文件记录详细的转换日志，包括:

- 文件扫描过程
- 转换成功/失败记录  
- 错误详情和原因
- 时间戳信息

## ⚠️ 注意事项

1. **FFmpeg依赖**: 确保系统已正确安装FFmpeg并可在命令行中调用
2. **磁盘空间**: 确保输出目录有足够的磁盘空间
3. **文件权限**: 确保对输入和输出目录有读写权限
4. **中文支持**: 完整支持中文路径和文件名
6. **重复文件检测**: 程序会自动识别并跳过内容相同的视频文件
7. **大文件处理**: 大视频文件转换可能需要较长时间，请耐心等待

## 🐛 故障排除

### 问题1: "FFmpeg not found"
**解决方案**: 
- 检查FFmpeg是否已安装
- 确认FFmpeg在系统PATH中
- 或在配置文件中指定FFmpeg完整路径

### 问题2: 转换失败
**解决方案**:
- 检查视频文件是否损坏
- 确认视频格式是否支持
- 查看日志文件获取详细错误信息

### 问题3: 权限错误  
**解决方案**:
- 确保对输入和输出目录有读写权限
- 在Windows上可能需要以管理员身份运行

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题或建议，请创建 [Issue](https://github.com/your-repo/video-audio-converter/issues)

---

**VideoAudio Batch Converter** - 让视频转音频变得简单高效！ 🎵
