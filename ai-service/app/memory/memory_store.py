"""
记忆存储模块
管理用户长期记忆，包括事实、偏好、目标和摘要
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger
from app.db.database import db


class MemoryStore:
    """
    用户长期记忆存储管理类
    
    支持的记忆类型:
    - fact: 事实性信息（如用户的年龄、职业等）
    - preference: 用户偏好（如喜欢的食物、运动方式等）
    - goal: 用户目标（如减重目标、健身计划等）
    - summary: 对话摘要（历史对话的总结）
    """
    
    # 有效的记忆类型
    VALID_MEMORY_TYPES = {'fact', 'preference', 'goal', 'summary'}
    
    def __init__(self):
        """初始化记忆存储"""
        logger.info("MemoryStore 初始化完成")
    
    async def add_memory(
        self, 
        user_id: int, 
        memory_type: str, 
        content: str, 
        importance: float = 1.0
    ) -> Optional[int]:
        """
        添加新的用户记忆
        
        Args:
            user_id: 用户ID
            memory_type: 记忆类型 ('fact', 'preference', 'goal', 'summary')
            content: 记忆内容
            importance: 重要性评分 (0.0 - 10.0)，默认为1.0
            
        Returns:
            新创建的记忆ID，失败返回None
            
        Raises:
            ValueError: 当memory_type无效时
        """
        # 验证记忆类型
        if memory_type not in self.VALID_MEMORY_TYPES:
            logger.error(f"无效的记忆类型: {memory_type}")
            raise ValueError(f"无效的记忆类型: {memory_type}。有效类型: {self.VALID_MEMORY_TYPES}")
        
        # 验证内容不为空
        if not content or not content.strip():
            logger.warning("记忆内容不能为空")
            return None
        
        # 如果没有提供重要性，自动计算
        if importance == 1.0:
            importance = self.calculate_importance(content)
        
        # 限制重要性范围
        importance = max(0.0, min(10.0, importance))
        
        try:
            query = """
                INSERT INTO user_memories 
                (user_id, memory_type, content, importance, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
            """
            
            # 执行插入
            await db.execute(query, (user_id, memory_type, content.strip(), importance))
            
            # 获取新插入记录的ID
            result = await db.fetch_one(
                "SELECT LAST_INSERT_ID() as memory_id"
            )
            
            memory_id = result['memory_id'] if result else None
            
            logger.info(
                f"记忆添加成功 - ID: {memory_id}, 用户: {user_id}, "
                f"类型: {memory_type}, 重要性: {importance:.2f}"
            )
            
            return memory_id
            
        except Exception as e:
            logger.error(f"添加记忆失败 - 用户: {user_id}, 错误: {e}")
            return None
    
    async def get_memories(
        self, 
        user_id: int, 
        memory_type: Optional[str] = None,
        limit: int = 100,
        min_importance: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        获取用户记忆列表
        
        Args:
            user_id: 用户ID
            memory_type: 可选，按记忆类型筛选
            limit: 返回记录数量限制，默认100条
            min_importance: 最小重要性阈值，默认0.0
            
        Returns:
            记忆记录列表，按重要性降序、更新时间降序排列
            
        Raises:
            ValueError: 当memory_type无效时
        """
        # 验证记忆类型（如果提供）
        if memory_type and memory_type not in self.VALID_MEMORY_TYPES:
            logger.error(f"无效的记忆类型: {memory_type}")
            raise ValueError(f"无效的记忆类型: {memory_type}")
        
        try:
            # 构建查询
            if memory_type:
                query = """
                    SELECT id, user_id, memory_type, content, importance, 
                           created_at, updated_at
                    FROM user_memories
                    WHERE user_id = %s AND memory_type = %s AND importance >= %s
                    ORDER BY importance DESC, updated_at DESC
                    LIMIT %s
                """
                params = (user_id, memory_type, min_importance, limit)
            else:
                query = """
                    SELECT id, user_id, memory_type, content, importance,
                           created_at, updated_at
                    FROM user_memories
                    WHERE user_id = %s AND importance >= %s
                    ORDER BY importance DESC, updated_at DESC
                    LIMIT %s
                """
                params = (user_id, min_importance, limit)
            
            memories = await db.fetch_all(query, params)
            
            logger.debug(
                f"获取记忆成功 - 用户: {user_id}, "
                f"类型: {memory_type or '全部'}, 数量: {len(memories)}"
            )
            
            return memories if memories else []
            
        except Exception as e:
            logger.error(f"获取记忆失败 - 用户: {user_id}, 错误: {e}")
            return []
    
    async def update_memory(
        self, 
        memory_id: int, 
        content: str
    ) -> bool:
        """
        更新记忆内容
        
        Args:
            memory_id: 记忆记录ID
            content: 新的记忆内容
            
        Returns:
            更新成功返回True，失败返回False
        """
        # 验证内容不为空
        if not content or not content.strip():
            logger.warning("记忆内容不能为空")
            return False
        
        try:
            # 重新计算重要性
            new_importance = self.calculate_importance(content)
            
            query = """
                UPDATE user_memories
                SET content = %s, importance = %s, updated_at = NOW()
                WHERE id = %s
            """
            
            rowcount = await db.execute(
                query, (content.strip(), new_importance, memory_id)
            )
            
            if rowcount > 0:
                logger.info(
                    f"记忆更新成功 - ID: {memory_id}, 新重要性: {new_importance:.2f}"
                )
                return True
            else:
                logger.warning(f"记忆不存在 - ID: {memory_id}")
                return False
                
        except Exception as e:
            logger.error(f"更新记忆失败 - ID: {memory_id}, 错误: {e}")
            return False
    
    async def delete_memory(self, memory_id: int) -> bool:
        """
        删除记忆记录
        
        Args:
            memory_id: 记忆记录ID
            
        Returns:
            删除成功返回True，失败返回False
        """
        try:
            query = "DELETE FROM user_memories WHERE id = %s"
            rowcount = await db.execute(query, (memory_id,))
            
            if rowcount > 0:
                logger.info(f"记忆删除成功 - ID: {memory_id}")
                return True
            else:
                logger.warning(f"要删除的记忆不存在 - ID: {memory_id}")
                return False
                
        except Exception as e:
            logger.error(f"删除记忆失败 - ID: {memory_id}, 错误: {e}")
            return False
    
    async def get_memory_by_id(self, memory_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取单条记忆
        
        Args:
            memory_id: 记忆记录ID
            
        Returns:
            记忆记录字典，不存在返回None
        """
        try:
            query = """
                SELECT id, user_id, memory_type, content, importance,
                       created_at, updated_at
                FROM user_memories
                WHERE id = %s
            """
            
            result = await db.fetch_one(query, (memory_id,))
            return result
            
        except Exception as e:
            logger.error(f"获取记忆失败 - ID: {memory_id}, 错误: {e}")
            return None
    
    async def delete_user_memories(
        self, 
        user_id: int, 
        memory_type: Optional[str] = None
    ) -> int:
        """
        删除用户的所有记忆（或指定类型的记忆）
        
        Args:
            user_id: 用户ID
            memory_type: 可选，指定要删除的记忆类型
            
        Returns:
            删除的记录数量
        """
        try:
            if memory_type:
                query = """
                    DELETE FROM user_memories 
                    WHERE user_id = %s AND memory_type = %s
                """
                params = (user_id, memory_type)
            else:
                query = "DELETE FROM user_memories WHERE user_id = %s"
                params = (user_id,)
            
            rowcount = await db.execute(query, params)
            
            logger.info(
                f"批量删除记忆成功 - 用户: {user_id}, "
                f"类型: {memory_type or '全部'}, 数量: {rowcount}"
            )
            
            return rowcount
            
        except Exception as e:
            logger.error(f"批量删除记忆失败 - 用户: {user_id}, 错误: {e}")
            return 0
    
    def calculate_importance(self, content: str) -> float:
        """
        计算记忆内容的重要性评分
        
        使用简单规则评估：
        - 基础分: 5.0
        - 关键词加分:
            - 健康相关词汇 (+1.0)
            - 目标/计划词汇 (+0.5)
            - 紧急/重要词汇 (+1.5)
        - 长度惩罚:
            - 内容过短 (< 5字): -1.0
            - 内容过长 (> 200字): -0.5
        - 特殊标记:
            - 包含数字: +0.3
            - 包含日期/时间: +0.5
        
        Args:
            content: 记忆内容
            
        Returns:
            重要性评分 (0.0 - 10.0)
        """
        if not content:
            return 0.0
        
        content_lower = content.lower()
        importance = 5.0  # 基础分
        
        # 健康相关关键词
        health_keywords = [
            '健康', '疾病', '病症', '症状', '血压', '血糖', '体重', '身高',
            '过敏', '药物', '手术', '住院', '体检', '疫苗', '慢性', '急性',
            '糖尿病', '高血压', '心脏病', '健康', 'disease', 'symptom',
            'blood pressure', 'diabetes', 'allergy', 'medicine', 'surgery'
        ]
        
        # 目标/计划关键词
        goal_keywords = [
            '目标', '计划', '想要', '希望', '打算', '决定', '开始', '完成',
            'goal', 'plan', 'target', 'want', 'hope', 'decide', 'start'
        ]
        
        # 紧急/重要关键词
        urgent_keywords = [
            '紧急', '重要', '严重', '必须', '一定', '关键', '核心',
            'urgent', 'important', 'serious', 'must', 'critical', 'key'
        ]
        
        # 检查关键词
        for keyword in health_keywords:
            if keyword in content_lower:
                importance += 1.0
                break  # 健康类只加一次
        
        for keyword in goal_keywords:
            if keyword in content_lower:
                importance += 0.5
                break  # 目标类只加一次
        
        for keyword in urgent_keywords:
            if keyword in content_lower:
                importance += 1.5
                break  # 紧急类只加一次
        
        # 长度评估
        content_length = len(content.strip())
        if content_length < 5:
            importance -= 1.0
        elif content_length > 200:
            importance -= 0.5
        
        # 检查是否包含数字
        if any(c.isdigit() for c in content):
            importance += 0.3
        
        # 检查日期/时间模式 (简单检查)
        date_patterns = ['年', '月', '日', '号', '周', '星期', '点', '分']
        if any(pattern in content for pattern in date_patterns):
            importance += 0.5
        
        # 限制在 0-10 范围内
        importance = max(0.0, min(10.0, importance))
        
        logger.debug(f"重要性计算 - 内容长度: {content_length}, 评分: {importance:.2f}")
        
        return round(importance, 2)
    
    async def search_memories(
        self, 
        user_id: int, 
        keyword: str,
        memory_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        搜索用户记忆
        
        Args:
            user_id: 用户ID
            keyword: 搜索关键词
            memory_type: 可选，按记忆类型筛选
            limit: 返回记录数量限制
            
        Returns:
            匹配的记忆记录列表
        """
        try:
            search_pattern = f"%{keyword}%"
            
            if memory_type:
                query = """
                    SELECT id, user_id, memory_type, content, importance,
                           created_at, updated_at
                    FROM user_memories
                    WHERE user_id = %s AND memory_type = %s AND content LIKE %s
                    ORDER BY importance DESC, updated_at DESC
                    LIMIT %s
                """
                params = (user_id, memory_type, search_pattern, limit)
            else:
                query = """
                    SELECT id, user_id, memory_type, content, importance,
                           created_at, updated_at
                    FROM user_memories
                    WHERE user_id = %s AND content LIKE %s
                    ORDER BY importance DESC, updated_at DESC
                    LIMIT %s
                """
                params = (user_id, search_pattern, limit)
            
            memories = await db.fetch_all(query, params)
            
            logger.debug(
                f"搜索记忆 - 用户: {user_id}, 关键词: {keyword}, "
                f"找到: {len(memories)} 条"
            )
            
            return memories if memories else []
            
        except Exception as e:
            logger.error(f"搜索记忆失败 - 用户: {user_id}, 错误: {e}")
            return []


# 全局记忆存储实例
memory_store = MemoryStore()


# 便捷函数
def get_memory_store() -> MemoryStore:
    """
    获取记忆存储实例
    
    Returns:
        MemoryStore: 记忆存储实例
    """
    return memory_store
