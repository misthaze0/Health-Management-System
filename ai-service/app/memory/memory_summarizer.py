"""
记忆摘要模块

提供用户对话记忆的摘要生成、压缩和管理功能。
通过Kimi AI服务将多条历史记忆汇总为简洁的摘要，减少Token消耗，提升对话效率。
"""
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from loguru import logger

from app.core.config import settings
from app.services.kimi_service import kimi_service


class MemorySummarizer:
    """
    记忆摘要器类
    
    负责将用户的对话历史记忆进行智能摘要，包括：
    - 将多条记忆汇总为简洁的摘要文本
    - 根据记忆数量阈值触发摘要生成
    - 压缩旧记忆为摘要以优化存储
    - 管理摘要的生命周期
    
    Attributes:
        summary_threshold: 触发摘要生成的记忆数量阈值
        kimi_service: Kimi AI服务实例，用于生成摘要
    """
    
    def __init__(self):
        """
        初始化记忆摘要器
        
        从配置中读取摘要阈值，初始化Kimi服务实例
        """
        self.summary_threshold: int = settings.MEMORY_SUMMARY_THRESHOLD
        self.kimi_service = kimi_service
        logger.info(f"MemorySummarizer初始化完成，摘要阈值: {self.summary_threshold}")
    
    async def summarize_memories(self, memories: List[Dict[str, Any]]) -> str:
        """
        将多条记忆汇总为摘要
        
        使用Kimi AI服务分析记忆内容，提取关键信息并生成简洁的摘要文本。
        摘要应包含用户的主要关注点、健康问题和偏好等关键信息。
        
        Args:
            memories: 记忆列表，每条记忆包含content, timestamp, type等字段
                示例: [
                    {"content": "用户询问高血压饮食建议", "timestamp": "2024-01-01", "type": "query"},
                    {"content": "用户提到有家族糖尿病史", "timestamp": "2024-01-02", "type": "fact"}
                ]
        
        Returns:
            str: 生成的摘要文本
            
        Raises:
            ValueError: 当memories为空列表时
            Exception: 当Kimi API调用失败时
        """
        if not memories:
            logger.warning("记忆列表为空，无法生成摘要")
            raise ValueError("记忆列表不能为空")
        
        logger.info(f"开始为 {len(memories)} 条记忆生成摘要")
        
        # 构建记忆内容文本
        memories_text = self._format_memories_for_summary(memories)
        
        # 构建系统提示词
        system_prompt = """你是一位专业的健康档案管理助手。你的任务是将用户的对话历史记录汇总成一份简洁的摘要。

请遵循以下原则：
1. 提取关键健康信息：疾病史、过敏史、用药情况、体检异常指标等
2. 记录用户的健康偏好：饮食偏好、运动习惯、关注的健康问题
3. 总结用户的咨询模式：常问的问题类型、关注的健康领域
4. 保持客观准确，不要添加记忆中没有的信息
5. 使用第三人称描述，如"用户"、"该用户"
6. 摘要应简洁明了，控制在300字以内

请直接返回摘要文本，不要添加任何格式标记或解释性文字。"""

        # 构建消息列表
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请将以下记忆记录汇总成摘要：\n\n{memories_text}"}
        ]
        
        try:
            # 调用Kimi服务生成摘要
            response = await self.kimi_service.chat_completion(
                messages=messages,
                temperature=0.3,  # 低温度确保输出稳定
                max_tokens=500
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"摘要生成成功，长度: {len(summary)} 字符")
            return summary
            
        except Exception as e:
            logger.error(f"摘要生成失败: {str(e)}")
            raise
    
    def _format_memories_for_summary(self, memories: List[Dict[str, Any]]) -> str:
        """
        将记忆列表格式化为适合摘要的文本格式
        
        Args:
            memories: 记忆列表
            
        Returns:
            str: 格式化后的记忆文本
        """
        formatted_lines = []
        
        for idx, memory in enumerate(memories, 1):
            content = memory.get("content", "")
            timestamp = memory.get("timestamp", "")
            memory_type = memory.get("type", "unknown")
            
            # 格式化时间戳
            if timestamp:
                if isinstance(timestamp, datetime):
                    time_str = timestamp.strftime("%Y-%m-%d %H:%M")
                else:
                    time_str = str(timestamp)
                formatted_lines.append(f"[{idx}] {time_str} [{memory_type}] {content}")
            else:
                formatted_lines.append(f"[{idx}] [{memory_type}] {content}")
        
        return "\n".join(formatted_lines)
    
    async def should_summarize(self, user_id: int, memory_count: Optional[int] = None) -> bool:
        """
        检查是否需要为用户生成摘要
        
        基于记忆数量阈值判断是否需要触发摘要生成。
        当用户的记忆数量达到或超过阈值时，返回True。
        
        Args:
            user_id: 用户ID
            memory_count: 可选，直接传入记忆数量。如果不传入，则需要外部查询
        
        Returns:
            bool: 是否需要生成摘要
        """
        if memory_count is None:
            # 如果没有传入记忆数量，记录日志并返回False
            # 实际使用时应该查询数据库获取记忆数量
            logger.debug(f"用户 {user_id} 未提供记忆数量，无法判断是否需要摘要")
            return False
        
        should_trigger = memory_count >= self.summary_threshold
        
        if should_trigger:
            logger.info(f"用户 {user_id} 的记忆数量({memory_count})达到阈值({self.summary_threshold})，需要生成摘要")
        else:
            logger.debug(f"用户 {user_id} 的记忆数量({memory_count})未达到阈值({self.summary_threshold})")
        
        return should_trigger
    
    async def compress_old_memories(
        self, 
        user_id: int, 
        memories: List[Dict[str, Any]], 
        days: int = 30
    ) -> Dict[str, Any]:
        """
        压缩旧记忆为摘要
        
        将指定时间范围之前的记忆进行摘要生成，并返回压缩结果。
        压缩后的摘要可以替代原始记忆，减少存储和Token消耗。
        
        Args:
            user_id: 用户ID
            memories: 用户的所有记忆列表
            days: 压缩多少天之前的记忆，默认30天
        
        Returns:
            Dict[str, Any]: 压缩结果，包含以下字段：
                - summary: 生成的摘要文本
                - compressed_count: 被压缩的记忆数量
                - compressed_ids: 被压缩的记忆ID列表
                - summary_timestamp: 摘要生成时间
                - days_threshold: 时间阈值（天）
        """
        logger.info(f"开始为用户 {user_id} 压缩 {days} 天前的记忆")
        
        # 计算时间阈值
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # 筛选旧记忆
        old_memories = []
        compressed_ids = []
        
        for memory in memories:
            timestamp = memory.get("timestamp")
            if timestamp:
                if isinstance(timestamp, str):
                    try:
                        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except ValueError:
                        continue
                
                if isinstance(timestamp, datetime) and timestamp < cutoff_date:
                    old_memories.append(memory)
                    memory_id = memory.get("id")
                    if memory_id:
                        compressed_ids.append(memory_id)
        
        if not old_memories:
            logger.info(f"用户 {user_id} 没有需要压缩的旧记忆（{days}天前）")
            return {
                "summary": "",
                "compressed_count": 0,
                "compressed_ids": [],
                "summary_timestamp": datetime.now().isoformat(),
                "days_threshold": days
            }
        
        logger.info(f"找到 {len(old_memories)} 条需要压缩的旧记忆")
        
        # 生成摘要
        summary = await self.summarize_memories(old_memories)
        
        result = {
            "summary": summary,
            "compressed_count": len(old_memories),
            "compressed_ids": compressed_ids,
            "summary_timestamp": datetime.now().isoformat(),
            "days_threshold": days
        }
        
        logger.info(f"用户 {user_id} 的记忆压缩完成，压缩了 {len(old_memories)} 条记忆")
        return result
    
    async def trigger_summary_check(
        self, 
        user_id: int, 
        memories: Optional[List[Dict[str, Any]]] = None,
        memory_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        触发摘要检查并执行
        
        检查用户是否需要生成摘要，如果需要则执行摘要生成。
        这是主要的入口方法，整合了阈值检查和摘要生成逻辑。
        
        Args:
            user_id: 用户ID
            memories: 可选，用户的记忆列表。如果不传入，需要外部提供memory_count
            memory_count: 可选，记忆数量。如果不传入且memories也不传入，则无法执行
        
        Returns:
            Dict[str, Any]: 检查结果，包含以下字段：
                - triggered: 是否触发了摘要生成
                - summary: 生成的摘要（如果triggered为True）
                - memory_count: 当前记忆数量
                - threshold: 摘要阈值
                - timestamp: 检查时间
                - message: 状态信息
        """
        timestamp = datetime.now().isoformat()
        
        # 确定记忆数量
        if memory_count is None and memories is not None:
            memory_count = len(memories)
        
        if memory_count is None:
            logger.error(f"用户 {user_id} 的摘要检查失败：未提供记忆数量或记忆列表")
            return {
                "triggered": False,
                "summary": None,
                "memory_count": None,
                "threshold": self.summary_threshold,
                "timestamp": timestamp,
                "message": "未提供记忆数据，无法执行检查"
            }
        
        # 检查是否需要摘要
        should_trigger = await self.should_summarize(user_id, memory_count)
        
        if not should_trigger:
            return {
                "triggered": False,
                "summary": None,
                "memory_count": memory_count,
                "threshold": self.summary_threshold,
                "timestamp": timestamp,
                "message": f"记忆数量({memory_count})未达到阈值({self.summary_threshold})"
            }
        
        # 需要生成摘要
        try:
            if memories is None:
                logger.error(f"用户 {user_id} 需要生成摘要但未提供记忆列表")
                return {
                    "triggered": False,
                    "summary": None,
                    "memory_count": memory_count,
                    "threshold": self.summary_threshold,
                    "timestamp": timestamp,
                    "message": "需要生成摘要但未提供记忆列表"
                }
            
            summary = await self.summarize_memories(memories)
            
            logger.info(f"用户 {user_id} 的摘要检查完成，已成功生成摘要")
            return {
                "triggered": True,
                "summary": summary,
                "memory_count": memory_count,
                "threshold": self.summary_threshold,
                "timestamp": timestamp,
                "message": "摘要生成成功"
            }
            
        except Exception as e:
            logger.error(f"用户 {user_id} 的摘要生成失败: {str(e)}")
            return {
                "triggered": False,
                "summary": None,
                "memory_count": memory_count,
                "threshold": self.summary_threshold,
                "timestamp": timestamp,
                "message": f"摘要生成失败: {str(e)}"
            }


# 全局记忆摘要器实例
memory_summarizer = MemorySummarizer()


async def get_memory_summarizer() -> MemorySummarizer:
    """
    获取记忆摘要器实例（依赖注入）
    
    Returns:
        MemorySummarizer: 记忆摘要器实例
    """
    return memory_summarizer


async def trigger_summary(user_id: int, memories: list = None, memory_count: int = None) -> dict:
    """
    触发记忆摘要检查（便捷函数）
    
    Args:
        user_id: 用户ID
        memories: 记忆列表
        memory_count: 记忆数量
        
    Returns:
        dict: 摘要检查结果
    """
    summarizer = await get_memory_summarizer()
    return await summarizer.trigger_summary_check(user_id, memories, memory_count)
