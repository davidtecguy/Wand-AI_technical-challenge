from typing import Dict, Any, List
from .base import BaseTool
from app.models import ToolType
import json
import logging
import base64
from io import BytesIO
from datetime import datetime

logger = logging.getLogger(__name__)

class ChartGeneratorTool(BaseTool):
    """Tool for generating charts and visualizations from data"""
    
    def __init__(self):
        super().__init__(
            name="chart_generator",
            description="Generates charts and visualizations from structured data",
            tool_type=ToolType.CHART_GENERATOR
        )
        self.parameters_schema = {
            "chart_type": {"type": "string", "enum": ["line", "bar", "pie", "scatter", "histogram"], "required": True},
            "data": {"type": "object", "description": "Data to visualize", "required": True},
            "title": {"type": "string", "default": "Generated Chart"},
            "x_label": {"type": "string", "default": "X Axis"},
            "y_label": {"type": "string", "default": "Y Axis"},
            "width": {"type": "integer", "default": 800},
            "height": {"type": "integer", "default": 600},
            "output_format": {"type": "string", "enum": ["png", "svg", "html"], "default": "png"}
        }
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        required_fields = ["chart_type", "data"]
        if not all(field in parameters for field in required_fields):
            return False
        
        valid_types = ["line", "bar", "pie", "scatter", "histogram"]
        if parameters["chart_type"] not in valid_types:
            return False
        
        data = parameters["data"]
        if not isinstance(data, dict) or "values" not in data:
            return False
        
        return True
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        try:
            chart_type = parameters["chart_type"]
            data = parameters["data"]
            title = parameters.get("title", "Generated Chart")
            x_label = parameters.get("x_label", "X Axis")
            y_label = parameters.get("y_label", "Y Axis")
            width = parameters.get("width", 800)
            height = parameters.get("height", 600)
            output_format = parameters.get("output_format", "png")
            
            if chart_type == "line":
                chart_data = self._generate_line_chart(data, title, x_label, y_label, width, height)
            elif chart_type == "bar":
                chart_data = self._generate_bar_chart(data, title, x_label, y_label, width, height)
            elif chart_type == "pie":
                chart_data = self._generate_pie_chart(data, title, width, height)
            elif chart_type == "scatter":
                chart_data = self._generate_scatter_chart(data, title, x_label, y_label, width, height)
            elif chart_type == "histogram":
                chart_data = self._generate_histogram(data, title, x_label, y_label, width, height)
            else:
                raise ValueError(f"Unsupported chart type: {chart_type}")
            
            if output_format == "html":
                output = self._to_html(chart_data)
            elif output_format == "svg":
                output = self._to_svg(chart_data)
            else:  # png
                output = self._to_png(chart_data, width, height)
            
            return {
                "success": True,
                "chart_type": chart_type,
                "output_format": output_format,
                "data": output,
                "metadata": {
                    "title": title,
                    "dimensions": {"width": width, "height": height},
                    "generated_at": str(datetime.utcnow())
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating chart: {e}")
            return {
                "success": False,
                "error": str(e),
                "chart_type": parameters.get("chart_type", "unknown")
            }
    
    def _generate_line_chart(self, data: Dict[str, Any], title: str, x_label: str, y_label: str, width: int, height: int) -> Dict[str, Any]:
        """Generate line chart data"""
        values = data.get("values", [])
        if not values:
            raise ValueError("No data values provided")
        
        return {
            "type": "line",
            "title": title,
            "x_label": x_label,
            "y_label": y_label,
            "data": values,
            "width": width,
            "height": height
        }
    
    def _generate_bar_chart(self, data: Dict[str, Any], title: str, x_label: str, y_label: str, width: int, height: int) -> Dict[str, Any]:
        """Generate bar chart data"""
        values = data.get("values", [])
        if not values:
            raise ValueError("No data values provided")
        
        return {
            "type": "bar",
            "title": title,
            "x_label": x_label,
            "y_label": y_label,
            "data": values,
            "width": width,
            "height": height
        }
    
    def _generate_pie_chart(self, data: Dict[str, Any], title: str, width: int, height: int) -> Dict[str, Any]:
        """Generate pie chart data"""
        values = data.get("values", [])
        if not values:
            raise ValueError("No data values provided")
        
        return {
            "type": "pie",
            "title": title,
            "data": values,
            "width": width,
            "height": height
        }
    
    def _generate_scatter_chart(self, data: Dict[str, Any], title: str, x_label: str, y_label: str, width: int, height: int) -> Dict[str, Any]:
        """Generate scatter chart data"""
        values = data.get("values", [])
        if not values:
            raise ValueError("No data values provided")
        
        return {
            "type": "scatter",
            "title": title,
            "x_label": x_label,
            "y_label": y_label,
            "data": values,
            "width": width,
            "height": height
        }
    
    def _generate_histogram(self, data: Dict[str, Any], title: str, x_label: str, y_label: str, width: int, height: int) -> Dict[str, Any]:
        """Generate histogram data"""
        values = data.get("values", [])
        if not values:
            raise ValueError("No data values provided")
        
        return {
            "type": "histogram",
            "title": title,
            "x_label": x_label,
            "y_label": y_label,
            "data": values,
            "width": width,
            "height": height
        }
    
    def _to_html(self, chart_data: Dict[str, Any]) -> str:
        """Convert chart data to HTML representation"""
        html = f"""
        <div class="chart" style="width: {chart_data['width']}px; height: {chart_data['height']}px;">
            <h3>{chart_data['title']}</h3>
            <div class="chart-content">
                <p>Chart Type: {chart_data['type']}</p>
                <p>Data Points: {len(chart_data.get('data', []))}</p>
            </div>
        </div>
        """
        return html
    
    def _to_svg(self, chart_data: Dict[str, Any]) -> str:
        """Convert chart data to SVG representation"""
        svg = f"""
        <svg width="{chart_data['width']}" height="{chart_data['height']}" xmlns="http://www.w3.org/2000/svg">
            <title>{chart_data['title']}</title>
            <rect width="100%" height="100%" fill="white" stroke="black"/>
            <text x="50%" y="30" text-anchor="middle" font-size="16">{chart_data['title']}</text>
            <text x="50%" y="50" text-anchor="middle" font-size="12">Chart Type: {chart_data['type']}</text>
        </svg>
        """
        return svg
    
    def _to_png(self, chart_data: Dict[str, Any], width: int, height: int) -> str:
        """Convert chart data to PNG representation (base64 encoded)"""
        # For now, we'll return a simple base64 encoded placeholder
        placeholder_svg = self._to_svg(chart_data)
        # In a real implementation, you'd convert SVG to PNG here
        return f"data:image/svg+xml;base64,{base64.b64encode(placeholder_svg.encode()).decode()}"
