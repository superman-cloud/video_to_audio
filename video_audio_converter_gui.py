#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VideoAudio Batch Converter GUI - 视频转音频批量处理工具图形界面
基于 tkinter 的现代化可视化界面

作者: VideoAudio Converter Team
版本: 1.0.0
日期: 2025-09-07
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import os
import sys
from pathlib import Path
from video_audio_converter import VideoAudioConverter


class VideoAudioConverterGUI:
    """视频转音频转换器GUI界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 VideoAudio Batch Converter v1.0.0")
        self.root.geometry("950x750")  # 增大窗口尺寸以适应新布局
        self.root.minsize(850, 650)  # 调整最小尺寸
        self.root.resizable(True, True)
        
        # 设置窗口居中
        self.center_window()
        
        # 设置现代化主题和样式
        try:
            self.setup_styles()
        except Exception as e:
            print(f"⚠️ 样式设置失败: {e}")
        
        # 设置窗口图标（如果有的话）
        try:
            # self.root.iconbitmap('icon.ico')  # 可以添加图标文件
            pass
        except Exception as e:
            pass  # 静默处理图标设置失败
        
        # 初始化变量
        self.converter = None
        self.conversion_thread = None
        self.is_converting = False
        self.stop_conversion = False
        
        # 创建消息队列用于线程间通信
        self.message_queue = queue.Queue()
        
        # 创建界面
        try:
            self.create_widgets()
        except Exception as e:
            print(f"❌ 界面组件创建失败: {e}")
            raise
            
        # 加载配置
        try:
            self.load_config()
        except Exception as e:
            print(f"⚠️ 配置加载失败: {e}")
        
        # 显示欢迎信息
        self.show_welcome_message()
        
        # 启动消息处理
        try:
            self.process_queue()
        except Exception as e:
            print(f"❌ 消息处理启动失败: {e}")
        
    def center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_styles(self):
        """设置现代化样式"""
        style = ttk.Style()
        
        # 尝试使用现代主题
        available_themes = style.theme_names()
        
        if 'vista' in available_themes:
            style.theme_use('vista')
        elif 'winnative' in available_themes:
            style.theme_use('winnative')
        elif 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
        
    def create_widgets(self):
        """创建现代化GUI组件"""
        
        # 主框架直接放在root上（简化布局，避免Canvas的复杂性）
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题区域
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 30))
        header_frame.columnconfigure(0, weight=1)
        
        # 主标题
        title_label = ttk.Label(header_frame, text="🎬 VideoAudio Batch Converter", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 5))
        
        # 副标题
        subtitle_label = ttk.Label(header_frame, 
                                  text="专业的视频转音频批量处理工具 - 支持多种格式，高效转换", 
                                  font=('Segoe UI', 9))
        subtitle_label.grid(row=1, column=0, pady=(0, 10))
        
        # 分隔线
        separator = ttk.Separator(header_frame, orient='horizontal')
        separator.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 输入选择（目录或文件）
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        input_frame.columnconfigure(1, weight=1)
        
        ttk.Label(input_frame, text="📂 输入路径:").grid(row=0, column=0, sticky=tk.W)
        self.input_path_var = tk.StringVar()
        self.input_path_entry = ttk.Entry(input_frame, textvariable=self.input_path_var, width=50)
        self.input_path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        
        # 输入选择按钮框架
        input_btn_frame = ttk.Frame(input_frame)
        input_btn_frame.grid(row=0, column=2)
        
        ttk.Button(input_btn_frame, text="选择目录", command=self.browse_input_dir).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(input_btn_frame, text="选择文件", command=self.browse_input_file).pack(side=tk.LEFT)
        
        # 输出目录选择
        ttk.Label(main_frame, text="📁 输出目录:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_dir_var = tk.StringVar()
        self.output_dir_entry = ttk.Entry(main_frame, textvariable=self.output_dir_var, width=50)
        self.output_dir_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="浏览", command=self.browse_output_dir).grid(row=2, column=2, pady=5)
        
        # 设置选项框架
        options_frame = ttk.LabelFrame(main_frame, text="转换设置", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        options_frame.columnconfigure(1, weight=1)
        
        # 音频格式选择
        ttk.Label(options_frame, text="🎵 输出格式:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.format_var = tk.StringVar(value="mp3")
        format_combo = ttk.Combobox(options_frame, textvariable=self.format_var, 
                                   values=["mp3", "wav", "aac", "m4a", "ogg", "flac"],
                                   state="readonly", width=10)
        format_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # 音频质量选择
        ttk.Label(options_frame, text="🔊 音频质量:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        self.quality_var = tk.StringVar(value="192k")
        quality_combo = ttk.Combobox(options_frame, textvariable=self.quality_var,
                                    values=["64k", "128k", "192k", "256k", "320k"],
                                    state="readonly", width=10)
        quality_combo.grid(row=0, column=3, sticky=tk.W, padx=(5, 0), pady=5)
        
        # 线程数设置
        ttk.Label(options_frame, text="🧵 并发线程:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.threads_var = tk.StringVar(value="1")
        threads_spin = ttk.Spinbox(options_frame, from_=1, to=16, textvariable=self.threads_var, width=10)
        threads_spin.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # 选项复选框
        self.recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="📊 递归扫描子目录", 
                       variable=self.recursive_var).grid(row=1, column=2, columnspan=2, sticky=tk.W, padx=(20, 0), pady=5)
        
        self.overwrite_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="🔄 覆盖已存在文件", 
                       variable=self.overwrite_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 控制按钮框架
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        # 开始/停止按钮
        self.start_button = ttk.Button(control_frame, text="🎬 开始转换", 
                                      command=self.start_conversion)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="⏹️ 停止转换", 
                                     command=self.stop_conversion_func, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 清空日志按钮
        ttk.Button(control_frame, text="🗑️ 清空日志", 
                  command=self.clear_log).pack(side=tk.LEFT)
        
        # 状态标签（移到控制按钮下方）
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                    font=('Arial', 10, 'bold'))
        self.status_label.grid(row=5, column=0, columnspan=3, pady=5)
        
        # 日志显示区域（提前到第6行，增加高度权重）
        log_frame = ttk.LabelFrame(main_frame, text="📝 转换日志", padding="5")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=2)  # 给日志区域更多空间
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=80, 
                                                 font=('Consolas', 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 为日志文本框添加双击清空功能
        self.log_text.bind("<Double-Button-1>", self.on_log_double_click)
        
        # 进度显示框架（移到日志区域下方）
        progress_frame = ttk.LabelFrame(main_frame, text="📊 转换进度", padding="10")
        progress_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        progress_frame.columnconfigure(0, weight=1)
        
        # 总体进度条
        ttk.Label(progress_frame, text="总体进度:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.overall_progress_var = tk.DoubleVar()
        self.overall_progress_bar = ttk.Progressbar(progress_frame, variable=self.overall_progress_var, 
                                                   maximum=100, length=400)
        self.overall_progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 当前文件进度条（显示当前正在转换的文件进度）
        self.current_progress_label = ttk.Label(progress_frame, text="当前文件:")
        self.current_progress_var = tk.DoubleVar()
        self.current_progress_bar = ttk.Progressbar(progress_frame, variable=self.current_progress_var, 
                                                   maximum=100, length=400)
        
        # 当前文件名显示
        self.current_file_var = tk.StringVar()
        self.current_file_label = ttk.Label(progress_frame, textvariable=self.current_file_var, 
                                          font=('Arial', 9), foreground='blue')
        
        # 进度信息标签
        self.progress_info_var = tk.StringVar()
        self.progress_info_label = ttk.Label(progress_frame, textvariable=self.progress_info_var, 
                                           font=('Arial', 9))
        self.progress_info_label.grid(row=5, column=0, sticky=tk.W, pady=(5, 0))
        
    def browse_input_dir(self):
        """浏览输入目录"""
        directory = filedialog.askdirectory(title="选择输入视频目录")
        if directory:
            self.input_path_var.set(directory)
            
    def browse_input_file(self):
        """浏览输入视频文件"""
        # 支持的视频格式
        video_formats = [
            ("视频文件", "*.mp4;*.avi;*.mov;*.wmv;*.flv;*.mkv;*.webm;*.mp4v;*.m4v;*.3gp;*.mpg;*.mpeg;*.m2v;*.vob;*.asf"),
            ("MP4文件", "*.mp4"),
            ("AVI文件", "*.avi"),
            ("MOV文件", "*.mov"),
            ("所有文件", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=video_formats
        )
        if filename:
            # 验证是否为支持的视频格式
            supported_formats = {'.mp4', '.avi', '.mov', '.wmv', '.flv', 
                               '.mkv', '.webm', '.mp4v', '.m4v', '.3gp',
                               '.mpg', '.mpeg', '.m2v', '.vob', '.asf'}
            
            file_ext = Path(filename).suffix.lower()
            if file_ext in supported_formats:
                self.input_path_var.set(filename)
                self.log_message(f"✅ 已选择视频文件: {Path(filename).name}")
            else:
                messagebox.showerror("格式错误", 
                                   f"不支持的文件格式: {file_ext}\n"
                                   f"支持的格式: {', '.join(sorted(supported_formats))}")
                self.log_message(f"❌ 不支持的文件格式: {file_ext}")
            
    def browse_output_dir(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(title="选择输出音频目录")
        if directory:
            self.output_dir_var.set(directory)
            
    def show_welcome_message(self):
        """显示欢迎信息"""
        self.log_message("🎉 欢迎使用 VideoAudio Batch Converter!")
        self.log_message("📝 转换日志将在这里显示")
        self.log_message("📌 使用说明: 选择视频文件或目录 → 设置输出目录 → 点击开始转换")
        self.log_message("✨ 支持格式: MP4, AVI, MOV, WMV, FLV, MKV, WEBM 等")
        self.log_message("-" * 60)
        
    def load_config(self):
        """加载配置文件"""
        try:
            self.converter = VideoAudioConverter()
            
            # 从配置文件加载默认值
            config = self.converter.config
            
            default_input = config.get('DEFAULT', 'default_input_directory', fallback='')
            if default_input and os.path.exists(default_input):
                self.input_path_var.set(default_input)
                
            default_output = config.get('DEFAULT', 'default_output_directory', fallback='')
            if default_output:
                self.output_dir_var.set(default_output)
                
            self.format_var.set(config.get('DEFAULT', 'output_format', fallback='mp3'))
            
            bitrate = config.get('DEFAULT', 'audio_bitrate', fallback='192k')
            self.quality_var.set(bitrate)
            
            max_jobs = config.get('DEFAULT', 'max_concurrent_jobs', fallback='1')
            self.threads_var.set(max_jobs)
            
            self.overwrite_var.set(config.getboolean('DEFAULT', 'overwrite_existing', fallback=False))
            
            self.log_message("✅ 配置文件加载成功")
            
        except Exception as e:
            self.log_message(f"⚠️ 配置文件加载失败: {e}")
            
    def log_message(self, message):
        """添加日志消息"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
        # 限制日志长度，防止占用过多内存
        lines = self.log_text.get("1.0", tk.END).split('\n')
        if len(lines) > 1000:  # 保留最近的1000行
            self.log_text.delete("1.0", "100.0")
            self.log_text.see(tk.END)
        
    def clear_log(self):
        """清空日志"""
        if messagebox.askyesno("清空日志", "确定要清空所有日志内容吗？"):
            self.log_text.delete(1.0, tk.END)
            self.log_message("🗑️ 日志已清空")
            
    def on_log_double_click(self, event):
        """双击日志区域时的处理"""
        self.clear_log()
        
    def validate_inputs(self):
        """验证输入参数"""
        input_path = self.input_path_var.get()
        
        if not input_path:
            messagebox.showerror("错误", "请选择输入目录或文件")
            return False
            
        if not os.path.exists(input_path):
            messagebox.showerror("错误", "输入路径不存在")
            return False
        
        # 如果是文件，验证格式
        if os.path.isfile(input_path):
            supported_formats = {'.mp4', '.avi', '.mov', '.wmv', '.flv', 
                               '.mkv', '.webm', '.mp4v', '.m4v', '.3gp',
                               '.mpg', '.mpeg', '.m2v', '.vob', '.asf'}
            
            file_ext = Path(input_path).suffix.lower()
            if file_ext not in supported_formats:
                messagebox.showerror("格式错误", 
                                   f"不支持的文件格式: {file_ext}\n"
                                   f"支持的格式: {', '.join(sorted(supported_formats))}")
                return False
            
        if not self.output_dir_var.get():
            messagebox.showerror("错误", "请选择输出目录")
            return False
            
        return True
        
    def start_conversion(self):
        """开始转换"""
        if not self.validate_inputs():
            return
            
        if self.is_converting:
            messagebox.showwarning("警告", "转换正在进行中")
            return
            
        # 更新UI状态
        self.is_converting = True
        self.stop_conversion = False
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.overall_progress_var.set(0)
        self.current_progress_var.set(0)
        self.progress_info_var.set("")
        self.status_var.set("正在转换...")
        
        # 显示当前文件进度条（无论单文件还是批量都显示）
        self.current_progress_label.grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        self.current_progress_bar.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        self.current_file_label.grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        
        # 清空日志
        self.clear_log()
        
        # 判断输入类型并显示相应信息
        input_path = self.input_path_var.get()
        if os.path.isfile(input_path):
            self.log_message(f"🎬 开始转换单个视频文件: {Path(input_path).name}")
        else:
            self.log_message("🎬 开始批量视频转音频转换...")
        
        # 启动转换线程
        self.conversion_thread = threading.Thread(target=self.conversion_worker, daemon=True)
        self.conversion_thread.start()
        
    def stop_conversion_func(self):
        """停止转换"""
        if self.is_converting:
            self.stop_conversion = True
            self.log_message("⏹️ 正在停止转换...")
            self.status_var.set("正在停止...")
            
    def conversion_worker(self):
        """转换工作线程"""
        try:
            # 获取参数
            input_path = self.input_path_var.get()
            output_dir = self.output_dir_var.get()
            audio_format = self.format_var.get()
            bitrate = self.quality_var.get()
            recursive = self.recursive_var.get()
            max_workers = int(self.threads_var.get())
            
            # 更新转换器配置
            if self.overwrite_var.get():
                self.converter.config.set('DEFAULT', 'overwrite_existing', 'true')
            else:
                self.converter.config.set('DEFAULT', 'overwrite_existing', 'false')
            
            # 扫描文件
            if os.path.isfile(input_path):
                self.message_queue.put(("log", f"🔎 验证视频文件: {Path(input_path).name}"))
            else:
                self.message_queue.put(("log", "🔎 正在扫描视频文件..."))
                
            video_files = self.converter.scan_video_files(input_path, recursive)
            
            if not video_files:
                if os.path.isfile(input_path):
                    self.message_queue.put(("log", "❌ 文件格式不支持或验证失败"))
                else:
                    self.message_queue.put(("log", "❌ 没有找到视频文件"))
                self.message_queue.put(("complete", (0, 0, 0)))
                return
                
            total_files = len(video_files)
            if os.path.isfile(input_path):
                self.message_queue.put(("log", f"✅ 文件验证通过，准备转换"))
            else:
                self.message_queue.put(("log", f"📋 找到 {total_files} 个视频文件"))
            
            # 开始转换
            success_count = 0
            is_single_file = total_files == 1
            
            # 定义文件级进度回调函数（用于显示当前文件转换进度）
            def file_progress_callback(filename, current_time, total_time, percentage):
                if not self.stop_conversion:
                    self.message_queue.put(("current_progress", percentage))
                    self.message_queue.put(("current_file", filename))
                    
                    # 格式化时间显示
                    if total_time > 0 and current_time <= total_time:
                        # 有准确的总时长
                        current_min, current_sec = divmod(int(current_time), 60)
                        total_min, total_sec = divmod(int(total_time), 60)
                        time_info = f"{current_min:02d}:{current_sec:02d} / {total_min:02d}:{total_sec:02d}"
                        self.message_queue.put(("progress_info", 
                                              f"转换进度: {percentage:.1f}% - {time_info}"))
                    elif current_time > 0:
                        # 只有当前处理时间，没有总时长
                        current_min, current_sec = divmod(int(current_time), 60)
                        time_info = f"已处理: {current_min:02d}:{current_sec:02d}"
                        self.message_queue.put(("progress_info", 
                                              f"转换进度: {percentage:.1f}% - {time_info}"))
                    else:
                        # 只显示百分比
                        self.message_queue.put(("progress_info", 
                                              f"转换进度: {percentage:.1f}%"))
            
            for i, video_file in enumerate(video_files):
                if self.stop_conversion:
                    self.message_queue.put(("log", "⏹️ 用户停止了转换"))
                    break
                    
                # 更新总体进度
                overall_progress = (i / total_files) * 100
                self.message_queue.put(("overall_progress", overall_progress))
                self.message_queue.put(("status", f"正在处理: {video_file.name}"))
                self.message_queue.put(("log", f"📹 [{i+1}/{total_files}] {video_file.name}"))
                
                # 重置当前文件进度
                self.message_queue.put(("current_progress", 0))
                self.message_queue.put(("current_file", video_file.name))
                self.message_queue.put(("progress_info", "正在初始化转换..."))
                
                # 定义单文件进度回调函数（仅单文件时使用，用于兼容性）
                def progress_callback(current_time, total_time, percentage):
                    if is_single_file and not self.stop_conversion:
                        file_progress_callback(video_file.name, current_time, total_time, percentage)
                
                # 转换单个文件
                callback = progress_callback if is_single_file else None
                success, _, audio_file = self.converter._convert_single_task(
                    video_file, output_dir, audio_format, bitrate, callback, file_progress_callback
                )
                
                if success:
                    success_count += 1
                    self.message_queue.put(("log", f"✅ 转换成功: {audio_file.name}"))
                    self.message_queue.put(("current_progress", 100))
                    self.message_queue.put(("progress_info", "转换完成!"))
                else:
                    self.message_queue.put(("log", f"❌ 转换失败: {video_file.name}"))
                    self.message_queue.put(("progress_info", "转换失败"))
                    
            # 完成
            self.message_queue.put(("overall_progress", 100))
            self.message_queue.put(("complete", (success_count, total_files, len(self.converter.duplicate_files))))
            
        except Exception as e:
            self.message_queue.put(("log", f"❌ 转换过程出错: {e}"))
            self.message_queue.put(("complete", (0, 0, 0)))
            
    def process_queue(self):
        """处理消息队列"""
        try:
            while True:
                message_type, data = self.message_queue.get_nowait()
                
                if message_type == "log":
                    self.log_message(data)
                elif message_type == "overall_progress":
                    self.overall_progress_var.set(data)
                elif message_type == "current_progress":
                    self.current_progress_var.set(data)
                elif message_type == "current_file":
                    self.current_file_var.set(f"正在转换: {data}")
                elif message_type == "progress_info":
                    self.progress_info_var.set(data)
                elif message_type == "status":
                    self.status_var.set(data)
                elif message_type == "complete":
                    success, total, duplicates = data
                    self.conversion_complete(success, total, duplicates)
                    
        except queue.Empty:
            pass
            
        # 继续处理队列
        self.root.after(100, self.process_queue)
        
    def conversion_complete(self, success, total, duplicates):
        """转换完成处理"""
        self.is_converting = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        # 清空当前文件显示
        self.current_file_var.set("")
        self.current_progress_var.set(0)
        
        if self.stop_conversion:
            self.status_var.set("已停止")
            self.progress_info_var.set("转换已停止")
            self.log_message("⏹️ 转换已停止")
        else:
            self.status_var.set("转换完成")
            self.progress_info_var.set(f"全部完成! 成功: {success}/{total}")
            self.log_message("🎉 转换完成!")
            
        # 显示统计信息
        self.log_message("=" * 50)
        self.log_message(f"📊 转换统计:")
        self.log_message(f"   总文件数: {total}")
        self.log_message(f"   ✅ 成功: {success}")
        self.log_message(f"   ❌ 失败: {total - success}")
        if duplicates > 0:
            self.log_message(f"   🔄 重复跳过: {duplicates}")
        if total > 0:
            self.log_message(f"   📈 成功率: {success/total*100:.1f}%")
            
        # 显示完成对话框
        if not self.stop_conversion and total > 0:
            messagebox.showinfo("转换完成", 
                              f"转换完成!\n成功: {success}/{total}\n成功率: {success/total*100:.1f}%")


def main():
    """主函数"""
    try:
        # 创建主窗口
        root = tk.Tk()
        
        # 设置主题样式
        try:
            style = ttk.Style()
            # 尝试使用现代主题
            available_themes = style.theme_names()
            
            if 'vista' in available_themes:
                style.theme_use('vista')
            elif 'winnative' in available_themes:
                style.theme_use('winnative')
            elif 'clam' in available_themes:
                style.theme_use('clam')
        except Exception as e:
            print(f"⚠️ 主题设置失败: {e}，使用默认主题")
        
        # 创建应用实例
        try:
            app = VideoAudioConverterGUI(root)
        except Exception as e:
            print(f"❌ GUI应用创建失败: {e}")
            messagebox.showerror("启动错误", f"GUI初始化失败:\n{e}")
            return
        
        # 设置窗口关闭事件
        def on_closing():
            try:
                if app.is_converting:
                    if messagebox.askokcancel("退出", "转换正在进行中，确定要退出吗？"):
                        app.stop_conversion = True
                        root.destroy()
                else:
                    root.destroy()
            except Exception as e:
                print(f"⚠️ 窗口关闭处理错误: {e}")
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # 显示窗口并启动GUI
        root.deiconify()  # 确保窗口显示
        root.lift()       # 将窗口提升到最前面
        root.focus_force()  # 强制获取焦点
        
        # 启动GUI主事件循环
        root.mainloop()
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有依赖已安装: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        print(f"错误详情:\n{traceback.format_exc()}")


if __name__ == '__main__':
    main()