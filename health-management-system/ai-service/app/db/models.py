"""
数据库模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class AiChatHistory(BaseModel):
    """AI对话历史记录模型"""
    id: Optional[int] = None
    user_id: int
    session_id: Optional[str] = None
    message_role: int  # 1-用户, 2-AI
    message_content: str
    tokens_used: Optional[int] = None
    response_time: Optional[int] = None
    create_time: Optional[datetime] = None


class PhysicalExamReport(BaseModel):
    """体检报告模型"""
    id: Optional[int] = None
    user_id: int
    exam_date: datetime
    hospital: Optional[str] = None
    overall_result: Optional[str] = None
    ai_analysis: Optional[str] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None


class ExamIndicator(BaseModel):
    """体检指标模型"""
    id: Optional[int] = None
    report_id: int
    indicator_name: str
    indicator_value: str
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    status: Optional[str] = None  # normal/abnormal/critical
    create_time: Optional[datetime] = None


class HealthArticle(BaseModel):
    """健康知识文章模型"""
    id: Optional[int] = None
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    tag: Optional[str] = None
    tag_type: Optional[str] = None
    icon: Optional[str] = None
    gradient: Optional[str] = None
    image_url: Optional[str] = None
    views: int = 0
    is_carousel: int = 0
    carousel_order: int = 0
    status: int = 1
    created_by: Optional[int] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None


class UserModelPreference(BaseModel):
    """用户AI模型偏好设置"""
    id: Optional[int] = None
    user_id: int
    model_id: str  # 模型ID，如 "kimi-k2-turbo-preview"
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
