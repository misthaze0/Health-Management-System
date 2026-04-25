"""
语音合成模块
使用 edge-tts 库实现中文语音合成
支持流式输出和缓存机制
"""

import io
import hashlib
import logging
from pathlib import Path
from typing import Optional, AsyncGenerator
import asyncio

import edge_tts

from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)


class VoiceSynthesizer:
    """
    语音合成器类
    
    基于 edge-tts 实现高质量的文本转语音功能
    支持中文语音合成、流式输出和缓存机制
    """
    
    # 默认中文语音选项
    DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"
    
    # 可用的中文语音列表
    AVAILABLE_VOICES = [
        "zh-CN-XiaoxiaoNeural",      # 晓晓 - 女声
        "zh-CN-YunxiNeural",         # 云希 - 男声
        "zh-CN-YunjianNeural",       # 云健 - 男声
        "zh-CN-XiaoyiNeural",        # 晓伊 - 女声
        "zh-CN-YunyangNeural",       # 云扬 - 男声
        "zh-CN-XiaochenNeural",      # 晓辰 - 女声
        "zh-CN-XiaohanNeural",       # 晓涵 - 女声
        "zh-CN-XiaomengNeural",      # 晓梦 - 女声
        "zh-CN-XiaomoNeural",        # 晓墨 - 女声
        "zh-CN-XiaoqiuNeural",       # 晓秋 - 女声
        "zh-CN-XiaoruiNeural",       # 晓睿 - 女声
        "zh-CN-XiaoshuangNeural",    # 晓双 - 女声
        "zh-CN-XiaoyanNeural",       # 晓颜 - 女声
        "zh-CN-XiaoyouNeural",       # 晓悠 - 女声
        "zh-CN-YunfengNeural",       # 云峰 - 男声
        "zh-CN-YunhaoNeural",        # 云浩 - 男声
        "zh-CN-YunyeNeural",         # 云野 - 男声
        "zh-CN-YunzeNeural",         # 云泽 - 男声
    ]
    
    def __init__(
        self,
        voice: Optional[str] = None,
        rate: Optional[str] = None,
        volume: Optional[str] = None,
        cache_dir: Optional[str] = None
    ):
        """
        初始化语音合成器
        
        Args:
            voice: 语音类型，默认为配置中的 TTS_VOICE
            rate: 语速调整，如 "+0%", "-10%", "+20%"
            volume: 音量调整，如 "+0%", "-10%", "+20%"
            cache_dir: 缓存目录路径
        """
        # 从配置获取参数，允许运行时覆盖
        self.voice = voice or settings.TTS_VOICE or self.DEFAULT_VOICE
        self.rate = rate or settings.TTS_RATE or "+0%"
        self.volume = volume or settings.TTS_VOLUME or "+0%"
        
        # 初始化缓存
        self._cache: dict[str, bytes] = {}
        self._max_cache_size = 100  # 最大缓存条目数
        
        # 设置缓存目录
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path("data/audio_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(
            f"VoiceSynthesizer 初始化完成: "
            f"voice={self.voice}, rate={self.rate}, volume={self.volume}"
        )
    
    def _get_cache_key(self, text: str, voice: str) -> str:
        """
        生成缓存键
        
        Args:
            text: 待合成文本
            voice: 语音类型
            
        Returns:
            缓存键（MD5哈希值）
        """
        content = f"{text}:{voice}:{self.rate}:{self.volume}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """
        获取缓存文件路径
        
        Args:
            cache_key: 缓存键
            
        Returns:
            缓存文件路径
        """
        return self.cache_dir / f"{cache_key}.mp3"
    
    def _get_from_cache(self, cache_key: str) -> Optional[bytes]:
        """
        从缓存获取音频数据
        
        Args:
            cache_key: 缓存键
            
        Returns:
            音频字节流，缓存未命中返回 None
        """
        # 先检查内存缓存
        if cache_key in self._cache:
            logger.debug(f"内存缓存命中: {cache_key[:8]}...")
            return self._cache[cache_key]
        
        # 再检查文件缓存
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            try:
                audio_bytes = cache_path.read_bytes()
                # 加载到内存缓存
                self._add_to_memory_cache(cache_key, audio_bytes)
                logger.debug(f"文件缓存命中: {cache_key[:8]}...")
                return audio_bytes
            except Exception as e:
                logger.warning(f"读取缓存文件失败: {e}")
        
        return None
    
    def _add_to_memory_cache(self, cache_key: str, audio_bytes: bytes) -> None:
        """
        添加到内存缓存
        
        Args:
            cache_key: 缓存键
            audio_bytes: 音频字节流
        """
        # 如果缓存已满，移除最早的条目
        if len(self._cache) >= self._max_cache_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            logger.debug(f"内存缓存已满，移除: {oldest_key[:8]}...")
        
        self._cache[cache_key] = audio_bytes
    
    def _save_to_cache(self, cache_key: str, audio_bytes: bytes) -> None:
        """
        保存到缓存
        
        Args:
            cache_key: 缓存键
            audio_bytes: 音频字节流
        """
        try:
            # 保存到内存缓存
            self._add_to_memory_cache(cache_key, audio_bytes)
            
            # 保存到文件缓存
            cache_path = self._get_cache_path(cache_key)
            cache_path.write_bytes(audio_bytes)
            logger.debug(f"音频已缓存: {cache_key[:8]}...")
        except Exception as e:
            logger.warning(f"保存缓存失败: {e}")
    
    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None
    ) -> bytes:
        """
        合成语音
        
        将文本转换为音频字节流，支持缓存机制
        
        Args:
            text: 待合成的文本内容
            voice: 语音类型，默认使用初始化时的设置
            
        Returns:
            音频字节流（MP3格式）
            
        Raises:
            ValueError: 文本为空或语音类型无效
            RuntimeError: 合成失败
        """
        # 参数验证
        if not text or not text.strip():
            raise ValueError("合成文本不能为空")
        
        # 清理文本
        text = text.strip()
        
        # 确定使用的语音
        use_voice = voice or self.voice
        if use_voice not in self.AVAILABLE_VOICES:
            logger.warning(f"未知语音类型 '{use_voice}'，使用默认语音")
            use_voice = self.DEFAULT_VOICE
        
        # 检查缓存
        cache_key = self._get_cache_key(text, use_voice)
        cached_audio = self._get_from_cache(cache_key)
        if cached_audio is not None:
            logger.info(f"缓存命中，直接返回音频: {text[:30]}...")
            return cached_audio
        
        try:
            logger.info(f"开始合成语音: {text[:50]}...")
            
            # 创建 TTS 通信对象
            communicate = edge_tts.Communicate(
                text=text,
                voice=use_voice,
                rate=self.rate,
                volume=self.volume
            )
            
            # 收集音频数据
            audio_buffer = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_buffer.write(chunk["data"])
            
            audio_bytes = audio_buffer.getvalue()
            
            if not audio_bytes:
                raise RuntimeError("合成结果为空")
            
            # 保存到缓存
            self._save_to_cache(cache_key, audio_bytes)
            
            logger.info(f"语音合成完成: {len(audio_bytes)} 字节")
            return audio_bytes
            
        except Exception as e:
            logger.error(f"语音合成失败: {e}")
            raise RuntimeError(f"语音合成失败: {str(e)}")
    
    async def synthesize_stream(
        self,
        text: str,
        voice: Optional[str] = None
    ) -> AsyncGenerator[bytes, None]:
        """
        流式合成语音
        
        以生成器方式返回音频数据块，适合实时播放场景
        
        Args:
            text: 待合成的文本内容
            voice: 语音类型，默认使用初始化时的设置
            
        Yields:
            音频数据块（MP3格式）
            
        Raises:
            ValueError: 文本为空
            RuntimeError: 合成失败
        """
        # 参数验证
        if not text or not text.strip():
            raise ValueError("合成文本不能为空")
        
        text = text.strip()
        use_voice = voice or self.voice
        
        if use_voice not in self.AVAILABLE_VOICES:
            logger.warning(f"未知语音类型 '{use_voice}'，使用默认语音")
            use_voice = self.DEFAULT_VOICE
        
        try:
            logger.info(f"开始流式合成: {text[:50]}...")
            
            # 创建 TTS 通信对象
            communicate = edge_tts.Communicate(
                text=text,
                voice=use_voice,
                rate=self.rate,
                volume=self.volume
            )
            
            # 流式返回音频数据
            chunk_count = 0
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    chunk_count += 1
                    yield chunk["data"]
            
            logger.info(f"流式合成完成: {chunk_count} 个数据块")
            
        except Exception as e:
            logger.error(f"流式合成失败: {e}")
            raise RuntimeError(f"流式语音合成失败: {str(e)}")
    
    def save_audio(
        self,
        audio_bytes: bytes,
        filename: str
    ) -> Path:
        """
        保存音频文件
        
        将音频字节流保存到指定文件
        
        Args:
            audio_bytes: 音频字节流
            filename: 文件名（支持 .mp3, .wav 等格式）
            
        Returns:
            保存的文件路径
            
        Raises:
            ValueError: 音频数据为空
            RuntimeError: 保存失败
        """
        if not audio_bytes:
            raise ValueError("音频数据不能为空")
        
        try:
            # 确保输出目录存在
            output_dir = Path("data/audio_output")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 构建完整路径
            file_path = output_dir / filename
            
            # 写入文件
            file_path.write_bytes(audio_bytes)
            
            logger.info(f"音频已保存: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"保存音频失败: {e}")
            raise RuntimeError(f"保存音频失败: {str(e)}")
    
    def clear_cache(self) -> int:
        """
        清除缓存
        
        清除内存缓存和文件缓存
        
        Returns:
            清除的文件数量
        """
        # 清除内存缓存
        cache_count = len(self._cache)
        self._cache.clear()
        
        # 清除文件缓存
        file_count = 0
        try:
            for cache_file in self.cache_dir.glob("*.mp3"):
                cache_file.unlink()
                file_count += 1
        except Exception as e:
            logger.warning(f"清除文件缓存时出错: {e}")
        
        logger.info(f"缓存已清除: 内存 {cache_count} 条, 文件 {file_count} 个")
        return file_count
    
    def get_cache_info(self) -> dict:
        """
        获取缓存信息
        
        Returns:
            缓存统计信息字典
        """
        # 统计文件缓存
        file_count = len(list(self.cache_dir.glob("*.mp3")))
        total_size = sum(
            f.stat().st_size 
            for f in self.cache_dir.glob("*.mp3")
        )
        
        return {
            "memory_cache_count": len(self._cache),
            "file_cache_count": file_count,
            "file_cache_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_dir": str(self.cache_dir),
            "max_memory_cache": self._max_cache_size
        }
    
    @classmethod
    def list_available_voices(cls) -> list[str]:
        """
        获取可用语音列表
        
        Returns:
            可用语音类型列表
        """
        return cls.AVAILABLE_VOICES.copy()


# 单例实例
_synthesizer_instance: Optional[VoiceSynthesizer] = None


def get_synthesizer() -> VoiceSynthesizer:
    """
    获取语音合成器单例实例
    
    Returns:
        VoiceSynthesizer 实例
    """
    global _synthesizer_instance
    if _synthesizer_instance is None:
        _synthesizer_instance = VoiceSynthesizer()
    return _synthesizer_instance


def reset_synthesizer() -> None:
    """重置语音合成器单例"""
    global _synthesizer_instance
    _synthesizer_instance = None
    logger.info("语音合成器单例已重置")
