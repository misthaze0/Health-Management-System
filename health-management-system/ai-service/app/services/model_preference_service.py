"""
用户模型偏好服务
管理用户的AI模型偏好设置
"""
from typing import Optional
from datetime import datetime
from loguru import logger

from app.db.database import db
from app.db.models import UserModelPreference


class ModelPreferenceService:
    """模型偏好服务类"""

    async def get_user_model_preference(self, user_id: int) -> Optional[str]:
        """
        获取用户的模型偏好

        Args:
            user_id: 用户ID

        Returns:
            模型ID，如果没有设置则返回None
        """
        try:
            query = """
                SELECT model_id FROM user_model_preference
                WHERE user_id = %s
                ORDER BY update_time DESC
                LIMIT 1
            """
            result = await db.fetchone(query, (user_id,))

            if result:
                logger.info(f"获取用户 {user_id} 的模型偏好: {result['model_id']}")
                return result['model_id']

            logger.info(f"用户 {user_id} 未设置模型偏好")
            return None

        except Exception as e:
            logger.error(f"获取用户模型偏好失败: {e}")
            return None

    async def save_user_model_preference(self, user_id: int, model_id: str) -> bool:
        """
        保存用户的模型偏好

        Args:
            user_id: 用户ID
            model_id: 模型ID

        Returns:
            是否保存成功
        """
        try:
            # 检查是否已存在记录
            check_query = """
                SELECT id FROM user_model_preference
                WHERE user_id = %s
            """
            existing = await db.fetchone(check_query, (user_id,))

            if existing:
                # 更新现有记录
                update_query = """
                    UPDATE user_model_preference
                    SET model_id = %s, update_time = %s
                    WHERE user_id = %s
                """
                await db.execute(update_query, (model_id, datetime.now(), user_id))
                logger.info(f"更新用户 {user_id} 的模型偏好为: {model_id}")
            else:
                # 插入新记录
                insert_query = """
                    INSERT INTO user_model_preference (user_id, model_id, create_time, update_time)
                    VALUES (%s, %s, %s, %s)
                """
                await db.execute(insert_query, (user_id, model_id, datetime.now(), datetime.now()))
                logger.info(f"创建用户 {user_id} 的模型偏好: {model_id}")

            return True

        except Exception as e:
            logger.error(f"保存用户模型偏好失败: {e}")
            return False

    async def delete_user_model_preference(self, user_id: int) -> bool:
        """
        删除用户的模型偏好

        Args:
            user_id: 用户ID

        Returns:
            是否删除成功
        """
        try:
            query = """
                DELETE FROM user_model_preference
                WHERE user_id = %s
            """
            await db.execute(query, (user_id,))
            logger.info(f"删除用户 {user_id} 的模型偏好")
            return True

        except Exception as e:
            logger.error(f"删除用户模型偏好失败: {e}")
            return False


# 全局服务实例
model_preference_service = ModelPreferenceService()
