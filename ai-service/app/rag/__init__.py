"""
RAG (Retrieval-Augmented Generation) 模块
提供向量数据库检索和知识库管理功能
"""

from .milvus_client import MilvusClient, get_milvus_client, init_milvus
from .embedding_service import EmbeddingService, get_embedding_service, encode_text, encode_texts
from .retriever import RAGRetriever, get_retriever, retrieve_documents, format_retrieval_context
from .knowledge_base import KnowledgeBase, get_knowledge_base, add_knowledge_document, search_knowledge

__all__ = [
    # Milvus客户端
    'MilvusClient',
    'get_milvus_client',
    'init_milvus',
    # 嵌入服务
    'EmbeddingService',
    'get_embedding_service',
    'encode_text',
    'encode_texts',
    # 检索器
    'RAGRetriever',
    'get_retriever',
    'retrieve_documents',
    'format_retrieval_context',
    # 知识库
    'KnowledgeBase',
    'get_knowledge_base',
    'add_knowledge_document',
    'search_knowledge',
]
