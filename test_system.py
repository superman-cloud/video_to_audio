#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VideoAudio Batch Converter - 测试脚本
用于验证程序功能和FFmpeg可用性
"""

import sys
import os
from pathlib import Path
import subprocess

def test_python_version():
    """测试Python版本"""
    print("🐍 检查Python版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - 版本符合要求")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - 需要Python 3.8+")
        return False

def test_dependencies():
    """测试依赖包"""
    print("\n📦 检查依赖包...")
    
    # 测试tqdm
    try:
        import tqdm
        print(f"   ✅ tqdm {tqdm.__version__} - 已安装")
    except ImportError:
        print("   ❌ tqdm - 未安装，请运行: pip install tqdm")
        return False
    
    # 测试标准库
    try:
        import pathlib, configparser, argparse, logging, subprocess
        print("   ✅ 标准库 - 已导入")
    except ImportError as e:
        print(f"   ❌ 标准库导入失败: {e}")
        return False
    
    return True

def test_ffmpeg():
    """测试FFmpeg可用性"""
    print("\n🎬 检查FFmpeg...")
    
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            # 提取版本信息
            lines = result.stdout.split('\n')
            version_line = lines[0] if lines else "ffmpeg"
            print(f"   ✅ {version_line}")
            return True
        else:
            print("   ❌ FFmpeg调用失败")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ❌ FFmpeg调用超时")
        return False
    except FileNotFoundError:
        print("   ❌ FFmpeg未找到")
        print("   💡 请安装FFmpeg:")
        print("      Windows: choco install ffmpeg")
        print("      macOS:   brew install ffmpeg") 
        print("      Linux:   sudo apt install ffmpeg")
        return False
    except Exception as e:
        print(f"   ❌ FFmpeg检查出错: {e}")
        return False

def test_converter_import():
    """测试转换器模块导入"""
    print("\n🔧 测试转换器模块...")
    
    try:
        # 添加当前目录到路径
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        
        # 导入转换器
        from video_audio_converter import VideoAudioConverter
        
        # 创建实例
        converter = VideoAudioConverter()
        print("   ✅ 转换器模块 - 导入成功")
        print("   ✅ 转换器实例 - 创建成功")
        
        # 测试配置
        if converter.config:
            print("   ✅ 配置系统 - 加载成功")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 转换器模块测试失败: {e}")
        return False

def test_file_system():
    """测试文件系统权限"""
    print("\n📁 测试文件系统...")
    
    try:
        # 测试当前目录写权限
        test_file = Path("test_write.tmp")
        test_file.write_text("test")
        test_file.unlink()
        print("   ✅ 写权限 - 正常")
        
        # 测试logs目录创建
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        print("   ✅ logs目录 - 创建成功")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 文件系统测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🧪 VideoAudio Batch Converter - 系统测试")
    print("=" * 50)
    
    tests = [
        ("Python版本", test_python_version),
        ("依赖包", test_dependencies), 
        ("FFmpeg", test_ffmpeg),
        ("转换器模块", test_converter_import),
        ("文件系统", test_file_system)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"   ❌ {test_name}测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 项通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统已准备就绪。")
        print("\n💡 现在可以使用以下命令开始转换:")
        print("   python video_audio_converter.py /path/to/videos")
        return True
    else:
        print("⚠️  部分测试未通过，请解决上述问题后重试。")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)