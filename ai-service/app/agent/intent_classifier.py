"""
意图识别模块
提供用户查询意图分类和槽位提取功能
使用关键词匹配 + LLM分类的混合策略
"""

import re
import json
from enum import Enum
from typing import Tuple, Dict, List, Optional, Any
from dataclasses import dataclass, field
from loguru import logger

from app.services.kimi_service import kimi_service


class Intent(Enum):
    """
    用户意图枚举
    
    定义了健康管理系统中支持的所有用户意图类型
    """
    HEALTH_CONSULT = "health_consult"           # 健康咨询
    REPORT_ANALYSIS = "report_analysis"         # 报告分析
    DIET_PLAN = "diet_plan"                     # 饮食计划
    EXERCISE_PLAN = "exercise_plan"             # 运动计划
    MENTAL_SUPPORT = "mental_support"           # 心理支持
    GENERAL_CHAT = "general_chat"               # 通用对话


@dataclass
class SlotDefinition:
    """槽位定义"""
    name: str                                   # 槽位名称
    description: str                            # 槽位描述
    required: bool = False                      # 是否必需
    examples: List[str] = field(default_factory=list)  # 示例值


@dataclass
class IntentResult:
    """意图识别结果"""
    intent: Intent                              # 识别到的意图
    confidence: float                           # 置信度 (0-1)
    slots: Dict[str, Any] = field(default_factory=dict)  # 提取的槽位
    raw_query: str = ""                         # 原始查询


class IntentClassifier:
    """
    意图分类器
    
    使用关键词匹配 + LLM分类的混合策略进行意图识别
    同时支持槽位信息提取
    """
    
    # 关键词映射表：意图 -> 关键词列表
    INTENT_KEYWORDS = {
        Intent.HEALTH_CONSULT: [
            "健康", "咨询", "病", "症状", "不舒服", "疼", "痛", "难受",
            "医生", "怎么办", "是什么病", "什么原因", "正常吗", "严重吗",
            "检查", "体检", "身体", "感觉", "头晕", "恶心", "发烧", "感冒",
            "血压", "血糖", "血脂", "心脏", "肝", "肾", "胃", "肺",
            "失眠", "疲劳", "乏力", "咳嗽", "腹泻", "便秘", "过敏"
        ],
        Intent.REPORT_ANALYSIS: [
            "报告", "化验单", "检查结果", "体检报告", "分析", "解读",
            "指标", "数值", "参考范围", "异常", "阳性", "阴性",
            "血常规", "尿常规", "肝功能", "肾功能", "心电图", "B超",
            "CT", "核磁", "MRI", "X光", "片子", "单据", "单子上"
        ],
        Intent.DIET_PLAN: [
            "饮食", "吃", "食谱", "营养", "减肥", "增重", "膳食",
            "食物", "菜谱", "吃什么", "不能吃", "忌口", "搭配",
            "热量", "卡路里", "蛋白质", "脂肪", "碳水", "维生素",
            "早餐", "午餐", "晚餐", "加餐", "零食", "水果", "蔬菜",
            "糖尿病饮食", "高血压饮食", "低脂", "低盐", "低糖", "高蛋白"
        ],
        Intent.EXERCISE_PLAN: [
            "运动", "锻炼", "健身", "训练", "活动", "跑步", "游泳",
            "瑜伽", "太极", "走路", "散步", "强度", "频率", "时长",
            "有氧运动", "无氧运动", "力量训练", "拉伸", "热身",
            "减肥运动", "增肌", "塑形", "体能", "耐力", "柔韧",
            "步数", "公里", "卡路里消耗", "心率", "配速"
        ],
        Intent.MENTAL_SUPPORT: [
            "心理", "情绪", "压力", "焦虑", "抑郁", "紧张", "担心",
            "害怕", "恐惧", "烦躁", "易怒", "失眠", "睡不好", "做梦",
            "心情", "开心", "难过", "悲伤", "孤独", "失落", "空虚",
            "工作压力大", "学习压力", "人际关系", "家庭矛盾", "情感",
            "放松", "减压", "冥想", "正念", "心理咨询", "疏导"
        ],
        Intent.GENERAL_CHAT: [
            "你好", "您好", "嗨", "哈喽", "Hello", "Hi",
            "谢谢", "感谢", "再见", "拜拜", "好的", "OK", "嗯",
            "在吗", "在不在", "忙吗", "请问", "打扰了"
        ]
    }
    
    # 槽位定义
    SLOT_DEFINITIONS = {
        Intent.HEALTH_CONSULT: [
            SlotDefinition("disease", "疾病名称", False, ["高血压", "糖尿病", "感冒"]),
            SlotDefinition("symptom", "症状描述", False, ["头痛", "发烧", "咳嗽"]),
            SlotDefinition("body_part", "身体部位", False, ["头部", "胸部", "腹部"]),
            SlotDefinition("duration", "持续时间", False, ["3天", "一周", "一个月"]),
            SlotDefinition("severity", "严重程度", False, ["轻微", "中等", "严重"]),
        ],
        Intent.REPORT_ANALYSIS: [
            SlotDefinition("report_type", "报告类型", False, ["血常规", "尿常规", "肝功能"]),
            SlotDefinition("indicator", "指标名称", False, ["白细胞", "血糖", "血压"]),
            SlotDefinition("value", "检测数值", False, ["120", "6.5", "正常"]),
            SlotDefinition("exam_date", "检查日期", False, ["2024-01-01", "上周"]),
        ],
        Intent.DIET_PLAN: [
            SlotDefinition("goal", "饮食目标", False, ["减肥", "增肌", "控制血糖"]),
            SlotDefinition("diet_type", "饮食类型", False, ["素食", "低碳水", "高蛋白"]),
            SlotDefinition("allergy", "过敏食物", False, ["花生", "海鲜", "牛奶"]),
            SlotDefinition("preference", "口味偏好", False, ["清淡", "辣", "甜"]),
            SlotDefinition("meal", "餐次", False, ["早餐", "午餐", "晚餐"]),
        ],
        Intent.EXERCISE_PLAN: [
            SlotDefinition("goal", "运动目标", False, ["减肥", "增肌", "提高耐力"]),
            SlotDefinition("exercise_type", "运动类型", False, ["跑步", "游泳", "瑜伽"]),
            SlotDefinition("level", "运动水平", False, ["初学者", "中级", "高级"]),
            SlotDefinition("duration", "运动时长", False, ["30分钟", "1小时"]),
            SlotDefinition("frequency", "运动频率", False, ["每天", "每周3次"]),
            SlotDefinition("limitation", "身体限制", False, ["膝盖不好", "腰伤"]),
        ],
        Intent.MENTAL_SUPPORT: [
            SlotDefinition("emotion", "情绪状态", False, ["焦虑", "抑郁", "压力大"]),
            SlotDefinition("cause", "情绪原因", False, ["工作压力", "家庭问题"]),
            SlotDefinition("duration", "持续时间", False, ["最近一周", "一个月"]),
            SlotDefinition("severity", "严重程度", False, ["轻微", "严重"]),
        ],
        Intent.GENERAL_CHAT: [
            SlotDefinition("greeting_type", "问候类型", False, ["打招呼", "道别", "感谢"]),
        ]
    }
    
    def __init__(self):
        """初始化意图分类器"""
        logger.info("意图分类器初始化完成")
    
    def _keyword_match(self, query: str) -> Tuple[Optional[Intent], float]:
        """
        基于关键词匹配的意图识别
        
        Args:
            query: 用户查询文本
            
        Returns:
            Tuple[Optional[Intent], float]: 识别的意图和置信度
        """
        query_lower = query.lower()
        scores = {}
        
        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = 0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword in query_lower:
                    # 根据关键词长度给予不同权重
                    weight = len(keyword) / 10.0 + 0.5
                    score += weight
                    matched_keywords.append(keyword)
            
            if score > 0:
                scores[intent] = {
                    'score': score,
                    'matched': matched_keywords
                }
        
        if not scores:
            return None, 0.0
        
        # 找出得分最高的意图
        best_intent = max(scores.keys(), key=lambda k: scores[k]['score'])
        best_score = scores[best_intent]['score']
        
        # 计算置信度（归一化到0-1范围）
        total_score = sum(s['score'] for s in scores.values())
        confidence = best_score / total_score if total_score > 0 else 0.0
        
        # 根据匹配关键词数量调整置信度
        keyword_count = len(scores[best_intent]['matched'])
        if keyword_count >= 3:
            confidence = min(confidence * 1.2, 0.95)
        elif keyword_count == 1:
            confidence = confidence * 0.8
        
        logger.debug(f"关键词匹配结果: {best_intent.value}, 置信度: {confidence:.2f}, "
                    f"匹配词: {scores[best_intent]['matched']}")
        
        return best_intent, confidence
    
    async def _llm_classify(self, query: str) -> Tuple[Intent, float]:
        """
        使用LLM进行意图分类
        
        Args:
            query: 用户查询文本
            
        Returns:
            Tuple[Intent, float]: 识别的意图和置信度
        """
        system_prompt = """你是一位专业的健康管理系统意图识别专家。
请分析用户的查询，判断其意图属于以下哪一类：

1. health_consult - 健康咨询：用户询问疾病、症状、健康问题等
2. report_analysis - 报告分析：用户上传或询问体检报告、化验单等
3. diet_plan - 饮食计划：用户询问饮食建议、食谱、营养搭配等
4. exercise_plan - 运动计划：用户询问运动建议、健身计划等
5. mental_support - 心理支持：用户表达情绪问题、心理压力等
6. general_chat - 通用对话：日常问候、闲聊等

请严格按照以下JSON格式返回结果：
{
    "intent": "意图代码",
    "confidence": 0.95,
    "reason": "简要说明判断理由"
}

confidence取值范围0-1，表示你对判断的置信程度。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请分析以下查询的意图：\n\n{query}"}
        ]
        
        try:
            response = await kimi_service.chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            
            # 清理可能的markdown代码块
            if content.startswith('```json'):
                content = content[7:]
            elif content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # 解析JSON响应
            result = json.loads(content)
            intent_str = result.get('intent', 'general_chat')
            confidence = float(result.get('confidence', 0.5))
            
            # 将字符串转换为Intent枚举
            intent_map = {i.value: i for i in Intent}
            intent = intent_map.get(intent_str, Intent.GENERAL_CHAT)
            
            logger.debug(f"LLM分类结果: {intent.value}, 置信度: {confidence:.2f}")
            
            return intent, confidence
            
        except Exception as e:
            logger.error(f"LLM分类失败: {str(e)}")
            return Intent.GENERAL_CHAT, 0.3
    
    async def classify_intent(self, query: str) -> Tuple[Intent, float]:
        """
        意图分类主方法
        
        使用关键词匹配 + LLM分类的混合策略
        当关键词匹配置信度足够高时直接返回，否则使用LLM分类
        
        Args:
            query: 用户查询文本
            
        Returns:
            Tuple[Intent, float]: 识别的意图和置信度
        """
        logger.info(f"开始意图分类: {query[:50]}...")
        
        # 第一步：关键词匹配
        keyword_intent, keyword_confidence = self._keyword_match(query)
        
        # 如果关键词匹配置信度很高，直接返回结果
        if keyword_intent and keyword_confidence >= 0.85:
            logger.info(f"关键词匹配高置信度，直接返回: {keyword_intent.value}, "
                       f"置信度: {keyword_confidence:.2f}")
            return keyword_intent, keyword_confidence
        
        # 第二步：LLM分类
        llm_intent, llm_confidence = await self._llm_classify(query)
        
        # 第三步：融合策略
        if keyword_intent is None:
            # 关键词未匹配到，使用LLM结果
            final_intent = llm_intent
            final_confidence = llm_confidence
        elif keyword_intent == llm_intent:
            # 两者一致，提高置信度
            final_intent = keyword_intent
            final_confidence = min((keyword_confidence + llm_confidence) / 2 * 1.1, 0.98)
        else:
            # 两者不一致，根据置信度选择
            if keyword_confidence >= 0.7 and llm_confidence < 0.8:
                # 关键词置信度高，优先使用
                final_intent = keyword_intent
                final_confidence = keyword_confidence
            elif llm_confidence >= 0.85:
                # LLM置信度很高，优先使用
                final_intent = llm_intent
                final_confidence = llm_confidence
            else:
                # 默认使用LLM结果（通常更准确）
                final_intent = llm_intent
                final_confidence = llm_confidence * 0.9
        
        logger.info(f"意图分类完成: {final_intent.value}, 置信度: {final_confidence:.2f}")
        
        return final_intent, final_confidence
    
    def _extract_slots_with_pattern(self, query: str, intent: Intent) -> Dict[str, Any]:
        """
        使用正则表达式提取槽位
        
        Args:
            query: 用户查询文本
            intent: 识别到的意图
            
        Returns:
            Dict[str, Any]: 提取的槽位字典
        """
        slots = {}
        
        # 时间模式
        time_patterns = [
            (r'(\d+)天', 'duration_days'),
            (r'(\d+)周', 'duration_weeks'),
            (r'(\d+)个月', 'duration_months'),
            (r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2})', 'date'),
            (r'(最近|过去|这)(几天|一周|一个月|段时间)', 'recent_time'),
        ]
        
        # 数值模式
        number_patterns = [
            (r'(\d+\.?\d*)\s*(mg|g|kg|ml|l|mmHg|mmol/L|U/L)', 'measurement'),
            (r'(\d+)\s*岁', 'age'),
            (r'(\d+)\s*cm', 'height'),
            (r'(\d+)\s*kg', 'weight'),
        ]
        
        # 提取时间信息
        for pattern, slot_type in time_patterns:
            matches = re.findall(pattern, query)
            if matches:
                if 'time' not in slots:
                    slots['time'] = []
                slots['time'].extend(matches if isinstance(matches[0], str) else [m[0] for m in matches])
        
        # 提取数值信息
        for pattern, slot_type in number_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                slots[slot_type] = matches
        
        # 意图特定的槽位提取
        if intent == Intent.HEALTH_CONSULT:
            # 提取常见疾病名称
            disease_patterns = [
                r'([\u4e00-\u9fa5]{2,6}病)',
                r'([\u4e00-\u9fa5]{2,6}炎)',
                r'([\u4e00-\u9fa5]{2,6}症)',
                r'感冒|发烧|咳嗽|头痛|胃痛|腹泻|便秘|失眠|高血压|糖尿病|高血脂'
            ]
            diseases = []
            for pattern in disease_patterns:
                matches = re.findall(pattern, query)
                diseases.extend(matches)
            if diseases:
                slots['disease'] = list(set(diseases))
            
            # 提取症状
            symptom_keywords = ['疼', '痛', '痒', '肿', '麻', '晕', '恶心', '呕吐', '乏力', '疲劳']
            symptoms = []
            for keyword in symptom_keywords:
                if keyword in query:
                    # 找到关键词前后的上下文
                    idx = query.find(keyword)
                    start = max(0, idx - 5)
                    end = min(len(query), idx + 6)
                    context = query[start:end]
                    symptoms.append(context)
            if symptoms:
                slots['symptom'] = symptoms
        
        elif intent == Intent.DIET_PLAN or intent == Intent.EXERCISE_PLAN:
            # 提取目标
            goal_keywords = ['减肥', '减重', '瘦身', '增重', '增肌', '塑形', '健身', '健康', 
                           '控制血糖', '降血压', '降血脂', '增强体质', '提高耐力']
            goals = [g for g in goal_keywords if g in query]
            if goals:
                slots['goal'] = goals
        
        elif intent == Intent.MENTAL_SUPPORT:
            # 提取情绪状态
            emotion_keywords = ['焦虑', '抑郁', '压力大', '紧张', '担心', '害怕', '烦躁', 
                              '易怒', '失眠', '孤独', '失落', '空虚', '不开心', '难过']
            emotions = [e for e in emotion_keywords if e in query]
            if emotions:
                slots['emotion'] = emotions
        
        return slots
    
    async def _extract_slots_with_llm(self, query: str, intent: Intent) -> Dict[str, Any]:
        """
        使用LLM提取槽位
        
        Args:
            query: 用户查询文本
            intent: 识别到的意图
            
        Returns:
            Dict[str, Any]: 提取的槽位字典
        """
        # 获取该意图的槽位定义
        slot_defs = self.SLOT_DEFINITIONS.get(intent, [])
        
        if not slot_defs:
            return {}
        
        # 构建槽位描述
        slot_descriptions = []
        for slot in slot_defs:
            required_mark = "(必需)" if slot.required else "(可选)"
            examples = f"，例如: {', '.join(slot.examples)}" if slot.examples else ""
            slot_descriptions.append(f"- {slot.name}: {slot.description}{required_mark}{examples}")
        
        system_prompt = f"""你是一位专业的信息提取助手。请从用户的查询中提取以下槽位信息：

意图类型: {intent.value}

需要提取的槽位：
{chr(10).join(slot_descriptions)}

请严格按照以下JSON格式返回结果（只返回JSON，不要其他内容）：
{{
    "slots": {{
        "槽位名1": "提取的值",
        "槽位名2": "提取的值"
    }}
}}

如果某个槽位在查询中未提及，请省略该槽位或设为null。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请从以下查询中提取槽位信息：\n\n{query}"}
        ]
        
        try:
            response = await kimi_service.chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            
            # 清理可能的markdown代码块
            if content.startswith('```json'):
                content = content[7:]
            elif content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # 解析JSON响应
            result = json.loads(content)
            slots = result.get('slots', {})
            
            # 过滤掉null值
            slots = {k: v for k, v in slots.items() if v is not None and v != ""}
            
            logger.debug(f"LLM槽位提取结果: {slots}")
            
            return slots
            
        except Exception as e:
            logger.error(f"LLM槽位提取失败: {str(e)}")
            return {}
    
    async def extract_slots(self, query: str, intent: Intent) -> Dict[str, Any]:
        """
        槽位提取主方法
        
        结合正则表达式和LLM进行槽位提取
        
        Args:
            query: 用户查询文本
            intent: 识别到的意图
            
        Returns:
            Dict[str, Any]: 提取的槽位字典
        """
        logger.info(f"开始槽位提取 - 意图: {intent.value}, 查询: {query[:50]}...")
        
        # 第一步：使用正则表达式提取
        pattern_slots = self._extract_slots_with_pattern(query, intent)
        
        # 第二步：使用LLM提取
        llm_slots = await self._extract_slots_with_llm(query, intent)
        
        # 第三步：合并结果（LLM结果优先）
        merged_slots = {**pattern_slots, **llm_slots}
        
        # 确保槽位值是基本类型或可JSON序列化
        for key, value in merged_slots.items():
            if isinstance(value, (list, tuple)):
                merged_slots[key] = value[0] if len(value) == 1 else list(value)
        
        logger.info(f"槽位提取完成: {merged_slots}")
        
        return merged_slots
    
    async def classify_and_extract(self, query: str) -> IntentResult:
        """
        完整的意图识别和槽位提取流程
        
        Args:
            query: 用户查询文本
            
        Returns:
            IntentResult: 包含意图、置信度和槽位的完整结果
        """
        logger.info(f"开始完整意图识别流程: {query[:50]}...")
        
        # 意图分类
        intent, confidence = await self.classify_intent(query)
        
        # 槽位提取
        slots = await self.extract_slots(query, intent)
        
        result = IntentResult(
            intent=intent,
            confidence=confidence,
            slots=slots,
            raw_query=query
        )
        
        logger.info(f"意图识别流程完成: intent={intent.value}, confidence={confidence:.2f}, "
                   f"slots={list(slots.keys())}")
        
        return result


# 全局意图分类器实例
intent_classifier = IntentClassifier()


# 依赖注入函数
async def get_intent_classifier() -> IntentClassifier:
    """获取意图分类器实例"""
    return intent_classifier


async def classify_intent(query: str) -> tuple:
    """
    便捷函数：分类意图
    
    Args:
        query: 用户查询文本
        
    Returns:
        tuple: (Intent, confidence)
    """
    return await intent_classifier.classify_intent(query)
