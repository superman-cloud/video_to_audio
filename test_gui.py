#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI测试脚本 - 验证界面是否正常显示和工作

使用方法:
    python test_gui.py
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_gui():
    """测试GUI界面"""
    print("🧪 开始GUI测试...")
    
    try:
        # 导入GUI模块
        from video_audio_converter_gui import VideoAudioConverterGUI
        print("✅ GUI模块导入成功")
        
        # 创建测试窗口
        root = tk.Tk()
        print("✅ Tkinter根窗口创建成功")
        
        # 创建GUI应用
        app = VideoAudioConverterGUI(root)
        print("✅ GUI应用实例创建成功")
        
        # 检查界面元素是否存在
        assert hasattr(app, 'input_path_var'), "缺少输入路径变量"
        assert hasattr(app, 'output_dir_var'), "缺少输出目录变量"
        assert hasattr(app, 'start_button'), "缺少开始按钮"
        assert hasattr(app, 'log_text'), "缺少日志文本框"
        print("✅ 界面元素检查通过")
        
        # 检查变量初始值
        assert app.input_path_var.get() == "" or os.path.exists(app.input_path_var.get()), "输入路径无效"
        print("✅ 变量初始值检查通过")
        
        # 测试日志功能
        app.log_message("🧪 测试日志消息")
        log_content = app.log_text.get("1.0", tk.END)
        assert "测试日志消息" in log_content, "日志功能异常"
        print("✅ 日志功能测试通过")
        
        # 显示窗口进行视觉测试（3秒后自动关闭）
        print("🖥️ 显示GUI界面进行视觉测试（3秒后自动关闭）...")
        
        def close_after_delay():
            root.after(3000, lambda: root.destroy())
            
        close_after_delay()
        root.mainloop()
        
        print("✅ GUI测试完成 - 所有测试通过！")
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        print(f"错误详情:\n{traceback.format_exc()}")
        return False

if __name__ == '__main__':
    success = test_gui()
    if success:
        print("\n🎉 GUI测试成功！界面应该能够正常显示和使用。")
    else:
        print("\n💥 GUI测试失败！需要进一步排查问题。")
    
    sys.exit(0 if success else 1)