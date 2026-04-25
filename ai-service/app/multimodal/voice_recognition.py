"""
语音识别模块
提供语音转文字功能，支持多种音频格式和降噪预处理
"""

import io
import logging
import os
import tempfile
from dataclasses import dataclass
from typing import Optional, Union

import numpy as np
import speech_recognition as sr
from pydub import AudioSegment

# 配置日志记录
logger = logging.getLogger(__name__)


@dataclass
class RecognitionResult:
    """语音识别结果数据类"""
    text: str
    confidence: float
    success: bool
    error_message: Optional[str] = None


class VoiceRecognizer:
    """
    语音识别器类
    
    使用SpeechRecognition库实现语音转文字功能
    支持从文件或字节流识别，包含降噪预处理
    """
    
    # 支持的音频格式
    SUPPORTED_FORMATS = {'.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac'}
    
    def __init__(self, 
                 sample_rate: int = 16000,
                 enable_noise_reduction: bool = True,
                 recognizer_api: str = "google"):
        """
        初始化语音识别器
        
        Args:
            sample_rate: 目标采样率，默认16000Hz
            enable_noise_reduction: 是否启用降噪预处理
            recognizer_api: 使用的识别API，默认google
        """
        self.sample_rate = sample_rate
        self.enable_noise_reduction = enable_noise_reduction
        self.recognizer_api = recognizer_api
        self.recognizer = sr.Recognizer()
        
        # 配置识别器参数
        self.recognizer.energy_threshold = 300  # 能量阈值
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8  # 停顿阈值（秒）
        self.recognizer.phrase_threshold = 0.3  # 短语阈值（秒）
        
        logger.info(f"VoiceRecognizer初始化完成 - 采样率: {sample_rate}, "
                   f"降噪: {enable_noise_reduction}, API: {recognizer_api}")
    
    def _convert_to_wav(self, audio_path: str) -> str:
        """
        将音频文件转换为WAV格式
        
        Args:
            audio_path: 原始音频文件路径
            
        Returns:
            转换后的WAV文件路径（临时文件）
        """
        file_ext = os.path.splitext(audio_path)[1].lower()
        
        if file_ext == '.wav':
            return audio_path
        
        if file_ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"不支持的音频格式: {file_ext}，"
                           f"支持的格式: {self.SUPPORTED_FORMATS}")
        
        try:
            # 加载音频文件
            audio = AudioSegment.from_file(audio_path, format=file_ext[1:])
            
            # 转换为单声道、目标采样率
            audio = audio.set_channels(1).set_frame_rate(self.sample_rate)
            
            # 创建临时WAV文件
            temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            audio.export(temp_wav.name, format='wav')
            temp_wav.close()
            
            logger.debug(f"音频转换完成: {audio_path} -> {temp_wav.name}")
            return temp_wav.name
            
        except Exception as e:
            logger.error(f"音频转换失败: {audio_path}, 错误: {str(e)}")
            raise
    
    def _convert_bytes_to_wav(self, audio_bytes: bytes, 
                              format_hint: Optional[str] = None) -> str:
        """
        将音频字节流转换为WAV格式
        
        Args:
            audio_bytes: 音频字节数据
            format_hint: 音频格式提示（如 'mp3', 'wav'）
            
        Returns:
            转换后的WAV文件路径（临时文件）
        """
        try:
            # 从字节流加载音频
            audio = AudioSegment.from_file(
                io.BytesIO(audio_bytes),
                format=format_hint
            )
            
            # 转换为单声道、目标采样率
            audio = audio.set_channels(1).set_frame_rate(self.sample_rate)
            
            # 创建临时WAV文件
            temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            audio.export(temp_wav.name, format='wav')
            temp_wav.close()
            
            logger.debug(f"字节流音频转换完成 -> {temp_wav.name}")
            return temp_wav.name
            
        except Exception as e:
            logger.error(f"字节流音频转换失败: {str(e)}")
            raise
    
    def _apply_noise_reduction(self, audio_data: sr.AudioData) -> sr.AudioData:
        """
        对音频数据进行降噪处理
        
        Args:
            audio_data: 原始音频数据
            
        Returns:
            降噪后的音频数据
        """
        if not self.enable_noise_reduction:
            return audio_data
        
        try:
            # 将音频数据转换为numpy数组
            raw_data = audio_data.get_raw_data(
                convert_rate=self.sample_rate,
                convert_width=2
            )
            audio_array = np.frombuffer(raw_data, dtype=np.int16)
            
            # 简单的降噪处理：去除静音段
            # 计算音频能量
            frame_length = int(self.sample_rate * 0.025)  # 25ms帧
            hop_length = int(self.sample_rate * 0.010)    # 10ms步长
            
            # 计算每帧的能量
            frames = []
            for i in range(0, len(audio_array) - frame_length, hop_length):
                frame = audio_array[i:i + frame_length]
                energy = np.sum(frame.astype(np.float64) ** 2) / len(frame)
                frames.append((i, energy))
            
            # 计算能量阈值（使用中位数）
            energies = [f[1] for f in frames]
            if len(energies) > 0:
                energy_threshold = np.median(energies) * 0.1
                
                # 标记有效帧
                valid_frames = [f for f in frames if f[1] > energy_threshold]
                
                if valid_frames:
                    # 重建音频（保留有效帧周围的数据）
                    start_idx = max(0, valid_frames[0][0] - hop_length)
                    end_idx = min(len(audio_array), 
                                 valid_frames[-1][0] + frame_length + hop_length)
                    filtered_audio = audio_array[start_idx:end_idx]
                    
                    # 转换回字节
                    filtered_bytes = filtered_audio.astype(np.int16).tobytes()
                    
                    return sr.AudioData(
                        filtered_bytes,
                        self.sample_rate,
                        2  # 16-bit = 2 bytes
                    )
            
            return audio_data
            
        except Exception as e:
            logger.warning(f"降噪处理失败，使用原始音频: {str(e)}")
            return audio_data
    
    def _recognize_with_api(self, audio_data: sr.AudioData, 
                           language: str) -> tuple[str, float]:
        """
        使用指定API进行语音识别
        
        Args:
            audio_data: 音频数据
            language: 语言代码
            
        Returns:
            (识别文本, 置信度) 元组
        """
        try:
            if self.recognizer_api == "google":
                # Google Speech Recognition
                text = self.recognizer.recognize_google(
                    audio_data,
                    language=language,
                    show_all=False
                )
                # Google API不返回置信度，默认返回0.85
                confidence = 0.85
                
            elif self.recognizer_api == "bing":
                # Microsoft Bing Voice Recognition (需要API key)
                text = self.recognizer.recognize_bing(
                    audio_data,
                    key=os.getenv("BING_SPEECH_API_KEY", ""),
                    language=language
                )
                confidence = 0.90
                
            elif self.recognizer_api == " whisper":
                # OpenAI Whisper (本地或API)
                text = self.recognizer.recognize_whisper(
                    audio_data,
                    language=language[:2] if language else None,
                    show_dict=True
                )
                if isinstance(text, dict):
                    confidence = text.get('confidence', 0.0)
                    text = text.get('text', '')
                else:
                    confidence = 0.80
                    
            else:
                raise ValueError(f"不支持的识别API: {self.recognizer_api}")
            
            return text, confidence
            
        except sr.UnknownValueError:
            logger.warning("无法识别音频内容")
            raise
        except sr.RequestError as e:
            logger.error(f"识别服务请求失败: {str(e)}")
            raise
    
    def recognize_from_file(self, audio_path: str, 
                           language: str = "zh-CN") -> RecognitionResult:
        """
        从音频文件识别语音
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码，默认"zh-CN"（中文）
            
        Returns:
            RecognitionResult: 识别结果对象
        """
        logger.info(f"开始识别音频文件: {audio_path}, 语言: {language}")
        
        temp_file = None
        try:
            # 验证文件存在
            if not os.path.exists(audio_path):
                error_msg = f"音频文件不存在: {audio_path}"
                logger.error(error_msg)
                return RecognitionResult(
                    text="",
                    confidence=0.0,
                    success=False,
                    error_message=error_msg
                )
            
            # 转换为WAV格式
            temp_file = self._convert_to_wav(audio_path)
            
            # 加载音频
            with sr.AudioFile(temp_file) as source:
                # 调整环境噪音
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # 录制音频
                audio_data = self.recognizer.record(source)
            
            # 降噪处理
            if self.enable_noise_reduction:
                audio_data = self._apply_noise_reduction(audio_data)
                logger.debug("降噪处理完成")
            
            # 语音识别
            text, confidence = self._recognize_with_api(audio_data, language)
            
            logger.info(f"识别成功: 文本长度={len(text)}, 置信度={confidence:.2f}")
            
            return RecognitionResult(
                text=text,
                confidence=confidence,
                success=True
            )
            
        except sr.UnknownValueError:
            error_msg = "无法识别音频内容，请检查音频质量或语言设置"
            logger.warning(error_msg)
            return RecognitionResult(
                text="",
                confidence=0.0,
                success=False,
                error_message=error_msg
            )
            
        except Exception as e:
            error_msg = f"识别过程发生错误: {str(e)}"
            logger.error(error_msg)
            return RecognitionResult(
                text="",
                confidence=0.0,
                success=False,
                error_message=error_msg
            )
            
        finally:
            # 清理临时文件
            if temp_file and temp_file != audio_path and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    logger.debug(f"临时文件已清理: {temp_file}")
                except Exception as e:
                    logger.warning(f"清理临时文件失败: {temp_file}, {str(e)}")
    
    def recognize_from_bytes(self, audio_bytes: bytes, 
                            language: str = "zh-CN",
                            format_hint: Optional[str] = None) -> RecognitionResult:
        """
        从音频字节流识别语音
        
        Args:
            audio_bytes: 音频字节数据
            language: 语言代码，默认"zh-CN"（中文）
            format_hint: 音频格式提示（如 'mp3', 'wav', 'm4a'）
            
        Returns:
            RecognitionResult: 识别结果对象
        """
        logger.info(f"开始识别音频字节流, 大小: {len(audio_bytes)} bytes, 语言: {language}")
        
        temp_file = None
        try:
            # 验证数据
            if not audio_bytes or len(audio_bytes) == 0:
                error_msg = "音频字节流为空"
                logger.error(error_msg)
                return RecognitionResult(
                    text="",
                    confidence=0.0,
                    success=False,
                    error_message=error_msg
                )
            
            # 转换为WAV格式
            temp_file = self._convert_bytes_to_wav(audio_bytes, format_hint)
            
            # 加载音频
            with sr.AudioFile(temp_file) as source:
                # 调整环境噪音
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # 录制音频
                audio_data = self.recognizer.record(source)
            
            # 降噪处理
            if self.enable_noise_reduction:
                audio_data = self._apply_noise_reduction(audio_data)
                logger.debug("降噪处理完成")
            
            # 语音识别
            text, confidence = self._recognize_with_api(audio_data, language)
            
            logger.info(f"识别成功: 文本长度={len(text)}, 置信度={confidence:.2f}")
            
            return RecognitionResult(
                text=text,
                confidence=confidence,
                success=True
            )
            
        except sr.UnknownValueError:
            error_msg = "无法识别音频内容，请检查音频质量或语言设置"
            logger.warning(error_msg)
            return RecognitionResult(
                text="",
                confidence=0.0,
                success=False,
                error_message=error_msg
            )
            
        except Exception as e:
            error_msg = f"识别过程发生错误: {str(e)}"
            logger.error(error_msg)
            return RecognitionResult(
                text="",
                confidence=0.0,
                success=False,
                error_message=error_msg
            )
            
        finally:
            # 清理临时文件
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    logger.debug(f"临时文件已清理: {temp_file}")
                except Exception as e:
                    logger.warning(f"清理临时文件失败: {temp_file}, {str(e)}")
    
    def get_supported_formats(self) -> set[str]:
        """
        获取支持的音频格式
        
        Returns:
            支持的音频格式扩展名集合
        """
        return self.SUPPORTED_FORMATS.copy()
    
    def set_noise_reduction(self, enabled: bool) -> None:
        """
        设置降噪开关
        
        Args:
            enabled: 是否启用降噪
        """
        self.enable_noise_reduction = enabled
        logger.info(f"降噪功能已{'启用' if enabled else '禁用'}")


# 创建默认识别器实例
def create_recognizer(**kwargs) -> VoiceRecognizer:
    """
    创建语音识别器实例
    
    Args:
        **kwargs: 传递给VoiceRecognizer构造函数的参数
        
    Returns:
        VoiceRecognizer实例
    """
    return VoiceRecognizer(**kwargs)


# 便捷函数：快速识别文件
def recognize_file(audio_path: str, language: str = "zh-CN", **kwargs) -> RecognitionResult:
    """
    快速识别音频文件
    
    Args:
        audio_path: 音频文件路径
        language: 语言代码
        **kwargs: 识别器配置参数
        
    Returns:
        RecognitionResult: 识别结果
    """
    recognizer = create_recognizer(**kwargs)
    return recognizer.recognize_from_file(audio_path, language)


# 便捷函数：快速识别字节流
def recognize_bytes(audio_bytes: bytes, language: str = "zh-CN", 
                   format_hint: Optional[str] = None, **kwargs) -> RecognitionResult:
    """
    快速识别音频字节流
    
    Args:
        audio_bytes: 音频字节数据
        language: 语言代码
        format_hint: 音频格式提示
        **kwargs: 识别器配置参数
        
    Returns:
        RecognitionResult: 识别结果
    """
    recognizer = create_recognizer(**kwargs)
    return recognizer.recognize_from_bytes(audio_bytes, language, format_hint)
