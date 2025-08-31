from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.models import Tool, ToolType
import asyncio
import logging

logger = logging.getLogger(__name__)

class BaseTool(ABC):
    """Base class for all tools in the system"""
    
    def __init__(self, name: str, description: str, tool_type: ToolType):
        self.name = name
        self.description = description
        self.tool_type = tool_type
        self.is_available = True
        self.version = "1.0.0"
        self.parameters_schema = {}
        
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        pass
    
    @abstractmethod
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate input parameters"""
        pass
    
    async def execute_with_timeout(self, parameters: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
        """Execute tool with timeout protection"""
        try:
            if not self.validate_parameters(parameters):
                raise ValueError(f"Invalid parameters for tool {self.name}")
            
            result = await asyncio.wait_for(
                self.execute(parameters), 
                timeout=timeout
            )
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"Tool {self.name} execution timed out after {timeout}s")
            raise
        except Exception as e:
            logger.error(f"Tool {self.name} execution failed: {str(e)}")
            raise
    
    def get_tool_info(self) -> Tool:
        """Get tool information as a Tool model"""
        return Tool(
            name=self.name,
            tool_type=self.tool_type,
            description=self.description,
            parameters_schema=self.parameters_schema,
            is_available=self.is_available,
            version=self.version
        )
    
    def health_check(self) -> bool:
        """Check if tool is healthy and available"""
        return self.is_available
