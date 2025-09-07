# VideoAudio Converter - 实时进度显示功能

## 新增功能

### 🎯 实时转换进度显示

现在支持在转换过程中实时显示每个文件的转换进度，包括：

- **当前文件名**: 显示正在转换的文件名
- **转换进度**: 实时显示转换百分比
- **时间信息**: 显示已转换时间/总时间
- **总体进度**: 显示整体批量转换进度

### 📊 GUI界面增强

#### 进度显示区域
- **总体进度条**: 显示批量转换的整体进度
- **当前文件进度条**: 显示当前正在转换文件的实时进度
- **文件名显示**: 显示当前正在处理的文件名
- **时间信息**: 显示转换时间和剩余时间估算

#### 支持场景
- ✅ 单文件转换 - 显示详细的转换进度和时间信息
- ✅ 批量转换 - 显示每个文件的实时转换进度
- ✅ 多线程转换 - 支持并发转换时的进度显示

### 🔧 技术实现

#### 核心功能
```python
def file_progress_callback(filename, current_time, total_time, percentage):
    """
    文件级进度回调函数
    
    Args:
        filename: 当前转换的文件名
        current_time: 已转换时间（秒）
        total_time: 总时长（秒）
        percentage: 转换进度百分比
    """
    print(f"文件: {filename} - 进度: {percentage:.1f}%")
```

#### GUI消息队列
- 使用线程安全的消息队列进行UI更新
- 支持实时进度数据传递
- 避免界面冻结，保持响应性

### 🚀 使用方法

#### 1. GUI界面使用
```bash
python video_audio_converter_gui.py
```

- 选择输入文件或目录
- 设置输出参数
- 点击"开始转换"
- 观察实时进度显示

#### 2. 命令行使用
```bash
python video_audio_converter.py /path/to/videos -o /path/to/output
```

#### 3. 编程接口使用
```python
from video_audio_converter import VideoAudioConverter

def my_progress_callback(filename, current_time, total_time, percentage):
    print(f"转换 {filename}: {percentage:.1f}%")

converter = VideoAudioConverter()
success, total, duplicates = converter.batch_convert(
    input_path="/path/to/videos",
    output_directory="/path/to/output",
    file_progress_callback=my_progress_callback
)
```

### 🧪 测试功能

使用测试脚本验证进度显示功能：

```bash
python test_progress.py
```

### 📈 性能优化

- **智能进度更新**: 避免过于频繁的UI更新
- **线程安全**: 多线程环境下的安全进度报告
- **内存优化**: 高效的进度数据传递机制

### 🎨 界面特性

- **实时更新**: 进度条和信息实时更新
- **清晰显示**: 直观的进度可视化
- **状态指示**: 清楚的转换状态提示
- **错误处理**: 转换失败时的明确提示

### 🔍 进度信息详情

#### 显示内容
- 当前转换文件名（截断长文件名）
- 转换进度百分比（精确到小数点后1位）
- 已转换时间 / 总时间（MM:SS格式）
- 整体批量进度（文件数/总文件数）

#### 更新频率
- 进度条更新：每0.1秒检查一次
- 时间信息更新：实时更新
- 文件切换：立即更新

### 💡 使用建议

1. **单文件转换**: 可以看到详细的转换进度和时间信息
2. **批量转换**: 建议使用适当的线程数（1-4个）以获得最佳性能
3. **大文件处理**: 进度显示特别有用，可以估算剩余时间
4. **网络存储**: 如果输出到网络位置，进度显示帮助监控传输状态

### 🐛 故障排除

#### 进度不更新
- 检查FFmpeg是否正确安装
- 确认视频文件格式支持
- 查看日志输出了解详细错误

#### 时间信息不准确
- 某些视频格式可能无法准确获取时长
- 损坏的视频文件可能导致时间计算错误
- 使用ffprobe验证视频文件完整性

### 📝 更新日志

#### v1.0.0 - 2025-09-07
- ✅ 新增实时文件转换进度显示
- ✅ 增强GUI界面进度可视化
- ✅ 支持批量转换进度监控
- ✅ 添加时间信息显示
- ✅ 优化多线程进度报告
- ✅ 改进用户体验和界面响应性

---

## 技术支持

如有问题或建议，请查看项目文档或提交Issue。