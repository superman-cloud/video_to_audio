#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VideoAudio Batch Converter - GUI启动器
快速启动图形界面版本

使用方法:
    python run_gui.py
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from video_audio_converter_gui import main
    
    if __name__ == '__main__':
        print("🎬 启动 VideoAudio Batch Converter GUI...")
        main()
        
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保所有依赖已安装: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ 启动失败: {e}")
    sys.exit(1)