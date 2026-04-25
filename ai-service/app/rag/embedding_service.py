"""
嵌入向量服务模块

提供文本向量化的功能，使用 sentence-transformers 加载中文嵌入模型，
支持单文本和批量文本向量化，并包含模型缓存机制避免重复加载。
"""

import logging
from typing import List, Optional
from functools import lru_cache

from app.core.config import settings

# 配置日志记录器
logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    嵌入向量服务类
    
    负责加载和管理嵌入模型，提供文本向量化功能。
    使用单例模式确保模型只被加载一次，避免内存浪费。
    
    Attributes:
        _instance: 类的单例实例
        _model: sentence-transformers 模型实例
        _model_name: 当前使用的模型名称
    """
    
    _instance: Optional['EmbeddingService'] = None
    _model = None
    _model_name: Optional[str] = None
    
    def __new__(cls) -> 'EmbeddingService':
        """
        实现单例模式，确保只有一个 EmbeddingService 实例
        
        Returns:
            EmbeddingService: 单例实例
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.info("创建 EmbeddingService 单例实例")
        return cls._instance
    
    def __init__(self) -> None:
        """
        初始化嵌入服务
        
        注意：由于使用单例模式，初始化逻辑只在首次创建实例时执行
        """
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self._device = None  # 设备类型 (cpu/cuda)
        logger.info(f"EmbeddingService 初始化完成，模型配置: {settings.EMBEDDING_MODEL}")
    
    def _load_model(self) -> None:
        """
        加载 sentence-transformers 模型
        
        延迟加载机制：只有在首次调用向量化方法时才加载模型
        支持自动检测设备类型 (CPU/GPU)
        
        Raises:
            ImportError: 当 sentence-transformers 未安装时
            Exception: 模型加载失败时
        """
        if self._model is not None:
            # 检查是否需要切换模型
            if self._model_name == settings.EMBEDDING_MODEL:
                return
            else:
                logger.info(f"模型配置已变更，重新加载: {settings.EMBEDDING_MODEL}")
                self._model = None
        
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info(f"正在加载嵌入模型: {settings.EMBEDDING_MODEL}")
            
            # 加载模型，自动检测设备
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
            self._model_name = settings.EMBEDDING_MODEL
            self._device = str(self._model.device)
            
            logger.info(f"模型加载成功，使用设备: {self._device}")
            
        except ImportError:
            logger.error("sentence-transformers 未安装，请执行: pip install sentence-transformers")
            raise ImportError(
                "sentence-transformers 库未安装，"
                "请执行: pip install sentence-transformers"
            )
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            raise Exception(f"加载嵌入模型失败: {str(e)}")
    
    def encode(self, text: str) -> List[float]:
        """
        单文本向量化
        
        将输入文本转换为向量表示，向量维度由模型决定。
        
        Args:
            text: 输入文本字符串
        
        Returns:
            List[float]: 文本的向量表示，浮点数列表
        
        Raises:
            ValueError: 当输入文本为空或无效时
            Exception: 向量化过程出错时
        
        Example:
            >>> service = EmbeddingService()
            >>> vector = service.encode("这是一个测试文本")
            >>> print(len(vector))  # 输出向量维度，如 1024
        """
        # 参数校验
        if not text or not isinstance(text, str):
            raise ValueError("输入文本必须是非空字符串")
        
        # 确保模型已加载
        self._load_model()
        
        try:
            logger.debug(f"向量化文本 (长度: {len(text)})")
            
            # 执行向量化
            embedding = self._model.encode(text, convert_to_numpy=True)
            
            # 转换为 Python 列表
            vector = embedding.tolist()
            
            logger.debug(f"向量化完成，向量维度: {len(vector)}")
            
            return vector
            
        except Exception as e:
            logger.error(f"文本向量化失败: {str(e)}")
            raise Exception(f"文本向量化失败: {str(e)}")
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量文本向量化
        
        将多个文本批量转换为向量表示，比多次调用 encode 方法更高效。
        自动过滤空字符串，并记录警告日志。
        
        Args:
            texts: 输入文本字符串列表
        
        Returns:
            List[List[float]]: 文本向量列表，每个元素对应输入文本的向量
        
        Raises:
            ValueError: 当输入列表为空时
            Exception: 向量化过程出错时
        
        Example:
            >>> service = EmbeddingService()
            >>> texts = ["文本一", "文本二", "文本三"]
            >>> vectors = service.encode_batch(texts)
            >>> print(len(vectors))  # 输出: 3
        """
        # 参数校验
        if not texts or not isinstance(texts, list):
            raise ValueError("输入必须是包含至少一个字符串的列表")
        
        # 过滤空字符串并记录原始索引
        valid_texts = []
        valid_indices = []
        
        for i, text in enumerate(texts):
            if text and isinstance(text, str):
                valid_texts.append(text)
                valid_indices.append(i)
            else:
                logger.warning(f"跳过无效文本，索引: {i}")
        
        if not valid_texts:
            logger.warning("没有有效的文本需要向量化")
            return []
        
        # 确保模型已加载
        self._load_model()
        
        try:
            logger.info(f"批量向量化 {len(valid_texts)} 个文本")
            
            # 执行批量向量化
            embeddings = self._model.encode(
                valid_texts, 
                convert_to_numpy=True,
                batch_size=32,  # 批处理大小，可根据内存调整
                show_progress_bar=len(valid_texts) > 100  # 大量文本时显示进度条
            )
            
            # 转换为 Python 列表
            vectors = embeddings.tolist()
            
            logger.info(f"批量向量化完成，生成 {len(vectors)} 个向量，维度: {len(vectors[0]) if vectors else 0}")
            
            return vectors
            
        except Exception as e:
            logger.error(f"批量向量化失败: {str(e)}")
            raise Exception(f"批量向量化失败: {str(e)}")
    
    def get_model_info(self) -> dict:
        """
        获取当前模型信息
        
        Returns:
            dict: 包含模型名称、设备类型等信息的字典
        """
        return {
            "model_name": self._model_name,
            "device": self._device,
            "loaded": self._model is not None
        }
    
    def clear_cache(self) -> None:
        """
        清除模型缓存
        
        释放模型占用的内存，下次调用向量化方法时会重新加载模型。
        适用于需要释放内存或切换模型的场景。
        """
        if self._model is not None:
            logger.info(f"清除模型缓存: {self._model_name}")
            self._model = None
            self._model_name = None
            self._device = None
        else:
            logger.debug("模型缓存为空，无需清除")


# 模块级函数，提供便捷访问方式

@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    """
    获取 EmbeddingService 单例实例
    
    使用 LRU 缓存确保全局只有一个服务实例
    
    Returns:
        EmbeddingService: 嵌入服务实例
    """
    return EmbeddingService()


def encode_text(text: str) -> List[float]:
    """
    便捷函数：单文本向量化
    
    Args:
        text: 输入文本字符串
    
    Returns:
        List[float]: 文本向量
    """
    service = get_embedding_service()
    return service.encode(text)


def encode_texts(texts: List[str]) -> List[List[float]]:
    """
    便捷函数：批量文本向量化
    
    Args:
        texts: 输入文本列表
    
    Returns:
        List[List[float]]: 文本向量列表
    """
    service = get_embedding_service()
    return service.encode_batch(texts)
