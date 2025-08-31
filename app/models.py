from enum import Enum
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AgentStatus(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"

class ToolType(str, Enum):
    DATA_FETCHER = "data_fetcher"
    CHART_GENERATOR = "chart_generator"
    TEXT_PROCESSOR = "text_processor"
    CUSTOM = "custom"

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_graph: Dict[str, Any]
    parameters: Dict[str, Any] = Field(default_factory=dict)
    results: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

class Agent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    agent_type: str
    status: AgentStatus = AgentStatus.IDLE
    capabilities: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    last_heartbeat: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Tool(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    tool_type: ToolType
    description: str
    parameters_schema: Dict[str, Any] = Field(default_factory=dict)
    is_available: bool = True
    version: str = "1.0.0"

class ExecutionNode(BaseModel):
    agent_id: str
    agent_type: str
    dependencies: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class ExecutionGraph(BaseModel):
    nodes: Dict[str, ExecutionNode]
    edges: List[tuple[str, str]] = Field(default_factory=list)
    entry_points: List[str] = Field(default_factory=list)
    exit_points: List[str] = Field(default_factory=list)

class TaskRequest(BaseModel):
    name: str
    description: Optional[str] = None
    execution_graph: Dict[str, Any]
    parameters: Dict[str, Any] = Field(default_factory=dict)
    timeout: Optional[int] = 300  # seconds
    max_retries: Optional[int] = 3

class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    message: str
    estimated_completion: Optional[datetime] = None

class AgentMessage(BaseModel):
    from_agent: str
    to_agent: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
