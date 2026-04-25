"""
领域专家智能体模块

提供四个专业领域的AI智能体实现：
- NutritionistAgent: 营养师，专注饮食营养分析
- FitnessCoachAgent: 运动教练，专注运动健身指导
- PsychologyAgent: 心理咨询师，专注心理健康支持
- MedicalAnalystAgent: 体检分析师，专注体检报告解读

所有智能体继承自BaseAgent，集成Kimi服务进行对话，并支持记忆召回和知识检索。
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.agent.base_agent import BaseAgent
from app.services.kimi_service import kimi_service

# 配置日志记录器
logger = logging.getLogger(__name__)


# =============================================================================
# 营养师智能体
# =============================================================================

class NutritionistAgent(BaseAgent):
    """
    营养师智能体
    
    专注于营养分析、饮食建议和营养咨询的专业智能体。
    能够分析用户的饮食记录，提供个性化的营养建议。
    
    Attributes:
        name: 智能体名称
        description: 智能体描述
        system_prompt: 系统提示词
    
    Example:
        >>> agent = NutritionistAgent()
        >>> result = await agent.analyze_diet("早餐: 牛奶一杯, 鸡蛋一个...")
        >>> print(result)
    """
    
    # 营养师专业系统提示词
    NUTRITIONIST_PROMPT = """你是一位专业的营养师，拥有丰富的营养学知识和临床经验。

【角色定位】
- 专业营养师，专注于饮食营养分析和健康膳食指导
- 熟悉中国居民膳食指南和营养学原理
- 能够根据用户的身体状况、生活习惯提供个性化建议

【核心能力】
1. 饮食记录分析：分析用户的日常饮食，评估营养摄入是否均衡
2. 营养建议：根据用户的健康目标（减重、增肌、控糖等）提供饮食建议
3. 膳食规划：帮助用户制定合理的膳食计划
4. 营养知识普及：解答营养相关问题，普及健康饮食知识

【分析原则】
- 科学性：基于营养学原理和中国居民膳食指南
- 个性化：考虑用户的年龄、性别、身体状况、活动量等因素
- 实用性：提供可操作、易执行的建议
- 安全性：避免极端饮食建议，强调均衡营养

【输出格式】
分析结果应包含：
1. 营养摄入评估（热量、蛋白质、碳水化合物、脂肪、维生素、矿物质等）
2. 饮食优点和不足之处
3. 具体的改进建议
4. 推荐的食物搭配和食谱

请用专业但易懂的语言回答用户问题。"""
    
    def __init__(
        self,
        enable_memory: bool = True,
        enable_rag: bool = True
    ):
        """
        初始化营养师智能体
        
        Args:
            enable_memory: 是否启用记忆召回，默认True
            enable_rag: 是否启用知识检索，默认True
        """
        super().__init__(
            name="营养师",
            description="专业营养师，提供饮食营养分析和膳食建议",
            system_prompt=self.NUTRITIONIST_PROMPT,
            enable_memory=enable_memory,
            enable_rag=enable_rag
        )
        logger.info(f"[{self.name}] 营养师智能体初始化完成")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        执行对话
        
        与营养师进行对话，获取营养相关的专业建议。
        
        Args:
            messages: 消息列表
            **kwargs: 额外参数
                - user_id: 用户ID
                - use_memory: 是否使用记忆
                - use_rag: 是否使用知识检索
                - temperature: 温度参数
                - max_tokens: 最大token数
        
        Returns:
            str: 营养师的回复内容
        """
        try:
            user_id = kwargs.get("user_id")
            use_memory = kwargs.get("use_memory", True)
            use_rag = kwargs.get("use_rag", True)
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 2000)
            
            # 获取最后一条用户消息作为查询
            user_message = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    user_message = msg.get("content", "")
                    break
            
            # 构建上下文
            context = await self.build_context(
                query=user_message,
                user_id=user_id,
                use_memory=use_memory,
                use_rag=use_rag
            )
            
            # 格式化系统提示词
            formatted_system_prompt = self.format_system_prompt(context)
            
            # 构建完整消息列表
            full_messages = [
                {"role": "system", "content": formatted_system_prompt}
            ] + messages
            
            logger.info(f"[{self.name}] 开始对话请求")
            
            # 调用Kimi服务
            response = await kimi_service.chat_completion(
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            logger.info(f"[{self.name}] 对话完成，回复长度: {len(content)} 字符")
            
            return content
            
        except Exception as e:
            logger.error(f"[{self.name}] 对话失败: {str(e)}")
            raise
    
    async def analyze_diet(self, diet_log: str) -> Dict[str, Any]:
        """
        分析饮食记录
        
        分析用户的饮食记录，评估营养摄入情况，并提供改进建议。
        
        Args:
            diet_log: 饮食记录文本，包含一日三餐及加餐内容
        
        Returns:
            Dict: 分析结果，包含：
                - assessment: 整体评估
                - nutrition_analysis: 营养分析
                - strengths: 饮食优点
                - weaknesses: 不足之处
                - suggestions: 改进建议
                - recommendations: 推荐食谱
        
        Example:
            >>> diet = "早餐: 牛奶一杯, 鸡蛋一个, 面包两片\\n午餐: ..."
            >>> result = await agent.analyze_diet(diet)
            >>> print(result["assessment"])
        """
        try:
            logger.info(f"[{self.name}] 开始分析饮食记录")
            
            # 构建分析提示
            analysis_prompt = f"""请对以下饮食记录进行专业营养分析：

【饮食记录】
{diet_log}

请按照以下JSON格式返回分析结果（只返回JSON，不要其他内容）：
{{
    "assessment": "整体营养评估总结",
    "nutrition_analysis": {{
        "calories": "热量摄入评估",
        "protein": "蛋白质摄入评估",
        "carbs": "碳水化合物摄入评估",
        "fat": "脂肪摄入评估",
        "vitamins_minerals": "维生素和矿物质摄入评估"
    }},
    "strengths": ["饮食优点1", "饮食优点2"],
    "weaknesses": ["不足之处1", "不足之处2"],
    "suggestions": ["改进建议1", "改进建议2"],
    "recommendations": ["推荐食谱1", "推荐食谱2"]
}}"""
            
            messages = [
                {"role": "user", "content": analysis_prompt}
            ]
            
            # 调用对话功能
            response = await self.chat(
                messages=messages,
                temperature=0.5,
                max_tokens=2500
            )
            
            # 尝试解析JSON响应
            import json
            try:
                result = json.loads(response)
                logger.info(f"[{self.name}] 饮食分析完成")
                return result
            except json.JSONDecodeError:
                # 如果解析失败，返回原始文本
                logger.warning(f"[{self.name}] JSON解析失败，返回原始文本")
                return {
                    "assessment": response,
                    "nutrition_analysis": {},
                    "strengths": [],
                    "weaknesses": [],
                    "suggestions": [],
                    "recommendations": []
                }
                
        except Exception as e:
            logger.error(f"[{self.name}] 饮食分析失败: {str(e)}")
            raise


# =============================================================================
# 运动教练智能体
# =============================================================================

class FitnessCoachAgent(BaseAgent):
    """
    运动教练智能体
    
    专注于运动健身指导、训练计划制定的专业智能体。
    能够根据用户的目标和水平制定个性化的运动计划。
    
    Attributes:
        name: 智能体名称
        description: 智能体描述
        system_prompt: 系统提示词
    
    Example:
        >>> agent = FitnessCoachAgent()
        >>> plan = await agent.create_exercise_plan("减脂", "初级")
        >>> print(plan)
    """
    
    # 运动教练专业系统提示词
    FITNESS_COACH_PROMPT = """你是一位专业的运动教练和体能训练专家，拥有丰富的运动科学知识和训练经验。

【角色定位】
- 专业运动教练，专注于运动健身指导和训练计划制定
- 熟悉运动生理学、运动解剖学和运动营养学
- 能够根据用户的身体状况、运动目标制定科学的训练方案

【核心能力】
1. 运动计划制定：根据用户目标（减脂、增肌、塑形、提升体能等）制定训练计划
2. 动作指导：提供正确的运动动作指导和注意事项
3. 强度评估：评估运动强度是否适合用户当前水平
4. 运动安全：提供运动安全建议，预防运动损伤
5. 进度跟踪：指导用户如何跟踪训练进度和调整计划

【训练原则】
- 渐进性：遵循循序渐进原则，逐步增加训练强度
- 个性化：根据用户的年龄、体能水平、运动经验定制方案
- 全面性：包含有氧运动、力量训练、柔韧性训练等
- 安全性：强调热身、拉伸和正确的动作姿势
- 可持续性：制定用户能够长期坚持的训练计划

【运动水平定义】
- 初级：刚开始运动，体能基础较弱
- 中级：有一定运动经验，能够完成中等强度训练
- 高级：长期规律运动，能够完成高强度训练

【输出格式】
训练计划应包含：
1. 训练目标和时间周期
2. 每周训练安排（具体天数和内容）
3. 每次训练的详细内容（动作、组数、次数、休息时间）
4. 注意事项和安全提示
5. 进阶建议

请用专业但易懂的语言回答用户问题。"""
    
    def __init__(
        self,
        enable_memory: bool = True,
        enable_rag: bool = True
    ):
        """
        初始化运动教练智能体
        
        Args:
            enable_memory: 是否启用记忆召回，默认True
            enable_rag: 是否启用知识检索，默认True
        """
        super().__init__(
            name="运动教练",
            description="专业运动教练，提供运动健身指导和训练计划",
            system_prompt=self.FITNESS_COACH_PROMPT,
            enable_memory=enable_memory,
            enable_rag=enable_rag
        )
        logger.info(f"[{self.name}] 运动教练智能体初始化完成")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        执行对话
        
        与运动教练进行对话，获取运动健身相关的专业建议。
        
        Args:
            messages: 消息列表
            **kwargs: 额外参数
        
        Returns:
            str: 运动教练的回复内容
        """
        try:
            user_id = kwargs.get("user_id")
            use_memory = kwargs.get("use_memory", True)
            use_rag = kwargs.get("use_rag", True)
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 2000)
            
            # 获取最后一条用户消息作为查询
            user_message = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    user_message = msg.get("content", "")
                    break
            
            # 构建上下文
            context = await self.build_context(
                query=user_message,
                user_id=user_id,
                use_memory=use_memory,
                use_rag=use_rag
            )
            
            # 格式化系统提示词
            formatted_system_prompt = self.format_system_prompt(context)
            
            # 构建完整消息列表
            full_messages = [
                {"role": "system", "content": formatted_system_prompt}
            ] + messages
            
            logger.info(f"[{self.name}] 开始对话请求")
            
            # 调用Kimi服务
            response = await kimi_service.chat_completion(
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            logger.info(f"[{self.name}] 对话完成，回复长度: {len(content)} 字符")
            
            return content
            
        except Exception as e:
            logger.error(f"[{self.name}] 对话失败: {str(e)}")
            raise
    
    async def create_exercise_plan(
        self,
        goal: str,
        level: str,
        duration_weeks: int = 4
    ) -> Dict[str, Any]:
        """
        制定运动计划
        
        根据用户的运动目标和当前水平，制定个性化的训练计划。
        
        Args:
            goal: 运动目标，如"减脂"、"增肌"、"塑形"、"提升体能"等
            level: 运动水平，可选"初级"、"中级"、"高级"
            duration_weeks: 计划周期（周数），默认4周
        
        Returns:
            Dict: 运动计划，包含：
                - goal: 训练目标
                - level: 适用水平
                - duration: 计划周期
                - weekly_schedule: 每周训练安排
                - exercises: 具体训练动作说明
                - safety_tips: 安全提示
                - progression: 进阶建议
        
        Example:
            >>> plan = await agent.create_exercise_plan("减脂", "初级", 8)
            >>> print(plan["weekly_schedule"])
        """
        try:
            logger.info(f"[{self.name}] 开始制定运动计划: 目标={goal}, 水平={level}")
            
            # 验证运动水平
            valid_levels = ["初级", "中级", "高级"]
            if level not in valid_levels:
                level = "初级"
                logger.warning(f"[{self.name}] 无效的运动水平，使用默认值: 初级")
            
            # 构建计划制定提示
            plan_prompt = f"""请为以下需求制定专业的运动训练计划：

【训练目标】{goal}
【当前水平】{level}
【计划周期】{duration_weeks}周

请按照以下JSON格式返回训练计划（只返回JSON，不要其他内容）：
{{
    "goal": "{goal}",
    "level": "{level}",
    "duration": "{duration_weeks}周",
    "weekly_schedule": [
        {{
            "day": "周一",
            "focus": "训练重点",
            "duration": "训练时长",
            "activities": ["活动1", "活动2"]
        }},
        {{
            "day": "周二",
            "focus": "休息/恢复",
            "duration": "",
            "activities": ["轻度拉伸", "放松"]
        }}
    ],
    "exercises": [
        {{
            "name": "动作名称",
            "sets": "组数",
            "reps": "次数/时长",
            "rest": "休息时长",
            "notes": "动作要点和注意事项"
        }}
    ],
    "safety_tips": ["安全提示1", "安全提示2"],
    "progression": "进阶调整建议"
}}"""
            
            messages = [
                {"role": "user", "content": plan_prompt}
            ]
            
            # 调用对话功能
            response = await self.chat(
                messages=messages,
                temperature=0.5,
                max_tokens=3000
            )
            
            # 尝试解析JSON响应
            import json
            try:
                result = json.loads(response)
                logger.info(f"[{self.name}] 运动计划制定完成")
                return result
            except json.JSONDecodeError:
                # 如果解析失败，返回原始文本
                logger.warning(f"[{self.name}] JSON解析失败，返回原始文本")
                return {
                    "goal": goal,
                    "level": level,
                    "duration": f"{duration_weeks}周",
                    "plan_content": response,
                    "weekly_schedule": [],
                    "exercises": [],
                    "safety_tips": [],
                    "progression": ""
                }
                
        except Exception as e:
            logger.error(f"[{self.name}] 运动计划制定失败: {str(e)}")
            raise


# =============================================================================
# 心理咨询师智能体
# =============================================================================

class PsychologyAgent(BaseAgent):
    """
    心理咨询师智能体
    
    专注于心理健康、情绪支持的专业智能体。
    能够评估用户的情绪状态，提供心理支持和建议。
    
    Attributes:
        name: 智能体名称
        description: 智能体描述
        system_prompt: 系统提示词
    
    Example:
        >>> agent = PsychologyAgent()
        >>> assessment = await agent.assess_mood("最近总是感到焦虑...")
        >>> print(assessment)
    """
    
    # 心理咨询师专业系统提示词
    PSYCHOLOGY_PROMPT = """你是一位专业的心理咨询师，拥有丰富的心理学知识和咨询经验。

【角色定位】
- 专业心理咨询师，专注于心理健康支持和情绪管理
- 熟悉认知行为疗法、正念疗法、积极心理学等
- 能够提供温暖、支持性的倾听和专业的心理建议

【核心能力】
1. 情绪评估：评估用户的情绪状态和心理状况
2. 心理支持：提供情感支持和共情理解
3. 压力管理：帮助用户识别和管理压力源
4. 认知调整：引导用户进行积极的认知重构
5. 应对策略：提供实用的情绪调节和应对技巧

【咨询原则】
- 保密性：尊重用户隐私，保护咨询内容
- 非评判：保持中立，不对用户进行道德评判
- 共情理解：真诚理解用户的感受和处境
- 赋能导向：帮助用户发掘自身资源和力量
- 安全第一：识别危机信号，必要时建议寻求专业帮助

【重要声明】
- 你是AI助手，不是真人心理咨询师
- 对于严重的心理问题，建议用户寻求专业心理治疗
- 如果出现自伤或伤人的想法，请立即建议用户联系危机干预热线

【输出格式】
回复应包含：
1. 情绪状态评估
2. 共情理解和接纳
3. 实用的应对建议
4. 放松技巧或练习方法
5. 何时寻求专业帮助的建议

请用温暖、专业、支持性的语言回答用户问题。"""
    
    def __init__(
        self,
        enable_memory: bool = True,
        enable_rag: bool = True
    ):
        """
        初始化心理咨询师智能体
        
        Args:
            enable_memory: 是否启用记忆召回，默认True
            enable_rag: 是否启用知识检索，默认True
        """
        super().__init__(
            name="心理咨询师",
            description="专业心理咨询师，提供心理健康支持和情绪管理建议",
            system_prompt=self.PSYCHOLOGY_PROMPT,
            enable_memory=enable_memory,
            enable_rag=enable_rag
        )
        logger.info(f"[{self.name}] 心理咨询师智能体初始化完成")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        执行对话
        
        与心理咨询师进行对话，获取心理健康相关的专业支持。
        
        Args:
            messages: 消息列表
            **kwargs: 额外参数
        
        Returns:
            str: 心理咨询师的回复内容
        """
        try:
            user_id = kwargs.get("user_id")
            use_memory = kwargs.get("use_memory", True)
            use_rag = kwargs.get("use_rag", True)
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 2000)
            
            # 获取最后一条用户消息作为查询
            user_message = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    user_message = msg.get("content", "")
                    break
            
            # 构建上下文
            context = await self.build_context(
                query=user_message,
                user_id=user_id,
                use_memory=use_memory,
                use_rag=use_rag
            )
            
            # 格式化系统提示词
            formatted_system_prompt = self.format_system_prompt(context)
            
            # 构建完整消息列表
            full_messages = [
                {"role": "system", "content": formatted_system_prompt}
            ] + messages
            
            logger.info(f"[{self.name}] 开始对话请求")
            
            # 调用Kimi服务
            response = await kimi_service.chat_completion(
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            logger.info(f"[{self.name}] 对话完成，回复长度: {len(content)} 字符")
            
            return content
            
        except Exception as e:
            logger.error(f"[{self.name}] 对话失败: {str(e)}")
            raise
    
    async def assess_mood(self, mood_description: str) -> Dict[str, Any]:
        """
        评估情绪状态
        
        评估用户的情绪状态，提供心理分析和应对建议。
        
        Args:
            mood_description: 情绪描述文本，用户描述自己的情绪状态
        
        Returns:
            Dict: 情绪评估结果，包含：
                - mood_summary: 情绪状态总结
                - severity: 严重程度（轻度/中度/重度）
                - possible_causes: 可能的原因分析
                - coping_strategies: 应对策略
                - techniques: 推荐的放松技巧
                - when_to_seek_help: 何时寻求专业帮助
        
        Example:
            >>> description = "最近工作压力很大，晚上睡不好，总是担心工作做不完..."
            >>> assessment = await agent.assess_mood(description)
            >>> print(assessment["mood_summary"])
        """
        try:
            logger.info(f"[{self.name}] 开始评估情绪状态")
            
            # 构建评估提示
            assessment_prompt = f"""请对以下情绪描述进行专业心理评估：

【情绪描述】
{mood_description}

请按照以下JSON格式返回评估结果（只返回JSON，不要其他内容）：
{{
    "mood_summary": "情绪状态总结",
    "severity": "严重程度（轻度/中度/重度）",
    "possible_causes": ["可能原因1", "可能原因2"],
    "coping_strategies": [
        {{
            "strategy": "策略名称",
            "description": "具体做法"
        }}
    ],
    "techniques": [
        {{
            "name": "技巧名称",
            "steps": ["步骤1", "步骤2", "步骤3"]
        }}
    ],
    "when_to_seek_help": "何时建议寻求专业心理帮助",
    "crisis_warning": "是否存在危机信号（是/否）",
    "supportive_message": "温暖的支持性话语"
}}"""
            
            messages = [
                {"role": "user", "content": assessment_prompt}
            ]
            
            # 调用对话功能
            response = await self.chat(
                messages=messages,
                temperature=0.6,
                max_tokens=2500
            )
            
            # 尝试解析JSON响应
            import json
            try:
                result = json.loads(response)
                logger.info(f"[{self.name}] 情绪评估完成")
                
                # 检查危机信号
                if result.get("crisis_warning") == "是":
                    logger.warning(f"[{self.name}] 检测到可能的危机信号")
                
                return result
            except json.JSONDecodeError:
                # 如果解析失败，返回原始文本
                logger.warning(f"[{self.name}] JSON解析失败，返回原始文本")
                return {
                    "mood_summary": response,
                    "severity": "未知",
                    "possible_causes": [],
                    "coping_strategies": [],
                    "techniques": [],
                    "when_to_seek_help": "如有持续困扰，建议咨询专业心理医生",
                    "crisis_warning": "否",
                    "supportive_message": "感谢你分享你的感受，你并不孤单。"
                }
                
        except Exception as e:
            logger.error(f"[{self.name}] 情绪评估失败: {str(e)}")
            raise


# =============================================================================
# 体检分析师智能体
# =============================================================================

class MedicalAnalystAgent(BaseAgent):
    """
    体检分析师智能体
    
    专注于体检报告解读、健康指标分析的专业智能体。
    能够分析体检数据，提供健康评估和建议。
    
    Attributes:
        name: 智能体名称
        description: 智能体描述
        system_prompt: 系统提示词
    
    Example:
        >>> agent = MedicalAnalystAgent()
        >>> report_data = {"blood_pressure": "120/80", "blood_sugar": "5.6"}
        >>> analysis = await agent.analyze_report(report_data)
        >>> print(analysis)
    """
    
    # 体检分析师专业系统提示词
    MEDICAL_ANALYST_PROMPT = """你是一位专业的体检分析师和健康管理专家，拥有丰富的医学检验和健康管理知识。

【角色定位】
- 专业体检分析师，专注于体检报告解读和健康指标分析
- 熟悉常见体检项目的临床意义和参考范围
- 能够根据体检数据提供健康评估和生活方式建议

【核心能力】
1. 体检报告解读：解读各项体检指标的意义
2. 异常指标分析：识别异常指标并分析可能原因
3. 健康风险评估：评估潜在的健康风险
4. 健康建议：提供针对性的健康管理建议
5. 复查指导：建议需要复查或进一步检查的项目

【分析原则】
- 准确性：基于医学标准和参考范围进行分析
- 全面性：综合考虑多项指标的相互关系
- 预防导向：关注早期预警信号，强调预防
- 个性化：结合用户的年龄、性别、病史等因素
- 谨慎性：对于严重异常，建议就医检查

【重要声明】
- 你是AI助手，不是医生
- 分析结果仅供参考，不能替代医生的诊断
- 对于严重异常指标，必须建议用户咨询医生
- 不提供具体的药物治疗建议

【常见体检指标参考】
- 血压：正常<120/80 mmHg，高血压≥140/90 mmHg
- 空腹血糖：正常3.9-6.1 mmol/L，糖尿病≥7.0 mmol/L
- 总胆固醇：正常<5.2 mmol/L，升高≥6.2 mmol/L
- 甘油三酯：正常<1.7 mmol/L，升高≥2.3 mmol/L
- BMI：正常18.5-23.9，超重24-27.9，肥胖≥28

【输出格式】
分析报告应包含：
1. 体检概况总结
2. 各项指标详细解读
3. 异常指标分析（如有）
4. 健康风险评估
5. 健康管理建议
6. 复查建议（如有）

请用专业、清晰、易懂的语言回答用户问题。"""
    
    def __init__(
        self,
        enable_memory: bool = True,
        enable_rag: bool = True
    ):
        """
        初始化体检分析师智能体
        
        Args:
            enable_memory: 是否启用记忆召回，默认True
            enable_rag: 是否启用知识检索，默认True
        """
        super().__init__(
            name="体检分析师",
            description="专业体检分析师，提供体检报告解读和健康指标分析",
            system_prompt=self.MEDICAL_ANALYST_PROMPT,
            enable_memory=enable_memory,
            enable_rag=enable_rag
        )
        logger.info(f"[{self.name}] 体检分析师智能体初始化完成")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        执行对话
        
        与体检分析师进行对话，获取体检报告相关的专业解读。
        
        Args:
            messages: 消息列表
            **kwargs: 额外参数
        
        Returns:
            str: 体检分析师的回复内容
        """
        try:
            user_id = kwargs.get("user_id")
            use_memory = kwargs.get("use_memory", True)
            use_rag = kwargs.get("use_rag", True)
            temperature = kwargs.get("temperature", 0.5)
            max_tokens = kwargs.get("max_tokens", 2500)
            
            # 获取最后一条用户消息作为查询
            user_message = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    user_message = msg.get("content", "")
                    break
            
            # 构建上下文
            context = await self.build_context(
                query=user_message,
                user_id=user_id,
                use_memory=use_memory,
                use_rag=use_rag
            )
            
            # 格式化系统提示词
            formatted_system_prompt = self.format_system_prompt(context)
            
            # 构建完整消息列表
            full_messages = [
                {"role": "system", "content": formatted_system_prompt}
            ] + messages
            
            logger.info(f"[{self.name}] 开始对话请求")
            
            # 调用Kimi服务
            response = await kimi_service.chat_completion(
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            logger.info(f"[{self.name}] 对话完成，回复长度: {len(content)} 字符")
            
            return content
            
        except Exception as e:
            logger.error(f"[{self.name}] 对话失败: {str(e)}")
            raise
    
    async def analyze_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析体检报告
        
        分析体检数据，提供详细的健康评估和建议。
        
        Args:
            report_data: 体检数据字典，包含各项体检指标，如：
                {
                    "blood_pressure": "120/80",
                    "blood_sugar": "5.6",
                    "cholesterol": "5.0",
                    "height": "175",
                    "weight": "70",
                    ...
                }
        
        Returns:
            Dict: 分析报告，包含：
                - report_summary: 报告概况
                - indicators_analysis: 各项指标分析
                - abnormal_findings: 异常发现（如有）
                - risk_assessment: 健康风险评估
                - health_suggestions: 健康管理建议
                - follow_up: 复查建议
        
        Example:
            >>> report = {
            ...     "blood_pressure": "135/85",
            ...     "blood_sugar": "6.5",
            ...     "height": "170",
            ...     "weight": "80"
            ... }
            >>> analysis = await agent.analyze_report(report)
            >>> print(analysis["risk_assessment"])
        """
        try:
            logger.info(f"[{self.name}] 开始分析体检报告")
            
            # 格式化体检数据
            report_text = "\n".join([
                f"{key}: {value}"
                for key, value in report_data.items()
            ])
            
            # 构建分析提示
            analysis_prompt = f"""请对以下体检数据进行专业分析：

【体检数据】
{report_text}

请按照以下JSON格式返回分析报告（只返回JSON，不要其他内容）：
{{
    "report_summary": {{
        "exam_date": "体检日期（如有）",
        "overall_status": "整体健康状态评估"
    }},
    "indicators_analysis": [
        {{
            "indicator": "指标名称",
            "value": "检测值",
            "reference_range": "参考范围",
            "status": "正常/异常/临界",
            "interpretation": "临床意义解读"
        }}
    ],
    "abnormal_findings": [
        {{
            "item": "异常项目",
            "value": "异常值",
            "severity": "轻度/中度/重度",
            "possible_causes": "可能原因",
            "recommendation": "建议措施"
        }}
    ],
    "risk_assessment": {{
        "overall_risk": "整体风险等级（低/中/高）",
        "risk_factors": ["风险因素1", "风险因素2"],
        "attention_needed": "需要关注的方面"
    }},
    "health_suggestions": [
        {{
            "category": "建议类别（饮食/运动/生活习惯等）",
            "suggestions": ["具体建议1", "具体建议2"]
        }}
    ],
    "follow_up": {{
        "recommended_items": ["建议复查项目1", "建议复查项目2"],
        "recommended_time": "建议复查时间",
        "medical_consultation": "是否需要就医咨询"
    }}
}}"""
            
            messages = [
                {"role": "user", "content": analysis_prompt}
            ]
            
            # 调用对话功能
            response = await self.chat(
                messages=messages,
                temperature=0.4,
                max_tokens=3000
            )
            
            # 尝试解析JSON响应
            import json
            try:
                result = json.loads(response)
                logger.info(f"[{self.name}] 体检报告分析完成")
                return result
            except json.JSONDecodeError:
                # 如果解析失败，返回原始文本
                logger.warning(f"[{self.name}] JSON解析失败，返回原始文本")
                return {
                    "report_summary": {
                        "exam_date": "",
                        "overall_status": "分析完成"
                    },
                    "indicators_analysis": [],
                    "abnormal_findings": [],
                    "risk_assessment": {
                        "overall_risk": "未知",
                        "risk_factors": [],
                        "attention_needed": response
                    },
                    "health_suggestions": [],
                    "follow_up": {
                        "recommended_items": [],
                        "recommended_time": "",
                        "medical_consultation": "如有疑虑，建议咨询医生"
                    }
                }
                
        except Exception as e:
            logger.error(f"[{self.name}] 体检报告分析失败: {str(e)}")
            raise


# =============================================================================
# 智能体工厂函数
# =============================================================================

def create_nutritionist_agent(
    enable_memory: bool = True,
    enable_rag: bool = True
) -> NutritionistAgent:
    """
    创建营养师智能体
    
    Args:
        enable_memory: 是否启用记忆召回
        enable_rag: 是否启用知识检索
    
    Returns:
        NutritionistAgent: 营养师智能体实例
    """
    return NutritionistAgent(enable_memory=enable_memory, enable_rag=enable_rag)


def create_fitness_coach_agent(
    enable_memory: bool = True,
    enable_rag: bool = True
) -> FitnessCoachAgent:
    """
    创建运动教练智能体
    
    Args:
        enable_memory: 是否启用记忆召回
        enable_rag: 是否启用知识检索
    
    Returns:
        FitnessCoachAgent: 运动教练智能体实例
    """
    return FitnessCoachAgent(enable_memory=enable_memory, enable_rag=enable_rag)


def create_psychology_agent(
    enable_memory: bool = True,
    enable_rag: bool = True
) -> PsychologyAgent:
    """
    创建心理咨询师智能体
    
    Args:
        enable_memory: 是否启用记忆召回
        enable_rag: 是否启用知识检索
    
    Returns:
        PsychologyAgent: 心理咨询师智能体实例
    """
    return PsychologyAgent(enable_memory=enable_memory, enable_rag=enable_rag)


def create_medical_analyst_agent(
    enable_memory: bool = True,
    enable_rag: bool = True
) -> MedicalAnalystAgent:
    """
    创建体检分析师智能体
    
    Args:
        enable_memory: 是否启用记忆召回
        enable_rag: 是否启用知识检索
    
    Returns:
        MedicalAnalystAgent: 体检分析师智能体实例
    """
    return MedicalAnalystAgent(enable_memory=enable_memory, enable_rag=enable_rag)


# =============================================================================
# 全局智能体实例（单例模式）
# =============================================================================

# 懒加载的智能体实例
_nutritionist_agent: Optional[NutritionistAgent] = None
_fitness_coach_agent: Optional[FitnessCoachAgent] = None
_psychology_agent: Optional[PsychologyAgent] = None
_medical_analyst_agent: Optional[MedicalAnalystAgent] = None


def get_nutritionist_agent() -> NutritionistAgent:
    """获取营养师智能体单例"""
    global _nutritionist_agent
    if _nutritionist_agent is None:
        _nutritionist_agent = create_nutritionist_agent()
    return _nutritionist_agent


def get_fitness_coach_agent() -> FitnessCoachAgent:
    """获取运动教练智能体单例"""
    global _fitness_coach_agent
    if _fitness_coach_agent is None:
        _fitness_coach_agent = create_fitness_coach_agent()
    return _fitness_coach_agent


def get_psychology_agent() -> PsychologyAgent:
    """获取心理咨询师智能体单例"""
    global _psychology_agent
    if _psychology_agent is None:
        _psychology_agent = create_psychology_agent()
    return _psychology_agent


def get_medical_analyst_agent() -> MedicalAnalystAgent:
    """获取体检分析师智能体单例"""
    global _medical_analyst_agent
    if _medical_analyst_agent is None:
        _medical_analyst_agent = create_medical_analyst_agent()
    return _medical_analyst_agent


# 导出所有智能体类
__all__ = [
    # 智能体类
    "NutritionistAgent",
    "FitnessCoachAgent",
    "PsychologyAgent",
    "MedicalAnalystAgent",
    # 工厂函数
    "create_nutritionist_agent",
    "create_fitness_coach_agent",
    "create_psychology_agent",
    "create_medical_analyst_agent",
    # 单例获取函数
    "get_nutritionist_agent",
    "get_fitness_coach_agent",
    "get_psychology_agent",
    "get_medical_analyst_agent",
]
