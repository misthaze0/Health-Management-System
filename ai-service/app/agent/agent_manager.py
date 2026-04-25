"""
智能体管理器模块

提供智能体的统一管理功能，包括注册、获取、路由和协作。
使用单例模式确保全局唯一实例。
"""

import logging
import re
from typing import Dict, List, Optional, Any
from functools import wraps

from app.agent.base_agent import BaseAgent

# 配置日志记录器
logger = logging.getLogger(__name__)


def singleton(cls):
    """
    单例模式装饰器
    
    确保类只有一个实例，并提供全局访问点。
    
    Args:
        cls: 被装饰的类
    
    Returns:
        包装函数，返回唯一实例
    """
    instances = {}
    lock = __import__('threading').Lock()
    
    @wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in instances:
            with lock:
                # 双重检查锁定
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
                    logger.info(f"[{cls.__name__}] 单例实例创建成功")
        return instances[cls]
    
    return wrapper


@singleton
class AgentManager:
    """
    智能体管理器
    
    统一管理所有AI智能体的注册、获取、路由和协作。
    使用单例模式确保全局唯一实例。
    
    Attributes:
        _agents: 智能体字典，key为agent_type，value为BaseAgent实例
        _routing_rules: 路由规则列表
    
    Example:
        >>> # 获取管理器实例
        >>> manager = AgentManager()
        >>> 
        >>> # 注册智能体
        >>> manager.register_agent("health", health_agent)
        >>> 
        >>> # 获取智能体
        >>> agent = manager.get_agent("health")
        >>> 
        >>> # 路由查询
        >>> agent_type = manager.route_query("我的血压正常吗？")
    """
    
    # 预定义的智能体类型常量
    AGENT_TYPE_HEALTH = "health"
    AGENT_TYPE_NUTRITION = "nutrition"
    AGENT_TYPE_EXERCISE = "exercise"
    AGENT_TYPE_MEDICAL = "medical"
    
    # 默认智能体类型（兜底）
    DEFAULT_AGENT_TYPE = "health"
    
    def __init__(self):
        """
        初始化智能体管理器
        
        初始化智能体字典和路由规则，并注册默认智能体。
        注意：由于使用单例模式，此方法只会在第一次创建实例时执行。
        """
        # 智能体存储字典: {agent_type: BaseAgent}
        self._agents: Dict[str, BaseAgent] = {}
        
        # 路由规则列表，按优先级排序
        self._routing_rules: List[Dict[str, Any]] = []
        
        # 初始化路由规则
        self._init_routing_rules()
        
        # 注册默认智能体
        self._register_default_agents()
        
        logger.info("智能体管理器初始化完成")
    
    def _init_routing_rules(self) -> None:
        """
        初始化路由规则
        
        定义查询关键词与智能体类型的映射规则。
        规则按优先级排序，先匹配的规则优先。
        """
        self._routing_rules = [
            {
                "agent_type": self.AGENT_TYPE_MEDICAL,
                "keywords": [
                    "疾病", "症状", "诊断", "治疗", "药物", "药品", "处方", "医生",
                    "医院", "科室", "检查", "化验", "手术", "住院", "病历",
                    "发烧", "咳嗽", "疼痛", "炎症", "感染", "慢性病", "急性病",
                    "高血压", "糖尿病", "心脏病", "感冒", "流感", "过敏",
                    "disease", "symptom", "diagnosis", "treatment", "medicine",
                    "drug", "prescription", "doctor", "hospital", "surgery"
                ],
                "patterns": [
                    r"(什么|啥).*(病|症|问题)",
                    r"(怎么|如何).*(治|医|处理)",
                    r"(吃|服用|用).*(药|药物)",
                    r".*(不舒服|难受|痛|疼).*",
                ],
                "priority": 1
            },
            {
                "agent_type": self.AGENT_TYPE_NUTRITION,
                "keywords": [
                    "营养", "饮食", "食物", "食谱", "膳食", "热量", "卡路里",
                    "蛋白质", "脂肪", "碳水化合物", "维生素", "矿物质",
                    "减肥", "增重", "体重管理", "饮食计划", "营养搭配",
                    "吃什么", "怎么吃", "健康饮食", "均衡饮食", "忌口",
                    "nutrition", "diet", "food", "recipe", "calorie",
                    "protein", "fat", "carbohydrate", "vitamin", "weight loss"
                ],
                "patterns": [
                    r"(怎么|如何).*(吃|饮食)",
                    r".*(减肥|瘦身|减重).*(吃|饮食|食谱)",
                    r".*(营养|膳食).*(搭配|建议|计划)",
                    r"(吃|喝).*(什么|啥).*(好|合适)",
                ],
                "priority": 2
            },
            {
                "agent_type": self.AGENT_TYPE_EXERCISE,
                "keywords": [
                    "运动", "锻炼", "健身", "训练", "跑步", "游泳", "瑜伽",
                    "力量训练", "有氧运动", "无氧运动", "体能", "耐力",
                    "运动计划", "健身计划", "减脂", "增肌", "塑形",
                    "步数", "步频", "配速", "心率", "运动强度",
                    "exercise", "workout", "fitness", "training", "running",
                    "swimming", "yoga", "gym", "cardio", "strength"
                ],
                "patterns": [
                    r"(怎么|如何).*(运动|锻炼|健身)",
                    r".*(运动|锻炼).*(计划|方案|建议)",
                    r"(跑|游|练).*(多少|多久|怎么)",
                    r".*(减脂|增肌|塑形).*(运动|训练)",
                ],
                "priority": 3
            },
            {
                "agent_type": self.AGENT_TYPE_HEALTH,
                "keywords": [
                    "健康", "身体状况", "体检", "指标", "血压", "血糖", "血脂",
                    "心率", "脉搏", "体温", "睡眠", "作息", "生活习惯",
                    "养生", "保健", "预防", "健康管理", "健康建议",
                    "bmi", "身体质量指数", "体脂率", "肌肉量",
                    "health", "wellness", "physical", "checkup", "lifestyle"
                ],
                "patterns": [
                    r"(我的|身体).*(健康|状况|指标)",
                    r".*(体检|检查).*(结果|报告|指标)",
                    r"(怎么|如何).*(保持健康|养生|保健)",
                    r".*(血压|血糖|心率).*(多少|正常|高|低)",
                ],
                "priority": 4
            }
        ]
        
        # 按优先级排序
        self._routing_rules.sort(key=lambda x: x["priority"])
        
        logger.info(f"路由规则初始化完成，共 {len(self._routing_rules)} 条规则")
    
    def _register_default_agents(self) -> None:
        """
        注册默认智能体
        
        在管理器初始化时自动注册系统预定义的默认智能体。
        """
        try:
            # 延迟导入以避免循环依赖
            from app.agent.expert_agents import (
                NutritionistAgent,
                FitnessCoachAgent,
                PsychologyAgent,
                MedicalAnalystAgent
            )
            
            # 注册营养师智能体
            nutrition_agent = NutritionistAgent()
            self.register_agent(self.AGENT_TYPE_NUTRITION, nutrition_agent)
            logger.info(f"注册默认智能体: {self.AGENT_TYPE_NUTRITION}")
            
            # 注册运动教练智能体
            fitness_agent = FitnessCoachAgent()
            self.register_agent(self.AGENT_TYPE_EXERCISE, fitness_agent)
            logger.info(f"注册默认智能体: {self.AGENT_TYPE_EXERCISE}")
            
            # 注册心理咨询师智能体
            psychology_agent = PsychologyAgent()
            self.register_agent("psychology", psychology_agent)
            logger.info(f"注册默认智能体: psychology")
            
            # 注册体检分析师智能体
            medical_agent = MedicalAnalystAgent()
            self.register_agent(self.AGENT_TYPE_MEDICAL, medical_agent)
            logger.info(f"注册默认智能体: {self.AGENT_TYPE_MEDICAL}")
            
            # 注册通用健康顾问智能体（使用体检分析师作为默认）
            health_agent = MedicalAnalystAgent()
            health_agent.name = "健康顾问"
            health_agent.description = "提供综合健康咨询服务"
            self.register_agent(self.AGENT_TYPE_HEALTH, health_agent)
            logger.info(f"注册默认智能体: {self.AGENT_TYPE_HEALTH}")
            
            logger.info(f"默认智能体注册完成，共 {len(self._agents)} 个")
            
        except Exception as e:
            logger.error(f"注册默认智能体失败: {e}")
            # 不抛出异常，允许管理器继续工作
    
    def register_agent(self, agent_type: str, agent: BaseAgent) -> bool:
        """
        注册智能体
        
        将智能体实例注册到管理器中，使其可以通过类型标识被获取。
        
        Args:
            agent_type: 智能体类型标识符，如 "health", "medical" 等
            agent: BaseAgent 智能体实例
        
        Returns:
            bool: 注册是否成功
        
        Raises:
            ValueError: 当 agent_type 为空或 agent 不是 BaseAgent 实例时
        
        Example:
            >>> health_agent = HealthAgent()
            >>> manager.register_agent("health", health_agent)
            True
        """
        # 参数验证
        if not agent_type or not isinstance(agent_type, str):
            logger.error("注册智能体失败: agent_type 必须是非空字符串")
            raise ValueError("agent_type 必须是非空字符串")
        
        if not isinstance(agent, BaseAgent):
            logger.error("注册智能体失败: agent 必须是 BaseAgent 实例")
            raise ValueError("agent 必须是 BaseAgent 实例")
        
        # 检查是否已存在
        if agent_type in self._agents:
            logger.warning(f"智能体类型 '{agent_type}' 已存在，将被覆盖")
        
        # 注册智能体
        self._agents[agent_type] = agent
        logger.info(f"智能体注册成功: {agent_type} -> {agent.name}")
        
        return True
    
    def unregister_agent(self, agent_type: str) -> bool:
        """
        注销智能体
        
        从管理器中移除指定类型的智能体。
        
        Args:
            agent_type: 智能体类型标识符
        
        Returns:
            bool: 注销是否成功
        
        Example:
            >>> manager.unregister_agent("health")
            True
        """
        if agent_type not in self._agents:
            logger.warning(f"注销智能体失败: 类型 '{agent_type}' 不存在")
            return False
        
        agent_name = self._agents[agent_type].name
        del self._agents[agent_type]
        logger.info(f"智能体注销成功: {agent_type} ({agent_name})")
        
        return True
    
    def get_agent(self, agent_type: str) -> Optional[BaseAgent]:
        """
        获取智能体
        
        根据类型标识符获取对应的智能体实例。
        
        Args:
            agent_type: 智能体类型标识符
        
        Returns:
            Optional[BaseAgent]: 智能体实例，如果不存在则返回 None
        
        Example:
            >>> agent = manager.get_agent("health")
            >>> if agent:
            ...     print(agent.name)
        """
        agent = self._agents.get(agent_type)
        
        if agent:
            logger.debug(f"获取智能体成功: {agent_type}")
        else:
            logger.warning(f"获取智能体失败: 类型 '{agent_type}' 不存在")
        
        return agent
    
    def route_query(self, query: str) -> str:
        """
        根据查询路由到合适的智能体类型
        
        分析查询内容，根据关键词和正则模式匹配最合适的智能体类型。
        
        Args:
            query: 用户查询文本
        
        Returns:
            str: 匹配的智能体类型标识符，如果没有匹配则返回默认类型
        
        Example:
            >>> agent_type = manager.route_query("我的血压正常吗？")
            >>> print(agent_type)  # 输出: "health"
        """
        if not query or not isinstance(query, str):
            logger.warning("查询路由: 查询为空，返回默认智能体")
            return self.DEFAULT_AGENT_TYPE
        
        query_lower = query.lower()
        
        # 遍历路由规则进行匹配
        for rule in self._routing_rules:
            agent_type = rule["agent_type"]
            
            # 检查关键词匹配
            for keyword in rule.get("keywords", []):
                if keyword.lower() in query_lower:
                    logger.info(f"查询路由: 关键词 '{keyword}' 匹配到 '{agent_type}'")
                    return agent_type
            
            # 检查正则模式匹配
            for pattern in rule.get("patterns", []):
                try:
                    if re.search(pattern, query, re.IGNORECASE):
                        logger.info(f"查询路由: 模式 '{pattern}' 匹配到 '{agent_type}'")
                        return agent_type
                except re.error as e:
                    logger.error(f"正则表达式错误: {pattern}, {e}")
        
        # 没有匹配到任何规则，返回默认类型
        logger.info(f"查询路由: 未匹配到特定规则，返回默认类型 '{self.DEFAULT_AGENT_TYPE}'")
        return self.DEFAULT_AGENT_TYPE
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        返回所有可用智能体列表
        
        获取当前已注册的所有智能体的信息列表。
        
        Returns:
            List[Dict]: 智能体信息列表，每个字典包含:
                - type: 智能体类型标识符
                - name: 智能体名称
                - description: 智能体描述
                - info: 完整的智能体信息
        
        Example:
            >>> agents = manager.list_agents()
            >>> for agent in agents:
            ...     print(f"{agent['type']}: {agent['name']}")
        """
        agents_list = []
        
        for agent_type, agent in self._agents.items():
            agent_info = {
                "type": agent_type,
                "name": agent.name,
                "description": agent.description,
                "info": agent.get_info()
            }
            agents_list.append(agent_info)
        
        logger.debug(f"列出智能体: 共 {len(agents_list)} 个")
        return agents_list
    
    def get_agent_types(self) -> List[str]:
        """
        获取所有已注册的智能体类型
        
        Returns:
            List[str]: 智能体类型标识符列表
        """
        return list(self._agents.keys())
    
    def has_agent(self, agent_type: str) -> bool:
        """
        检查是否存在指定类型的智能体
        
        Args:
            agent_type: 智能体类型标识符
        
        Returns:
            bool: 是否存在
        """
        return agent_type in self._agents
    
    async def collaborate(
        self,
        agent_types: List[str],
        query: str,
        user_id: Optional[int] = None,
        collaboration_mode: str = "sequential"
    ) -> Dict[str, Any]:
        """
        多智能体协作
        
        协调多个智能体共同处理一个查询，支持顺序和并行两种协作模式。
        
        Args:
            agent_types: 参与协作的智能体类型列表
            query: 用户查询文本
            user_id: 用户ID（可选，用于记忆召回）
            collaboration_mode: 协作模式，可选:
                - "sequential": 顺序执行，每个智能体的输出作为下一个的输入
                - "parallel": 并行执行，汇总所有智能体的结果
        
        Returns:
            Dict: 协作结果，包含:
                - success: 是否成功
                - results: 各智能体的处理结果
                - final_response: 最终综合回复
                - errors: 错误信息列表（如果有）
        
        Raises:
            ValueError: 当 agent_types 为空或包含无效类型时
        
        Example:
            >>> result = await manager.collaborate(
            ...     ["nutrition", "exercise"],
            ...     "如何健康减重？",
            ...     user_id=1,
            ...     collaboration_mode="parallel"
            ... )
        """
        # 参数验证
        if not agent_types or not isinstance(agent_types, list):
            raise ValueError("agent_types 必须是非空列表")
        
        if not query or not isinstance(query, str):
            raise ValueError("query 必须是非空字符串")
        
        # 过滤有效的智能体类型
        valid_agents = []
        invalid_types = []
        
        for agent_type in agent_types:
            agent = self.get_agent(agent_type)
            if agent:
                valid_agents.append((agent_type, agent))
            else:
                invalid_types.append(agent_type)
        
        if not valid_agents:
            logger.error(f"协作失败: 没有有效的智能体类型")
            raise ValueError(f"没有有效的智能体类型: {agent_types}")
        
        if invalid_types:
            logger.warning(f"协作: 忽略无效的智能体类型: {invalid_types}")
        
        logger.info(f"开始多智能体协作: {len(valid_agents)} 个智能体，模式: {collaboration_mode}")
        
        # 初始化结果
        results = {}
        errors = []
        final_response = ""
        
        try:
            if collaboration_mode == "sequential":
                # 顺序执行模式
                current_query = query
                
                for agent_type, agent in valid_agents:
                    try:
                        # 构建消息
                        messages = [
                            {"role": "system", "content": agent.system_prompt},
                            {"role": "user", "content": current_query}
                        ]
                        
                        # 执行对话
                        response = await agent.chat(messages, user_id=user_id)
                        
                        results[agent_type] = {
                            "input": current_query,
                            "output": response,
                            "agent_name": agent.name
                        }
                        
                        # 更新查询为当前输出，作为下一个智能体的输入
                        current_query = response
                        
                        logger.info(f"协作顺序执行: {agent_type} 完成")
                        
                    except Exception as e:
                        error_msg = f"智能体 '{agent_type}' 执行失败: {str(e)}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                        results[agent_type] = {"error": error_msg}
                
                # 最终回复为最后一个智能体的输出
                if valid_agents:
                    last_type = valid_agents[-1][0]
                    if last_type in results and "output" in results[last_type]:
                        final_response = results[last_type]["output"]
            
            elif collaboration_mode == "parallel":
                # 并行执行模式
                import asyncio
                
                async def execute_agent(agent_type: str, agent: BaseAgent, query: str):
                    try:
                        messages = [
                            {"role": "system", "content": agent.system_prompt},
                            {"role": "user", "content": query}
                        ]
                        
                        response = await agent.chat(messages, user_id=user_id)
                        
                        return agent_type, {
                            "output": response,
                            "agent_name": agent.name
                        }
                    except Exception as e:
                        error_msg = f"智能体 '{agent_type}' 执行失败: {str(e)}"
                        logger.error(error_msg)
                        return agent_type, {"error": error_msg}
                
                # 并发执行所有智能体
                tasks = [
                    execute_agent(agent_type, agent, query)
                    for agent_type, agent in valid_agents
                ]
                
                # 等待所有任务完成
                completed_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 处理结果
                for result in completed_results:
                    if isinstance(result, Exception):
                        error_msg = f"并行执行异常: {str(result)}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                    else:
                        agent_type, agent_result = result
                        results[agent_type] = agent_result
                        
                        if "error" in agent_result:
                            errors.append(agent_result["error"])
                
                # 汇总所有成功结果
                successful_outputs = [
                    f"【{r['agent_name']}】\n{r['output']}"
                    for r in results.values()
                    if "output" in r
                ]
                
                if successful_outputs:
                    final_response = "\n\n".join(successful_outputs)
                else:
                    final_response = "所有智能体执行失败"
            
            else:
                raise ValueError(f"不支持的协作模式: {collaboration_mode}")
            
            logger.info(f"多智能体协作完成: {len(results)} 个结果, {len(errors)} 个错误")
            
            return {
                "success": len(errors) == 0,
                "results": results,
                "final_response": final_response,
                "errors": errors,
                "collaboration_mode": collaboration_mode,
                "agent_count": len(valid_agents)
            }
            
        except Exception as e:
            error_msg = f"多智能体协作异常: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "results": results,
                "final_response": "",
                "errors": errors + [error_msg],
                "collaboration_mode": collaboration_mode,
                "agent_count": len(valid_agents)
            }
    
    def get_manager_info(self) -> Dict[str, Any]:
        """
        获取管理器信息
        
        Returns:
            Dict: 管理器状态信息
        """
        return {
            "registered_agents_count": len(self._agents),
            "registered_types": self.get_agent_types(),
            "routing_rules_count": len(self._routing_rules),
            "default_agent_type": self.DEFAULT_AGENT_TYPE,
            "agents": self.list_agents()
        }


# 预注册的4类专家智能体占位类
# 这些类在实际实现时需要继承 BaseAgent 并实现 chat 方法

class HealthAgent(BaseAgent):
    """
    健康管理智能体
    
    负责处理一般健康咨询、健康指标分析、体检报告解读等。
    """
    
    def __init__(self):
        super().__init__(
            name="健康管理专家",
            description="提供全面的健康管理服务，包括健康指标分析、体检报告解读、健康建议等",
            system_prompt="""你是健康管理专家，专注于提供全面的健康管理服务。

你的职责包括：
1. 分析用户的健康指标（血压、血糖、心率等）
2. 解读体检报告，解释各项指标的含义
3. 提供个性化的健康建议和生活方式指导
4. 回答关于健康养生、疾病预防的问题
5. 帮助用户建立健康的作息习惯

在回答时，请注意：
- 使用通俗易懂的语言解释专业医学术语
- 提供具体、可操作的建议
- 提醒用户在必要时咨询专业医生
- 保持友善、鼓励的语气"""
        )
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """实现健康咨询对话逻辑"""
        # 这里需要接入实际的AI模型
        # 暂时返回模拟回复
        return f"【健康管理专家】我已收到您的问题，正在为您分析健康状况..."


class NutritionAgent(BaseAgent):
    """
    营养饮食智能体
    
    负责处理营养咨询、饮食建议、食谱推荐等。
    """
    
    def __init__(self):
        super().__init__(
            name="营养饮食专家",
            description="提供专业的营养咨询服务，包括饮食建议、食谱推荐、营养搭配指导等",
            system_prompt="""你是营养饮食专家，专注于提供科学的营养和饮食建议。

你的职责包括：
1. 根据用户的健康状况推荐合适的饮食方案
2. 提供营养均衡的食谱建议
3. 解答关于食物营养成分的问题
4. 帮助用户制定减肥或增重的饮食计划
5. 提供特殊人群（如糖尿病患者）的饮食指导

在回答时，请注意：
- 提供具体的食物建议和搭配方案
- 考虑用户的口味偏好和饮食习惯
- 解释营养搭配的科学原理
- 提醒用户注意饮食安全和食物过敏"""
        )
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """实现营养咨询对话逻辑"""
        return f"【营养饮食专家】我已收到您的饮食咨询，正在为您制定营养方案..."


class ExerciseAgent(BaseAgent):
    """
    运动健身智能体
    
    负责处理运动建议、健身计划、运动数据分析等。
    """
    
    def __init__(self):
        super().__init__(
            name="运动健身专家",
            description="提供专业的运动健身指导，包括运动计划制定、健身建议、运动数据分析等",
            system_prompt="""你是运动健身专家，专注于提供科学的运动指导。

你的职责包括：
1. 根据用户的身体状况制定个性化的运动计划
2. 提供各种运动形式的指导和建议
3. 分析用户的运动数据（步数、心率、配速等）
4. 帮助用户安全有效地减脂、增肌或塑形
5. 提供运动损伤预防和康复建议

在回答时，请注意：
- 根据用户的体能水平推荐合适的运动强度
- 提供循序渐进的运动方案
- 强调运动安全，避免过度训练
- 鼓励用户坚持运动，保持积极心态"""
        )
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """实现运动咨询对话逻辑"""
        return f"【运动健身专家】我已收到您的运动咨询，正在为您设计训练方案..."


class MedicalAgent(BaseAgent):
    """
    医疗咨询智能体
    
    负责处理疾病症状咨询、就医指导、药物知识等。
    注意：此智能体仅提供一般性医疗信息，不能替代专业医生诊断。
    """
    
    def __init__(self):
        super().__init__(
            name="医疗咨询专家",
            description="提供一般性医疗咨询服务，包括疾病症状解答、就医指导、药物知识等",
            system_prompt="""你是医疗咨询专家，提供一般性的医疗健康信息。

【重要免责声明】
你提供的信息仅供参考，不能替代专业医生的诊断和治疗建议。
对于任何具体的健康问题，用户应该咨询专业医生或前往医院就诊。

你的职责包括：
1. 解答常见疾病的基本知识和症状
2. 提供就医科室选择和就诊建议
3. 解释常见药物的基本信息（非处方建议）
4. 普及健康知识和疾病预防信息
5. 指导用户如何描述症状以便就医

在回答时，请注意：
- 始终强调你的建议不能替代专业医生
- 对于严重症状，强烈建议用户立即就医
- 不提供具体的处方或用药剂量建议
- 使用准确但通俗的医学语言
- 保持谨慎、专业的态度"""
        )
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """实现医疗咨询对话逻辑"""
        return f"【医疗咨询专家】我已收到您的医疗咨询，需要说明的是我提供的信息仅供参考，不能替代专业医生诊断..."


def initialize_default_agents() -> AgentManager:
    """
    初始化默认智能体
    
    创建并注册4类预定义的专家智能体。
    
    Returns:
        AgentManager: 已注册默认智能体的管理器实例
    
    Example:
        >>> manager = initialize_default_agents()
        >>> print(manager.list_agents())
    """
    manager = AgentManager()
    
    # 注册4类专家智能体
    agents_to_register = [
        (AgentManager.AGENT_TYPE_HEALTH, HealthAgent()),
        (AgentManager.AGENT_TYPE_NUTRITION, NutritionAgent()),
        (AgentManager.AGENT_TYPE_EXERCISE, ExerciseAgent()),
        (AgentManager.AGENT_TYPE_MEDICAL, MedicalAgent()),
    ]
    
    for agent_type, agent in agents_to_register:
        try:
            manager.register_agent(agent_type, agent)
        except Exception as e:
            logger.error(f"注册默认智能体 '{agent_type}' 失败: {e}")
    
    logger.info(f"默认智能体初始化完成，共注册 {len(agents_to_register)} 个智能体")
    
    return manager


# 便捷函数

def get_agent_manager() -> AgentManager:
    """
    获取智能体管理器实例
    
    获取 AgentManager 的单例实例。
    
    Returns:
        AgentManager: 智能体管理器实例
    
    Example:
        >>> manager = get_agent_manager()
        >>> agent = manager.get_agent("health")
    """
    return AgentManager()


def get_agent(agent_type: str) -> Optional[BaseAgent]:
    """
    便捷函数：获取指定类型的智能体
    
    Args:
        agent_type: 智能体类型标识符
    
    Returns:
        Optional[BaseAgent]: 智能体实例
    
    Example:
        >>> agent = get_agent("health")
    """
    return get_agent_manager().get_agent(agent_type)


def route_query(query: str) -> str:
    """
    便捷函数：路由查询到合适的智能体类型
    
    Args:
        query: 用户查询文本
    
    Returns:
        str: 智能体类型标识符
    
    Example:
        >>> agent_type = route_query("我的血压正常吗？")
    """
    return get_agent_manager().route_query(query)
