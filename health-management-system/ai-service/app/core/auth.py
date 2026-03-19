"""
JWT认证模块
与Java后端使用相同的JWT密钥和算法，确保Token互通
"""
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger

from app.core.config import settings

# JWT配置 - 需要与Java后端保持一致
JWT_SECRET = "your-secret-key-here-change-in-production"  # 与application.yml中的jwt.secret一致
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 1  # 默认1天

# 安全方案
security = HTTPBearer(auto_error=False)


class JWTUtil:
    """JWT工具类 - 与Java后端JwtUtil对应"""
    
    @staticmethod
    def validate_token(token: str) -> bool:
        """
        验证JWT Token是否有效
        
        Args:
            token: JWT Token字符串
            
        Returns:
            bool: 是否有效
        """
        try:
            jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return True
        except jwt.ExpiredSignatureError:
            logger.warning("Token已过期")
            return False
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token无效: {e}")
            return False
        except Exception as e:
            logger.error(f"Token验证异常: {e}")
            return False
    
    @staticmethod
    def get_user_id_from_token(token: str) -> Optional[int]:
        """
        从Token中获取用户ID
        
        Args:
            token: JWT Token字符串
            
        Returns:
            int: 用户ID，如果无效则返回None
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            # Java端使用subject存储userId
            user_id = payload.get("sub")
            if user_id:
                return int(user_id)
            return None
        except Exception as e:
            logger.error(f"解析Token失败: {e}")
            return None
    
    @staticmethod
    def get_username_from_token(token: str) -> Optional[str]:
        """
        从Token中获取用户名
        
        Args:
            token: JWT Token字符串
            
        Returns:
            str: 用户名，如果无效则返回None
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload.get("username")
        except Exception as e:
            logger.error(f"解析Token失败: {e}")
            return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    获取当前登录用户
    
    Args:
        credentials: HTTP认证凭证
        
    Returns:
        dict: 包含user_id和username的字典
        
    Raises:
        HTTPException: 未认证或认证失败时抛出401错误
    """
    # 如果没有提供认证信息
    if not credentials:
        logger.warning("请求缺少Authorization头")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # 验证Token
    if not JWTUtil.validate_token(token):
        logger.warning("Token验证失败")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录已过期，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 获取用户信息
    user_id = JWTUtil.get_user_id_from_token(token)
    username = JWTUtil.get_username_from_token(token)
    
    if not user_id:
        logger.warning("无法从Token中获取用户ID")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录已过期，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"用户认证成功: user_id={user_id}, username={username}")
    
    return {
        "user_id": user_id,
        "username": username,
        "token": token
    }


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    可选的当前用户获取（用于某些接口允许匿名访问）
    
    Args:
        credentials: HTTP认证凭证
        
    Returns:
        dict或None: 用户信息，如果未认证则返回None
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    
    if not JWTUtil.validate_token(token):
        return None
    
    user_id = JWTUtil.get_user_id_from_token(token)
    username = JWTUtil.get_username_from_token(token)
    
    if not user_id:
        return None
    
    return {
        "user_id": user_id,
        "username": username,
        "token": token
    }


# 便捷依赖
require_auth = Depends(get_current_user)
optional_auth = Depends(get_optional_user)
