"""
RAG检索器模块

实现基于向量数据库和关键词匹配的混合检索策略，支持检索结果重排序和上下文组装。
用于从知识库中检索与用户查询相关的文档，为大语言模型提供上下文支持。
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

from app.core.config import settings
from app.rag.milvus_client import get_milvus_client, MilvusClient
from app.rag.embedding_service import get_embedding_service, EmbeddingService

# 配置日志记录器
logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """
    检索结果数据类
    
    Attributes:
        id: 文档ID
        content: 文档内容
        score: 综合得分（越高越相关）
        vector_score: 向量相似度得分
        keyword_score: 关键词匹配得分
        source: 文档来源
        metadata: 文档元数据
        created_at: 创建时间戳
    """
    id: int
    content: str
    score: float
    vector_score: float
    keyword_score: float
    source: str
    metadata: Dict[str, Any]
    created_at: int


class RAGRetriever:
    """
    RAG检索器类
    
    实现混合检索策略，结合向量相似度搜索和关键词匹配，
    并对结果进行重排序，最终组装成适合大语言模型使用的上下文。
    
    Attributes:
        milvus_client: Milvus向量数据库客户端
        embedding_service: 文本嵌入服务
        collection_name: 默认检索的集合名称
        vector_weight: 向量得分权重（用于混合排序）
        keyword_weight: 关键词得分权重（用于混合排序）
    """
    
    # 默认权重配置
    DEFAULT_VECTOR_WEIGHT = 0.7
    DEFAULT_KEYWORD_WEIGHT = 0.3
    
    def __init__(
        self,
        collection_name: Optional[str] = None,
        vector_weight: float = DEFAULT_VECTOR_WEIGHT,
        keyword_weight: float = DEFAULT_KEYWORD_WEIGHT,
    ):
        """
        初始化RAG检索器
        
        Args:
            collection_name: 检索的集合名称，默认使用配置中的MILVUS_COLLECTION
            vector_weight: 向量得分权重（0-1之间）
            keyword_weight: 关键词得分权重（0-1之间）
        """
        self.milvus_client: MilvusClient = get_milvus_client()
        self.embedding_service: EmbeddingService = get_embedding_service()
        self.collection_name = collection_name or settings.MILVUS_COLLECTION
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight
        
        # 确保权重和为1
        total_weight = self.vector_weight + self.keyword_weight
        if total_weight != 1.0:
            self.vector_weight /= total_weight
            self.keyword_weight /= total_weight
        
        logger.info(
            f"RAGRetriever初始化完成，集合: {self.collection_name}, "
            f"向量权重: {self.vector_weight:.2f}, 关键词权重: {self.keyword_weight:.2f}"
        )
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        use_hybrid: bool = True,
        rerank: bool = True,
        filter_expr: Optional[str] = None,
    ) -> List[RetrievalResult]:
        """
        执行检索操作
        
        根据查询文本检索相关文档，支持纯向量检索、混合检索和重排序。
        
        Args:
            query: 用户查询文本
            top_k: 返回的最相关文档数量
            use_hybrid: 是否使用混合检索（向量+关键词）
            rerank: 是否对结果进行重排序
            filter_expr: 可选的过滤表达式（Milvus表达式语法）
            
        Returns:
            List[RetrievalResult]: 检索结果列表，按相关性排序
            
        Raises:
            ValueError: 查询文本为空时
            ConnectionError: 数据库连接失败时
            
        Example:
            >>> retriever = RAGRetriever()
            >>> results = retriever.retrieve("如何预防高血压？", top_k=3)
            >>> for r in results:
            ...     print(f"{r.score:.3f}: {r.content[:100]}...")
        """
        # 参数校验
        if not query or not isinstance(query, str):
            raise ValueError("查询文本必须是非空字符串")
        
        if top_k <= 0:
            top_k = 5
        
        logger.info(f"开始检索，查询: '{query[:50]}...', top_k: {top_k}, 混合检索: {use_hybrid}")
        
        try:
            # 确保Milvus连接
            if not self.milvus_client.connect():
                raise ConnectionError("无法连接到Milvus服务器")
            
            # 步骤1: 向量相似度检索
            vector_results = self._vector_search(query, top_k * 2, filter_expr)
            logger.debug(f"向量检索返回 {len(vector_results)} 条结果")
            
            if not vector_results:
                logger.warning("向量检索未返回任何结果")
                return []
            
            # 步骤2: 混合检索（关键词匹配）
            if use_hybrid:
                hybrid_results = self._hybrid_search(query, vector_results)
                logger.debug(f"混合检索后共 {len(hybrid_results)} 条结果")
            else:
                # 仅使用向量得分
                hybrid_results = [
                    {
                        **result,
                        "vector_score": result.get("score", 0),
                        "keyword_score": 0.0,
                    }
                    for result in vector_results
                ]
            
            # 步骤3: 计算综合得分
            scored_results = self._calculate_combined_scores(hybrid_results)
            
            # 步骤4: 重排序（可选）
            if rerank:
                scored_results = self._rerank_results(query, scored_results)
                logger.debug("完成重排序")
            
            # 步骤5: 转换为RetrievalResult对象并截取top_k
            final_results = self._convert_to_results(scored_results[:top_k])
            
            logger.info(f"检索完成，返回 {len(final_results)} 条结果")
            return final_results
            
        except Exception as e:
            logger.error(f"检索过程发生错误: {e}")
            raise
    
    def _vector_search(
        self,
        query: str,
        top_k: int,
        filter_expr: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        执行向量相似度搜索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            filter_expr: 过滤表达式
            
        Returns:
            List[Dict]: 向量搜索结果列表
        """
        # 生成查询向量
        query_vector = self.embedding_service.encode(query)
        
        # 执行向量搜索
        results = self.milvus_client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            top_k=top_k,
            metric_type="L2",
            output_fields=["id", "content", "metadata", "source", "created_at"],
            expr=filter_expr,
        )
        
        return results
    
    def _hybrid_search(
        self,
        query: str,
        vector_results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        执行混合检索，结合向量结果和关键词匹配
        
        使用BM25-inspired的关键词匹配算法，计算查询与文档的关键词匹配得分。
        
        Args:
            query: 查询文本
            vector_results: 向量检索结果列表
            
        Returns:
            List[Dict]: 包含向量得分和关键词得分的混合结果
        """
        # 提取查询关键词
        query_keywords = self._extract_keywords(query)
        
        if not query_keywords:
            # 如果没有提取到关键词，仅使用向量得分
            return [
                {
                    **result,
                    "vector_score": result.get("score", 0),
                    "keyword_score": 0.0,
                }
                for result in vector_results
            ]
        
        # 计算每个结果的关键词匹配得分
        hybrid_results = []
        for result in vector_results:
            content = result.get("content", "")
            keyword_score = self._calculate_keyword_score(query_keywords, content)
            
            hybrid_result = {
                **result,
                "vector_score": result.get("score", 0),
                "keyword_score": keyword_score,
            }
            hybrid_results.append(hybrid_result)
        
        return hybrid_results
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        从文本中提取关键词
        
        移除停用词，提取有意义的词汇用于关键词匹配。
        
        Args:
            text: 输入文本
            
        Returns:
            List[str]: 关键词列表
        """
        # 基础停用词列表（中文和英文）
        stopwords = {
            "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也",
            "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这", "那",
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
            "do", "does", "did", "will", "would", "could", "should", "may", "might", "must", "shall",
            "can", "need", "dare", "ought", "used", "to", "of", "in", "for", "on", "with", "at", "by",
            "from", "as", "into", "through", "during", "before", "after", "above", "below", "between",
            "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how",
            "all", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only",
            "own", "same", "so", "than", "too", "very", "just", "and", "but", "if", "or", "because",
            "until", "while", "what", "which", "who", "whom", "this", "that", "these", "those", "am",
        }
        
        # 清理文本并分词
        # 移除标点符号，转换为小写
        cleaned_text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # 简单分词（按空格和中文单字分割）
        words = []
        for token in cleaned_text.split():
            if len(token) > 1:  # 英文单词
                if token not in stopwords:
                    words.append(token)
            else:  # 中文单字或短词
                for char in token:
                    if char not in stopwords and len(char.strip()) > 0:
                        words.append(char)
        
        # 额外提取2-4字的词组（中文）
        text_no_space = re.sub(r'\s', '', text.lower())
        for i in range(len(text_no_space) - 1):
            for length in [2, 3, 4]:
                if i + length <= len(text_no_space):
                    phrase = text_no_space[i:i+length]
                    # 过滤纯数字或纯标点的词组
                    if not re.match(r'^\d+$', phrase) and not re.match(r'^[^\w]+$', phrase):
                        words.append(phrase)
        
        # 去重并返回
        return list(set(words))
    
    def _calculate_keyword_score(
        self,
        query_keywords: List[str],
        content: str,
    ) -> float:
        """
        计算关键词匹配得分
        
        基于TF-IDF思想的简化版本，计算查询关键词在文档中的匹配程度。
        
        Args:
            query_keywords: 查询关键词列表
            content: 文档内容
            
        Returns:
            float: 关键词匹配得分（0-1之间）
        """
        if not query_keywords or not content:
            return 0.0
        
        content_lower = content.lower()
        total_score = 0.0
        matched_keywords = 0
        
        for keyword in query_keywords:
            # 计算关键词出现次数
            count = content_lower.count(keyword.lower())
            if count > 0:
                matched_keywords += 1
                # 词频得分（使用log平滑）
                tf_score = 1 + (count - 1) * 0.5  # 首次匹配得1分，后续每次+0.5
                # 长度加权（较长的匹配词给予更高权重）
                length_weight = min(len(keyword) / 2, 3)  # 最大3倍权重
                total_score += tf_score * length_weight
        
        # 归一化：考虑匹配关键词比例和总得分
        if matched_keywords == 0:
            return 0.0
        
        # 匹配率（匹配的关键词数 / 总关键词数）
        match_rate = matched_keywords / len(query_keywords)
        
        # 密度得分（总得分 / 文档长度归一化）
        density_score = min(total_score / (len(content) / 100 + 1), 5)
        
        # 综合得分
        final_score = (match_rate * 0.6 + min(density_score / 5, 1.0) * 0.4)
        
        return min(final_score, 1.0)
    
    def _calculate_combined_scores(
        self,
        hybrid_results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        计算综合得分
        
        根据配置的权重，结合向量得分和关键词得分计算最终得分。
        
        Args:
            hybrid_results: 混合检索结果列表
            
        Returns:
            List[Dict]: 包含综合得分的结果列表
        """
        scored_results = []
        
        for result in hybrid_results:
            vector_score = result.get("vector_score", 0)
            keyword_score = result.get("keyword_score", 0)
            
            # 加权综合得分
            combined_score = (
                vector_score * self.vector_weight +
                keyword_score * self.keyword_weight
            )
            
            scored_result = {
                **result,
                "combined_score": combined_score,
            }
            scored_results.append(scored_result)
        
        # 按综合得分排序（降序）
        scored_results.sort(key=lambda x: x["combined_score"], reverse=True)
        
        return scored_results
    
    def _rerank_results(
        self,
        query: str,
        results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        对检索结果进行重排序
        
        使用多种启发式规则优化排序结果，包括：
        - 查询-文档相关性微调
        - 内容质量评分
        - 多样性增强
        
        Args:
            query: 原始查询
            results: 待重排序的结果列表
            
        Returns:
            List[Dict]: 重排序后的结果列表
        """
        if not results:
            return results
        
        reranked = []
        
        for result in results:
            content = result.get("content", "")
            base_score = result.get("combined_score", 0)
            
            # 1. 内容质量评分
            quality_score = self._calculate_quality_score(content)
            
            # 2. 查询相关性微调
            relevance_boost = self._calculate_relevance_boost(query, content)
            
            # 3. 计算最终重排序得分
            final_score = base_score * 0.7 + quality_score * 0.2 + relevance_boost * 0.1
            
            reranked.append({
                **result,
                "final_score": final_score,
                "quality_score": quality_score,
                "relevance_boost": relevance_boost,
            })
        
        # 按最终得分排序
        reranked.sort(key=lambda x: x["final_score"], reverse=True)
        
        return reranked
    
    def _calculate_quality_score(self, content: str) -> float:
        """
        计算内容质量得分
        
        基于内容长度、结构完整性、信息密度等因素评分。
        
        Args:
            content: 文档内容
            
        Returns:
            float: 质量得分（0-1之间）
        """
        if not content:
            return 0.0
        
        scores = []
        
        # 1. 长度得分（适中长度得分最高）
        length = len(content)
        if 100 <= length <= 1000:
            length_score = 1.0
        elif length < 100:
            length_score = length / 100 * 0.5
        else:
            length_score = max(0, 1 - (length - 1000) / 2000)
        scores.append(length_score)
        
        # 2. 结构得分（包含标题、列表、段落等）
        structure_score = 0.0
        if re.search(r'[一二三四五六七八九十]、|\d+\.', content):  # 有序列表
            structure_score += 0.3
        if re.search(r'[•·\-]\s', content):  # 无序列表
            structure_score += 0.2
        if '\n\n' in content:  # 段落分隔
            structure_score += 0.2
        if re.search(r'[。！？]', content):  # 完整句子
            structure_score += 0.3
        scores.append(min(structure_score, 1.0))
        
        # 3. 信息密度得分（关键词密度）
        words = len(re.findall(r'\w+', content))
        density = words / (length + 1)
        density_score = min(density * 10, 1.0)  # 归一化
        scores.append(density_score)
        
        # 4. 可读性得分（避免过长句子）
        sentences = re.split(r'[。！？.!?]', content)
        avg_sentence_length = sum(len(s) for s in sentences) / max(len(sentences), 1)
        readability_score = 1.0 if avg_sentence_length < 50 else max(0, 1 - (avg_sentence_length - 50) / 100)
        scores.append(readability_score)
        
        return sum(scores) / len(scores)
    
    def _calculate_relevance_boost(self, query: str, content: str) -> float:
        """
        计算查询相关性增强得分
        
        检测查询中的关键概念是否在文档中明确提及。
        
        Args:
            query: 查询文本
            content: 文档内容
            
        Returns:
            float: 相关性增强得分
        """
        query_lower = query.lower()
        content_lower = content.lower()
        
        boost = 0.0
        
        # 1. 完整查询匹配
        if query_lower in content_lower:
            boost += 0.5
        
        # 2. 关键短语匹配（提取2-3字短语）
        query_phrases = self._extract_keywords(query)
        matched_phrases = sum(1 for phrase in query_phrases if phrase in content_lower)
        if query_phrases:
            boost += (matched_phrases / len(query_phrases)) * 0.5
        
        return min(boost, 1.0)
    
    def _convert_to_results(
        self,
        scored_results: List[Dict[str, Any]],
    ) -> List[RetrievalResult]:
        """
        将原始结果转换为RetrievalResult对象
        
        Args:
            scored_results: 带得分的结果列表
            
        Returns:
            List[RetrievalResult]: 转换后的结果对象列表
        """
        results = []
        
        for result in scored_results:
            retrieval_result = RetrievalResult(
                id=result.get("id", 0),
                content=result.get("content", ""),
                score=result.get("final_score", result.get("combined_score", 0)),
                vector_score=result.get("vector_score", 0),
                keyword_score=result.get("keyword_score", 0),
                source=result.get("source", "unknown"),
                metadata=result.get("metadata", {}) or {},
                created_at=result.get("created_at", 0),
            )
            results.append(retrieval_result)
        
        return results
    
    def format_context(
        self,
        results: List[RetrievalResult],
        max_length: int = 3000,
        include_source: bool = True,
        include_score: bool = False,
        separator: str = "\n\n---\n\n",
    ) -> str:
        """
        将检索结果格式化为上下文字符串
        
        将多个检索结果组装成适合大语言模型使用的上下文格式。
        
        Args:
            results: 检索结果列表
            max_length: 上下文最大长度（字符数）
            include_source: 是否包含来源信息
            include_score: 是否包含相关性得分
            separator: 文档之间的分隔符
            
        Returns:
            str: 格式化后的上下文字符串
            
        Example:
            >>> retriever = RAGRetriever()
            >>> results = retriever.retrieve("如何预防高血压？")
            >>> context = retriever.format_context(results)
            >>> print(context)
        """
        if not results:
            logger.warning("没有检索结果可用于格式化上下文")
            return ""
        
        context_parts = []
        current_length = 0
        
        for i, result in enumerate(results, 1):
            # 构建单个文档的上下文片段
            parts = []
            
            # 文档编号
            parts.append(f"[文档 {i}]")
            
            # 来源信息（可选）
            if include_source and result.source:
                parts.append(f"来源: {result.source}")
            
            # 相关性得分（可选）
            if include_score:
                parts.append(f"相关性: {result.score:.3f}")
            
            # 文档内容
            parts.append(result.content)
            
            # 组装文档片段
            doc_context = "\n".join(parts)
            
            # 检查长度限制
            if current_length + len(doc_context) + len(separator) > max_length:
                # 尝试截断当前文档
                remaining = max_length - current_length - len(separator) - 100
                if remaining > 100:
                    truncated = doc_context[:remaining] + "..."
                    context_parts.append(truncated)
                break
            
            context_parts.append(doc_context)
            current_length += len(doc_context) + len(separator)
        
        # 使用分隔符连接所有片段
        context = separator.join(context_parts)
        
        logger.info(f"上下文格式化完成，包含 {len(context_parts)} 个文档，总长度: {len(context)}")
        
        return context
    
    def batch_retrieve(
        self,
        queries: List[str],
        top_k: int = 5,
        use_hybrid: bool = True,
        rerank: bool = True,
    ) -> List[List[RetrievalResult]]:
        """
        批量执行检索操作
        
        对多个查询进行批量检索，提高效率。
        
        Args:
            queries: 查询文本列表
            top_k: 每个查询返回的结果数量
            use_hybrid: 是否使用混合检索
            rerank: 是否重排序
            
        Returns:
            List[List[RetrievalResult]]: 每个查询的检索结果列表
        """
        if not queries:
            return []
        
        logger.info(f"开始批量检索，共 {len(queries)} 个查询")
        
        results = []
        for query in queries:
            try:
                result = self.retrieve(query, top_k, use_hybrid, rerank)
                results.append(result)
            except Exception as e:
                logger.error(f"查询 '{query[:30]}...' 检索失败: {e}")
                results.append([])
        
        logger.info(f"批量检索完成")
        return results


# 模块级函数，提供便捷访问方式

_retriever_instance: Optional[RAGRetriever] = None


def get_retriever(
    collection_name: Optional[str] = None,
    vector_weight: float = RAGRetriever.DEFAULT_VECTOR_WEIGHT,
    keyword_weight: float = RAGRetriever.DEFAULT_KEYWORD_WEIGHT,
) -> RAGRetriever:
    """
    获取RAG检索器单例实例
    
    使用单例模式确保全局只有一个检索器实例，避免重复初始化。
    
    Args:
        collection_name: 集合名称
        vector_weight: 向量权重
        keyword_weight: 关键词权重
        
    Returns:
        RAGRetriever: 检索器实例
    """
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = RAGRetriever(
            collection_name=collection_name,
            vector_weight=vector_weight,
            keyword_weight=keyword_weight,
        )
    return _retriever_instance


def retrieve_documents(
    query: str,
    top_k: int = 5,
    use_hybrid: bool = True,
    rerank: bool = True,
) -> List[RetrievalResult]:
    """
    便捷函数：执行文档检索
    
    Args:
        query: 查询文本
        top_k: 返回结果数量
        use_hybrid: 是否使用混合检索
        rerank: 是否重排序
        
    Returns:
        List[RetrievalResult]: 检索结果列表
    """
    retriever = get_retriever()
    return retriever.retrieve(query, top_k, use_hybrid, rerank)


def format_retrieval_context(
    results: List[RetrievalResult],
    max_length: int = 3000,
    include_source: bool = True,
) -> str:
    """
    便捷函数：格式化检索结果为上下文
    
    Args:
        results: 检索结果列表
        max_length: 最大长度
        include_source: 是否包含来源
        
    Returns:
        str: 格式化后的上下文
    """
    retriever = get_retriever()
    return retriever.format_context(results, max_length, include_source)
