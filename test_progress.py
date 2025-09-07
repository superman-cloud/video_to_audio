#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试实时进度显示功能
"""

import time
from pathlib import Path
from video_audio_converter import VideoAudioConverter

def test_file_progress_callback(filename, current_time, total_time, percentage):
    """测试文件级进度回调"""
    print(f"文件: {filename}")
    print(f"进度: {percentage:.1f}%")
    if total_time > 0:
        current_min, current_sec = divmod(int(current_time), 60)
        total_min, total_sec = divmod(int(total_time), 60)
        print(f"时间: {current_min:02d}:{current_sec:02d} / {total_min:02d}:{total_sec:02d}")
    print("-" * 40)

def main():
    """测试主函数"""
    print("🎬 测试实时进度显示功能")
    print("=" * 50)
    
    # 创建转换器实例
    converter = VideoAudioConverter()
    
    # 检查FFmpeg
    if not converter.check_ffmpeg_availability():
        print("❌ FFmpeg不可用，请先安装FFmpeg")
        return
    
    # 提示用户选择测试文件或目录
    test_path = input("请输入要测试的视频文件或目录路径: ").strip().strip('"')
    
    if not test_path:
        print("❌ 未输入路径")
        return
        
    path_obj = Path(test_path)
    if not path_obj.exists():
        print(f"❌ 路径不存在: {test_path}")
        return
    
    # 设置输出目录
    output_dir = "test_output"
    Path(output_dir).mkdir(exist_ok=True)
    
    print(f"📂 输入路径: {test_path}")
    print(f"📁 输出目录: {output_dir}")
    print("🚀 开始转换测试...")
    print("=" * 50)
    
    # 开始转换，使用文件级进度回调
    success, total, duplicates = converter.batch_convert(
        input_path=test_path,
        output_directory=output_dir,
        audio_format='mp3',
        bitrate='128k',  # 使用较低比特率加快测试
        recursive=True,
        max_workers=1,  # 使用单线程便于观察进度
        file_progress_callback=test_file_progress_callback
    )
    
    print("=" * 50)
    print("🎉 测试完成!")
    print(f"📊 结果统计:")
    print(f"   总文件数: {total}")
    print(f"   成功转换: {success}")
    print(f"   失败数量: {total - success}")
    print(f"   重复跳过: {duplicates}")
    if total > 0:
        print(f"   成功率: {success/total*100:.1f}%")

if __name__ == '__main__':
    main()