"""
智能体基类模块

提供所有AI智能体的抽象基类，定义统一的接口和通用功能。
支持工具管理、记忆召回、知识检索等核心能力。
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field

from app.memory.memory_retriever import (
    MemoryRetriever,
    get_memory_retriever,
    retrieve_memories_combined,
    format_memories
)
from app.rag.retriever import (
    RAGRetriever,
    get_retriever,
    retrieve_documents,
    format_retrieval_context,
    RetrievalResult
)

# 配置日志记录器
logger = logging.getLogger(__name__)


@dataclass
class Tool:
    """
    工具数据类
    
    Attributes:
        name: 工具名称
        func: 工具函数
        description: 工具描述
        parameters: 工具参数定义
    """
    name: str
    func: Callable
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    智能体抽象基类
    
    所有AI智能体的基类，定义统一的接口和通用功能。
    支持工具管理、记忆召回、知识检索等核心能力。
    
    Attributes:
        name: 智能体名称
        description: 智能体描述
        system_prompt: 系统提示词模板
        tools: 工具字典
        memory_retriever: 记忆检索器实例
        rag_retriever: RAG检索器实例
    
    Example:
        >>> class HealthAgent(BaseAgent):
        ...     def __init__(self):
        ...         super().__init__(
        ...             name="健康助手",
        ...             description="提供健康咨询服务",
        ...             system_prompt="你是一个健康助手..."
        ...         )
        ...     
        ...     async def chat(self, messages, **kwargs):
        ...         # 实现聊天逻辑
        ...         return "回复内容"
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        system_prompt: str,
        enable_memory: bool = True,
        enable_rag: bool = True
    ):
        """
        初始化智能体基类
        
        Args:
            name: 智能体名称
            description: 智能体描述
            system_prompt: 系统提示词模板
            enable_memory: 是否启用记忆召回，默认True
            enable_rag: 是否启用知识检索，默认True
        """
        self.name: str = name
        self.description: str = description
        self.system_prompt: str = system_prompt
        self._tools: Dict[str, Tool] = {}
        
        # 初始化记忆检索器
        self._memory_retriever: Optional[MemoryRetriever] = None
        if enable_memory:
            try:
                self._memory_retriever = get_memory_retriever()
                logger.info(f"[{self.name}] 记忆检索器初始化成功")
            except Exception as e:
                logger.warning(f"[{self.name}] 记忆检索器初始化失败: {e}")
        
        # 初始化RAG检索器
        self._rag_retriever: Optional[RAGRetriever] = None
        if enable_rag:
            try:
                self._rag_retriever = get_retriever()
                logger.info(f"[{self.name}] RAG检索器初始化成功")
            except Exception as e:
                logger.warning(f"[{self.name}] RAG检索器初始化失败: {e}")
        
        logger.info(f"智能体 [{self.name}] 初始化完成")
    
    @property
    def name(self) -> str:
        """获取智能体名称"""
        return self._name
    
    @name.setter
    def name(self, value: str):
        """设置智能体名称"""
        if not value or not isinstance(value, str):
            raise ValueError("智能体名称必须是非空字符串")
        self._name = value
    
    @property
    def description(self) -> str:
        """获取智能体描述"""
        return self._description
    
    @description.setter
    def description(self, value: str):
        """设置智能体描述"""
        if not isinstance(value, str):
            raise ValueError("智能体描述必须是字符串")
        self._description = value
    
    @property
    def system_prompt(self) -> str:
        """获取系统提示词"""
        return self._system_prompt
    
    @system_prompt.setter
    def system_prompt(self, value: str):
        """设置系统提示词"""
        if not isinstance(value, str):
            raise ValueError("系统提示词必须是字符串")
        self._system_prompt = value
    
    @abstractmethod
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """
        执行对话
        
        抽象方法，子类必须实现具体的对话逻辑。
        
        Args:
            messages: 消息列表，每个消息为字典格式，包含:
                - role: 角色 (system/user/assistant)
                - content: 消息内容
            **kwargs: 额外参数，可能包含:
                - user_id: 用户ID，用于记忆召回
                - use_memory: 是否使用记忆
                - use_rag: 是否使用知识检索
                - temperature: 温度参数
                - max_tokens: 最大token数
        
        Returns:
            str: AI回复内容
        
        Raises:
            NotImplementedError: 如果子类未实现此方法
        
        Example:
            >>> messages = [
            ...     {"role": "user", "content": "你好"}
            ... ]
            >>> response = await agent.chat(messages, user_id=1)
            >>> print(response)
        """
        pass
    
    def add_tool(
        self,
        name: str,
        func: Callable,
        description: str = "",
        parameters: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        添加工具
        
        为智能体添加一个可调用的工具函数。
        
        Args:
            name: 工具名称，必须唯一
            func: 工具函数
            description: 工具描述
            parameters: 工具参数定义
        
        Raises:
            ValueError: 当工具名称已存在或函数无效时
        
        Example:
            >>> def get_weather(city: str) -> str:
            ...     return f"{city}的天气是晴天"
            >>> agent.add_tool(
            ...     name="get_weather",
            ...     func=get_weather,
            ...     description="获取指定城市的天气",
            ...     parameters={"city": {"type": "string", "description": "城市名称"}}
            ... )
        """
        if not name or not isinstance(name, str):
            raise ValueError("工具名称必须是非空字符串")
        
        if name in self._tools:
            raise ValueError(f"工具 '{name}' 已存在")
        
        if not callable(func):
            raise ValueError("工具函数必须是可调用的")
        
        self._tools[name] = Tool(
            name=name,
            func=func,
            description=description or f"工具: {name}",
            parameters=parameters or {}
        )
        
        logger.info(f"[{self.name}] 添加工具: {name}")
    
    def remove_tool(self, name: str) -> bool:
        """
        移除工具
        
        Args:
            name: 工具名称
        
        Returns:
            bool: 是否成功移除
        """
        if name in self._tools:
            del self._tools[name]
            logger.info(f"[{self.name}] 移除工具: {name}")
            return True
        logger.warning(f"[{self.name}] 尝试移除不存在的工具: {name}")
        return False
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        获取可用工具列表
        
        Returns:
            List[Dict]: 工具信息列表，每个工具包含:
                - name: 工具名称
                - description: 工具描述
                - parameters: 工具参数定义
        
        Example:
            >>> tools = agent.get_tools()
            >>> for tool in tools:
            ...     print(f"{tool['name']}: {tool['description']}")
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in self._tools.values()
        ]
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """
        获取指定工具
        
        Args:
            name: 工具名称
        
        Returns:
            Optional[Tool]: 工具对象，如果不存在则返回None
        """
        return self._tools.get(name)
    
    def execute_tool(self, name: str, *args, **kwargs) -> Any:
        """
        执行工具
        
        Args:
            name: 工具名称
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            Any: 工具执行结果
        
        Raises:
            ValueError: 当工具不存在时
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"工具 '{name}' 不存在")
        
        logger.info(f"[{self.name}] 执行工具: {name}")
        return tool.func(*args, **kwargs)
    
    def format_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        格式化系统提示词
        
        使用上下文信息格式化系统提示词模板。
        
        Args:
            context: 上下文信息字典，可能包含:
                - user_info: 用户信息
                - memories: 记忆内容
                - knowledge: 知识库内容
                - tools: 可用工具描述
                - custom_vars: 自定义变量
        
        Returns:
            str: 格式化后的系统提示词
        
        Example:
            >>> context = {
            ...     "user_info": "用户张三，35岁",
            ...     "memories": "用户有高血压病史",
            ...     "knowledge": "高血压的预防方法..."
            ... }
            >>> prompt = agent.format_system_prompt(context)
        """
        if not context:
            return self.system_prompt
        
        try:
            formatted_prompt = self.system_prompt
            
            # 替换上下文变量
            for key, value in context.items():
                placeholder = f"{{{key}}}"
                if placeholder in formatted_prompt:
                    formatted_prompt = formatted_prompt.replace(placeholder, str(value))
            
            # 如果没有匹配到模板变量，则在提示词后追加上下文
            if formatted_prompt == self.system_prompt and context:
                context_parts = []
                
                if "user_info" in context:
                    context_parts.append(f"用户信息: {context['user_info']}")
                
                if "memories" in context:
                    context_parts.append(f"\n{context['memories']}")
                
                if "knowledge" in context:
                    context_parts.append(f"\n{context['knowledge']}")
                
                if "tools" in context:
                    context_parts.append(f"\n可用工具:\n{context['tools']}")
                
                if context_parts:
                    formatted_prompt += "\n\n" + "\n".join(context_parts)
            
            logger.debug(f"[{self.name}] 系统提示词格式化完成")
            return formatted_prompt
            
        except Exception as e:
            logger.error(f"[{self.name}] 格式化系统提示词失败: {e}")
            return self.system_prompt
    
    async def retrieve_memories(
        self,
        user_id: int,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        召回用户记忆
        
        使用记忆检索器召回与用户查询相关的历史记忆。
        
        Args:
            user_id: 用户ID
            query: 查询文本
            top_k: 返回的记忆数量
        
        Returns:
            List[Dict]: 记忆列表
        
        Example:
            >>> memories = await agent.retrieve_memories(1, "我的血压怎么样", top_k=3)
            >>> print(len(memories))
        """
        if not self._memory_retriever:
            logger.warning(f"[{self.name}] 记忆检索器未启用")
            return []
        
        try:
            memories = await retrieve_memories_combined(user_id, query, top_k)
            logger.info(f"[{self.name}] 召回 {len(memories)} 条记忆")
            return memories
        except Exception as e:
            logger.error(f"[{self.name}] 记忆召回失败: {e}")
            return []
    
    def format_memories_for_context(self, memories: List[Dict[str, Any]]) -> str:
        """
        格式化记忆为上下文字符串
        
        Args:
            memories: 记忆列表
        
        Returns:
            str: 格式化后的记忆上下文
        """
        if not self._memory_retriever or not memories:
            return ""
        
        return self._memory_retriever.format_memories_for_context(memories)
    
    def retrieve_knowledge(
        self,
        query: str,
        top_k: int = 5,
        use_hybrid: bool = True
    ) -> List[RetrievalResult]:
        """
        检索知识库
        
        使用RAG检索器从知识库中检索相关信息。
        
        Args:
            query: 查询文本
            top_k: 返回的文档数量
            use_hybrid: 是否使用混合检索
        
        Returns:
            List[RetrievalResult]: 检索结果列表
        
        Example:
            >>> results = agent.retrieve_knowledge("如何预防高血压？", top_k=3)
            >>> for r in results:
            ...     print(f"{r.score:.3f}: {r.content[:100]}")
        """
        if not self._rag_retriever:
            logger.warning(f"[{self.name}] RAG检索器未启用")
            return []
        
        try:
            results = self._rag_retriever.retrieve(query, top_k, use_hybrid)
            logger.info(f"[{self.name}] 检索到 {len(results)} 条知识")
            return results
        except Exception as e:
            logger.error(f"[{self.name}] 知识检索失败: {e}")
            return []
    
    def format_knowledge_for_context(
        self,
        results: List[RetrievalResult],
        max_length: int = 3000
    ) -> str:
        """
        格式化知识检索结果为上下文字符串
        
        Args:
            results: 检索结果列表
            max_length: 最大长度
        
        Returns:
            str: 格式化后的知识上下文
        """
        if not self._rag_retriever or not results:
            return ""
        
        return self._rag_retriever.format_context(results, max_length)
    
    async def build_context(
        self,
        query: str,
        user_id: Optional[int] = None,
        use_memory: bool = True,
        use_rag: bool = True,
        memory_top_k: int = 5,
        rag_top_k: int = 5
    ) -> Dict[str, Any]:
        """
        构建完整上下文
        
        整合记忆召回和知识检索结果，构建完整的上下文信息。
        
        Args:
            query: 用户查询
            user_id: 用户ID（用于记忆召回）
            use_memory: 是否使用记忆
            use_rag: 是否使用知识检索
            memory_top_k: 记忆召回数量
            rag_top_k: 知识检索数量
        
        Returns:
            Dict: 上下文信息字典，包含:
                - memories: 格式化后的记忆上下文
                - knowledge: 格式化后的知识上下文
                - tools: 可用工具描述
        
        Example:
            >>> context = await agent.build_context("我的血压怎么样？", user_id=1)
            >>> prompt = agent.format_system_prompt(context)
        """
        context = {}
        
        # 召回记忆
        if use_memory and user_id is not None and self._memory_retriever:
            try:
                memories = await self.retrieve_memories(user_id, query, memory_top_k)
                if memories:
                    context["memories"] = self.format_memories_for_context(memories)
            except Exception as e:
                logger.error(f"[{self.name}] 构建上下文时记忆召回失败: {e}")
        
        # 检索知识
        if use_rag and self._rag_retriever:
            try:
                results = self.retrieve_knowledge(query, rag_top_k)
                if results:
                    context["knowledge"] = self.format_knowledge_for_context(results)
            except Exception as e:
                logger.error(f"[{self.name}] 构建上下文时知识检索失败: {e}")
        
        # 添加工具描述
        if self._tools:
            tools_desc = []
            for tool in self._tools.values():
                desc = f"- {tool.name}: {tool.description}"
                if tool.parameters:
                    params = ", ".join(
                        f"{k}: {v.get('type', 'any')}"
                        for k, v in tool.parameters.items()
                    )
                    desc += f" (参数: {params})"
                tools_desc.append(desc)
            context["tools"] = "\n".join(tools_desc)
        
        logger.info(f"[{self.name}] 上下文构建完成")
        return context
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取智能体信息
        
        Returns:
            Dict: 智能体信息字典
        """
        return {
            "name": self.name,
            "description": self.description,
            "tools_count": len(self._tools),
            "tools": [name for name in self._tools.keys()],
            "memory_enabled": self._memory_retriever is not None,
            "rag_enabled": self._rag_retriever is not None
        }


# 便捷函数

def create_agent_info(agent: BaseAgent) -> Dict[str, Any]:
    """
    获取智能体信息
    
    Args:
        agent: 智能体实例
    
    Returns:
        Dict: 智能体信息
    """
    return agent.get_info()
