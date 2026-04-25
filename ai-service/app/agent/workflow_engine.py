"""
工作流引擎模块
实现AI对话工作流的定义、执行、状态管理和控制
"""

import json
import uuid
import asyncio
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Awaitable
from dataclasses import dataclass, field, asdict
from loguru import logger

from app.db.database import db


# =============================================================================
# 工作流状态枚举
# =============================================================================

class WorkflowStatus(str, Enum):
    """工作流执行状态"""
    PENDING = "pending"           # 待执行
    RUNNING = "running"           # 执行中
    PAUSED = "paused"             # 已暂停
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 执行失败
    CANCELLED = "cancelled"       # 已取消


class StepStatus(str, Enum):
    """工作流步骤执行状态"""
    PENDING = "pending"           # 待执行
    RUNNING = "running"           # 执行中
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 执行失败
    SKIPPED = "skipped"           # 已跳过


# =============================================================================
# 工作流步骤数据类
# =============================================================================

@dataclass
class WorkflowStep:
    """
    工作流步骤定义
    
    Attributes:
        step_id: 步骤唯一标识
        name: 步骤名称
        description: 步骤描述
        step_type: 步骤类型 (llm_call, tool_call, condition, wait, parallel)
        config: 步骤配置参数
        dependencies: 依赖的步骤ID列表
        retry_count: 失败重试次数
        timeout: 步骤超时时间(秒)
        condition: 执行条件表达式
    """
    step_id: str
    name: str
    description: str = ""
    step_type: str = "llm_call"  # llm_call, tool_call, condition, wait, parallel
    config: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 3
    timeout: int = 300
    condition: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowStep':
        """从字典创建实例"""
        return cls(**data)


# =============================================================================
# 工作流定义数据类
# =============================================================================

@dataclass
class WorkflowDefinition:
    """
    工作流定义
    
    Attributes:
        workflow_id: 工作流唯一标识
        name: 工作流名称
        description: 工作流描述
        steps: 工作流步骤列表
        version: 版本号
        created_at: 创建时间
        updated_at: 更新时间
    """
    workflow_id: str
    name: str
    description: str = ""
    steps: List[WorkflowStep] = field(default_factory=list)
    version: str = "1.0"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "steps": [step.to_dict() for step in self.steps],
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowDefinition':
        """从字典创建实例"""
        steps = [WorkflowStep.from_dict(s) for s in data.get("steps", [])]
        return cls(
            workflow_id=data["workflow_id"],
            name=data["name"],
            description=data.get("description", ""),
            steps=steps,
            version=data.get("version", "1.0"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
        )


# =============================================================================
# 工作流执行状态数据类
# =============================================================================

@dataclass
class WorkflowExecutionState:
    """
    工作流执行状态
    
    Attributes:
        execution_id: 执行实例唯一标识
        workflow_id: 工作流定义ID
        user_id: 用户ID
        session_id: 会话ID
        status: 当前状态
        context: 执行上下文数据
        step_states: 各步骤执行状态
        current_step_id: 当前执行步骤ID
        started_at: 开始时间
        completed_at: 完成时间
        error_message: 错误信息
    """
    execution_id: str
    workflow_id: str
    user_id: int
    session_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    context: Dict[str, Any] = field(default_factory=dict)
    step_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    current_step_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "status": self.status.value,
            "context": self.context,
            "step_states": self.step_states,
            "current_step_id": self.current_step_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowExecutionState':
        """从字典创建实例"""
        return cls(
            execution_id=data["execution_id"],
            workflow_id=data["workflow_id"],
            user_id=data["user_id"],
            session_id=data["session_id"],
            status=WorkflowStatus(data.get("status", "pending")),
            context=data.get("context", {}),
            step_states=data.get("step_states", {}),
            current_step_id=data.get("current_step_id"),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            error_message=data.get("error_message")
        )


# =============================================================================
# 工作流引擎核心类
# =============================================================================

class WorkflowEngine:
    """
    工作流引擎
    
    负责工作流的定义、执行、状态管理和控制
    """
    
    def __init__(self):
        # 内存中的工作流定义缓存
        self._workflows: Dict[str, WorkflowDefinition] = {}
        # 内存中的执行状态缓存
        self._executions: Dict[str, WorkflowExecutionState] = {}
        # 步骤执行处理器映射
        self._step_handlers: Dict[str, Callable[[WorkflowStep, Dict], Awaitable[Dict]]] = {}
        # 初始化预定义工作流
        self._init_predefined_workflows()
        # 注册默认步骤处理器
        self._register_default_handlers()
        logger.info("工作流引擎初始化完成")
    
    def _init_predefined_workflows(self):
        """初始化预定义工作流"""
        # 健康咨询工作流
        self._workflows["health_consultation"] = self._create_health_consultation_workflow()
        # 报告分析工作流
        self._workflows["report_analysis"] = self._create_report_analysis_workflow()
        # 计划制定工作流
        self._workflows["plan_creation"] = self._create_plan_creation_workflow()
        logger.info("预定义工作流初始化完成")
    
    def _register_default_handlers(self):
        """注册默认的步骤执行处理器"""
        self._step_handlers["llm_call"] = self._handle_llm_call
        self._step_handlers["tool_call"] = self._handle_tool_call
        self._step_handlers["condition"] = self._handle_condition
        self._step_handlers["wait"] = self._handle_wait
        self._step_handlers["parallel"] = self._handle_parallel
        logger.info("默认步骤处理器注册完成")
    
    # =========================================================================
    # 工作流定义管理
    # =========================================================================
    
    def create_workflow(self, name: str, steps: List[WorkflowStep], 
                       description: str = "", version: str = "1.0") -> str:
        """
        创建工作流定义
        
        Args:
            name: 工作流名称
            steps: 工作流步骤列表
            description: 工作流描述
            version: 版本号
            
        Returns:
            workflow_id: 工作流唯一标识
        """
        workflow_id = str(uuid.uuid4())
        now = datetime.now()
        
        workflow = WorkflowDefinition(
            workflow_id=workflow_id,
            name=name,
            description=description,
            steps=steps,
            version=version,
            created_at=now,
            updated_at=now
        )
        
        self._workflows[workflow_id] = workflow
        logger.info(f"工作流创建成功: {workflow_id} - {name}")
        return workflow_id
    
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """
        获取工作流定义
        
        Args:
            workflow_id: 工作流ID
            
        Returns:
            WorkflowDefinition: 工作流定义，不存在则返回None
        """
        return self._workflows.get(workflow_id)
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """
        列出所有工作流定义
        
        Returns:
            List[Dict]: 工作流定义列表
        """
        return [wf.to_dict() for wf in self._workflows.values()]
    
    def update_workflow(self, workflow_id: str, **kwargs) -> bool:
        """
        更新工作流定义
        
        Args:
            workflow_id: 工作流ID
            **kwargs: 要更新的字段
            
        Returns:
            bool: 是否更新成功
        """
        if workflow_id not in self._workflows:
            logger.warning(f"工作流不存在: {workflow_id}")
            return False
        
        workflow = self._workflows[workflow_id]
        for key, value in kwargs.items():
            if hasattr(workflow, key):
                setattr(workflow, key, value)
        
        workflow.updated_at = datetime.now()
        logger.info(f"工作流更新成功: {workflow_id}")
        return True
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """
        删除工作流定义
        
        Args:
            workflow_id: 工作流ID
            
        Returns:
            bool: 是否删除成功
        """
        if workflow_id not in self._workflows:
            logger.warning(f"工作流不存在: {workflow_id}")
            return False
        
        del self._workflows[workflow_id]
        logger.info(f"工作流删除成功: {workflow_id}")
        return True
    
    # =========================================================================
    # 工作流执行控制
    # =========================================================================
    
    async def execute_workflow(self, workflow_id: str, user_id: int, 
                              context: Dict[str, Any] = None,
                              session_id: str = None) -> str:
        """
        执行工作流
        
        Args:
            workflow_id: 工作流ID
            user_id: 用户ID
            context: 执行上下文数据
            session_id: 会话ID，不传则自动生成
            
        Returns:
            execution_id: 执行实例ID
        """
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"工作流不存在: {workflow_id}")
        
        execution_id = str(uuid.uuid4())
        session_id = session_id or str(uuid.uuid4())
        
        # 创建执行状态
        execution = WorkflowExecutionState(
            execution_id=execution_id,
            workflow_id=workflow_id,
            user_id=user_id,
            session_id=session_id,
            status=WorkflowStatus.RUNNING,
            context=context or {},
            started_at=datetime.now()
        )
        
        # 初始化步骤状态
        for step in workflow.steps:
            execution.step_states[step.step_id] = {
                "status": StepStatus.PENDING.value,
                "started_at": None,
                "completed_at": None,
                "result": None,
                "error": None,
                "retry_count": 0
            }
        
        self._executions[execution_id] = execution
        
        # 异步执行工作流
        asyncio.create_task(self._run_workflow(execution_id))
        
        logger.info(f"工作流开始执行: execution_id={execution_id}, workflow_id={workflow_id}, user_id={user_id}")
        return execution_id
    
    async def _run_workflow(self, execution_id: str):
        """
        运行工作流（内部方法）
        
        Args:
            execution_id: 执行实例ID
        """
        execution = self._executions.get(execution_id)
        if not execution:
            logger.error(f"执行实例不存在: {execution_id}")
            return
        
        workflow = self.get_workflow(execution.workflow_id)
        if not workflow:
            execution.status = WorkflowStatus.FAILED
            execution.error_message = f"工作流定义不存在: {execution.workflow_id}"
            await self._save_execution_state(execution)
            return
        
        try:
            # 按依赖顺序执行步骤
            executed_steps = set()
            pending_steps = [s.step_id for s in workflow.steps]
            
            while pending_steps:
                # 检查是否被取消或暂停
                if execution.status == WorkflowStatus.CANCELLED:
                    logger.info(f"工作流已取消: {execution_id}")
                    return
                
                if execution.status == WorkflowStatus.PAUSED:
                    logger.info(f"工作流已暂停，等待恢复: {execution_id}")
                    await asyncio.sleep(1)
                    continue
                
                # 找到可以执行的步骤（依赖已满足）
                executable_steps = []
                for step in workflow.steps:
                    if step.step_id in pending_steps:
                        deps_satisfied = all(d in executed_steps for d in step.dependencies)
                        if deps_satisfied:
                            executable_steps.append(step)
                
                if not executable_steps:
                    if pending_steps:
                        raise Exception(f"存在循环依赖或无法执行的步骤: {pending_steps}")
                    break
                
                # 执行步骤
                for step in executable_steps:
                    execution.current_step_id = step.step_id
                    await self._execute_step(execution, step)
                    executed_steps.add(step.step_id)
                    pending_steps.remove(step.step_id)
            
            # 检查是否所有步骤都成功完成
            all_completed = all(
                execution.step_states[s.step_id]["status"] == StepStatus.COMPLETED.value
                for s in workflow.steps
            )
            
            if all_completed:
                execution.status = WorkflowStatus.COMPLETED
                execution.completed_at = datetime.now()
                logger.info(f"工作流执行完成: {execution_id}")
            else:
                execution.status = WorkflowStatus.FAILED
                execution.error_message = "部分步骤执行失败"
                logger.error(f"工作流执行失败: {execution_id}")
        
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            logger.error(f"工作流执行异常: {execution_id}, error={e}")
        
        finally:
            execution.completed_at = execution.completed_at or datetime.now()
            await self._save_execution_state(execution)
    
    async def _execute_step(self, execution: WorkflowExecutionState, step: WorkflowStep):
        """
        执行单个步骤
        
        Args:
            execution: 执行状态
            step: 工作流步骤
        """
        step_state = execution.step_states[step.step_id]
        step_state["status"] = StepStatus.RUNNING.value
        step_state["started_at"] = datetime.now().isoformat()
        
        logger.info(f"开始执行步骤: {execution.execution_id} - {step.step_id}")
        
        try:
            # 检查执行条件
            if step.condition and not self._evaluate_condition(step.condition, execution.context):
                step_state["status"] = StepStatus.SKIPPED.value
                step_state["completed_at"] = datetime.now().isoformat()
                logger.info(f"步骤跳过（条件不满足）: {step.step_id}")
                return
            
            # 获取步骤处理器
            handler = self._step_handlers.get(step.step_type)
            if not handler:
                raise ValueError(f"未知的步骤类型: {step.step_type}")
            
            # 执行步骤（带重试）
            retry_count = 0
            last_error = None
            
            while retry_count <= step.retry_count:
                try:
                    result = await asyncio.wait_for(
                        handler(step, execution.context),
                        timeout=step.timeout
                    )
                    step_state["result"] = result
                    step_state["status"] = StepStatus.COMPLETED.value
                    step_state["completed_at"] = datetime.now().isoformat()
                    
                    # 更新上下文
                    execution.context[f"step_{step.step_id}_result"] = result
                    
                    logger.info(f"步骤执行成功: {step.step_id}")
                    return
                
                except asyncio.TimeoutError:
                    last_error = "步骤执行超时"
                    retry_count += 1
                    logger.warning(f"步骤超时，准备重试: {step.step_id}, retry={retry_count}")
                
                except Exception as e:
                    last_error = str(e)
                    retry_count += 1
                    logger.warning(f"步骤执行失败，准备重试: {step.step_id}, error={e}, retry={retry_count}")
                    
                    if retry_count <= step.retry_count:
                        await asyncio.sleep(2 ** retry_count)  # 指数退避
            
            # 重试耗尽
            step_state["status"] = StepStatus.FAILED.value
            step_state["error"] = last_error
            step_state["completed_at"] = datetime.now().isoformat()
            raise Exception(f"步骤执行失败（重试{step.retry_count}次）: {last_error}")
        
        except Exception as e:
            step_state["status"] = StepStatus.FAILED.value
            step_state["error"] = str(e)
            step_state["completed_at"] = datetime.now().isoformat()
            logger.error(f"步骤执行失败: {step.step_id}, error={e}")
            raise
    
    def _evaluate_condition(self, condition: str, context: Dict) -> bool:
        """
        评估条件表达式
        
        Args:
            condition: 条件表达式字符串
            context: 执行上下文
            
        Returns:
            bool: 条件是否满足
        """
        try:
            # 简单条件评估，实际项目中可能需要更复杂的表达式引擎
            # 支持格式: "context.key == value" 或 "context.key exists"
            if "==" in condition:
                key, value = condition.split("==", 1)
                key = key.strip().replace("context.", "")
                value = value.strip().strip('"\'')
                return str(context.get(key, "")) == value
            elif "exists" in condition:
                key = condition.replace("exists", "").strip().replace("context.", "")
                return key in context and context[key] is not None
            return True
        except Exception as e:
            logger.warning(f"条件评估失败: {condition}, error={e}")
            return True
    
    # =========================================================================
    # 步骤执行处理器
    # =========================================================================
    
    async def _handle_llm_call(self, step: WorkflowStep, context: Dict) -> Dict:
        """处理LLM调用步骤"""
        from app.services.kimi_service import kimi_service
        
        prompt = step.config.get("prompt", "")
        model = step.config.get("model", "kimi-k2-turbo-preview")
        
        # 替换上下文变量
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            if placeholder in prompt:
                prompt = prompt.replace(placeholder, str(value))
        
        response = await kimi_service.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model=model
        )
        
        return {
            "response": response.get("content", ""),
            "tokens_used": response.get("tokens_used", 0),
            "model": model
        }
    
    async def _handle_tool_call(self, step: WorkflowStep, context: Dict) -> Dict:
        """处理工具调用步骤"""
        tool_name = step.config.get("tool_name")
        tool_params = step.config.get("params", {})
        
        # 替换上下文变量
        for key, value in context.items():
            for param_key, param_value in tool_params.items():
                placeholder = f"{{{key}}}"
                if isinstance(param_value, str) and placeholder in param_value:
                    tool_params[param_key] = param_value.replace(placeholder, str(value))
        
        # 根据工具名称调用相应功能
        if tool_name == "retrieve_memory":
            from app.memory.memory_retriever import memory_retriever
            memories = await memory_retriever.retrieve(
                user_id=context.get("user_id"),
                query=tool_params.get("query", ""),
                limit=tool_params.get("limit", 5)
            )
            return {"memories": memories}
        
        elif tool_name == "store_memory":
            from app.memory.memory_store import memory_store
            await memory_store.store(
                user_id=context.get("user_id"),
                content=tool_params.get("content", ""),
                metadata=tool_params.get("metadata", {})
            )
            return {"stored": True}
        
        elif tool_name == "generate_document":
            from app.multimodal.document_generator import document_generator
            doc_path = await document_generator.generate(
                content=tool_params.get("content", ""),
                doc_type=tool_params.get("doc_type", "pdf"),
                template=tool_params.get("template")
            )
            return {"document_path": doc_path}
        
        else:
            return {"tool_name": tool_name, "params": tool_params, "result": "unknown_tool"}
    
    async def _handle_condition(self, step: WorkflowStep, context: Dict) -> Dict:
        """处理条件判断步骤"""
        condition = step.config.get("condition", "")
        true_branch = step.config.get("true_branch")
        false_branch = step.config.get("false_branch")
        
        result = self._evaluate_condition(condition, context)
        
        return {
            "condition": condition,
            "result": result,
            "next_branch": true_branch if result else false_branch
        }
    
    async def _handle_wait(self, step: WorkflowStep, context: Dict) -> Dict:
        """处理等待步骤"""
        wait_time = step.config.get("wait_time", 1)
        wait_for_input = step.config.get("wait_for_input", False)
        
        if wait_for_input:
            # 等待用户输入，实际实现可能需要更复杂的机制
            return {"status": "waiting_for_input", "message": "等待用户输入"}
        else:
            await asyncio.sleep(wait_time)
            return {"waited": wait_time}
    
    async def _handle_parallel(self, step: WorkflowStep, context: Dict) -> Dict:
        """处理并行执行步骤"""
        sub_steps = step.config.get("sub_steps", [])
        
        async def run_sub_step(sub_step_config):
            sub_step = WorkflowStep.from_dict(sub_step_config)
            handler = self._step_handlers.get(sub_step.step_type)
            if handler:
                return await handler(sub_step, context)
            return {"error": "unknown_step_type"}
        
        results = await asyncio.gather(
            *[run_sub_step(s) for s in sub_steps],
            return_exceptions=True
        )
        
        return {
            "parallel_results": [
                {"success": not isinstance(r, Exception), "result": str(r) if isinstance(r, Exception) else r}
                for r in results
            ]
        }
    
    # =========================================================================
    # 工作流状态管理
    # =========================================================================
    
    async def get_workflow_state(self, user_id: int, session_id: str) -> Optional[Dict]:
        """
        获取工作流状态
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            
        Returns:
            Dict: 工作流执行状态，不存在则返回None
        """
        # 先从内存查找
        for execution in self._executions.values():
            if execution.user_id == user_id and execution.session_id == session_id:
                return execution.to_dict()
        
        # 从数据库查找
        try:
            query = """
                SELECT * FROM workflow_executions 
                WHERE user_id = %s AND session_id = %s 
                ORDER BY started_at DESC LIMIT 1
            """
            result = await db.fetch_one(query, (user_id, session_id))
            
            if result:
                state_data = json.loads(result.get("state_data", "{}"))
                return state_data
        
        except Exception as e:
            logger.error(f"从数据库获取工作流状态失败: {e}")
        
        return None
    
    async def get_execution(self, execution_id: str) -> Optional[Dict]:
        """
        获取执行实例详情
        
        Args:
            execution_id: 执行实例ID
            
        Returns:
            Dict: 执行实例详情
        """
        execution = self._executions.get(execution_id)
        if execution:
            return execution.to_dict()
        
        # 从数据库查找
        try:
            query = "SELECT * FROM workflow_executions WHERE execution_id = %s"
            result = await db.fetch_one(query, (execution_id,))
            
            if result:
                state_data = json.loads(result.get("state_data", "{}"))
                return state_data
        
        except Exception as e:
            logger.error(f"从数据库获取执行实例失败: {e}")
        
        return None
    
    async def pause_workflow(self, execution_id: str) -> bool:
        """
        暂停工作流执行
        
        Args:
            execution_id: 执行实例ID
            
        Returns:
            bool: 是否暂停成功
        """
        execution = self._executions.get(execution_id)
        if not execution:
            logger.warning(f"执行实例不存在: {execution_id}")
            return False
        
        if execution.status != WorkflowStatus.RUNNING:
            logger.warning(f"工作流不在运行状态，无法暂停: {execution_id}, status={execution.status}")
            return False
        
        execution.status = WorkflowStatus.PAUSED
        await self._save_execution_state(execution)
        
        logger.info(f"工作流已暂停: {execution_id}")
        return True
    
    async def resume_workflow(self, execution_id: str) -> bool:
        """
        恢复工作流执行
        
        Args:
            execution_id: 执行实例ID
            
        Returns:
            bool: 是否恢复成功
        """
        execution = self._executions.get(execution_id)
        if not execution:
            logger.warning(f"执行实例不存在: {execution_id}")
            return False
        
        if execution.status != WorkflowStatus.PAUSED:
            logger.warning(f"工作流不在暂停状态，无法恢复: {execution_id}, status={execution.status}")
            return False
        
        execution.status = WorkflowStatus.RUNNING
        await self._save_execution_state(execution)
        
        logger.info(f"工作流已恢复: {execution_id}")
        return True
    
    async def cancel_workflow(self, execution_id: str) -> bool:
        """
        取消工作流执行
        
        Args:
            execution_id: 执行实例ID
            
        Returns:
            bool: 是否取消成功
        """
        execution = self._executions.get(execution_id)
        if not execution:
            logger.warning(f"执行实例不存在: {execution_id}")
            return False
        
        if execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.CANCELLED]:
            logger.warning(f"工作流已结束，无法取消: {execution_id}, status={execution.status}")
            return False
        
        execution.status = WorkflowStatus.CANCELLED
        execution.completed_at = datetime.now()
        await self._save_execution_state(execution)
        
        logger.info(f"工作流已取消: {execution_id}")
        return True
    
    async def _save_execution_state(self, execution: WorkflowExecutionState):
        """
        保存执行状态到数据库
        
        Args:
            execution: 执行状态实例
        """
        try:
            # 检查表是否存在，不存在则创建
            await self._ensure_tables_exist()
            
            query = """
                INSERT INTO workflow_executions 
                (execution_id, workflow_id, user_id, session_id, status, 
                 state_data, started_at, completed_at, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                ON DUPLICATE KEY UPDATE
                status = VALUES(status),
                state_data = VALUES(state_data),
                completed_at = VALUES(completed_at),
                updated_at = NOW()
            """
            
            await db.execute(query, (
                execution.execution_id,
                execution.workflow_id,
                execution.user_id,
                execution.session_id,
                execution.status.value,
                json.dumps(execution.to_dict(), ensure_ascii=False, default=str),
                execution.started_at,
                execution.completed_at
            ))
        
        except Exception as e:
            logger.error(f"保存执行状态失败: {e}")
    
    async def _ensure_tables_exist(self):
        """确保数据库表存在"""
        try:
            # 工作流执行记录表
            create_executions_table = """
                CREATE TABLE IF NOT EXISTS workflow_executions (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    execution_id VARCHAR(64) UNIQUE NOT NULL,
                    workflow_id VARCHAR(64) NOT NULL,
                    user_id INT NOT NULL,
                    session_id VARCHAR(64) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    state_data JSON,
                    started_at DATETIME,
                    completed_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_user_session (user_id, session_id),
                    INDEX idx_workflow (workflow_id),
                    INDEX idx_status (status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            await db.execute(create_executions_table)
            
            # 工作流定义表
            create_definitions_table = """
                CREATE TABLE IF NOT EXISTS workflow_definitions (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    workflow_id VARCHAR(64) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    definition_data JSON,
                    version VARCHAR(20) DEFAULT '1.0',
                    is_predefined TINYINT(1) DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_workflow_id (workflow_id),
                    INDEX idx_name (name)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            await db.execute(create_definitions_table)
            
        except Exception as e:
            logger.error(f"创建工作流表失败: {e}")
    
    # =========================================================================
    # 预定义工作流
    # =========================================================================
    
    def _create_health_consultation_workflow(self) -> WorkflowDefinition:
        """
        创建健康咨询工作流
        
        流程：
        1. 接收用户问题
        2. 检索历史记忆
        3. 分析问题意图
        4. 生成专业回复
        5. 存储对话记忆
        """
        steps = [
            WorkflowStep(
                step_id="receive_question",
                name="接收用户问题",
                description="接收并记录用户提出的健康问题",
                step_type="llm_call",
                config={
                    "prompt": "请分析用户的健康问题: {user_question}",
                    "model": "kimi-k2-turbo-preview"
                }
            ),
            WorkflowStep(
                step_id="retrieve_memory",
                name="检索历史记忆",
                description="检索用户的历史健康记录和对话记忆",
                step_type="tool_call",
                config={
                    "tool_name": "retrieve_memory",
                    "params": {
                        "query": "{user_question}",
                        "limit": 5
                    }
                },
                dependencies=["receive_question"]
            ),
            WorkflowStep(
                step_id="analyze_intent",
                name="分析问题意图",
                description="分析用户问题的意图和关键信息",
                step_type="llm_call",
                config={
                    "prompt": """基于用户问题: {user_question}
                    和历史记忆: {step_retrieve_memory_result}
                    请分析：
                    1. 用户的主要健康诉求
                    2. 需要关注的重点
                    3. 建议的回复方向""",
                    "model": "kimi-k2-turbo-preview"
                },
                dependencies=["retrieve_memory"]
            ),
            WorkflowStep(
                step_id="generate_response",
                name="生成专业回复",
                description="生成专业的健康咨询回复",
                step_type="llm_call",
                config={
                    "prompt": """作为健康顾问，请基于以下信息回复用户：
                    
                    用户问题: {user_question}
                    历史记忆: {step_retrieve_memory_result}
                    意图分析: {step_analyze_intent_result}
                    
                    请提供：
                    1. 对用户问题的理解
                    2. 专业的健康建议
                    3. 需要注意的事项
                    4. 后续建议
                    
                    注意：建议仅供参考，如有严重症状请及时就医。""",
                    "model": "kimi-k2-turbo-preview"
                },
                dependencies=["analyze_intent"]
            ),
            WorkflowStep(
                step_id="store_memory",
                name="存储对话记忆",
                description="将本次对话存储到记忆系统",
                step_type="tool_call",
                config={
                    "tool_name": "store_memory",
                    "params": {
                        "content": "用户咨询: {user_question}\nAI回复: {step_generate_response_result}",
                        "metadata": {
                            "type": "health_consultation",
                            "timestamp": "{timestamp}"
                        }
                    }
                },
                dependencies=["generate_response"]
            )
        ]
        
        return WorkflowDefinition(
            workflow_id="health_consultation",
            name="健康咨询",
            description="处理用户健康咨询的完整流程",
            steps=steps,
            version="1.0",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def _create_report_analysis_workflow(self) -> WorkflowDefinition:
        """
        创建报告分析工作流
        
        流程：
        1. 接收报告数据
        2. 提取关键指标
        3. 分析异常项
        4. 生成解读报告
        5. 生成健康建议
        6. 存储分析结果
        """
        steps = [
            WorkflowStep(
                step_id="receive_report",
                name="接收报告数据",
                description="接收体检报告或健康报告数据",
                step_type="llm_call",
                config={
                    "prompt": "请解析以下健康报告数据: {report_data}",
                    "model": "kimi-k2-turbo-preview"
                }
            ),
            WorkflowStep(
                step_id="extract_indicators",
                name="提取关键指标",
                description="从报告中提取关键健康指标",
                step_type="llm_call",
                config={
                    "prompt": """从以下报告中提取所有健康指标：
                    {report_data}
                    
                    请按以下格式输出：
                    - 指标名称: 数值 (参考范围) - 状态""",
                    "model": "kimi-k2-turbo-preview"
                },
                dependencies=["receive_report"]
            ),
            WorkflowStep(
                step_id="analyze_abnormal",
                name="分析异常项",
                description="分析指标中的异常情况",
                step_type="llm_call",
                config={
                    "prompt": """基于提取的指标: {step_extract_indicators_result}
                    
                    请分析：
                    1. 哪些指标超出正常范围
                    2. 异常的可能原因
                    3. 严重程度评估
                    4. 需要关注的重点""",
                    "model": "kimi-k2-turbo-preview"
                },
                dependencies=["extract_indicators"]
            ),
            WorkflowStep(
                step_id="generate_interpretation",
                name="生成解读报告",
                description="生成专业的报告解读",
                step_type="llm_call",
                config={
                    "prompt": """基于以下分析结果，生成完整的报告解读：
                    
                    原始报告: {report_data}
                    指标提取: {step_extract_indicators_result}
                    异常分析: {step_analyze_abnormal_result}
                    
                    请生成包含以下内容的解读报告：
                    1. 整体健康状况概述
                    2. 各项指标的详细解读
                    3. 异常指标的医学解释
                    4. 与历史数据的对比（如有）
                    5. 总结和建议""",
                    "model": "kimi-k2-turbo-preview"
                },
                dependencies=["analyze_abnormal"]
            ),
            WorkflowStep(
                step_id="generate_recommendations",
                name="生成健康建议",
                description="基于分析结果生成个性化健康建议",
                step_type="llm_call",
                config={
                    "prompt": """基于报告分析结果：
                    {step_analyze_abnormal_result}
                    
                    请生成以下方面的建议：
                    1. 饮食调整建议
                    2. 运动锻炼建议
                    3. 生活习惯改善
                    4. 复查和就医建议
                    5. 日常监测建议""",
                    "model": "kimi-k2-turbo-preview"
                },
                dependencies=["analyze_abnormal"]
            ),
            WorkflowStep(
                step_id="store_analysis",
                name="存储分析结果",
                description="将报告分析结果存储到记忆系统",
                step_type="tool_call",
                config={
                    "tool_name": "store_memory",
                    "params": {
                        "content": "报告分析: {step_generate_interpretation_result}\n健康建议: {step_generate_recommendations_result}",
                        "metadata": {
                            "type": "report_analysis",
                            "report_date": "{report_date}",
                            "timestamp": "{timestamp}"
                        }
                    }
                },
                dependencies=["generate_interpretation", "generate_recommendations"]
            ),
            WorkflowStep(
                step_id="generate_document",
                name="生成分析文档",
                description="生成PDF格式的分析报告文档",
                step_type="tool_call",
                config={
                    "tool_name": "generate_document",
                    "params": {
                        "content": "{step_generate_interpretation_result}\n\n{step_generate_recommendations_result}",
                        "doc_type": "pdf",
                        "template": "health_report"
                    }
                },
                dependencies=["store_analysis"]
            )
        ]
        
        return WorkflowDefinition(
            workflow_id="report_analysis",
            name="报告分析",
            description="分析体检报告和健康报告的完整流程",
            steps=steps,
            version="1.0",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def _create_plan_creation_workflow(self) -> WorkflowDefinition:
        """
        创建计划制定工作流
        
        流程：
        1. 收集用户信息
        2. 分析健康目标
        3. 检索相关知识
        4. 制定健康计划
        5. 生成执行方案
        6. 创建提醒设置
        7. 存储计划
        """
        steps = [
            WorkflowStep(
                step_id="collect_info",
                name="收集用户信息",
                description="收集用户的健康信息和目标",
                step_type="llm_call",
                config={
                    "prompt": """请分析用户的健康信息：
                    {user_health_info}
                    
                    用户目标: {health_goal}
                    
                    请提取关键信息用于制定计划。""",
                    "model": "kimi-k2-turbo-preview"
                }
            ),
            WorkflowStep(
                step_id="retrieve_knowledge",
                name="检索健康知识",
                description="检索相关的健康知识和计划模板",
                step_type="tool_call",
                config={
                    "tool_name": "retrieve_memory",
                    "params": {
                        "query": "{health_goal} 健康计划",
                        "limit": 10
                    }
                },
                dependencies=["collect_info"]
            ),
            WorkflowStep(
                step_id="analyze_goal",
                name="分析健康目标",
                description="分析用户健康目标的可行性和优先级",
                step_type="llm_call",
                config={
                    "prompt": """基于用户信息: {step_collect_info_result}
                    和相关知识: {step_retrieve_knowledge_result}
                    
                    请分析：
                    1. 目标的合理性
                    2. 实现目标的关键因素
                    3. 可能遇到的挑战
                    4. 优先级排序""",
                    "model": "kimi-k2-turbo-preview"
                },
                dependencies=["retrieve_knowledge"]
            ),
            WorkflowStep(
                step_id="create_plan",
                name="制定健康计划",
                description="制定详细的健康管理计划",
                step_type="llm_call",
                config={
                    "prompt": """基于目标分析: {step_analyze_goal_result}
                    
                    请制定包含以下内容的详细计划：
                    
                    ## 1. 计划概述
                    - 计划名称和目标
                    - 计划周期
                    - 预期成果
                    
                    ## 2. 饮食计划
                    - 每日饮食建议
                    - 营养搭配原则
                    - 需要避免的食物
                    
                    ## 3. 运动计划
                    - 运动类型和频率
                    - 运动强度建议
                    - 注意事项
                    
                    ## 4. 作息计划
                    - 睡眠建议
                    - 日常作息安排
                    
                    ## 5. 监测指标
                    - 需要监测的健康指标
                    - 监测频率
                    
                    ## 6. 里程碑
                    - 阶段性目标
                    - 评估时间点""",
                    "model": "kimi-k2-turbo-preview"
                },
                dependencies=["analyze_goal"]
            ),
            WorkflowStep(
                step_id="create_schedule",
                name="生成执行方案",
                description="生成可执行的具体日程安排",
                step_type="llm_call",
                config={
                    "prompt": """基于健康计划: {step_create_plan_result}
                    
                    请生成详细的执行日程：
                    1. 每日具体安排（时间、活动）
                    2. 每周计划概览
                    3. 月度目标检查点
                    4. 灵活调整建议""",
                    "model": "kimi-k2-turbo-preview"
                },
                dependencies=["create_plan"]
            ),
            WorkflowStep(
                step_id="store_plan",
                name="存储健康计划",
                description="将制定的计划存储到记忆系统",
                step_type="tool_call",
                config={
                    "tool_name": "store_memory",
                    "params": {
                        "content": "健康计划: {step_create_plan_result}\n执行方案: {step_create_schedule_result}",
                        "metadata": {
                            "type": "health_plan",
                            "goal": "{health_goal}",
                            "created_at": "{timestamp}",
                            "status": "active"
                        }
                    }
                },
                dependencies=["create_schedule"]
            ),
            WorkflowStep(
                step_id="generate_plan_doc",
                name="生成计划文档",
                description="生成PDF格式的健康计划文档",
                step_type="tool_call",
                config={
                    "tool_name": "generate_document",
                    "params": {
                        "content": "{step_create_plan_result}\n\n执行方案:\n{step_create_schedule_result}",
                        "doc_type": "pdf",
                        "template": "health_plan"
                    }
                },
                dependencies=["store_plan"]
            )
        ]
        
        return WorkflowDefinition(
            workflow_id="plan_creation",
            name="计划制定",
            description="制定个性化健康管理计划的完整流程",
            steps=steps,
            version="1.0",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )


# =============================================================================
# 全局工作流引擎实例
# =============================================================================

workflow_engine = WorkflowEngine()


def get_workflow_engine() -> WorkflowEngine:
    """
    获取工作流引擎实例
    
    Returns:
        WorkflowEngine: 工作流引擎实例
    """
    return workflow_engine
