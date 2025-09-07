#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VideoAudio Batch Converter - 视频转音频批量处理工具
功能：遍历指定目录下的所有视频文件，批量转换为音频格式

作者: VideoAudio Converter Team
版本: 1.0.0
日期: 2025-09-07
"""

import os
import sys
import argparse
import logging
import subprocess
import configparser
import hashlib
import re
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Set
from tqdm import tqdm
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


class VideoAudioConverter:
    """视频转音频转换器 - 核心处理类"""
    
    # 支持的视频格式
    SUPPORTED_VIDEO_FORMATS = {
        '.mp4', '.avi', '.mov', '.wmv', '.flv', 
        '.mkv', '.webm', '.mp4v', '.m4v', '.3gp',
        '.mpg', '.mpeg', '.m2v', '.vob', '.asf'
    }
    
    # 支持的音频格式及对应编码器
    SUPPORTED_AUDIO_FORMATS = {
        'mp3': 'libmp3lame',
        'wav': 'pcm_s16le', 
        'aac': 'aac',
        'm4a': 'aac',
        'ogg': 'libvorbis',
        'flac': 'flac'
    }
    
    def __init__(self, config_file: str = 'config.ini'):
        """
        初始化转换器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.logger = None
        self.config = None
        # 重复文件检测相关
        self.file_hashes: Dict[str, Path] = {}  # 存储文件哈希值和路径的映射
        self.duplicate_files: Set[Path] = set()  # 存储重复文件路径
        self.processed_files: Set[Path] = set()  # 存储已处理文件路径
        
        # 多线程相关
        self._lock = threading.Lock()  # 线程锁，用于保护共享资源
        
        self.setup_logging()
        self.load_config()
        
    def setup_logging(self):
        """设置日志系统"""
        # 创建logs目录
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # 配置日志格式
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        # 设置日志处理器
        handlers = [
            logging.FileHandler(
                log_dir / 'conversion.log', 
                encoding='utf-8'
            ),
            logging.StreamHandler(sys.stdout)
        ]
        
        # 配置logging
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=handlers,
            force=True
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("日志系统初始化完成")
        
    def load_config(self):
        """加载配置文件"""
        self.config = configparser.ConfigParser()
        
        if os.path.exists(self.config_file):
            try:
                self.config.read(self.config_file, encoding='utf-8')
                self.logger.info(f"已加载配置文件: {self.config_file}")
            except Exception as e:
                self.logger.warning(f"配置文件读取失败: {e}，将使用默认配置")
                self.create_default_config()
        else:
            self.create_default_config()
            
    def create_default_config(self):
        """创建默认配置文件"""
        self.config['DEFAULT'] = {
            'default_input_directory': '',
            'default_output_directory': '',
            'output_format': 'mp3',
            'audio_bitrate': '192k',
            'audio_sample_rate': '44100',
            'ffmpeg_path': 'ffmpeg',
            'overwrite_existing': 'false',
            'preserve_directory_structure': 'true',
            'max_concurrent_jobs': '1'
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
            self.logger.info(f"已创建默认配置文件: {self.config_file}")
        except Exception as e:
            self.logger.warning(f"无法创建配置文件: {e}")
        
    def check_ffmpeg_availability(self) -> bool:
        """检查FFmpeg是否可用"""
        ffmpeg_path = self.config.get('DEFAULT', 'ffmpeg_path', fallback='ffmpeg')
        
        try:
            result = subprocess.run(
                [ffmpeg_path, '-version'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',  # 忽略编码错误
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info("FFmpeg检查通过")
                return True
            else:
                self.logger.error("FFmpeg不可用")
                return False
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.error(f"FFmpeg检查失败: {e}")
            return False
            
    def calculate_file_hash(self, file_path: Path, chunk_size: int = 8192) -> Optional[str]:
        """
        计算文件的MD5哈希值
        
        Args:
            file_path: 文件路径
            chunk_size: 读取块大小
            
        Returns:
            文件MD5哈希值，失败返回None
        """
        try:
            hash_md5 = hashlib.md5()
            
            with open(file_path, 'rb') as f:
                # 分块读取文件，防止大文件占用过多内存
                while chunk := f.read(chunk_size):
                    hash_md5.update(chunk)
                    
            return hash_md5.hexdigest()
            
        except Exception as e:
            self.logger.warning(f"计算文件哈希失败 {file_path.name}: {e}")
            return None
            
    def is_duplicate_file(self, file_path: Path) -> bool:
        """
        检查文件是否为重复文件
        
        Args:
            file_path: 要检查的文件路径
            
        Returns:
            True 如果是重复文件，False 否则
        """
        try:
            # 检查文件是否存在
            if not file_path.exists() or not file_path.is_file():
                return False
                
            # 先检查文件大小，大小不同的文件肯定不重复
            file_size = file_path.stat().st_size
            
            # 计算文件哈希值
            file_hash = self.calculate_file_hash(file_path)
            
            if file_hash is None:
                # 如果无法计算哈希值，认为不重复（保守做法）
                return False
                
            # 检查哈希值是否已存在
            if file_hash in self.file_hashes:
                existing_file = self.file_hashes[file_hash]
                
                # 检查原文件是否仍然存在
                if existing_file.exists():
                    self.logger.info(f"🔄 检测到重复文件: {file_path.name}")
                    self.logger.info(f"   原文件: {existing_file}")
                    self.logger.info(f"   重复文件: {file_path}")
                    
                    # 记录重复文件
                    self.duplicate_files.add(file_path)
                    return True
                else:
                    # 原文件已不存在，更新映射
                    self.file_hashes[file_hash] = file_path
                    return False
            else:
                # 新文件，记录哈希值
                self.file_hashes[file_hash] = file_path
                return False
                
        except Exception as e:
            self.logger.warning(f"重复文件检查失败 {file_path.name}: {e}")
            return False
        
    def scan_video_files(self, directory: str, recursive: bool = True) -> List[Path]:
        """
        扫描目录下的所有视频文件（包括重复文件检测）
        
        Args:
            directory: 要扫描的目录路径
            recursive: 是否递归扫描子目录
            
        Returns:
            视频文件路径列表（已排除重复文件）
        """
        directory = Path(directory)
        video_files = []
        
        if not directory.exists():
            self.logger.error(f"目录不存在: {directory}")
            return video_files
            
        if not directory.is_dir():
            self.logger.error(f"路径不是目录: {directory}")
            return video_files
            
        # 设置扫描模式
        pattern = '**/*' if recursive else '*'
        
        self.logger.info(f"🔎 开始扫描目录: {directory}")
        
        # 重置重复文件检测状态
        self.file_hashes.clear()
        self.duplicate_files.clear()
        
        duplicate_count = 0
        total_scanned = 0
        
        try:
            for file_path in directory.glob(pattern):
                if (file_path.is_file() and 
                    file_path.suffix.lower() in self.SUPPORTED_VIDEO_FORMATS):
                    total_scanned += 1
                    
                    # 检查是否为重复文件
                    if self.is_duplicate_file(file_path):
                        duplicate_count += 1
                        self.logger.info(f"⛔ 跳过重复文件: {file_path.name}")
                    else:
                        video_files.append(file_path)
                        
        except Exception as e:
            self.logger.error(f"扫描目录时出错: {e}")
            
        # 按文件名排序
        video_files = sorted(video_files, key=lambda x: x.name.lower())
        
        self.logger.info(f"📋 扫描统计:")
        self.logger.info(f"   总文件数: {total_scanned}")
        self.logger.info(f"   重复文件: {duplicate_count}")
        self.logger.info(f"   待处理文件: {len(video_files)}")
        
        return video_files
        
    def clean_filename(self, filename: str) -> str:
        """
        清理文件名，移除或替换特殊字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            清理后的文件名
        """
        # 定义需要移除或替换的特殊字符
        # Windows 文件名不允许的字符: < > : " | ? * \ /
        # 其他可能导致问题的字符
        
        # 先移除或替换特殊字符
        cleaned = filename
        
        # 替换常见的特殊字符
        replacements = {
            '<': '',
            '>': '',
            ':': '-',
            '"': '',
            '|': '-',
            '?': '',
            '*': '',
            '\\': '',
            '/': '-',
            '【': '[',
            '】': ']',
            '（': '(',
            '）': ')',
            '？': '',
            '！': '',
            '：': '-',
            '；': '',
            '，': ',',
            '。': '.',
            '、': '',
            '～': '-',
            '…': '...',
            '—': '-',
            '–': '-',
            ''': "'",
            ''': "'",
            '"': '"',
            '"': '"',
        }
        
        for old_char, new_char in replacements.items():
            cleaned = cleaned.replace(old_char, new_char)
        
        # 移除连续的空格和特殊字符
        cleaned = re.sub(r'\s+', ' ', cleaned)  # 多个空格替换为单个空格
        cleaned = re.sub(r'[-_]+', '-', cleaned)  # 多个连字符替换为单个
        cleaned = re.sub(r'\.+', '.', cleaned)  # 多个点替换为单个
        
        # 移除开头和结尾的空格、点、连字符
        cleaned = cleaned.strip(' .-_')
        
        # 如果文件名为空或只有扩展名，使用默认名称
        if not cleaned or cleaned.startswith('.'):
            cleaned = 'converted_file'
        
        # 限制文件名长度（Windows 路径限制）
        if len(cleaned) > 200:
            cleaned = cleaned[:200]
        
        self.logger.debug(f"文件名清理: '{filename}' -> '{cleaned}'")
        
        return cleaned
    
    def generate_audio_filename(self, 
                              video_path: Path, 
                              output_dir: Optional[str] = None,
                              output_format: str = 'mp3') -> Path:
        """
        根据视频文件路径生成音频文件名
        
        Args:
            video_path: 原视频文件路径
            output_dir: 输出目录（可选）
            output_format: 输出音频格式
            
        Returns:
            生成的音频文件路径
        """
        # 清理文件名
        clean_stem = self.clean_filename(video_path.stem)
        
        if output_dir:
            output_path = Path(output_dir)
            
            # 如果需要保持目录结构
            if self.config.getboolean('DEFAULT', 'preserve_directory_structure', fallback=True):
                # 计算相对路径
                try:
                    # 获取视频文件相对于其根目录的路径
                    relative_dir = video_path.parent.name if video_path.parent != video_path.anchor else ""
                    if relative_dir:
                        # 也清理目录名
                        clean_relative_dir = self.clean_filename(relative_dir)
                        output_path = output_path / clean_relative_dir
                except:
                    # 如果计算相对路径失败，直接使用输出目录
                    pass
            
            # 创建输出目录
            output_path.mkdir(parents=True, exist_ok=True)
            audio_filename = output_path / f"{clean_stem}.{output_format}"
        else:
            # 输出到原文件同目录
            audio_filename = video_path.parent / f"{clean_stem}.{output_format}"
            
        return audio_filename
        
    def convert_single_file(self, 
                          input_path: Path, 
                          output_path: Path,
                          audio_format: str = 'mp3', 
                          bitrate: str = '192k') -> bool:
        """
        转换单个视频文件为音频
        
        Args:
            input_path: 输入视频文件路径
            output_path: 输出音频文件路径
            audio_format: 音频格式
            bitrate: 音频比特率
            
        Returns:
            转换是否成功
        """
        try:
            # 检查输出文件是否已存在
            if (output_path.exists() and 
                not self.config.getboolean('DEFAULT', 'overwrite_existing', fallback=False)):
                self.logger.info(f"跳过已存在的文件: {output_path.name}")
                return True
                
            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
                
            # 获取音频编码器
            codec = self.SUPPORTED_AUDIO_FORMATS.get(audio_format.lower(), 'libmp3lame')
            ffmpeg_path = self.config.get('DEFAULT', 'ffmpeg_path', fallback='ffmpeg')
            sample_rate = self.config.get('DEFAULT', 'audio_sample_rate', fallback='44100')
            
            # 构建FFmpeg命令
            cmd = [
                ffmpeg_path,
                '-i', str(input_path),  # 输入文件
                '-vn',                  # 不包含视频流
                '-acodec', codec,       # 音频编码器
                '-ab', bitrate,         # 音频比特率
                '-ar', sample_rate,     # 采样率
                '-y' if self.config.getboolean('DEFAULT', 'overwrite_existing', fallback=False) else '-n',
                str(output_path)        # 输出文件
            ]
            
            # 执行转换
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',  # 忽略编码错误
                timeout=300,  # 5分钟超时
                check=True
            )
            
            # 验证输出文件是否创建成功
            if output_path.exists() and output_path.stat().st_size > 0:
                self.logger.info(f"✓ 转换成功: {input_path.name} -> {output_path.name}")
                return True
            else:
                self.logger.error(f"✗ 转换失败: 输出文件未创建或为空")
                return False
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"✗ FFmpeg转换失败 {input_path.name}: {e.stderr if e.stderr else str(e)}")
            return False
        except subprocess.TimeoutExpired:
            self.logger.error(f"✗ 转换超时 {input_path.name}: 操作超过5分钟")
            return False
        except Exception as e:
            self.logger.error(f"✗ 转换出错 {input_path.name}: {str(e)}")
            return False
            
    def _convert_single_task(self, video_file: Path, output_directory: Optional[str], 
                           audio_format: str, bitrate: str) -> Tuple[bool, Path, Path]:
        """
        单个文件转换任务（用于多线程）
        
        Returns:
            (是否成功, 输入文件路径, 输出文件路径)
        """
        try:
            # 生成输出文件路径
            audio_file = self.generate_audio_filename(
                video_file, output_directory, audio_format
            )
            
            # 如果文件名被清理了，显示信息
            if video_file.stem != audio_file.stem:
                with self._lock:
                    self.logger.info(f"🔧 文件名已清理: {video_file.name} -> {audio_file.name}")
            
            # 转换文件
            success = self.convert_single_file(video_file, audio_file, audio_format, bitrate)
            return success, video_file, audio_file
            
        except Exception as e:
            with self._lock:
                self.logger.error(f"任务执行出错 {video_file.name}: {e}")
            return False, video_file, Path("")

    def batch_convert(self, 
                     input_directory: str, 
                     output_directory: Optional[str] = None,
                     audio_format: str = 'mp3',
                     bitrate: str = '192k',
                     recursive: bool = True,
                     max_workers: Optional[int] = None) -> Tuple[int, int, int]:
        """
        批量转换视频文件
        
        Args:
            input_directory: 输入目录
            output_directory: 输出目录
            audio_format: 音频格式
            bitrate: 音频比特率
            recursive: 是否递归扫描
            max_workers: 最大线程数，None表示使用配置文件中的设置
            
        Returns:
            (成功数量, 总数量, 重复数量)
        """
        
        # 验证FFmpeg可用性
        if not self.check_ffmpeg_availability():
            self.logger.error("FFmpeg不可用，请检查安装和配置")
            return 0, 0, 0
        
        # 扫描视频文件（包括重复文件检测）
        video_files = self.scan_video_files(input_directory, recursive)
        duplicate_count = len(self.duplicate_files)
        
        if not video_files:
            self.logger.warning("没有找到任何需要处理的视频文件")
            return 0, 0, duplicate_count
            
        success_count = 0
        total_count = len(video_files)
        
        # 确定线程数
        if max_workers is None:
            max_workers = self.config.getint('DEFAULT', 'max_concurrent_jobs', fallback=1)
        
        self.logger.info(f"🎥 开始批量转换 {total_count} 个文件")
        if duplicate_count > 0:
            print(f"\n🔄 检测到 {duplicate_count} 个重复文件，已跳过")
        print(f"\n🎥 开始处理 {total_count} 个视频文件...")
        print(f"🧵 使用线程数: {max_workers}")
        
        if max_workers == 1:
            # 单线程处理
            with tqdm(
                video_files, 
                desc="转换进度", 
                unit="文件",
                ncols=100,
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
            ) as pbar:
                
                for video_file in pbar:
                    # 更新进度条描述
                    pbar.set_description(f"📹 {video_file.name[:30]}...")
                    
                    success, _, audio_file = self._convert_single_task(
                        video_file, output_directory, audio_format, bitrate
                    )
                    
                    if success:
                        success_count += 1
                        
                    # 更新进度条后缀信息
                    pbar.set_postfix({
                        '✅': success_count,
                        '❌': total_count - success_count,
                        '🔄': duplicate_count,
                        '当前': audio_file.name[:15] + "..." if audio_file.name and len(audio_file.name) > 15 else str(audio_file.name)
                    })
        else:
            # 多线程处理
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有任务
                future_to_file = {
                    executor.submit(self._convert_single_task, video_file, output_directory, audio_format, bitrate): video_file
                    for video_file in video_files
                }
                
                # 使用tqdm显示进度
                with tqdm(
                    total=total_count,
                    desc="转换进度", 
                    unit="文件",
                    ncols=100,
                    bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
                ) as pbar:
                    
                    for future in as_completed(future_to_file):
                        video_file = future_to_file[future]
                        
                        try:
                            success, _, audio_file = future.result()
                            
                            if success:
                                success_count += 1
                            
                            # 更新进度条
                            pbar.update(1)
                            pbar.set_description(f"📹 {video_file.name[:30]}...")
                            pbar.set_postfix({
                                '✅': success_count,
                                '❌': pbar.n - success_count,
                                '🔄': duplicate_count,
                                '线程': max_workers
                            })
                            
                        except Exception as e:
                            self.logger.error(f"任务执行异常 {video_file.name}: {e}")
                            pbar.update(1)
                
        return success_count, total_count, duplicate_count


def print_banner():
    """打印程序横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║              VideoAudio Batch Converter v1.0.0                  ║
║                    视频转音频批量处理工具                          ║
║                                                                  ║
║  🎬 支持格式: MP4, AVI, MOV, WMV, FLV, MKV, WEBM 等            ║
║  🎵 输出格式: MP3, WAV, AAC, M4A, OGG, FLAC                    ║
║  ⚡ 特    性: 批量处理 | 重复检测 | 进度显示 | 错误处理           ║
╚══════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """主函数 - 程序入口点"""
    
    # 显示程序信息
    print_banner()
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(
        description='VideoAudio Batch Converter - 视频转音频批量处理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s /path/to/videos                     # 转换目录下所有视频为MP3
  %(prog)s                                     # 使用配置文件中的默认目录
  %(prog)s /path/to/videos -o /path/to/output  # 指定输出目录
  %(prog)s /path/to/videos -f wav -q 320k      # 指定格式和质量
  %(prog)s /path/to/videos --no-recursive      # 不包含子目录
  %(prog)s /path/to/videos --overwrite         # 覆盖已存在文件

支持的视频格式: MP4, AVI, MOV, WMV, FLV, MKV, WEBM, MP4V, M4V, 3GP
支持的音频格式: MP3, WAV, AAC, M4A, OGG, FLAC

配置文件设置:
  在 config.ini 中设置 default_input_directory 和 default_output_directory
  可避免每次都需要指定目录参数
        """
    )
    
    # 添加命令行参数
    parser.add_argument(
        'input_dir', 
        nargs='?',  # 使参数可选
        help='输入视频文件目录路径 (可在配置文件中设置默认值)'
    )
    parser.add_argument(
        '-o', '--output-dir', 
        help='输出音频文件目录 (默认与输入文件同目录，或使用配置文件中的默认值)'
    )
    parser.add_argument(
        '-f', '--format', 
        default='mp3',
        choices=['mp3', 'wav', 'aac', 'm4a', 'ogg', 'flac'],
        help='输出音频格式 (默认: mp3)'
    )
    parser.add_argument(
        '-q', '--quality', 
        default='192k',
        choices=['64k', '128k', '192k', '256k', '320k'],
        help='音频质量/比特率 (默认: 192k)'
    )
    parser.add_argument(
        '--overwrite', 
        action='store_true',
        help='覆盖已存在的文件'
    )
    parser.add_argument(
        '--no-recursive', 
        action='store_true',
        help='不递归扫描子目录'
    )
    parser.add_argument(
        '--config', 
        default='config.ini',
        help='配置文件路径 (默认: config.ini)'
    )
    parser.add_argument(
        '-j', '--jobs', 
        type=int,
        help='并发线程数 (默认使用配置文件中的设置，1表示单线程)'
    )
    parser.add_argument(
        '--version', 
        action='version',
        version='VideoAudio Batch Converter v1.0.0'
    )
    
    # 解析命令行参数
    args = parser.parse_args()
    
    try:
        # 创建转换器实例
        converter = VideoAudioConverter(args.config)
        
        # 处理输入目录
        if args.input_dir:
            input_directory = args.input_dir
        else:
            # 使用配置文件中的默认输入目录
            input_directory = converter.config.get('DEFAULT', 'default_input_directory', fallback='')
            if not input_directory:
                print("❌ 错误: 未指定输入目录，请在命令行中指定或在配置文件中设置 default_input_directory")
                sys.exit(1)
        
        # 处理输出目录
        if args.output_dir:
            output_directory = args.output_dir
        else:
            # 使用配置文件中的默认输出目录
            output_directory = converter.config.get('DEFAULT', 'default_output_directory', fallback='')
            if not output_directory:
                output_directory = None  # 表示使用与输入文件同目录
        
        # 更新配置（如果用户指定了覆盖选项）
        if args.overwrite:
            converter.config.set('DEFAULT', 'overwrite_existing', 'true')
        
        # 显示操作信息
        print(f"📂 输入目录: {input_directory}")
        if output_directory:
            print(f"📁 输出目录: {output_directory}")
        else:
            print(f"📁 输出目录: 与原文件同目录")
        print(f"🎵 输出格式: {args.format.upper()}")
        print(f"🔊 音频质量: {args.quality}")
        print(f"📊 递归扫描: {'否' if args.no_recursive else '是'}")
        print(f"🔄 覆盖文件: {'是' if args.overwrite else '否'}")
        
        # 显示线程信息
        max_workers = args.jobs if args.jobs else converter.config.getint('DEFAULT', 'max_concurrent_jobs', fallback=1)
        print(f"🧵 并发线程: {max_workers}")
        print("=" * 60)
        
        # 开始批量转换
        start_time = time.time()
        
        success, total, duplicates = converter.batch_convert(
            input_directory,
            output_directory,
            args.format,
            args.quality,
            not args.no_recursive,
            args.jobs
        )
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # 显示结果统计
        print("\n" + "=" * 60)
        print("🎉 转换完成！")
        print(f"📊 处理统计:")
        print(f"   总文件数: {total}")
        print(f"   ✅ 成功: {success}")
        print(f"   ❌ 失败: {total - success}")
        if duplicates > 0:
            print(f"   🔄 重复跳过: {duplicates}")
        print(f"   📈 成功率: {success/total*100:.1f}%" if total > 0 else "   📈 成功率: 0%")
        print(f"   ⏱️  总耗时: {elapsed_time:.2f} 秒")
        
        if success > 0:
            avg_time = elapsed_time / success
            print(f"   ⚡ 平均每文件: {avg_time:.2f} 秒")
        
        # 设置退出状态码
        if total == 0:
            sys.exit(1)  # 没找到文件
        elif success == 0:
            sys.exit(2)  # 全部转换失败
        elif success < total:
            sys.exit(3)  # 部分转换失败
        else:
            sys.exit(0)  # 全部成功
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()