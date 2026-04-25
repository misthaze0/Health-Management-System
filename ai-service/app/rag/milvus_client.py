"""
Milvus客户端封装模块

提供向量数据库的连接管理、集合操作、向量插入/删除/检索等功能
"""
import logging
from typing import List, Dict, Any, Optional, Union
from contextlib import contextmanager

from pymilvus import (
    connections,
    utility,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    MilvusException,
)

from app.core.config import settings

# 配置日志记录器
logger = logging.getLogger(__name__)


class MilvusClient:
    """
    Milvus向量数据库客户端封装类
    
    功能：
    - 连接管理（连接池、连接异常处理）
    - 集合管理（创建、删除、查询）
    - 向量操作（插入、删除、相似度搜索）
    """

    def __init__(self):
        """初始化Milvus客户端"""
        self.host = settings.MILVUS_HOST
        self.port = settings.MILVUS_PORT
        self.default_collection = settings.MILVUS_COLLECTION
        self.default_dim = settings.MILVUS_DIM
        self._connection_alias = "default"
        self._is_connected = False

    # ==================== 连接管理 ====================

    def connect(self) -> bool:
        """
        建立与Milvus服务器的连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            if self._is_connected and connections.has_connection(self._connection_alias):
                logger.debug("Milvus连接已存在，跳过连接")
                return True

            connections.connect(
                alias=self._connection_alias,
                host=self.host,
                port=self.port,
            )
            self._is_connected = True
            logger.info(f"成功连接到Milvus服务器: {self.host}:{self.port}")
            return True

        except MilvusException as e:
            logger.error(f"连接Milvus服务器失败: {e}")
            self._is_connected = False
            return False
        except Exception as e:
            logger.error(f"连接Milvus时发生未知错误: {e}")
            self._is_connected = False
            return False

    def disconnect(self) -> None:
        """断开与Milvus服务器的连接"""
        try:
            if connections.has_connection(self._connection_alias):
                connections.disconnect(self._connection_alias)
                self._is_connected = False
                logger.info("已断开Milvus连接")
        except Exception as e:
            logger.error(f"断开Milvus连接时出错: {e}")

    def check_connection(self) -> bool:
        """
        检查当前连接状态
        
        Returns:
            bool: 是否已连接
        """
        try:
            self._is_connected = connections.has_connection(self._connection_alias)
            return self._is_connected
        except Exception as e:
            logger.error(f"检查连接状态时出错: {e}")
            return False

    @contextmanager
    def connection_context(self):
        """
        连接上下文管理器
        
        使用示例：
            with client.connection_context():
                # 执行Milvus操作
                pass
        """
        try:
            if not self.connect():
                raise ConnectionError("无法连接到Milvus服务器")
            yield self
        finally:
            # 注意：这里不自动断开，保持连接复用
            pass

    def ensure_connected(self) -> None:
        """
        确保已连接到Milvus，如果未连接则尝试连接
        
        Raises:
            ConnectionError: 连接失败时抛出
        """
        if not self._is_connected or not self.check_connection():
            if not self.connect():
                raise ConnectionError(
                    f"无法连接到Milvus服务器 {self.host}:{self.port}"
                )

    # ==================== 集合管理 ====================

    def create_collection(
        self,
        collection_name: str,
        dim: Optional[int] = None,
        description: str = "",
        auto_id: bool = True,
    ) -> bool:
        """
        创建向量集合
        
        Args:
            collection_name: 集合名称
            dim: 向量维度，默认使用配置中的MILVUS_DIM
            description: 集合描述
            auto_id: 是否自动生成ID
            
        Returns:
            bool: 创建是否成功
        """
        try:
            self.ensure_connected()

            # 检查集合是否已存在
            if utility.has_collection(collection_name):
                logger.warning(f"集合 '{collection_name}' 已存在")
                return False

            # 使用默认维度
            vector_dim = dim or self.default_dim

            # 定义字段
            fields = [
                # 主键字段
                FieldSchema(
                    name="id",
                    dtype=DataType.INT64,
                    is_primary=True,
                    auto_id=auto_id,
                    description="主键ID",
                ),
                # 向量字段
                FieldSchema(
                    name="vector",
                    dtype=DataType.FLOAT_VECTOR,
                    dim=vector_dim,
                    description="向量数据",
                ),
                # 文本内容字段
                FieldSchema(
                    name="content",
                    dtype=DataType.VARCHAR,
                    max_length=65535,
                    description="原始文本内容",
                ),
                # 元数据字段（JSON格式存储）
                FieldSchema(
                    name="metadata",
                    dtype=DataType.VARCHAR,
                    max_length=65535,
                    description="元数据JSON",
                ),
                # 来源字段
                FieldSchema(
                    name="source",
                    dtype=DataType.VARCHAR,
                    max_length=512,
                    description="数据来源",
                ),
                # 创建时间字段
                FieldSchema(
                    name="created_at",
                    dtype=DataType.INT64,
                    description="创建时间戳",
                ),
            ]

            # 创建集合schema
            schema = CollectionSchema(
                fields=fields,
                description=description or f"Collection for {collection_name}",
            )

            # 创建集合
            collection = Collection(
                name=collection_name,
                schema=schema,
                using=self._connection_alias,
            )

            logger.info(f"成功创建集合 '{collection_name}'，向量维度: {vector_dim}")
            return True

        except MilvusException as e:
            logger.error(f"创建集合 '{collection_name}' 失败: {e}")
            return False
        except Exception as e:
            logger.error(f"创建集合时发生未知错误: {e}")
            return False

    def drop_collection(self, collection_name: str) -> bool:
        """
        删除集合
        
        Args:
            collection_name: 要删除的集合名称
            
        Returns:
            bool: 删除是否成功
        """
        try:
            self.ensure_connected()

            if not utility.has_collection(collection_name):
                logger.warning(f"集合 '{collection_name}' 不存在")
                return False

            utility.drop_collection(collection_name)
            logger.info(f"成功删除集合 '{collection_name}'")
            return True

        except MilvusException as e:
            logger.error(f"删除集合 '{collection_name}' 失败: {e}")
            return False
        except Exception as e:
            logger.error(f"删除集合时发生未知错误: {e}")
            return False

    def has_collection(self, collection_name: str) -> bool:
        """
        检查集合是否存在
        
        Args:
            collection_name: 集合名称
            
        Returns:
            bool: 集合是否存在
        """
        try:
            self.ensure_connected()
            return utility.has_collection(collection_name)
        except Exception as e:
            logger.error(f"检查集合存在性时出错: {e}")
            return False

    def list_collections(self) -> List[str]:
        """
        获取所有集合列表
        
        Returns:
            List[str]: 集合名称列表
        """
        try:
            self.ensure_connected()
            collections = utility.list_collections()
            logger.debug(f"获取到 {len(collections)} 个集合")
            return collections
        except Exception as e:
            logger.error(f"获取集合列表时出错: {e}")
            return []

    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        获取集合统计信息
        
        Args:
            collection_name: 集合名称
            
        Returns:
            Dict: 包含行数等统计信息的字典
        """
        try:
            self.ensure_connected()

            if not utility.has_collection(collection_name):
                return {"error": f"集合 '{collection_name}' 不存在"}

            collection = Collection(collection_name)
            collection.load()

            stats = {
                "name": collection_name,
                "row_count": collection.num_entities,
                "is_loaded": True,
                "schema": {
                    "fields": [
                        {
                            "name": field.name,
                            "type": str(field.dtype),
                        }
                        for field in collection.schema.fields
                    ]
                },
            }

            return stats

        except Exception as e:
            logger.error(f"获取集合统计信息时出错: {e}")
            return {"error": str(e)}

    # ==================== 索引管理 ====================

    def create_index(
        self,
        collection_name: str,
        field_name: str = "vector",
        index_type: str = "IVF_FLAT",
        metric_type: str = "L2",
        params: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        为集合创建索引
        
        Args:
            collection_name: 集合名称
            field_name: 要索引的字段名，默认为vector
            index_type: 索引类型（IVF_FLAT, HNSW等）
            metric_type: 距离度量类型（L2, IP等）
            params: 索引参数
            
        Returns:
            bool: 创建是否成功
        """
        try:
            self.ensure_connected()

            if not utility.has_collection(collection_name):
                logger.error(f"集合 '{collection_name}' 不存在")
                return False

            collection = Collection(collection_name)

            # 默认索引参数
            default_params = {"nlist": 128}
            if index_type == "HNSW":
                default_params = {"M": 16, "efConstruction": 200}

            index_params = params or default_params

            # 创建索引
            index = {
                "index_type": index_type,
                "metric_type": metric_type,
                "params": index_params,
            }

            collection.create_index(field_name=field_name, index_params=index)
            logger.info(
                f"成功为集合 '{collection_name}' 的字段 '{field_name}' 创建索引"
            )
            return True

        except MilvusException as e:
            logger.error(f"创建索引失败: {e}")
            return False
        except Exception as e:
            logger.error(f"创建索引时发生未知错误: {e}")
            return False

    def load_collection(self, collection_name: str) -> bool:
        """
        加载集合到内存
        
        Args:
            collection_name: 集合名称
            
        Returns:
            bool: 加载是否成功
        """
        try:
            self.ensure_connected()

            if not utility.has_collection(collection_name):
                logger.error(f"集合 '{collection_name}' 不存在")
                return False

            collection = Collection(collection_name)
            collection.load()
            logger.debug(f"集合 '{collection_name}' 已加载到内存")
            return True

        except Exception as e:
            logger.error(f"加载集合失败: {e}")
            return False

    def release_collection(self, collection_name: str) -> bool:
        """
        释放集合内存
        
        Args:
            collection_name: 集合名称
            
        Returns:
            bool: 释放是否成功
        """
        try:
            self.ensure_connected()

            if not utility.has_collection(collection_name):
                logger.error(f"集合 '{collection_name}' 不存在")
                return False

            collection = Collection(collection_name)
            collection.release()
            logger.debug(f"集合 '{collection_name}' 已从内存释放")
            return True

        except Exception as e:
            logger.error(f"释放集合失败: {e}")
            return False

    # ==================== 向量操作 ====================

    def insert(
        self,
        collection_name: str,
        vectors: List[List[float]],
        contents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        sources: Optional[List[str]] = None,
        timestamps: Optional[List[int]] = None,
    ) -> Optional[List[int]]:
        """
        插入向量数据
        
        Args:
            collection_name: 集合名称
            vectors: 向量列表，每个向量是float列表
            contents: 对应的原始文本内容列表
            metadatas: 元数据字典列表，可选
            sources: 数据来源列表，可选
            timestamps: 创建时间戳列表，可选
            
        Returns:
            Optional[List[int]]: 插入记录的主键ID列表，失败返回None
        """
        try:
            self.ensure_connected()

            if not utility.has_collection(collection_name):
                logger.error(f"集合 '{collection_name}' 不存在")
                return None

            # 参数校验
            if len(vectors) != len(contents):
                raise ValueError("vectors和contents长度必须相同")

            # 准备默认数据
            import json
            import time

            count = len(vectors)
            metadatas = metadatas or [{} for _ in range(count)]
            sources = sources or ["unknown" for _ in range(count)]
            timestamps = timestamps or [int(time.time()) for _ in range(count)]

            # 构建插入数据
            entities = [
                # vector字段
                vectors,
                # content字段
                contents,
                # metadata字段（转为JSON字符串）
                [json.dumps(m, ensure_ascii=False) for m in metadatas],
                # source字段
                sources,
                # created_at字段
                timestamps,
            ]

            collection = Collection(collection_name)
            insert_result = collection.insert(entities)

            # 刷新以确保持久化
            collection.flush()

            ids = insert_result.primary_keys
            logger.info(f"成功向集合 '{collection_name}' 插入 {count} 条记录，ID: {ids}")
            return ids

        except MilvusException as e:
            logger.error(f"插入数据失败: {e}")
            return None
        except Exception as e:
            logger.error(f"插入数据时发生未知错误: {e}")
            return None

    def delete(
        self,
        collection_name: str,
        ids: Optional[List[int]] = None,
        expr: Optional[str] = None,
    ) -> bool:
        """
        删除向量数据
        
        Args:
            collection_name: 集合名称
            ids: 要删除的记录ID列表
            expr: 删除表达式（如 "id in [1,2,3]" 或 "source == 'xxx'"）
            
        Returns:
            bool: 删除是否成功
        """
        try:
            self.ensure_connected()

            if not utility.has_collection(collection_name):
                logger.error(f"集合 '{collection_name}' 不存在")
                return False

            collection = Collection(collection_name)
            collection.load()

            # 构建删除表达式
            if ids:
                expr = f"id in {ids}"
            elif not expr:
                logger.error("必须提供ids或expr参数")
                return False

            delete_result = collection.delete(expr)
            collection.flush()

            logger.info(f"从集合 '{collection_name}' 删除数据，表达式: {expr}")
            return True

        except MilvusException as e:
            logger.error(f"删除数据失败: {e}")
            return False
        except Exception as e:
            logger.error(f"删除数据时发生未知错误: {e}")
            return False

    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        top_k: int = 10,
        metric_type: str = "L2",
        output_fields: Optional[List[str]] = None,
        expr: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        向量相似度搜索
        
        Args:
            collection_name: 集合名称
            query_vector: 查询向量
            top_k: 返回最相似的结果数量
            metric_type: 距离度量类型（L2, IP, COSINE等）
            output_fields: 要返回的字段列表
            expr: 过滤表达式
            
        Returns:
            List[Dict]: 搜索结果列表，每个结果包含id、distance、content等字段
        """
        try:
            self.ensure_connected()

            if not utility.has_collection(collection_name):
                logger.error(f"集合 '{collection_name}' 不存在")
                return []

            # 默认返回字段
            output_fields = output_fields or ["id", "content", "metadata", "source", "created_at"]

            collection = Collection(collection_name)
            collection.load()

            # 构建搜索参数
            search_params = {
                "metric_type": metric_type,
                "params": {"nprobe": 10},
            }

            # 执行搜索
            results = collection.search(
                data=[query_vector],
                anns_field="vector",
                param=search_params,
                limit=top_k,
                expr=expr,
                output_fields=output_fields,
            )

            # 解析结果
            search_results = []
            import json

            for hits in results:
                for hit in hits:
                    result = {
                        "id": hit.id,
                        "distance": hit.distance,
                        "score": 1 / (1 + hit.distance) if metric_type == "L2" else hit.distance,
                    }

                    # 添加其他字段
                    for field in output_fields:
                        if field in hit.entity.fields:
                            value = hit.entity.get(field)
                            # 解析metadata JSON
                            if field == "metadata" and isinstance(value, str):
                                try:
                                    value = json.loads(value)
                                except json.JSONDecodeError:
                                    pass
                            result[field] = value

                    search_results.append(result)

            logger.debug(
                f"在集合 '{collection_name}' 中搜索，返回 {len(search_results)} 条结果"
            )
            return search_results

        except MilvusException as e:
            logger.error(f"向量搜索失败: {e}")
            return []
        except Exception as e:
            logger.error(f"向量搜索时发生未知错误: {e}")
            return []

    def batch_search(
        self,
        collection_name: str,
        query_vectors: List[List[float]],
        top_k: int = 10,
        metric_type: str = "L2",
        output_fields: Optional[List[str]] = None,
        expr: Optional[str] = None,
    ) -> List[List[Dict[str, Any]]]:
        """
        批量向量相似度搜索
        
        Args:
            collection_name: 集合名称
            query_vectors: 查询向量列表
            top_k: 每个查询返回最相似的结果数量
            metric_type: 距离度量类型
            output_fields: 要返回的字段列表
            expr: 过滤表达式
            
        Returns:
            List[List[Dict]]: 每个查询向量的搜索结果列表
        """
        try:
            self.ensure_connected()

            if not utility.has_collection(collection_name):
                logger.error(f"集合 '{collection_name}' 不存在")
                return [[] for _ in query_vectors]

            output_fields = output_fields or ["id", "content", "metadata", "source", "created_at"]

            collection = Collection(collection_name)
            collection.load()

            search_params = {
                "metric_type": metric_type,
                "params": {"nprobe": 10},
            }

            results = collection.search(
                data=query_vectors,
                anns_field="vector",
                param=search_params,
                limit=top_k,
                expr=expr,
                output_fields=output_fields,
            )

            # 解析结果
            all_results = []
            import json

            for hits in results:
                search_results = []
                for hit in hits:
                    result = {
                        "id": hit.id,
                        "distance": hit.distance,
                        "score": 1 / (1 + hit.distance) if metric_type == "L2" else hit.distance,
                    }

                    for field in output_fields:
                        if field in hit.entity.fields:
                            value = hit.entity.get(field)
                            if field == "metadata" and isinstance(value, str):
                                try:
                                    value = json.loads(value)
                                except json.JSONDecodeError:
                                    pass
                            result[field] = value

                    search_results.append(result)
                all_results.append(search_results)

            logger.debug(
                f"批量搜索完成，{len(query_vectors)} 个查询，平均每个返回 {len(all_results[0]) if all_results else 0} 条结果"
            )
            return all_results

        except MilvusException as e:
            logger.error(f"批量向量搜索失败: {e}")
            return [[] for _ in query_vectors]
        except Exception as e:
            logger.error(f"批量向量搜索时发生未知错误: {e}")
            return [[] for _ in query_vectors]

    def get_by_id(
        self,
        collection_name: str,
        ids: List[int],
        output_fields: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        根据ID获取记录
        
        Args:
            collection_name: 集合名称
            ids: 记录ID列表
            output_fields: 要返回的字段列表
            
        Returns:
            List[Dict]: 记录列表
        """
        try:
            self.ensure_connected()

            if not utility.has_collection(collection_name):
                logger.error(f"集合 '{collection_name}' 不存在")
                return []

            output_fields = output_fields or ["id", "content", "metadata", "source", "created_at"]

            collection = Collection(collection_name)
            collection.load()

            expr = f"id in {ids}"
            results = collection.query(
                expr=expr,
                output_fields=output_fields,
            )

            # 解析metadata
            import json
            for result in results:
                if "metadata" in result and isinstance(result["metadata"], str):
                    try:
                        result["metadata"] = json.loads(result["metadata"])
                    except json.JSONDecodeError:
                        pass

            return results

        except Exception as e:
            logger.error(f"根据ID获取记录失败: {e}")
            return []

    def count(self, collection_name: str, expr: Optional[str] = None) -> int:
        """
        统计集合中的记录数
        
        Args:
            collection_name: 集合名称
            expr: 过滤表达式
            
        Returns:
            int: 记录数量
        """
        try:
            self.ensure_connected()

            if not utility.has_collection(collection_name):
                logger.error(f"集合 '{collection_name}' 不存在")
                return 0

            collection = Collection(collection_name)

            if expr:
                collection.load()
                result = collection.query(expr=expr, output_fields=["count(*)"])
                return result[0].get("count(*)", 0) if result else 0
            else:
                return collection.num_entities

        except Exception as e:
            logger.error(f"统计记录数失败: {e}")
            return 0


# 全局客户端实例（单例模式）
_milvus_client: Optional[MilvusClient] = None


def get_milvus_client() -> MilvusClient:
    """
    获取Milvus客户端单例
    
    Returns:
        MilvusClient: Milvus客户端实例
    """
    global _milvus_client
    if _milvus_client is None:
        _milvus_client = MilvusClient()
    return _milvus_client


def init_milvus() -> bool:
    """
    初始化Milvus连接和默认集合
    
    Returns:
        bool: 初始化是否成功
    """
    try:
        client = get_milvus_client()

        # 建立连接
        if not client.connect():
            logger.error("Milvus初始化失败：无法建立连接")
            return False

        # 创建默认集合（如果不存在）
        if not client.has_collection(settings.MILVUS_COLLECTION):
            logger.info(f"创建默认集合: {settings.MILVUS_COLLECTION}")
            if client.create_collection(settings.MILVUS_COLLECTION):
                # 创建索引
                client.create_index(settings.MILVUS_COLLECTION)
                # 加载集合
                client.load_collection(settings.MILVUS_COLLECTION)
            else:
                logger.error("创建默认集合失败")
                return False
        else:
            # 加载已存在的集合
            client.load_collection(settings.MILVUS_COLLECTION)

        logger.info("Milvus初始化完成")
        return True

    except Exception as e:
        logger.error(f"Milvus初始化时发生错误: {e}")
        return False
