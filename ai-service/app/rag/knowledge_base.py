"""
知识库管理模块

提供健康知识库的文档管理功能，包括：
- 文档分块处理
- 文档向量化存储
- 语义检索
- 文档删除
"""

import logging
import time
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.config import settings
from app.rag.milvus_client import get_milvus_client, MilvusClient
from app.rag.embedding_service import get_embedding_service, EmbeddingService

# 配置日志记录器
logger = logging.getLogger(__name__)


class KnowledgeBase:
    """
    知识库管理类

    集成Milvus向量数据库和嵌入服务，提供完整的知识库管理功能。
    支持文档的自动分块、向量化存储、语义检索和删除操作。

    Attributes:
        milvus_client: Milvus向量数据库客户端
        embedding_service: 文本嵌入服务
        collection_name: 当前使用的集合名称
    """

    def __init__(self, collection_name: Optional[str] = None):
        """
        初始化知识库管理器

        Args:
            collection_name: 集合名称，默认使用配置中的MILVUS_COLLECTION
        """
        self.milvus_client: MilvusClient = get_milvus_client()
        self.embedding_service: EmbeddingService = get_embedding_service()
        self.collection_name: str = collection_name or settings.MILVUS_COLLECTION

        # 确保Milvus连接和集合初始化
        self._ensure_collection_ready()

        logger.info(f"KnowledgeBase初始化完成，使用集合: {self.collection_name}")

    def _ensure_collection_ready(self) -> None:
        """
        确保Milvus连接正常且集合已创建

        如果集合不存在，自动创建集合并建立索引。
        """
        try:
            # 建立连接
            if not self.milvus_client.connect():
                raise ConnectionError("无法连接到Milvus服务器")

            # 检查集合是否存在
            if not self.milvus_client.has_collection(self.collection_name):
                logger.info(f"创建知识库集合: {self.collection_name}")

                # 创建集合
                success = self.milvus_client.create_collection(
                    collection_name=self.collection_name,
                    description="健康知识库集合，存储医疗文档的向量表示"
                )
                if not success:
                    raise RuntimeError(f"创建集合 {self.collection_name} 失败")

                # 创建索引
                index_success = self.milvus_client.create_index(
                    collection_name=self.collection_name,
                    index_type="IVF_FLAT",
                    metric_type="L2"
                )
                if not index_success:
                    logger.warning(f"为集合 {self.collection_name} 创建索引失败")

            # 加载集合到内存
            self.milvus_client.load_collection(self.collection_name)
            logger.debug(f"集合 {self.collection_name} 已加载到内存")

        except Exception as e:
            logger.error(f"初始化知识库集合时出错: {e}")
            raise

    @staticmethod
    def chunk_document(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        文档分块处理

        将长文本按照指定大小分块，支持重叠以保持上下文连贯性。
        优先按句子边界分块，如果句子过长则按字符数强制分割。

        Args:
            text: 原始文本内容
            chunk_size: 每个块的最大字符数，默认500
            overlap: 块之间的重叠字符数，默认50

        Returns:
            List[str]: 分块后的文本列表

        Example:
            >>> chunks = KnowledgeBase.chunk_document("这是一个很长的文本...", chunk_size=100)
            >>> print(len(chunks))
        """
        if not text or not isinstance(text, str):
            logger.warning("输入文本为空或类型错误")
            return []

        text = text.strip()
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            # 计算当前块的结束位置
            end = start + chunk_size

            if end >= len(text):
                # 剩余文本不足一个块，直接添加
                chunks.append(text[start:].strip())
                break

            # 尝试在句子边界处分割（查找句号、问号、感叹号）
            chunk_text = text[start:end]

            # 查找最后一个句子结束符
            sentence_end = -1
            for i in range(len(chunk_text) - 1, -1, -1):
                if chunk_text[i] in '。！？.!?':
                    sentence_end = i + 1
                    break

            if sentence_end > chunk_size // 2:  # 如果找到合适的句子边界
                end = start + sentence_end
            # 否则在chunk_size处强制分割

            # 添加当前块
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # 计算下一个块的起始位置（考虑重叠）
            start = end - overlap
            if start <= 0:
                start = end

        logger.debug(f"文档分块完成: {len(text)} 字符 -> {len(chunks)} 个块")
        return chunks

    def add_document(
        self,
        title: str,
        content: str,
        category: str,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[List[int]]:
        """
        添加文档到知识库

        自动将文档分块、向量化并存储到Milvus向量数据库。
        每个文档块都会保留原始文档的标题、分类等元数据。

        Args:
            title: 文档标题
            content: 文档内容
            category: 文档分类（如"疾病知识"、"健康建议"等）
            source: 文档来源，可选
            metadata: 额外元数据字典，可选

        Returns:
            Optional[List[int]]: 插入记录的ID列表，失败返回None

        Raises:
            ValueError: 当标题或内容为空时
            ConnectionError: 当Milvus连接失败时

        Example:
            >>> kb = KnowledgeBase()
            >>> ids = kb.add_document(
            ...     title="高血压防治指南",
            ...     content="高血压是一种常见的慢性病...",
            ...     category="疾病知识",
            ...     source="卫生部"
            ... )
        """
        # 参数校验
        if not title or not isinstance(title, str):
            raise ValueError("文档标题必须是非空字符串")
        if not content or not isinstance(content, str):
            raise ValueError("文档内容必须是非空字符串")
        if not category or not isinstance(category, str):
            raise ValueError("文档分类必须是非空字符串")

        try:
            logger.info(f"开始添加文档: '{title}' (分类: {category})")

            # 1. 文档分块
            chunks = self.chunk_document(content)
            if not chunks:
                logger.warning(f"文档 '{title}' 分块后为空")
                return None

            logger.info(f"文档分块完成: '{title}' -> {len(chunks)} 个块")

            # 2. 文本向量化
            vectors = self.embedding_service.encode_batch(chunks)
            if not vectors or len(vectors) != len(chunks):
                logger.error(f"文档 '{title}' 向量化失败")
                return None

            logger.info(f"向量化完成: '{title}' -> {len(vectors)} 个向量")

            # 3. 准备元数据
            base_metadata = metadata or {}
            current_time = int(time.time())

            metadatas = []
            sources = []
            timestamps = []

            for i, chunk in enumerate(chunks):
                # 每个块的元数据
                chunk_metadata = {
                    **base_metadata,
                    "title": title,
                    "category": category,
                    "chunk_index": i,
                    "chunk_count": len(chunks),
                    "chunk_size": len(chunk),
                    "added_at": datetime.now().isoformat(),
                }
                metadatas.append(chunk_metadata)
                sources.append(source or "knowledge_base")
                timestamps.append(current_time)

            # 4. 插入到Milvus
            doc_ids = self.milvus_client.insert(
                collection_name=self.collection_name,
                vectors=vectors,
                contents=chunks,
                metadatas=metadatas,
                sources=sources,
                timestamps=timestamps,
            )

            if doc_ids:
                logger.info(f"文档添加成功: '{title}' -> IDs: {doc_ids}")
            else:
                logger.error(f"文档添加失败: '{title}'")

            return doc_ids

        except Exception as e:
            logger.error(f"添加文档 '{title}' 时发生错误: {e}")
            raise

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        top_k: int = 5,
        score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        语义检索

        根据查询文本进行向量相似度搜索，返回最相关的知识库内容。
        支持按分类过滤，并可根据相似度分数阈值筛选结果。

        Args:
            query: 查询文本
            category: 文档分类过滤，可选
            top_k: 返回结果数量，默认5
            score_threshold: 相似度分数阈值（0-1），默认0.5

        Returns:
            List[Dict]: 搜索结果列表，每个结果包含：
                - id: 记录ID
                - content: 文本内容
                - score: 相似度分数（0-1，越高越相似）
                - metadata: 元数据（包含title、category等）
                - source: 数据来源
                - created_at: 创建时间戳

        Raises:
            ValueError: 当查询文本为空时

        Example:
            >>> kb = KnowledgeBase()
            >>> results = kb.search("高血压的治疗方法", category="疾病知识", top_k=3)
            >>> for r in results:
            ...     print(f"{r['metadata']['title']}: {r['score']:.2f}")
        """
        # 参数校验
        if not query or not isinstance(query, str):
            raise ValueError("查询文本必须是非空字符串")

        try:
            logger.info(f"执行语义检索: '{query}' (分类: {category}, top_k: {top_k})")

            # 1. 查询向量化
            query_vector = self.embedding_service.encode(query)

            # 2. 执行向量搜索（不添加过滤条件，因为metadata是JSON类型）
            results = self.milvus_client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                top_k=top_k * 3,  # 获取更多结果以便过滤
                metric_type="L2",
                output_fields=["id", "content", "metadata", "source", "created_at"],
                expr=None,
            )

            # 3. 处理结果
            # 注意：L2距离越小越相似
            filtered_results = []
            for result in results:
                # 如果指定了分类，进行过滤
                if category:
                    metadata = result.get("metadata", {})
                    if isinstance(metadata, str):
                        import json
                        try:
                            metadata = json.loads(metadata)
                        except:
                            metadata = {}
                    if metadata.get("category") != category:
                        continue
                filtered_results.append(result)
                if len(filtered_results) >= top_k:
                    break
            
            # 将L2距离转换为相似度分数（0-1范围，1表示最相似）
            for result in filtered_results:
                l2_distance = result.get("score", 0)
                # 使用指数函数将距离转换为相似度
                # 距离为0时相似度为1，距离越大相似度越小
                similarity = max(0, 1 - (l2_distance / 10))
                result["score"] = round(similarity, 4)

            logger.info(f"检索完成: '{query}' -> 找到 {len(filtered_results)} 条相关结果")

            return filtered_results

        except Exception as e:
            logger.error(f"执行检索 '{query}' 时发生错误: {e}")
            raise

    def delete_document(self, doc_id: str) -> bool:
        """
        删除知识库中的文档

        根据文档ID删除对应的向量记录。

        Args:
            doc_id: 要删除的文档ID（Milvus中的主键ID）

        Returns:
            bool: 删除是否成功

        Raises:
            ValueError: 当doc_id为空时

        Example:
            >>> kb = KnowledgeBase()
            >>> success = kb.delete_document("12345")
            >>> print(f"删除{'成功' if success else '失败'}")
        """
        if not doc_id:
            raise ValueError("文档ID不能为空")

        try:
            logger.info(f"删除文档: ID={doc_id}")

            # 将字符串ID转换为整数（Milvus默认使用INT64作为主键）
            try:
                id_int = int(doc_id)
            except ValueError:
                logger.error(f"无效的文档ID格式: {doc_id}")
                return False

            # 执行删除
            success = self.milvus_client.delete(
                collection_name=self.collection_name,
                ids=[id_int]
            )

            if success:
                logger.info(f"文档删除成功: ID={doc_id}")
            else:
                logger.error(f"文档删除失败: ID={doc_id}")

            return success

        except Exception as e:
            logger.error(f"删除文档 ID={doc_id} 时发生错误: {e}")
            return False

    def delete_by_title(self, title: str) -> int:
        """
        根据标题删除文档

        删除所有标题匹配的文档块。

        Args:
            title: 文档标题

        Returns:
            int: 删除的记录数量
        """
        if not title:
            raise ValueError("文档标题不能为空")

        try:
            logger.info(f"根据标题删除文档: '{title}'")

            # 构建查询表达式
            expr = f'json_contains(metadata, "{title}", "$.title")'

            # 先查询获取ID列表
            results = self.milvus_client.get_by_id(
                collection_name=self.collection_name,
                ids=[],  # 空列表表示查询所有
                output_fields=["id"]
            )

            # 过滤出匹配的ID
            matching_ids = []
            for result in results:
                metadata = result.get("metadata", {})
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except json.JSONDecodeError:
                        continue

                if metadata.get("title") == title:
                    matching_ids.append(result.get("id"))

            if not matching_ids:
                logger.warning(f"未找到标题为 '{title}' 的文档")
                return 0

            # 批量删除
            success = self.milvus_client.delete(
                collection_name=self.collection_name,
                ids=matching_ids
            )

            if success:
                logger.info(f"成功删除 {len(matching_ids)} 条记录 (标题: '{title}')")
                return len(matching_ids)
            else:
                logger.error(f"删除文档失败 (标题: '{title}')")
                return 0

        except Exception as e:
            logger.error(f"根据标题删除文档 '{title}' 时发生错误: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """
        获取知识库统计信息

        Returns:
            Dict: 包含以下字段的字典：
                - total_documents: 总记录数
                - collection_name: 集合名称
                - categories: 分类统计
        """
        try:
            stats = self.milvus_client.get_collection_stats(self.collection_name)
            return {
                "total_documents": stats.get("row_count", 0),
                "collection_name": self.collection_name,
                "schema": stats.get("schema", {}),
            }
        except Exception as e:
            logger.error(f"获取知识库统计信息时出错: {e}")
            return {"error": str(e)}


# ==================== 便捷函数 ====================

_knowledge_base_instance: Optional[KnowledgeBase] = None


def get_knowledge_base() -> KnowledgeBase:
    """
    获取KnowledgeBase单例实例

    Returns:
        KnowledgeBase: 知识库管理器实例
    """
    global _knowledge_base_instance
    if _knowledge_base_instance is None:
        _knowledge_base_instance = KnowledgeBase()
    return _knowledge_base_instance


def add_knowledge_document(
    title: str,
    content: str,
    category: str,
    source: Optional[str] = None
) -> Optional[List[int]]:
    """
    便捷函数：添加文档到知识库

    Args:
        title: 文档标题
        content: 文档内容
        category: 文档分类
        source: 文档来源

    Returns:
        Optional[List[int]]: 插入记录的ID列表
    """
    kb = get_knowledge_base()
    return kb.add_document(title, content, category, source)


def search_knowledge(
    query: str,
    category: Optional[str] = None,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    便捷函数：检索知识库

    Args:
        query: 查询文本
        category: 分类过滤
        top_k: 返回结果数量

    Returns:
        List[Dict]: 搜索结果列表
    """
    kb = get_knowledge_base()
    return kb.search(query, category, top_k)
