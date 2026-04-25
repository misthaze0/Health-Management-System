"""
专家智能体系统初始化脚本
用于验证环境、创建Milvus集合、初始化知识库
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger


async def check_milvus_available():
    """检查Milvus是否可用"""
    try:
        from app.core.config import settings
        from pymilvus import connections, utility
        
        # 尝试连接
        connections.connect(host=settings.MILVUS_HOST, port=settings.MILVUS_PORT, timeout=5)
        collections = utility.list_collections()
        return True, collections
    except Exception as e:
        return False, str(e)


async def init_milvus():
    """初始化Milvus集合"""
    from app.core.config import settings
    
    logger.info("正在检查Milvus连接...")
    logger.info(f"Milvus地址: {settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
    
    # 先检查Milvus是否可用
    is_available, info = await check_milvus_available()
    
    if not is_available:
        logger.warning("⚠️ 无法连接到Milvus服务器")
        logger.warning(f"   错误信息: {info}")
        logger.warning("   请确保:")
        logger.warning("   1. Docker Desktop已启动")
        logger.warning("   2. Milvus容器正在运行")
        logger.warning("   3. 端口19530未被占用")
        logger.warning("")
        logger.info("💡 提示: 初始化脚本可以继续运行，但知识库功能将不可用")
        logger.info("   你可以在启动Milvus后重新运行此脚本")
        return False
    
    logger.info(f"✅ Milvus连接成功")
    logger.info(f"   现有集合: {info}")
    
    try:
        from app.rag import init_milvus as do_init_milvus
        
        # 初始化默认集合
        logger.info(f"正在初始化集合: {settings.MILVUS_COLLECTION}")
        do_init_milvus()
        
        logger.info("✅ Milvus初始化完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ Milvus初始化失败: {e}")
        return False


async def init_knowledge_base():
    """初始化知识库"""
    try:
        from app.rag import get_knowledge_base
        
        logger.info("正在初始化知识库...")
        kb = get_knowledge_base()
        
        # 添加示例知识
        sample_docs = [
            {
                "title": "高血压饮食指南",
                "content": "高血压患者应控制钠盐摄入，每日不超过6克。增加钾的摄入，多吃新鲜蔬菜水果。限制饮酒，男性每日酒精摄入不超过25克，女性不超过15克。建议采用DASH饮食模式，多摄入全谷物、低脂乳制品、鱼类和坚果。",
                "category": "nutrition"
            },
            {
                "title": "糖尿病患者运动建议",
                "content": "糖尿病患者建议每周至少150分钟中等强度有氧运动，如快走、游泳、骑车。运动前后监测血糖，避免低血糖发生。运动时间建议在餐后1-2小时进行，避免空腹运动。",
                "category": "exercise"
            },
            {
                "title": "心理健康自评",
                "content": "心理健康包括情绪稳定、睡眠良好、人际关系和谐等方面。如出现持续情绪低落、失眠、焦虑等症状超过两周，建议寻求专业帮助。保持规律作息、适度运动、社交活动有助于心理健康。",
                "category": "mental"
            },
            {
                "title": "体检报告解读-血脂",
                "content": "血脂四项包括总胆固醇(TC)、甘油三酯(TG)、高密度脂蛋白胆固醇(HDL-C)、低密度脂蛋白胆固醇(LDL-C)。LDL-C过高是心血管疾病的主要危险因素。正常参考值：TC < 5.2 mmol/L，TG < 1.7 mmol/L，HDL-C > 1.0 mmol/L，LDL-C < 3.4 mmol/L。",
                "category": "medical"
            },
            {
                "title": "健康体重管理",
                "content": "BMI（身体质量指数）= 体重(kg) / 身高²(m²)。正常范围为18.5-23.9。减重应遵循循序渐进原则，每周减重0.5-1公斤为宜。合理控制总热量摄入，增加体力活动是减重的基本原则。",
                "category": "general"
            }
        ]
        
        added_count = 0
        for doc in sample_docs:
            try:
                result = kb.add_document(
                    title=doc["title"],
                    content=doc["content"],
                    category=doc["category"],
                    source="系统初始化"
                )
                if result:
                    added_count += 1
                    logger.info(f"✅ 已添加知识: {doc['title']}")
            except Exception as e:
                logger.warning(f"添加知识失败 {doc['title']}: {e}")
        
        logger.info(f"✅ 知识库初始化完成，共添加 {added_count} 条知识")
        return True
        
    except Exception as e:
        logger.error(f"❌ 知识库初始化失败: {e}")
        return False


async def test_embedding():
    """测试嵌入服务"""
    try:
        from app.rag import get_embedding_service
        
        logger.info("正在测试嵌入服务...")
        embedding_service = get_embedding_service()
        
        # 测试向量化
        test_text = "这是一段测试文本"
        vector = embedding_service.encode(test_text)
        
        if vector and len(vector) > 0:
            logger.info(f"✅ 嵌入服务测试成功，向量维度: {len(vector)}")
            return True
        else:
            logger.error("❌ 嵌入服务返回空向量")
            return False
            
    except Exception as e:
        logger.error(f"❌ 嵌入服务测试失败: {e}")
        return False


async def test_agent_system():
    """测试智能体系统"""
    try:
        from app.agent import get_agent_manager
        
        logger.info("正在测试智能体系统...")
        agent_manager = get_agent_manager()
        
        # 列出所有智能体
        agents = agent_manager.list_agents()
        logger.info(f"✅ 发现 {len(agents)} 个智能体:")
        for agent in agents:
            logger.info(f"  - {agent['type']}: {agent['name']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 智能体系统测试失败: {e}")
        return False


async def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("专家智能体系统初始化")
    logger.info("=" * 60)
    
    results = []
    
    # 1. 测试嵌入服务
    logger.info("\n[1/4] 测试嵌入服务...")
    results.append(("嵌入服务", await test_embedding()))
    
    # 2. 初始化Milvus
    logger.info("\n[2/4] 初始化Milvus...")
    milvus_ok = await init_milvus()
    results.append(("Milvus", milvus_ok))
    
    # 3. 初始化知识库（仅在Milvus可用时）
    logger.info("\n[3/4] 初始化知识库...")
    if milvus_ok:
        results.append(("知识库", await init_knowledge_base()))
    else:
        logger.warning("⏭️ 跳过知识库初始化（Milvus不可用）")
        results.append(("知识库", False))
    
    # 4. 测试智能体系统
    logger.info("\n[4/4] 测试智能体系统...")
    results.append(("智能体系统", await test_agent_system()))
    
    # 汇总结果
    logger.info("\n" + "=" * 60)
    logger.info("初始化结果汇总")
    logger.info("=" * 60)
    
    for name, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        logger.info(f"{name}: {status}")
    
    # 判断核心组件是否成功
    core_success = results[0][1] and results[3][1]  # 嵌入服务和智能体系统
    
    if core_success:
        logger.info("\n🎉 核心组件初始化成功！")
        if not milvus_ok:
            logger.info("💡 提示: Milvus未连接，知识库功能不可用")
            logger.info("   启动Milvus后重新运行脚本可启用知识库功能")
        return 0
    else:
        logger.warning("\n⚠️ 部分核心组件初始化失败，请检查日志")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
