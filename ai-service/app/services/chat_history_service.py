"""
对话历史服务
管理AI对话记录的增删改查
"""
from typing import List, Optional
from datetime import datetime
from app.db.database import db
from app.db.models import AiChatHistory
from loguru import logger


class ChatHistoryService:
    """对话历史服务类"""
    
    async def save_chat_history(
        self,
        user_id: int,
        session_id: str,
        message_role: int,
        message_content: str,
        tokens_used: Optional[int] = None,
        response_time: Optional[int] = None
    ) -> int:
        """
        保存对话历史记录
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            message_role: 角色 1-用户, 2-AI
            message_content: 消息内容
            tokens_used: 使用的token数
            response_time: 响应时间(ms)
            
        Returns:
            插入的记录ID
        """
        query = """
            INSERT INTO ai_chat_history 
            (user_id, session_id, message_role, message_content, tokens_used, response_time, create_time)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """
        
        try:
            await db.execute(query, (
                user_id, session_id, message_role, message_content, 
                tokens_used, response_time
            ))
            
            # 获取刚插入记录的ID
            result = await db.fetch_one(
                "SELECT LAST_INSERT_ID() as id"
            )
            record_id = result['id'] if result else 0
            
            logger.info(f"对话历史已保存 - user_id: {user_id}, session_id: {session_id}, role: {message_role}")
            return record_id
            
        except Exception as e:
            logger.error(f"保存对话历史失败: {e}")
            raise
    
    async def save_chat_history_batch(
        self,
        user_id: int,
        session_id: str,
        user_message: str,
        ai_message: str,
        response_time: Optional[int] = None,
        tokens_used: Optional[int] = None
    ) -> tuple:
        """
        批量保存一轮对话（用户消息+AI回复）
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            user_message: 用户消息
            ai_message: AI回复
            response_time: 响应时间
            tokens_used: 使用的token数
            
        Returns:
            (用户消息ID, AI消息ID)
        """
        try:
            # 保存用户消息
            user_id_db = await self.save_chat_history(
                user_id=user_id,
                session_id=session_id,
                message_role=1,  # 用户
                message_content=user_message,
                response_time=0,
                tokens_used=None  # 用户消息不单独计算token
            )
            
            # 保存AI回复（记录总token使用量）
            ai_id_db = await self.save_chat_history(
                user_id=user_id,
                session_id=session_id,
                message_role=2,  # AI
                message_content=ai_message,
                response_time=response_time,
                tokens_used=tokens_used  # 记录本轮对话的总token数
            )
            
            logger.info(f"批量保存对话完成 - user_id: {user_id}, session_id: {session_id}, tokens: {tokens_used}")
            return (user_id_db, ai_id_db)
            
        except Exception as e:
            logger.error(f"批量保存对话失败: {e}")
            raise
    
    async def get_chat_history(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[AiChatHistory]:
        """
        获取用户的对话历史
        
        Args:
            user_id: 用户ID
            limit: 限制条数
            
        Returns:
            对话历史列表（按时间升序排列，时间早的在前面）
        """
        # 使用子查询先获取最新的limit条，然后再按升序排列
        query = """
            SELECT * FROM (
                SELECT * FROM ai_chat_history 
                WHERE user_id = %s 
                ORDER BY create_time DESC 
                LIMIT %s
            ) AS recent_history
            ORDER BY create_time ASC
        """
        
        try:
            rows = await db.fetch_all(query, (user_id, limit))
            return [AiChatHistory(**row) for row in rows]
        except Exception as e:
            logger.error(f"获取对话历史失败: {e}")
            raise
    
    async def get_chat_history_by_session(
        self,
        user_id: int,
        session_id: str,
        limit: int = 50
    ) -> List[AiChatHistory]:
        """
        获取指定会话的对话历史
        
        Args:
            user_id: 用户ID（用于权限验证）
            session_id: 会话ID
            limit: 限制条数
            
        Returns:
            对话历史列表
        """
        query = """
            SELECT * FROM ai_chat_history 
            WHERE session_id = %s AND user_id = %s
            ORDER BY create_time ASC 
            LIMIT %s
        """
        
        try:
            rows = await db.fetch_all(query, (session_id, user_id, limit))
            return [AiChatHistory(**row) for row in rows]
        except Exception as e:
            logger.error(f"获取会话历史失败: {e}")
            raise
    
    async def get_session_messages(
        self,
        user_id: int,
        session_id: str,
        limit: int = 20
    ) -> List[dict]:
        """
        获取会话的messages格式历史（用于AI对话上下文）
        
        Args:
            user_id: 用户ID（用于权限验证）
            session_id: 会话ID
            limit: 限制轮数（用户+AI算一轮）
            
        Returns:
            messages格式列表 [{"role": "user"/"assistant", "content": "..."}]
        """
        # 首先验证该会话是否属于该用户
        verify_query = """
            SELECT COUNT(*) as count FROM ai_chat_history 
            WHERE session_id = %s AND user_id = %s 
            LIMIT 1
        """
        
        try:
            result = await db.fetch_one(verify_query, (session_id, user_id))
            if not result or result['count'] == 0:
                logger.warning(f"会话不存在或不属于该用户 - user_id: {user_id}, session_id: {session_id}")
                return []  # 返回空列表，表示没有权限或会话不存在
            
            # 获取最近limit*2条消息（用户+AI）
            query = """
                SELECT message_role, message_content 
                FROM ai_chat_history 
                WHERE session_id = %s AND user_id = %s
                ORDER BY create_time DESC 
                LIMIT %s
            """
            
            rows = await db.fetch_all(query, (session_id, user_id, limit * 2))
            
            # 转换为messages格式并反转顺序（按时间正序）
            messages = []
            for row in reversed(rows):
                role = "user" if row['message_role'] == 1 else "assistant"
                messages.append({
                    "role": role,
                    "content": row['message_content']
                })
            
            return messages
            
        except Exception as e:
            logger.error(f"获取会话messages失败: {e}")
            raise
    
    async def delete_chat_history_by_id(
        self,
        user_id: int,
        record_id: int
    ) -> bool:
        """
        删除单条对话记录
        
        Args:
            user_id: 用户ID（用于权限验证）
            record_id: 记录ID
            
        Returns:
            是否删除成功
        """
        # 先验证记录是否属于该用户
        check_query = """
            SELECT user_id FROM ai_chat_history WHERE id = %s
        """
        
        try:
            record = await db.fetch_one(check_query, (record_id,))
            
            if not record:
                logger.warning(f"记录不存在 - id: {record_id}")
                return False
            
            if record['user_id'] != user_id:
                logger.error(f"无权删除记录 - user_id: {user_id}, record_id: {record_id}")
                raise PermissionError("无权删除该对话记录")
            
            # 删除记录
            delete_query = "DELETE FROM ai_chat_history WHERE id = %s"
            await db.execute(delete_query, (record_id,))
            
            logger.info(f"对话记录已删除 - user_id: {user_id}, record_id: {record_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除对话记录失败: {e}")
            raise
    
    async def delete_chat_history_batch(
        self,
        user_id: int,
        record_ids: List[int]
    ) -> int:
        """
        批量删除对话记录
        
        Args:
            user_id: 用户ID
            record_ids: 记录ID列表
            
        Returns:
            删除的记录数
        """
        if not record_ids:
            return 0
        
        # 验证所有记录是否属于该用户
        placeholders = ','.join(['%s'] * len(record_ids))
        check_query = f"""
            SELECT id, user_id FROM ai_chat_history 
            WHERE id IN ({placeholders})
        """
        
        try:
            records = await db.fetch_all(check_query, tuple(record_ids))
            
            valid_ids = []
            for record in records:
                if record['user_id'] != user_id:
                    logger.error(f"无权删除记录 - user_id: {user_id}, record_id: {record['id']}")
                    raise PermissionError("无权删除部分对话记录")
                valid_ids.append(record['id'])
            
            if not valid_ids:
                return 0
            
            # 批量删除
            placeholders = ','.join(['%s'] * len(valid_ids))
            delete_query = f"DELETE FROM ai_chat_history WHERE id IN ({placeholders})"
            
            deleted_count = await db.execute(delete_query, tuple(valid_ids))
            
            logger.info(f"批量删除完成 - user_id: {user_id}, 删除: {deleted_count} 条")
            return deleted_count
            
        except Exception as e:
            logger.error(f"批量删除对话记录失败: {e}")
            raise
    
    async def clear_all_chat_history(self, user_id: int) -> int:
        """
        清空用户的所有对话历史
        
        Args:
            user_id: 用户ID
            
        Returns:
            删除的记录数
        """
        query = "DELETE FROM ai_chat_history WHERE user_id = %s"
        
        try:
            deleted_count = await db.execute(query, (user_id,))
            logger.info(f"用户对话历史已清空 - user_id: {user_id}, 删除: {deleted_count} 条")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清空对话历史失败: {e}")
            raise
    
    async def get_user_sessions(self, user_id: int, limit: int = 20) -> List[dict]:
        """
        获取用户的会话列表
        
        Args:
            user_id: 用户ID
            limit: 限制条数
            
        Returns:
            会话列表，包含会话ID、标题、最后消息时间
        """
        query = """
            SELECT 
                session_id,
                MAX(create_time) as last_time,
                COUNT(*) as message_count
            FROM ai_chat_history 
            WHERE user_id = %s AND session_id IS NOT NULL
            GROUP BY session_id
            ORDER BY last_time DESC
            LIMIT %s
        """
        
        try:
            rows = await db.fetch_all(query, (user_id, limit))
            sessions = []
            for row in rows:
                # 获取会话的第一条用户消息作为标题
                title_query = """
                    SELECT message_content 
                    FROM ai_chat_history 
                    WHERE session_id = %s AND message_role = 1
                    ORDER BY create_time ASC
                    LIMIT 1
                """
                title_result = await db.fetch_one(title_query, (row['session_id'],))
                title = title_result['message_content'] if title_result else '新对话'
                # 限制标题长度
                if len(title) > 20:
                    title = title[:20] + '...'
                
                sessions.append({
                    'id': row['session_id'],
                    'title': title,
                    'lastTime': row['last_time'],
                    'messageCount': row['message_count']
                })
            return sessions
        except Exception as e:
            logger.error(f"获取用户会话列表失败: {e}")
            raise


# 全局服务实例
chat_history_service = ChatHistoryService()
