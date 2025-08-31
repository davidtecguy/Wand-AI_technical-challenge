from typing import Dict, Any, List
from .base import BaseAgent
from app.tools import ChartGeneratorTool
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ChartGeneratorAgent(BaseAgent):
    """Agent specialized in generating charts and visualizations from data"""
    
    def __init__(self):
        super().__init__(
            name="ChartGeneratorAgent",
            agent_type="chart_generator",
            capabilities=["chart_generation", "data_visualization", "chart_customization"]
        )
        
        self.register_tool(ChartGeneratorTool())
        
        logger.info(f"ChartGeneratorAgent initialized with ID: {self.id}")
    
    def can_handle_task(self, task_type: str) -> bool:
        """Check if this agent can handle a specific task type"""
        return task_type in ["generate_chart", "customize_chart", "batch_chart_generation", "chart_analysis"]
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a chart generation task"""
        try:
            task_type = task_data.get("task_type", "generate_chart")
            parameters = task_data.get("parameters", {})
            
            logger.info(f"ChartGeneratorAgent processing task: {task_type}")
            
            if task_type == "generate_chart":
                return await self._generate_chart(parameters)
            elif task_type == "customize_chart":
                return await self._customize_chart(parameters)
            elif task_type == "batch_chart_generation":
                return await self._batch_chart_generation(parameters)
            elif task_type == "chart_analysis":
                return await self._analyze_chart(parameters)
            else:
                raise ValueError(f"Unsupported task type: {task_type}")
                
        except Exception as e:
            logger.error(f"Error processing task in ChartGeneratorAgent: {e}")
            raise
    
    async def _generate_chart(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a chart from data"""
        try:
            result = await self.execute_tool("chart_generator", parameters)
            
            if result.get("success"):
                result["agent_id"] = self.id
                result["generation_timestamp"] = str(datetime.utcnow())
                result["input_parameters"] = parameters
                
                logger.info(f"Chart generated successfully: {result.get('chart_type', 'unknown')}")
                return result
            else:
                logger.error(f"Chart generation failed: {result.get('error', 'Unknown error')}")
                return result
                
        except Exception as e:
            logger.error(f"Error in _generate_chart: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.id
            }
    
    async def _customize_chart(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Customize an existing chart"""
        chart_data = parameters.get("chart_data")
        customization_rules = parameters.get("customization_rules", {})
        
        if not chart_data:
            return {
                "success": False,
                "error": "No chart data provided for customization",
                "agent_id": self.id
            }
        
        try:
            customized_chart = chart_data.copy()
            
            for rule in customization_rules:
                rule_type = rule.get("type")
                
                if rule_type == "change_title":
                    customized_chart["title"] = rule.get("new_title", customized_chart.get("title"))
                
                elif rule_type == "change_dimensions":
                    if "width" in rule:
                        customized_chart["width"] = rule["width"]
                    if "height" in rule:
                        customized_chart["height"] = rule["height"]
                
                elif rule_type == "change_labels":
                    if "x_label" in rule:
                        customized_chart["x_label"] = rule["x_label"]
                    if "y_label" in rule:
                        customized_chart["y_label"] = rule["y_label"]
                
                elif rule_type == "change_output_format":
                    customized_chart["output_format"] = rule.get("new_format", "png")
            
            result = await self.execute_tool("chart_generator", customized_chart)
            
            if result.get("success"):
                result["customization_rules_applied"] = len(customization_rules)
                result["customization_timestamp"] = str(datetime.utcnow())
                result["agent_id"] = self.id
            
            return result
            
        except Exception as e:
            logger.error(f"Error in chart customization: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.id
            }
    
    async def _batch_chart_generation(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate multiple charts from a dataset"""
        dataset = parameters.get("dataset")
        chart_configs = parameters.get("chart_configs", [])
        
        if not dataset or not chart_configs:
            return {
                "success": False,
                "error": "Dataset and chart configurations required for batch generation",
                "agent_id": self.id
            }
        
        try:
            generated_charts = []
            failed_charts = []
            
            for config in chart_configs:
                try:
                    chart_params = {
                        "chart_type": config.get("chart_type", "line"),
                        "data": {"values": dataset},
                        "title": config.get("title", f"Chart {len(generated_charts) + 1}"),
                        "x_label": config.get("x_label", "X Axis"),
                        "y_label": config.get("y_label", "Y Axis"),
                        "width": config.get("width", 800),
                        "height": config.get("height", 600),
                        "output_format": config.get("output_format", "png")
                    }
                    
                    result = await self.execute_tool("chart_generator", chart_params)
                    
                    if result.get("success"):
                        result["config_index"] = len(generated_charts)
                        result["config"] = config
                        generated_charts.append(result)
                    else:
                        failed_charts.append({
                            "config": config,
                            "error": result.get("error", "Unknown error"),
                            "config_index": len(failed_charts)
                        })
                        
                except Exception as e:
                    failed_charts.append({
                        "config": config,
                        "error": str(e),
                        "config_index": len(failed_charts)
                    })
            
            return {
                "success": True,
                "total_charts_requested": len(chart_configs),
                "successfully_generated": len(generated_charts),
                "failed_generations": len(failed_charts),
                "generated_charts": generated_charts,
                "failed_charts": failed_charts,
                "batch_generation_timestamp": str(datetime.utcnow()),
                "agent_id": self.id
            }
            
        except Exception as e:
            logger.error(f"Error in batch chart generation: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.id
            }
    
    async def _analyze_chart(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze chart data and provide insights"""
        chart_data = parameters.get("chart_data")
        
        if not chart_data:
            return {
                "success": False,
                "error": "No chart data provided for analysis",
                "agent_id": self.id
            }
        
        try:
            analysis_results = {
                "chart_type": chart_data.get("chart_type", "unknown"),
                "data_points": 0,
                "insights": [],
                "recommendations": [],
                "analysis_timestamp": str(datetime.utcnow()),
                "agent_id": self.id
            }
            
            data = chart_data.get("data", {})
            values = data.get("values", [])
            analysis_results["data_points"] = len(values)
            
            if chart_data.get("chart_type") == "line":
                if len(values) > 10:
                    analysis_results["insights"].append("Line chart has sufficient data points for trend analysis")
                else:
                    analysis_results["insights"].append("Line chart has limited data points - consider collecting more data")
            
            elif chart_data.get("chart_type") == "bar":
                if len(values) > 20:
                    analysis_results["insights"].append("Bar chart has many categories - consider grouping or filtering")
                else:
                    analysis_results["insights"].append("Bar chart has manageable number of categories")
            
            elif chart_data.get("chart_type") == "pie":
                if len(values) > 8:
                    analysis_results["insights"].append("Pie chart has many segments - consider consolidating small segments")
                else:
                    analysis_results["insights"].append("Pie chart has good segment distribution")
            
            if analysis_results["data_points"] < 5:
                analysis_results["recommendations"].append("Consider collecting more data for better visualization")
            
            if chart_data.get("width", 800) < 600:
                analysis_results["recommendations"].append("Consider increasing chart width for better readability")
            
            if chart_data.get("height", 600) < 400:
                analysis_results["recommendations"].append("Consider increasing chart height for better readability")
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error in chart analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.id
            }
