"""
记忆检索模块

提供用户对话记忆的检索功能，支持基于语义相似度和时间的记忆召回。
集成embedding_service进行语义相似度计算，用于增强AI对话的上下文理解。
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from functools import lru_cache

from app.core.config import settings
from app.rag.embedding_service import EmbeddingService, get_embedding_service

# 配置日志记录器
logger = logging.getLogger(__name__)


@dataclass
class Memory:
    """记忆数据类"""
    id: int
    user_id: int
    content: str
    memory_type: str  # 'chat', 'summary', 'event', 'preference'
    create_time: datetime
    relevance_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class MemoryRetriever:
    """
    记忆检索器类
    
    负责检索和管理用户的对话记忆，支持多种检索策略：
    - 基于语义相似度的相关性检索
    - 基于时间范围的近期记忆检索
    - 融合相关性和时间的综合检索
    
    Attributes:
        embedding_service: 嵌入向量服务实例
        max_context_tokens: 最大上下文token数
        similarity_threshold: 相似度阈值
    """
    
    def __init__(self, embedding_service: Optional[EmbeddingService] = None):
        """
        初始化记忆检索器
        
        Args:
            embedding_service: 可选的嵌入服务实例，如未提供则自动创建
        """
        self.embedding_service = embedding_service or get_embedding_service()
        self.max_context_tokens = getattr(settings, 'MEMORY_MAX_TOKENS', 2000)
        self.similarity_threshold = 0.7  # 相似度阈值
        self.time_decay_factor = 0.1  # 时间衰减因子
        
        logger.info(f"MemoryRetriever 初始化完成，最大上下文token数: {self.max_context_tokens}")
    
    async def retrieve_by_relevance(
        self, 
        user_id: int, 
        query: str, 
        top_k: int = 5
    ) -> List[Dict]:
        """
        基于语义相似性召回记忆
        
        使用embedding_service计算查询文本与记忆的语义相似度，
        返回最相关的记忆列表。
        
        Args:
            user_id: 用户ID
            query: 查询文本
            top_k: 返回的记忆数量，默认5条
        
        Returns:
            List[Dict]: 按相似度排序的记忆列表，每个记忆包含：
                - id: 记忆ID
                - content: 记忆内容
                - memory_type: 记忆类型
                - create_time: 创建时间
                - relevance_score: 相关性分数 (0-1)
                - metadata: 额外元数据
        
        Raises:
            ValueError: 当查询文本为空时
            Exception: 向量化或检索过程出错时
        
        Example:
            >>> retriever = MemoryRetriever()
            >>> memories = await retriever.retrieve_by_relevance(1, "我的血压怎么样", top_k=3)
            >>> print(len(memories))  # 输出: 3
        """
        # 参数校验
        if not query or not isinstance(query, str):
            raise ValueError("查询文本必须是非空字符串")
        
        if top_k <= 0:
            top_k = 5
        
        try:
            logger.info(f"开始相关性检索 - 用户ID: {user_id}, 查询: '{query[:50]}...', top_k: {top_k}")
            
            # 将查询文本转换为向量
            query_vector = self.embedding_service.encode(query)
            logger.debug(f"查询向量化完成，维度: {len(query_vector)}")
            
            # 从数据库检索候选记忆（这里模拟从数据库获取）
            # 实际项目中应该从向量数据库（如Milvus）检索
            candidate_memories = await self._fetch_candidate_memories(user_id, limit=top_k * 3)
            
            if not candidate_memories:
                logger.warning(f"未找到用户 {user_id} 的候选记忆")
                return []
            
            # 计算语义相似度
            scored_memories = []
            for memory in candidate_memories:
                # 计算向量相似度（余弦相似度）
                similarity = self._calculate_similarity(query_vector, memory.get('embedding', []))
                
                if similarity >= self.similarity_threshold:
                    memory['relevance_score'] = round(similarity, 4)
                    scored_memories.append(memory)
            
            # 按相似度排序并取top_k
            scored_memories.sort(key=lambda x: x['relevance_score'], reverse=True)
            result = scored_memories[:top_k]
            
            logger.info(f"相关性检索完成，找到 {len(result)} 条相关记忆")
            return result
            
        except Exception as e:
            logger.error(f"相关性检索失败: {str(e)}")
            raise Exception(f"记忆相关性检索失败: {str(e)}")
    
    async def retrieve_by_time(
        self, 
        user_id: int, 
        days: int = 30, 
        limit: int = 10
    ) -> List[Dict]:
        """
        基于时间召回近期记忆
        
        检索指定用户最近N天内的记忆记录，按时间倒序排列。
        
        Args:
            user_id: 用户ID
            days: 时间范围（天），默认30天
            limit: 返回的记忆数量，默认10条
        
        Returns:
            List[Dict]: 按时间倒序排列的记忆列表，每个记忆包含：
                - id: 记忆ID
                - content: 记忆内容
                - memory_type: 记忆类型
                - create_time: 创建时间
                - metadata: 额外元数据
        
        Raises:
            ValueError: 当参数无效时
            Exception: 检索过程出错时
        
        Example:
            >>> retriever = MemoryRetriever()
            >>> memories = await retriever.retrieve_by_time(1, days=7, limit=5)
            >>> print(memories[0]['create_time'])  # 最新的记忆时间
        """
        # 参数校验
        if days <= 0:
            days = 30
        if limit <= 0:
            limit = 10
        
        try:
            logger.info(f"开始时间检索 - 用户ID: {user_id}, 时间范围: {days}天, 限制: {limit}")
            
            # 计算起始时间
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # 从数据库检索时间范围内的记忆
            memories = await self._fetch_memories_by_time_range(
                user_id=user_id,
                start_time=start_time,
                end_time=end_time,
                limit=limit
            )
            
            logger.info(f"时间检索完成，找到 {len(memories)} 条记忆")
            return memories
            
        except Exception as e:
            logger.error(f"时间检索失败: {str(e)}")
            raise Exception(f"记忆时间检索失败: {str(e)}")
    
    async def retrieve_combined(
        self, 
        user_id: int, 
        query: str, 
        top_k: int = 5
    ) -> List[Dict]:
        """
        融合相关性和时间召回
        
        综合语义相似度和时间因素，返回最相关的记忆。
        使用加权评分机制平衡相关性和时效性。
        
        Args:
            user_id: 用户ID
            query: 查询文本
            top_k: 返回的记忆数量，默认5条
        
        Returns:
            List[Dict]: 融合评分后的记忆列表，每个记忆包含：
                - id: 记忆ID
                - content: 记忆内容
                - memory_type: 记忆类型
                - create_time: 创建时间
                - relevance_score: 相关性分数
                - time_score: 时间新鲜度分数
                - combined_score: 综合评分
                - metadata: 额外元数据
        
        Raises:
            ValueError: 当查询文本为空时
            Exception: 检索过程出错时
        
        Example:
            >>> retriever = MemoryRetriever()
            >>> memories = await retriever.retrieve_combined(1, "最近的体检结果", top_k=5)
            >>> print(memories[0]['combined_score'])  # 最高综合评分
        """
        # 参数校验
        if not query or not isinstance(query, str):
            raise ValueError("查询文本必须是非空字符串")
        
        if top_k <= 0:
            top_k = 5
        
        try:
            logger.info(f"开始融合检索 - 用户ID: {user_id}, 查询: '{query[:50]}...'")
            
            # 获取相关性检索结果
            relevance_memories = await self.retrieve_by_relevance(user_id, query, top_k=top_k * 2)
            
            # 获取时间检索结果（最近90天）
            time_memories = await self.retrieve_by_time(user_id, days=90, limit=top_k * 2)
            
            # 合并结果并去重
            memory_map = {}
            
            # 处理相关性记忆
            for memory in relevance_memories:
                memory_id = memory['id']
                memory_map[memory_id] = {
                    **memory,
                    'relevance_score': memory.get('relevance_score', 0),
                    'time_score': 0
                }
            
            # 处理时间记忆并计算时间分数
            now = datetime.now()
            for memory in time_memories:
                memory_id = memory['id']
                create_time = memory.get('create_time')
                
                # 计算时间新鲜度分数（越新分数越高）
                if create_time:
                    age_days = (now - create_time).days
                    time_score = max(0, 1 - (age_days / 90))  # 90天内线性衰减
                else:
                    time_score = 0
                
                if memory_id in memory_map:
                    memory_map[memory_id]['time_score'] = round(time_score, 4)
                else:
                    memory_map[memory_id] = {
                        **memory,
                        'relevance_score': 0,
                        'time_score': round(time_score, 4)
                    }
            
            # 计算综合评分（相关性权重0.7，时间权重0.3）
            RELEVANCE_WEIGHT = 0.7
            TIME_WEIGHT = 0.3
            
            combined_memories = []
            for memory in memory_map.values():
                combined_score = (
                    memory['relevance_score'] * RELEVANCE_WEIGHT +
                    memory['time_score'] * TIME_WEIGHT
                )
                memory['combined_score'] = round(combined_score, 4)
                combined_memories.append(memory)
            
            # 按综合评分排序并取top_k
            combined_memories.sort(key=lambda x: x['combined_score'], reverse=True)
            result = combined_memories[:top_k]
            
            logger.info(f"融合检索完成，返回 {len(result)} 条记忆")
            return result
            
        except Exception as e:
            logger.error(f"融合检索失败: {str(e)}")
            raise Exception(f"记忆融合检索失败: {str(e)}")
    
    def format_memories_for_context(self, memories: List[Dict]) -> str:
        """
        格式化记忆为AI上下文
        
        将检索到的记忆列表格式化为适合AI模型理解的上下文字符串。
        自动处理token限制，优先保留高相关性记忆。
        
        Args:
            memories: 记忆字典列表，每个字典应包含：
                - content: 记忆内容（必需）
                - memory_type: 记忆类型（可选）
                - create_time: 创建时间（可选）
                - relevance_score: 相关性分数（可选）
        
        Returns:
            str: 格式化后的上下文字符串，可直接用于AI对话提示
        
        Example:
            >>> memories = [
            ...     {"content": "用户血压偏高", "memory_type": "health", "relevance_score": 0.95},
            ...     {"content": "用户喜欢晨跑", "memory_type": "preference", "relevance_score": 0.82}
            ... ]
            >>> context = retriever.format_memories_for_context(memories)
            >>> print(context)
            # 输出格式化的记忆上下文
        """
        if not memories:
            logger.debug("没有记忆需要格式化")
            return ""
        
        try:
            logger.info(f"开始格式化 {len(memories)} 条记忆为上下文")
            
            # 按相关性排序（如果存在相关性分数）
            if memories and 'relevance_score' in memories[0]:
                memories = sorted(memories, key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            context_parts = []
            total_length = 0
            max_length = self.max_context_tokens * 4  # 粗略估计：1个token约4个字符
            
            for i, memory in enumerate(memories, 1):
                content = memory.get('content', '')
                if not content:
                    continue
                
                # 构建记忆条目
                memory_type = memory.get('memory_type', 'general')
                create_time = memory.get('create_time')
                relevance = memory.get('relevance_score')
                
                # 格式化时间
                time_str = ""
                if isinstance(create_time, datetime):
                    time_str = f"[{create_time.strftime('%Y-%m-%d')}] "
                
                # 格式化相关性
                relevance_str = ""
                if relevance is not None:
                    relevance_str = f"(相关度: {relevance:.2f}) "
                
                # 组合记忆条目
                entry = f"{i}. [{memory_type}] {time_str}{relevance_str}{content}"
                
                # 检查长度限制
                if total_length + len(entry) > max_length and context_parts:
                    logger.debug(f"达到上下文长度限制，截断记忆列表")
                    break
                
                context_parts.append(entry)
                total_length += len(entry)
            
            if not context_parts:
                return ""
            
            # 组合最终上下文
            formatted_context = "【历史记忆】\n" + "\n".join(context_parts)
            
            logger.info(f"记忆格式化完成，上下文长度: {len(formatted_context)} 字符")
            return formatted_context
            
        except Exception as e:
            logger.error(f"记忆格式化失败: {str(e)}")
            # 返回简化版本
            return "\n".join([f"- {m.get('content', '')}" for m in memories if m.get('content')])
    
    def _calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        计算两个向量的余弦相似度
        
        Args:
            vec1: 第一个向量
            vec2: 第二个向量
        
        Returns:
            float: 余弦相似度，范围[-1, 1]
        """
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        import math
        
        # 计算点积
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # 计算模长
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        # 避免除以零
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    async def _fetch_candidate_memories(self, user_id: int, limit: int = 100) -> List[Dict]:
        """
        从数据库获取候选记忆（用于语义相似度计算）
        
        Args:
            user_id: 用户ID
            limit: 返回的记忆数量限制
        
        Returns:
            List[Dict]: 候选记忆列表
        """
        # 这里应该连接实际的数据库
        # 目前返回模拟数据，实际项目中需要实现数据库查询
        logger.debug(f"获取用户 {user_id} 的候选记忆，限制: {limit}")
        
        # TODO: 实现实际的数据库查询
        # 示例查询：
        # query = """
        #     SELECT id, user_id, content, memory_type, create_time, embedding 
        #     FROM user_memories 
        #     WHERE user_id = %s 
        #     ORDER BY create_time DESC 
        #     LIMIT %s
        # """
        # return await db.fetch_all(query, (user_id, limit))
        
        return []
    
    async def _fetch_memories_by_time_range(
        self, 
        user_id: int, 
        start_time: datetime, 
        end_time: datetime, 
        limit: int = 10
    ) -> List[Dict]:
        """
        从数据库获取指定时间范围内的记忆
        
        Args:
            user_id: 用户ID
            start_time: 开始时间
            end_time: 结束时间
            limit: 返回的记忆数量限制
        
        Returns:
            List[Dict]: 记忆列表
        """
        logger.debug(f"获取用户 {user_id} 在时间范围内的记忆: {start_time} ~ {end_time}")
        
        # TODO: 实现实际的数据库查询
        # 示例查询：
        # query = """
        #     SELECT id, user_id, content, memory_type, create_time 
        #     FROM user_memories 
        #     WHERE user_id = %s AND create_time BETWEEN %s AND %s
        #     ORDER BY create_time DESC 
        #     LIMIT %s
        # """
        # return await db.fetch_all(query, (user_id, start_time, end_time, limit))
        
        return []


# 模块级函数，提供便捷访问方式

@lru_cache(maxsize=1)
def get_memory_retriever() -> MemoryRetriever:
    """
    获取 MemoryRetriever 单例实例
    
    Returns:
        MemoryRetriever: 记忆检索器实例
    """
    return MemoryRetriever()


async def retrieve_memories_by_relevance(
    user_id: int, 
    query: str, 
    top_k: int = 5
) -> List[Dict]:
    """
    便捷函数：基于相关性检索记忆
    
    Args:
        user_id: 用户ID
        query: 查询文本
        top_k: 返回的记忆数量
    
    Returns:
        List[Dict]: 记忆列表
    """
    retriever = get_memory_retriever()
    return await retriever.retrieve_by_relevance(user_id, query, top_k)


async def retrieve_memories_by_time(
    user_id: int, 
    days: int = 30, 
    limit: int = 10
) -> List[Dict]:
    """
    便捷函数：基于时间检索记忆
    
    Args:
        user_id: 用户ID
        days: 时间范围（天）
        limit: 返回的记忆数量
    
    Returns:
        List[Dict]: 记忆列表
    """
    retriever = get_memory_retriever()
    return await retriever.retrieve_by_time(user_id, days, limit)


async def retrieve_memories_combined(
    user_id: int, 
    query: str, 
    top_k: int = 5
) -> List[Dict]:
    """
    便捷函数：融合检索记忆
    
    Args:
        user_id: 用户ID
        query: 查询文本
        top_k: 返回的记忆数量
    
    Returns:
        List[Dict]: 记忆列表
    """
    retriever = get_memory_retriever()
    return await retriever.retrieve_combined(user_id, query, top_k)


def format_memories(memories: List[Dict]) -> str:
    """
    便捷函数：格式化记忆为上下文
    
    Args:
        memories: 记忆列表
    
    Returns:
        str: 格式化后的上下文字符串
    """
    retriever = get_memory_retriever()
    return retriever.format_memories_for_context(memories)
