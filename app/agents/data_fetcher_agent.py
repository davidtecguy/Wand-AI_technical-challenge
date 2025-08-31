from typing import Dict, Any, List
from .base import BaseAgent
from app.tools import DataFetcherTool
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class DataFetcherAgent(BaseAgent):
    """Agent specialized in fetching and processing data from various sources"""
    
    def __init__(self):
        super().__init__(
            name="DataFetcherAgent",
            agent_type="data_fetcher",
            capabilities=["data_fetching", "data_validation", "data_transformation"]
        )
        
        self.register_tool(DataFetcherTool())
        
        logger.info(f"DataFetcherAgent initialized with ID: {self.id}")
    
    def can_handle_task(self, task_type: str) -> bool:
        """Check if this agent can handle a specific task type"""
        return task_type in ["fetch_data", "validate_data", "transform_data", "aggregate_data"]
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a data fetching task"""
        try:
            task_type = task_data.get("task_type", "fetch_data")
            parameters = task_data.get("parameters", {})
            
            logger.info(f"DataFetcherAgent processing task: {task_type}")
            
            if task_type == "fetch_data":
                return await self._fetch_data(parameters)
            elif task_type == "validate_data":
                return await self._validate_data(parameters)
            elif task_type == "transform_data":
                return await self._transform_data(parameters)
            elif task_type == "aggregate_data":
                return await self._aggregate_data(parameters)
            else:
                raise ValueError(f"Unsupported task type: {task_type}")
                
        except Exception as e:
            logger.error(f"Error processing task in DataFetcherAgent: {e}")
            raise
    
    async def _fetch_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from specified source"""
        try:
            result = await self.execute_tool("data_fetcher", parameters)
            
            if result.get("success"):
                result["agent_id"] = self.id
                result["fetch_timestamp"] = str(datetime.utcnow())
                result["source_parameters"] = parameters
                
                logger.info(f"Data fetched successfully from {parameters.get('source', 'unknown')}")
                return result
            else:
                logger.error(f"Data fetch failed: {result.get('error', 'Unknown error')}")
                return result
                
        except Exception as e:
            logger.error(f"Error in _fetch_data: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.id
            }
    
    async def _validate_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate fetched data"""
        data = parameters.get("data")
        validation_rules = parameters.get("validation_rules", {})
        
        if not data:
            return {
                "success": False,
                "error": "No data provided for validation",
                "agent_id": self.id
            }
        
        validation_results = {
            "is_valid": True,
            "validation_errors": [],
            "validation_warnings": [],
            "validation_timestamp": str(datetime.utcnow()),
            "agent_id": self.id
        }
        
        if validation_rules.get("check_required_fields"):
            required_fields = validation_rules.get("required_fields", [])
            for field in required_fields:
                if field not in data:
                    validation_results["is_valid"] = False
                    validation_results["validation_errors"].append(f"Missing required field: {field}")
        
        if validation_rules.get("check_data_types"):
            type_checks = validation_rules.get("type_checks", {})
            for field, expected_type in type_checks.items():
                if field in data:
                    if not isinstance(data[field], expected_type):
                        validation_results["is_valid"] = False
                        validation_results["validation_errors"].append(
                            f"Field {field} has wrong type. Expected {expected_type}, got {type(data[field])}"
                        )
        
        if validation_rules.get("check_data_quality"):
            for key, value in data.items():
                if value is None or (isinstance(value, str) and value.strip() == ""):
                    validation_results["validation_warnings"].append(f"Field {key} has empty/null value")
        
        return validation_results
    
    async def _transform_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data according to specified rules"""
        data = parameters.get("data")
        transformation_rules = parameters.get("transformation_rules", {})
        
        if not data:
            return {
                "success": False,
                "error": "No data provided for transformation",
                "agent_id": self.id
            }
        
        try:
            transformed_data = data.copy()
            
            for rule in transformation_rules:
                rule_type = rule.get("type")
                
                if rule_type == "rename_field":
                    old_name = rule.get("old_name")
                    new_name = rule.get("new_name")
                    if old_name in transformed_data:
                        transformed_data[new_name] = transformed_data.pop(old_name)
                
                elif rule_type == "convert_type":
                    field_name = rule.get("field_name")
                    target_type = rule.get("target_type")
                    if field_name in transformed_data:
                        if target_type == "int":
                            transformed_data[field_name] = int(transformed_data[field_name])
                        elif target_type == "float":
                            transformed_data[field_name] = float(transformed_data[field_name])
                        elif target_type == "string":
                            transformed_data[field_name] = str(transformed_data[field_name])
                
                elif rule_type == "filter_data":
                    field_name = rule.get("field_name")
                    filter_value = rule.get("filter_value")
                    if isinstance(transformed_data, list):
                        transformed_data = [
                            item for item in transformed_data 
                            if item.get(field_name) != filter_value
                        ]
            
            return {
                "success": True,
                "original_data": data,
                "transformed_data": transformed_data,
                "transformation_rules_applied": len(transformation_rules),
                "transformation_timestamp": str(datetime.utcnow()),
                "agent_id": self.id
            }
            
        except Exception as e:
            logger.error(f"Error in data transformation: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.id
            }
    
    async def _aggregate_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate data according to specified criteria"""
        data = parameters.get("data")
        aggregation_rules = parameters.get("aggregation_rules", {})
        
        if not data or not isinstance(data, list):
            return {
                "success": False,
                "error": "Data must be a list for aggregation",
                "agent_id": self.id
            }
        
        try:
            aggregation_results = {}
            
            for rule in aggregation_rules:
                operation = rule.get("operation")
                field_name = rule.get("field_name")
                result_key = rule.get("result_key", f"{operation}_{field_name}")
                
                if operation == "sum":
                    values = [item.get(field_name, 0) for item in data if item.get(field_name) is not None]
                    aggregation_results[result_key] = sum(values)
                
                elif operation == "average":
                    values = [item.get(field_name, 0) for item in data if item.get(field_name) is not None]
                    aggregation_results[result_key] = sum(values) / len(values) if values else 0
                
                elif operation == "count":
                    aggregation_results[result_key] = len(data)
                
                elif operation == "min":
                    values = [item.get(field_name) for item in data if item.get(field_name) is not None]
                    aggregation_results[result_key] = min(values) if values else None
                
                elif operation == "max":
                    values = [item.get(field_name) for item in data if item.get(field_name) is not None]
                    aggregation_results[result_key] = max(values) if values else None
            
            return {
                "success": True,
                "aggregation_results": aggregation_results,
                "data_count": len(data),
                "aggregation_timestamp": str(datetime.utcnow()),
                "agent_id": self.id
            }
            
        except Exception as e:
            logger.error(f"Error in data aggregation: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.id
            }
