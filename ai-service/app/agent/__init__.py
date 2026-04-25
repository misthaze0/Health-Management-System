"""
专家智能体模块
提供多领域专家智能体、工作流引擎和意图识别功能
"""

from .base_agent import BaseAgent, Tool
from .expert_agents import (
    NutritionistAgent,
    FitnessCoachAgent,
    PsychologyAgent,
    MedicalAnalystAgent,
    create_nutritionist_agent,
    create_fitness_coach_agent,
    create_psychology_agent,
    create_medical_analyst_agent,
)
from .agent_manager import AgentManager, get_agent_manager, initialize_default_agents
from .workflow_engine import (
    WorkflowEngine,
    WorkflowStep,
    WorkflowDefinition,
    WorkflowExecutionState,
    WorkflowStatus,
    StepStatus,
    get_workflow_engine,
)
from .intent_classifier import (
    Intent,
    IntentResult,
    IntentClassifier,
    get_intent_classifier,
    classify_intent,
)

__all__ = [
    # 基类
    'BaseAgent',
    'Tool',
    # 专家智能体
    'NutritionistAgent',
    'FitnessCoachAgent',
    'PsychologyAgent',
    'MedicalAnalystAgent',
    'create_nutritionist_agent',
    'create_fitness_coach_agent',
    'create_psychology_agent',
    'create_medical_analyst_agent',
    # 智能体管理器
    'AgentManager',
    'get_agent_manager',
    'initialize_default_agents',
    # 工作流引擎
    'WorkflowEngine',
    'WorkflowStep',
    'WorkflowDefinition',
    'WorkflowExecutionState',
    'WorkflowStatus',
    'StepStatus',
    'get_workflow_engine',
    # 意图识别
    'Intent',
    'IntentResult',
    'IntentClassifier',
    'get_intent_classifier',
    'classify_intent',
]
