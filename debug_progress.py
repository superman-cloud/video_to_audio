#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试进度显示问题
"""

import sys
import time
from pathlib import Path
from video_audio_converter import VideoAudioConverter

def debug_progress_callback(current_time, total_time, percentage):
    """调试进度回调"""
    print(f"\r进度: {percentage:.1f}% | 时间: {current_time:.1f}s / {total_time:.1f}s", end='', flush=True)

def main():
    """调试主函数"""
    print("🔧 调试进度显示功能")
    print("=" * 50)
    
    # 创建转换器实例
    converter = VideoAudioConverter()
    
    # 检查FFmpeg
    if not converter.check_ffmpeg_availability():
        print("❌ FFmpeg不可用，请先安装FFmpeg")
        return
    
    # 提示用户选择测试文件
    test_file = input("请输入要测试的视频文件路径: ").strip().strip('"')
    
    if not test_file:
        print("❌ 未输入文件路径")
        return
        
    input_path = Path(test_file)
    if not input_path.exists():
        print(f"❌ 文件不存在: {test_file}")
        return
        
    if not input_path.is_file():
        print(f"❌ 不是文件: {test_file}")
        return
    
    # 检查文件格式
    if input_path.suffix.lower() not in converter.SUPPORTED_VIDEO_FORMATS:
        print(f"❌ 不支持的格式: {input_path.suffix}")
        return
    
    print(f"📹 测试文件: {input_path.name}")
    
    # 测试获取视频时长
    print("🔍 测试获取视频时长...")
    duration = converter._get_video_duration(input_path)
    if duration:
        print(f"✅ 视频时长: {duration:.2f}秒 ({duration//60:.0f}分{duration%60:.0f}秒)")
    else:
        print("⚠️ 无法获取视频时长，将使用估算进度")
    
    # 设置输出文件
    output_path = input_path.parent / f"{input_path.stem}_debug.mp3"
    
    print(f"📁 输出文件: {output_path.name}")
    print("🚀 开始转换测试...")
    print("-" * 50)
    
    # 开始转换
    start_time = time.time()
    success = converter.convert_single_file(
        input_path=input_path,
        output_path=output_path,
        audio_format='mp3',
        bitrate='128k',
        progress_callback=debug_progress_callback
    )
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    print(f"\n{'-' * 50}")
    if success:
        print(f"✅ 转换成功!")
        print(f"⏱️ 耗时: {elapsed:.2f}秒")
        if output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"📦 输出文件大小: {size_mb:.2f}MB")
    else:
        print(f"❌ 转换失败!")
        print(f"⏱️ 耗时: {elapsed:.2f}秒")

if __name__ == '__main__':
    main()