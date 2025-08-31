from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.models import Agent, AgentStatus, TaskStatus
from app.tools import BaseTool
import asyncio
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, name: str, agent_type: str, capabilities: List[str] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.agent_type = agent_type
        self.capabilities = capabilities or []
        self.tools: Dict[str, BaseTool] = {}
        self.status = AgentStatus.IDLE
        self.last_heartbeat = datetime.utcnow()
        self.metadata = {}
        self.current_task = None
        
    @abstractmethod
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task and return results"""
        pass
    
    @abstractmethod
    def can_handle_task(self, task_type: str) -> bool:
        """Check if agent can handle a specific task type"""
        pass
    
    def register_tool(self, tool: BaseTool):
        """Register a tool with this agent"""
        self.tools[tool.name] = tool
        logger.info(f"Tool {tool.name} registered with agent {self.name}")
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self.tools.get(tool_name)
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given parameters"""
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found in agent {self.name}")
        
        try:
            result = await tool.execute_with_timeout(parameters)
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            raise
    
    def update_status(self, status: AgentStatus):
        """Update agent status"""
        self.status = status
        self.last_heartbeat = datetime.utcnow()
        logger.info(f"Agent {self.name} status updated to {status}")
    
    def heartbeat(self):
        """Update heartbeat timestamp"""
        self.last_heartbeat = datetime.utcnow()
    
    def is_healthy(self) -> bool:
        """Check if agent is healthy (heartbeat within last 30 seconds)"""
        if not self.last_heartbeat:
            return False
        
        time_diff = (datetime.utcnow() - self.last_heartbeat).total_seconds()
        return time_diff < 30
    
    def get_agent_info(self) -> Agent:
        """Get agent information as an Agent model"""
        return Agent(
            id=self.id,
            name=self.name,
            agent_type=self.agent_type,
            status=self.status,
            capabilities=self.capabilities,
            tools=list(self.tools.keys()),
            last_heartbeat=self.last_heartbeat,
            metadata=self.metadata
        )
    
    async def start_task(self, task_id: str):
        """Start processing a task"""
        self.current_task = task_id
        self.update_status(AgentStatus.BUSY)
        logger.info(f"Agent {self.name} started task {task_id}")
    
    async def complete_task(self, task_id: str):
        """Complete a task"""
        if self.current_task == task_id:
            self.current_task = None
            self.update_status(AgentStatus.IDLE)
            logger.info(f"Agent {self.name} completed task {task_id}")
    
    async def fail_task(self, task_id: str, error: str):
        """Mark a task as failed"""
        if self.current_task == task_id:
            self.current_task = None
            self.update_status(AgentStatus.ERROR)
            logger.error(f"Agent {self.name} failed task {task_id}: {error}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        return {
            "agent_id": self.id,
            "name": self.name,
            "status": self.status,
            "is_healthy": self.is_healthy(),
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "current_task": self.current_task,
            "tools_count": len(self.tools),
            "capabilities": self.capabilities
        }
