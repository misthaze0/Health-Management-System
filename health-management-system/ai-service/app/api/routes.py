"""
API路由定义
"""
from fastapi import APIRouter, HTTPException, Query, Depends, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from loguru import logger
import uuid
import time
import os
import aiofiles

from app.utils.content_validator import content_validator
from app.services.chat_history_service import chat_history_service
from app.core.auth import get_current_user, get_optional_user, require_auth

router = APIRouter()

# 上传文件临时存储目录
UPLOAD_DIR = "/tmp/health_reports"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 延迟加载服务实例
_kimi_service = None

def get_kimi_service():
    """获取Kimi服务实例（延迟初始化）"""
    global _kimi_service
    if _kimi_service is None:
        from app.services.kimi_service import kimi_service
        _kimi_service = kimi_service
    return _kimi_service


# ============== 数据模型定义 ==============

class HealthDataRequest(BaseModel):
    """健康数据分析请求"""
    user_id: str
    health_data: Dict[str, Any]
    analysis_type: str = "general"  # general/risk_assessment


class ChatRequest(BaseModel):
    """对话请求"""
    user_id: Optional[str] = "anonymous"
    question: str
    sessionId: Optional[str] = None
    chat_history: Optional[List[Dict[str, str]]] = None
    enable_web_search: Optional[bool] = False  # 是否启用联网搜索
    save_history: Optional[bool] = True  # 是否保存对话历史


class ChatHistorySaveRequest(BaseModel):
    """保存对话历史请求"""
    user_id: int
    session_id: Optional[str] = None
    question: str
    answer: str
    response_time: Optional[int] = 0


class DeleteHistoryRequest(BaseModel):
    """删除对话历史请求"""
    ids: List[int]
    session_id: Optional[str] = None


class ReportRequest(BaseModel):
    """报告生成请求"""
    user_id: str
    exam_data: Dict[str, Any]
    user_profile: Dict[str, Any]


class RiskAssessmentRequest(BaseModel):
    """风险评估请求"""
    user_id: str
    age: int
    gender: str
    family_history: List[str]  # 家族病史
    lifestyle: Dict[str, Any]  # 生活习惯
    exam_results: Dict[str, Any]  # 体检结果


class MedicalReportAnalysisResult(BaseModel):
    """医疗报告分析结果"""
    report_summary: Dict[str, Any]
    indicators: List[Dict[str, Any]]
    abnormal_findings: List[Dict[str, Any]]
    health_suggestions: List[str]
    follow_up: Dict[str, Any]
    file_id: Optional[str] = None


# ============== API端点定义 ==============

@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "Health Management AI Service",
        "version": "1.0.0"
    }


# 可用模型列表配置
AVAILABLE_MODELS = [
    {
        "id": "moonshot-v1-8k",
        "name": "Kimi K1（8K上下文）",
        "description": "基础版本，适合日常对话和简单任务",
        "context_length": 8192,
        "features": ["联网搜索", "健康咨询"],
        "recommended": False
    },
    {
        "id": "moonshot-v1-32k",
        "name": "Kimi K1（32K上下文）",
        "description": "长文本版本，适合长文档分析",
        "context_length": 32768,
        "features": ["联网搜索", "长文档分析", "健康咨询"],
        "recommended": False
    },
    {
        "id": "moonshot-v1-128k",
        "name": "Kimi K1（128K上下文）",
        "description": "超长文本版本，适合大型报告分析",
        "context_length": 131072,
        "features": ["联网搜索", "超长文档分析", "健康咨询"],
        "recommended": False
    },
    {
        "id": "kimi-k2-turbo-preview",
        "name": "Kimi K2 Turbo",
        "description": "新一代高性能模型，代码和Agent能力更强",
        "context_length": 256000,
        "features": ["联网搜索", "代码编程", "Agent能力", "健康咨询", "复杂推理"],
        "recommended": True
    },
    {
        "id": "kimi-k2-0905-Preview",
        "name": "Kimi K2 Preview",
        "description": "K2预览版，具备强大的Agentic能力",
        "context_length": 256000,
        "features": ["联网搜索", "Agent能力", "工具调用", "复杂任务分解"],
        "recommended": False
    }
]

# 模型名称映射
MODEL_DISPLAY_NAMES = {
    "moonshot-v1-8k": "Kimi K1（8K上下文）",
    "moonshot-v1-32k": "Kimi K1（32K上下文）",
    "moonshot-v1-128k": "Kimi K1（128K上下文）",
    "moonshot-v1-auto": "Kimi K1（自动上下文）",
    "kimi-k2-turbo-preview": "Kimi K2 Turbo",
    "kimi-k2-0905-Preview": "Kimi K2 Preview",
    "kimi-k2-thinking": "Kimi K2 思考版",
    "kimi-k2-thinking-turbo": "Kimi K2 思考版 Turbo"
}


@router.get("/model/info")
async def get_model_info():
    """
    获取当前AI模型信息
    
    返回当前使用的Kimi模型名称和版本信息
    """
    try:
        from app.core.config import settings
        
        model_name = settings.MOONSHOT_MODEL
        display_name = MODEL_DISPLAY_NAMES.get(model_name, model_name)
        
        # 查找当前模型的详细信息
        current_model_detail = None
        for model in AVAILABLE_MODELS:
            if model["id"] == model_name:
                current_model_detail = model
                break
        
        return {
            "code": 200,
            "message": "获取模型信息成功",
            "data": {
                "model": model_name,
                "display_name": display_name,
                "provider": "Moonshot AI",
                "base_url": settings.MOONSHOT_BASE_URL,
                "supports_web_search": True,  # 标记支持联网搜索
                "detail": current_model_detail
            }
        }
    except Exception as e:
        logger.error(f"获取模型信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def get_available_models():
    """
    获取所有可用的AI模型列表
    
    返回支持的Kimi模型列表及其特性
    """
    try:
        from app.core.config import settings
        current_model = settings.MOONSHOT_MODEL
        
        return {
            "code": 200,
            "message": "获取模型列表成功",
            "data": {
                "models": AVAILABLE_MODELS,
                "current_model": current_model,
                "total": len(AVAILABLE_MODELS)
            }
        }
    except Exception as e:
        logger.error(f"获取模型列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


class ModelSwitchRequest(BaseModel):
    """模型切换请求"""
    model_id: str


# 内存中存储用户模型偏好（仅当前会话有效）
user_model_preferences = {}


@router.post("/model/switch")
async def switch_model(
    request: ModelSwitchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    切换当前使用的AI模型
    
    - **model_id**: 要切换的模型ID
    - **需要JWT认证**
    
    模型偏好保存在内存中，仅当前服务运行期间有效
    """
    try:
        user_id = current_user["user_id"]
        model_id = request.model_id
        
        # 验证模型ID是否有效
        valid_model_ids = [model["id"] for model in AVAILABLE_MODELS]
        if model_id not in valid_model_ids:
            raise HTTPException(
                status_code=400, 
                detail=f"无效的模型ID: {model_id}。可用模型: {', '.join(valid_model_ids)}"
            )
        
        # 获取模型显示名称
        display_name = MODEL_DISPLAY_NAMES.get(model_id, model_id)
        
        # 保存到内存中
        user_model_preferences[user_id] = model_id
        
        logger.info(f"用户 {user_id} 切换模型到: {display_name}")
        
        return {
            "code": 200,
            "message": "模型切换成功",
            "data": {
                "model_id": model_id,
                "display_name": display_name,
                "note": "模型偏好已保存（仅当前会话有效）"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"切换模型失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model/preference")
async def get_user_model_preference(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    获取用户的模型偏好
    
    - **需要JWT认证**
    
    返回用户保存的模型偏好，如果没有则返回默认模型
    """
    try:
        user_id = current_user["user_id"]
        from app.core.config import settings
        
        # 从内存中获取用户偏好
        preferred_model = user_model_preferences.get(user_id)
        
        # 如果没有偏好，使用默认模型
        model_id = preferred_model or settings.MOONSHOT_MODEL
        display_name = MODEL_DISPLAY_NAMES.get(model_id, model_id)
        
        # 查找模型详情
        model_detail = None
        for model in AVAILABLE_MODELS:
            if model["id"] == model_id:
                model_detail = model
                break
        
        return {
            "code": 200,
            "message": "获取模型偏好成功",
            "data": {
                "model_id": model_id,
                "display_name": display_name,
                "is_user_preference": preferred_model is not None,
                "detail": model_detail
            }
        }
    except Exception as e:
        logger.error(f"获取模型偏好失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/health")
async def analyze_health_data(request: HealthDataRequest):
    """
    分析健康数据
    
    - **analysis_type**: 分析类型 (general/blood_sugar/risk_assessment)
    """
    try:
        logger.info(f"分析健康数据 - 用户: {request.user_id}, 类型: {request.analysis_type}")
        service = get_kimi_service()
        result = await service.analyze_health_data(
            request.health_data,
            request.analysis_type
        )
        return {
            "code": 200,
            "message": "分析成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"健康数据分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def chat_with_ai(
    request: ChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    流式AI对话 - 支持联网搜索功能和自动保存历史
    
    - **enable_web_search**: 是否启用联网搜索，默认为false
    - **save_history**: 是否保存对话历史，默认为true
    - **需要JWT认证**: 必须在请求头中提供Authorization: Bearer <token>
    """
    import asyncio
    
    # 从JWT获取用户ID
    user_id = current_user["user_id"]
    
    # 生成会话ID
    session_id = request.sessionId or str(uuid.uuid4())
    
    logger.info(f"流式AI对话 - 用户: {user_id}, 会话: {session_id}, 问题: {request.question[:50]}...")
    logger.info(f"联网搜索: {'开启' if request.enable_web_search else '关闭'}")
    logger.info(f"保存历史: {'是' if request.save_history else '否'}")
    
    # 验证用户输入内容是否属于健康相关话题
    is_valid, message = content_validator.validate(request.question)
    
    # 如果验证不通过，直接返回拒绝信息
    if not is_valid:
        logger.warning(f"内容验证失败 - 用户: {user_id}, 原因: {message[:50]}...")
        
        # 保存拒绝记录（可选）
        if request.save_history and user_id > 0:
            try:
                await chat_history_service.save_chat_history_batch(
                    user_id=user_id,
                    session_id=session_id,
                    user_message=request.question,
                    ai_message=message,
                    response_time=0
                )
            except Exception as e:
                logger.error(f"保存拒绝记录失败: {e}")
        
        async def reject_stream():
            """返回拒绝信息的流"""
            yield f"data: {message}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            reject_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    # 构建系统提示词，添加强化的健康领域限制
    system_prompt = """你是一位专业的AI健康管理师，专注于为用户提供健康、养生、医疗方面的专业建议。

【核心职责】
1. 回答疾病症状、诊断、治疗相关问题
2. 提供健康饮食、营养搭配建议
3. 指导科学运动、健身方法
4. 解读体检报告、化验单
5. 慢病管理（糖尿病、高血压等）
6. 中医养生、调理建议
7. 心理健康、情绪管理

【严格限制】
- 只能回答健康、医疗、养生、营养、运动、心理相关话题
- 对于非健康问题（如天气、娱乐、政治、金融、技术等），必须礼貌拒绝并引导用户咨询健康问题
- 不提供医疗诊断，只提供健康建议，严重情况建议就医
- 紧急医疗情况必须建议立即拨打急救电话或前往急诊

【回复风格】
- 专业、友善、耐心
- 使用通俗易懂的语言解释医学概念
- 必要时提供具体的 actionable 建议"""
    
    # 如果是边缘话题，在系统提示词中加强限制
    if message == "边缘话题":
        system_prompt += "\n\n【特别提醒】用户的问题可能涉及非健康领域，请严格限制回答范围，只提供与健康相关的信息，或礼貌地引导用户提出健康问题。"
    
    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    # 从数据库加载历史对话
    if request.chat_history:
        # 使用前端传入的历史记录
        MAX_HISTORY_ROUNDS = 10
        valid_history = [h for h in request.chat_history if h.get('content')]
        trimmed_history = valid_history[-MAX_HISTORY_ROUNDS * 2:]
        messages.extend(trimmed_history)
        logger.info(f"使用前端传入的历史: {len(trimmed_history)} 条消息")
    elif request.save_history and user_id > 0:
        # 从数据库加载历史对话
        try:
            history_messages = await chat_history_service.get_session_messages(user_id, session_id, limit=10)
            messages.extend(history_messages)
            logger.info(f"从数据库加载历史: {len(history_messages)} 条消息")
        except Exception as e:
            logger.error(f"加载历史对话失败: {e}")
    
    messages.append({"role": "user", "content": request.question})
    
    # 记录开始时间
    start_time = time.time()
    
    # 用于收集完整回复
    full_response = []
    
    # 使用队列来缓冲数据
    queue = asyncio.Queue()
    
    # 获取用户模型偏好（从内存中）
    user_preferred_model = user_model_preferences.get(user_id)
    if user_preferred_model:
        logger.info(f"用户 {user_id} 使用偏好模型: {user_preferred_model}")

    async def producer():
        """生产者：从Kimi API获取数据并放入队列"""
        try:
            chunk_count = 0
            service = get_kimi_service()
            # 根据是否启用联网搜索选择不同的调用方式
            if request.enable_web_search:
                # 使用支持工具调用的流式对话
                async for chunk in service.chat_stream_with_tools(
                    messages,
                    enable_web_search=True,
                    model=user_preferred_model
                ):
                    chunk_count += 1
                    await queue.put(chunk)
            else:
                # 使用普通流式对话
                async for chunk in service.chat_stream(messages, model=user_preferred_model):
                    chunk_count += 1
                    await queue.put(chunk)
            await queue.put("[DONE]")  # 结束标记
            logger.info(f"Stream producer completed, total chunks: {chunk_count}")
        except Exception as e:
            logger.error(f"Producer error: {e}")
            await queue.put(f"[ERROR]: {str(e)}")
    
    async def consumer():
        """消费者：从队列取出数据并yield，同时收集完整回复"""
        nonlocal full_response
        
        # 启动生产者
        producer_task = asyncio.create_task(producer())
        
        try:
            while True:
                # 等待数据，设置超时防止永久阻塞
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=60.0)
                except asyncio.TimeoutError:
                    logger.warning("Stream timeout")
                    break
                
                if data == "[DONE]":
                    yield "data: [DONE]\n\n"
                    break
                elif isinstance(data, str) and data.startswith("[ERROR]"):
                    yield f"data: {data}\n\n"
                    break
                else:
                    full_response.append(data)
                    yield f"data: {data}\n\n"
        finally:
            # 确保生产者任务被取消
            if not producer_task.done():
                producer_task.cancel()
                try:
                    await producer_task
                except asyncio.CancelledError:
                    pass
    
    # 保存对话历史的回调
    async def save_history_after_stream():
        """流结束后保存对话历史，并计算token使用量"""
        if request.save_history and user_id > 0:
            try:
                response_time = int((time.time() - start_time) * 1000)
                ai_response = "".join(full_response)
                
                # 计算token使用量
                service = get_kimi_service()
                # 构建完整的对话消息用于计算token
                token_messages = messages.copy()
                token_messages.append({"role": "assistant", "content": ai_response})
                tokens_used = await service.estimate_tokens(token_messages)
                
                await chat_history_service.save_chat_history_batch(
                    user_id=user_id,
                    session_id=session_id,
                    user_message=request.question,
                    ai_message=ai_response,
                    response_time=response_time,
                    tokens_used=tokens_used
                )
                logger.info(f"对话历史已保存 - user_id: {user_id}, session_id: {session_id}, tokens: {tokens_used}")
            except Exception as e:
                logger.error(f"保存对话历史失败: {e}")
    
    # 包装consumer以添加保存历史的逻辑
    async def consumer_with_save():
        async for chunk in consumer():
            yield chunk
        # 流结束后保存历史
        await save_history_after_stream()
    
    return StreamingResponse(
        consumer_with_save(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Session-Id": session_id
        }
    )


@router.post("/report/generate")
async def generate_report(request: ReportRequest):
    """
    生成体检报告解读
    """
    try:
        logger.info(f"生成报告解读 - 用户: {request.user_id}")
        service = get_kimi_service()
        report = await service.generate_health_report(
            request.exam_data,
            request.user_profile
        )
        return {
            "code": 200,
            "message": "报告生成成功",
            "data": {
                "report": report,
                "user_id": request.user_id
            }
        }
    except Exception as e:
        logger.error(f"报告生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/risk/assess")
async def assess_health_risk(request: RiskAssessmentRequest):
    """
    健康风险评估
    
    评估用户患各种疾病的风险
    """
    try:
        logger.info(f"风险评估 - 用户: {request.user_id}")
        
        risk_data = {
            "age": request.age,
            "gender": request.gender,
            "family_history": request.family_history,
            "lifestyle": request.lifestyle,
            "exam_results": request.exam_results
        }
        
        service = get_kimi_service()
        result = await service.analyze_health_data(
            risk_data,
            "risk_assessment"
        )
        
        return {
            "code": 200,
            "message": "风险评估完成",
            "data": result
        }
    except Exception as e:
        logger.error(f"风险评估失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== 对话历史管理API ==============

@router.get("/history")
async def get_chat_history(
    limit: int = Query(50, ge=1, le=100, description="限制条数"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    获取用户的对话历史
    
    - **limit**: 限制条数，默认50
    - **需要JWT认证**
    """
    try:
        user_id = current_user["user_id"]
        logger.info(f"获取对话历史 - 用户: {user_id}, 限制: {limit}")
        history = await chat_history_service.get_chat_history(user_id, limit)
        return {
            "code": 200,
            "message": "获取成功",
            "data": [h.dict() for h in history]
        }
    except Exception as e:
        logger.error(f"获取对话历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_session_history(
    session_id: str,
    limit: int = Query(50, ge=1, le=100, description="限制条数"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    获取指定会话的对话历史
    
    - **session_id**: 会话ID
    - **limit**: 限制条数，默认50
    - **需要JWT认证**
    """
    try:
        user_id = current_user["user_id"]
        logger.info(f"获取会话历史 - 用户: {user_id}, 会话: {session_id}, 限制: {limit}")
        history = await chat_history_service.get_chat_history_by_session(user_id, session_id, limit)
        return {
            "code": 200,
            "message": "获取成功",
            "data": [h.dict() for h in history]
        }
    except Exception as e:
        logger.error(f"获取会话历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/save")
async def save_chat_history(
    request: ChatHistorySaveRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    保存对话历史
    
    用于前端直接调用AI服务后，手动保存对话记录
    - **需要JWT认证**
    """
    try:
        user_id = current_user["user_id"]
        session_id = request.session_id or str(uuid.uuid4())
        logger.info(f"保存对话历史 - 用户: {user_id}, 会话: {session_id}")
        
        user_id_db, ai_id_db = await chat_history_service.save_chat_history_batch(
            user_id=user_id,
            session_id=session_id,
            user_message=request.question,
            ai_message=request.answer,
            response_time=request.response_time
        )
        
        return {
            "code": 200,
            "message": "保存成功",
            "data": {
                "session_id": session_id,
                "user_message_id": user_id_db,
                "ai_message_id": ai_id_db
            }
        }
    except Exception as e:
        logger.error(f"保存对话历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/{record_id}")
async def delete_chat_history_by_id(
    record_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    删除单条对话记录
    
    - **record_id**: 记录ID
    - **需要JWT认证**
    """
    try:
        user_id = current_user["user_id"]
        logger.info(f"删除对话记录 - 用户: {user_id}, 记录: {record_id}")
        success = await chat_history_service.delete_chat_history_by_id(user_id, record_id)
        
        if success:
            return {
                "code": 200,
                "message": "删除成功"
            }
        else:
            return {
                "code": 404,
                "message": "记录不存在"
            }
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"删除对话记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/history/delete")
async def delete_chat_history_batch(
    request: DeleteHistoryRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    批量删除对话记录
    
    - **ids**: 记录ID列表
    - **需要JWT认证**
    """
    try:
        user_id = current_user["user_id"]
        logger.info(f"批量删除对话记录 - 用户: {user_id}, 记录数: {len(request.ids)}")
        deleted_count = await chat_history_service.delete_chat_history_batch(user_id, request.ids)
        
        return {
            "code": 200,
            "message": "删除成功",
            "data": {
                "deleted_count": deleted_count
            }
        }
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"批量删除对话记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/clear")
async def clear_all_chat_history(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    清空用户的所有对话历史
    
    - **需要JWT认证**
    """
    try:
        user_id = current_user["user_id"]
        logger.info(f"清空对话历史 - 用户: {user_id}")
        deleted_count = await chat_history_service.clear_all_chat_history(user_id)
        
        return {
            "code": 200,
            "message": "清空成功",
            "data": {
                "deleted_count": deleted_count
            }
        }
    except Exception as e:
        logger.error(f"清空对话历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 用于替代的端点 - 使用POST方法（避免某些浏览器的DELETE请求问题）
@router.post("/history/clear-all")
async def clear_all_chat_history_post(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    清空用户的所有对话历史（POST方法版本）
    
    - **需要JWT认证**
    """
    try:
        user_id = current_user["user_id"]
        logger.info(f"[POST] 清空对话历史 - 用户: {user_id}")
        deleted_count = await chat_history_service.clear_all_chat_history(user_id)
        
        return {
            "code": 200,
            "message": "清空成功",
            "data": {
                "deleted_count": deleted_count
            }
        }
    except Exception as e:
        logger.error(f"[POST] 清空对话历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def get_user_sessions(
    limit: int = Query(20, ge=1, le=50, description="限制条数"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    获取用户的会话列表
    
    - **limit**: 限制条数，默认20
    - **需要JWT认证**
    """
    try:
        user_id = current_user["user_id"]
        logger.info(f"获取用户会话列表 - 用户: {user_id}, 限制: {limit}")
        sessions = await chat_history_service.get_user_sessions(user_id, limit)
        return {
            "code": 200,
            "message": "获取成功",
            "data": sessions
        }
    except Exception as e:
        logger.error(f"获取用户会话列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== 医疗报告文件分析 API ==============

@router.post("/report/analyze-file")
async def analyze_medical_report_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    report_type: str = Query("general", description="报告类型: general/blood_test/imaging/physical_exam"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    上传并分析医疗报告文件

    使用 Kimi API 上传文件并进行智能分析，返回结构化的分析报告

    - **file**: PDF 或图片格式的体检报告文件
    - **report_type**: 报告类型
    - **需要JWT认证**

    返回格式：
    ```json
    {
        "code": 200,
        "message": "分析成功",
        "data": {
            "report_summary": {
                "report_type": "体检报告",
                "exam_date": "2024-01-15",
                "exam_center": "XX医院",
                "overall_assessment": "总体健康状况良好"
            },
            "indicators": [...],
            "abnormal_findings": [...],
            "health_suggestions": [...],
            "follow_up": {...}
        }
    }
    ```
    """
    try:
        user_id = current_user["user_id"]
        logger.info(f"医疗报告文件分析 - 用户: {user_id}, 文件: {file.filename}, 类型: {report_type}")

        # 验证文件类型
        allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff'}
        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file_ext}。支持的格式: {', '.join(allowed_extensions)}"
            )

        # 保存上传的文件
        file_id = str(uuid.uuid4())
        temp_file_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_ext}")

        async with aiofiles.open(temp_file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        logger.info(f"文件已保存: {temp_file_path}")

        # 调用 Kimi 服务分析文件
        service = get_kimi_service()
        analysis_result = await service.analyze_medical_report(temp_file_path, report_type)

        # 后台删除临时文件
        background_tasks.add_task(os.remove, temp_file_path)

        return {
            "code": 200,
            "message": "分析成功",
            "data": analysis_result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"医疗报告分析失败: {str(e)}")
        # 清理临时文件
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/report/analysis-template")
async def get_analysis_template():
    """
    获取医疗报告分析的标准输出模板

    返回分析结果的JSON结构模板，供前端参考
    """
    template = {
        "report_summary": {
            "report_type": "体检报告",
            "exam_date": "2024-01-15",
            "exam_center": "XX医院体检中心",
            "overall_assessment": "总体健康状况良好，部分指标需要关注"
        },
        "indicators": [
            {
                "name": "血压",
                "value": "120/80",
                "unit": "mmHg",
                "reference_range": "90-140/60-90",
                "status": "normal",
                "interpretation": "血压正常，维持在理想范围内"
            },
            {
                "name": "空腹血糖",
                "value": "6.2",
                "unit": "mmol/L",
                "reference_range": "3.9-6.1",
                "status": "warning",
                "interpretation": "血糖略高，建议控制饮食并定期监测"
            }
        ],
        "abnormal_findings": [
            {
                "indicator": "空腹血糖",
                "severity": "medium",
                "description": "血糖值6.2 mmol/L，略高于正常范围上限6.1 mmol/L",
                "recommendation": "建议减少精制糖摄入，增加运动，3个月后复查"
            }
        ],
        "health_suggestions": [
            "保持规律作息，每天保证7-8小时睡眠",
            "控制饮食，减少高糖高脂食物摄入",
            "每周进行至少150分钟中等强度运动",
            "定期监测血糖变化"
        ],
        "follow_up": {
            "recommended_items": ["空腹血糖", "糖化血红蛋白"],
            "recommended_departments": ["内分泌科"],
            "urgency_level": "medium"
        }
    }

    return {
        "code": 200,
        "message": "获取成功",
        "data": template
    }


