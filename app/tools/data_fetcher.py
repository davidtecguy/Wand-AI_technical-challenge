from typing import Dict, Any, List
from .base import BaseTool
from app.models import ToolType
import httpx
import json
import logging

logger = logging.getLogger(__name__)

class DataFetcherTool(BaseTool):
    """Tool for fetching data from various sources"""
    
    def __init__(self):
        super().__init__(
            name="data_fetcher",
            description="Fetches data from HTTP APIs, databases, and file systems",
            tool_type=ToolType.DATA_FETCHER
        )
        self.parameters_schema = {
            "source_type": {"type": "string", "enum": ["http", "file", "database"], "required": True},
            "source": {"type": "string", "description": "URL, file path, or connection string", "required": True},
            "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"], "default": "GET"},
            "headers": {"type": "object", "default": {}},
            "body": {"type": "object", "default": None},
            "timeout": {"type": "integer", "default": 30}
        }
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        required_fields = ["source_type", "source"]
        return all(field in parameters for field in required_fields)
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        source_type = parameters["source_type"]
        source = parameters["source"]
        
        if source_type == "http":
            return await self._fetch_http(parameters)
        elif source_type == "file":
            return await self._fetch_file(parameters)
        elif source_type == "database":
            return await self._fetch_database(parameters)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")
    
    async def _fetch_http(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from HTTP endpoints"""
        method = parameters.get("method", "GET")
        headers = parameters.get("headers", {})
        body = parameters.get("body")
        timeout = parameters.get("timeout", 30)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                if method == "GET":
                    response = await client.get(parameters["source"], headers=headers)
                elif method == "POST":
                    response = await client.post(parameters["source"], headers=headers, json=body)
                elif method == "PUT":
                    response = await client.put(parameters["source"], headers=headers, json=body)
                elif method == "DELETE":
                    response = await client.delete(parameters["source"], headers=headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                
                try:
                    data = response.json()
                except:
                    data = response.text
                
                return {
                    "success": True,
                    "data": data,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "source": parameters["source"]
                }
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error fetching from {parameters['source']}: {e}")
                return {
                    "success": False,
                    "error": f"HTTP {e.response.status_code}: {e.response.text}",
                    "source": parameters["source"]
                }
            except Exception as e:
                logger.error(f"Error fetching from {parameters['source']}: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "source": parameters["source"]
                }
    
    async def _fetch_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from file system"""
        import aiofiles
        
        try:
            async with aiofiles.open(parameters["source"], 'r') as file:
                content = await file.read()
                
                try:
                    data = json.loads(content)
                except:
                    data = content
                
                return {
                    "success": True,
                    "data": data,
                    "source": parameters["source"],
                    "size": len(content)
                }
        except Exception as e:
            logger.error(f"Error reading file {parameters['source']}: {e}")
            return {
                "success": False,
                "error": str(e),
                "source": parameters["source"]
            }
    
    async def _fetch_database(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from database (placeholder implementation)"""
        return {
            "success": False,
            "error": "Database fetching not implemented in this version",
            "source": parameters["source"]
        }
