"""
Health Management AI Service - 主入口
基于Kimi的健康管理AI服务
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.routes import router
from loguru import logger
import sys


# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
logger.add(
    settings.LOG_FILE,
    rotation="10 MB",
    retention="30 days",
    level=settings.LOG_LEVEL
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时执行
    logger.info("=" * 50)
    logger.info(f"{settings.APP_NAME} 启动中...")
    logger.info(f"版本: {settings.APP_VERSION}")
    logger.info(f"调试模式: {settings.DEBUG}")
    logger.info("=" * 50)
    
    # 初始化数据库连接
    try:
        from app.db.database import db
        await db.connect()
        logger.info("数据库连接初始化成功")
    except Exception as e:
        logger.error(f"数据库连接初始化失败: {e}")
        logger.warning("服务将继续运行，但数据库功能不可用")
    
    yield
    
    # 关闭时执行
    logger.info("应用正在关闭...")
    
    # 关闭数据库连接
    try:
        from app.db.database import db
        await db.disconnect()
        logger.info("数据库连接已关闭")
    except Exception as e:
        logger.error(f"关闭数据库连接失败: {e}")


# 自定义Swagger UI参数，添加中文支持
swagger_ui_parameters = {
    "deepLinking": True,
    "displayRequestDuration": True,
    "docExpansion": "list",
    "filter": True,
    "operationsSorter": "alpha",
    "showExtensions": True,
    "showCommonExtensions": True,
    "tryItOutEnabled": True,
    "supportedSubmitMethods": ["get", "put", "post", "delete", "options", "head", "patch", "trace"],
    "validatorUrl": None,
    # 中文本地化配置
    "urls.primaryName": "API文档",
    "layout": "BaseLayout",
    "persistAuthorization": True,
}

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description="基于Kimi AI技术的健康管理服务",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_parameters=swagger_ui_parameters,
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Session-Id"],  # 暴露自定义响应头
)

# 注册路由
app.include_router(router, prefix="/api/v1", tags=["AI服务"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
