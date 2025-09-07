#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试进度显示修复
"""

import subprocess
import sys
from pathlib import Path

def test_ffmpeg():
    """测试FFmpeg是否可用"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg可用")
            return True
        else:
            print("❌ FFmpeg不可用")
            return False
    except Exception as e:
        print(f"❌ FFmpeg测试失败: {e}")
        return False

def test_duration_detection():
    """测试时长检测"""
    from video_audio_converter import VideoAudioConverter
    
    converter = VideoAudioConverter()
    
    # 让用户提供一个测试文件
    test_file = input("请输入一个视频文件路径进行测试（或按回车跳过）: ").strip().strip('"')
    
    if test_file and Path(test_file).exists():
        print(f"🔍 测试文件: {test_file}")
        duration = converter._get_video_duration(Path(test_file))
        if duration:
            print(f"✅ 成功获取时长: {duration:.2f}秒")
            return True
        else:
            print("❌ 无法获取时长")
            return False
    else:
        print("⏭️ 跳过时长检测测试")
        return True

def main():
    """主测试函数"""
    print("🧪 快速测试进度显示修复")
    print("=" * 40)
    
    # 测试FFmpeg
    if not test_ffmpeg():
        print("请先安装FFmpeg")
        return
    
    # 测试时长检测
    if not test_duration_detection():
        print("时长检测有问题，但可能不影响转换")
    
    print("\n🎯 主要修复内容:")
    print("1. ✅ 改用stderr实时监控进度（更可靠）")
    print("2. ✅ 改进时长获取逻辑（支持多种方法）")
    print("3. ✅ 优化进度解析（避免卡在1%）")
    print("4. ✅ 增强错误处理和调试信息")
    
    print("\n🚀 建议测试步骤:")
    print("1. 运行 python debug_progress.py 测试单文件转换")
    print("2. 运行 python video_audio_converter_gui.py 测试GUI界面")
    print("3. 观察进度是否正常更新（不再卡在1%）")
    
    print("\n💡 如果仍有问题:")
    print("- 检查视频文件是否完整")
    print("- 尝试不同格式的视频文件")
    print("- 查看控制台输出的调试信息")

if __name__ == '__main__':
    main()