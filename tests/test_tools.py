import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.tools import DataFetcherTool, ChartGeneratorTool, TextProcessorTool
from app.models import ToolType

class TestDataFetcherTool:
    """Test cases for DataFetcherTool"""
    
    @pytest.fixture
    def tool(self):
        return DataFetcherTool()
    
    def test_initialization(self, tool):
        """Test tool initialization"""
        assert tool.name == "data_fetcher"
        assert tool.tool_type == ToolType.DATA_FETCHER
        assert tool.is_available is True
        assert "source_type" in tool.parameters_schema
    
    def test_validate_parameters(self, tool):
        """Test parameter validation"""
        # Valid parameters
        valid_params = {
            "source_type": "http",
            "source": "https://api.example.com/data"
        }
        assert tool.validate_parameters(valid_params) is True
        
        # Invalid parameters - missing required fields
        invalid_params = {"source_type": "http"}
        assert tool.validate_parameters(invalid_params) is False
        
        # Invalid parameters - empty source
        invalid_params = {
            "source_type": "http",
            "source": ""
        }
        assert tool.validate_parameters(invalid_params) is False
    
    @pytest.mark.asyncio
    async def test_execute_http_fetch(self, tool):
        """Test HTTP data fetching"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {"data": "test"}
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "application/json"}
            
            mock_client_instance = Mock()
            mock_client_instance.get.return_value = mock_response
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client.return_value = mock_client_instance
            
            result = await tool.execute({
                "source_type": "http",
                "source": "https://api.example.com/data"
            })
            
            assert result["success"] is True
            assert result["data"] == {"data": "test"}
            assert result["status_code"] == 200
    
    @pytest.mark.asyncio
    async def test_execute_file_fetch(self, tool):
        """Test file data fetching"""
        with patch('aiofiles.open') as mock_open:
            mock_file = Mock()
            mock_file.read.return_value = '{"file_data": "test"}'
            mock_open.return_value.__aenter__.return_value = mock_file
            mock_open.return_value.__aexit__.return_value = None
            
            result = await tool.execute({
                "source_type": "file",
                "source": "/path/to/file.json"
            })
            
            assert result["success"] is True
            assert result["data"] == {"file_data": "test"}
    
    @pytest.mark.asyncio
    async def test_execute_with_timeout(self, tool):
        """Test tool execution with timeout"""
        with patch.object(tool, 'execute', new_callable=AsyncMock) as mock_execute:
            mock_execute.side_effect = asyncio.TimeoutError()
            
            with pytest.raises(asyncio.TimeoutError):
                await tool.execute_with_timeout({"source_type": "http", "source": "test"}, timeout=1)
    
    def test_get_tool_info(self, tool):
        """Test getting tool information"""
        tool_info = tool.get_tool_info()
        assert tool_info.name == "data_fetcher"
        assert tool_info.tool_type == ToolType.DATA_FETCHER
        assert tool_info.is_available is True

class TestChartGeneratorTool:
    """Test cases for ChartGeneratorTool"""
    
    @pytest.fixture
    def tool(self):
        return ChartGeneratorTool()
    
    def test_initialization(self, tool):
        """Test tool initialization"""
        assert tool.name == "chart_generator"
        assert tool.tool_type == ToolType.CHART_GENERATOR
        assert "chart_type" in tool.parameters_schema
    
    def test_validate_parameters(self, tool):
        """Test parameter validation"""
        # Valid parameters
        valid_params = {
            "chart_type": "line",
            "data": {"values": [1, 2, 3, 4, 5]}
        }
        assert tool.validate_parameters(valid_params) is True
        
        # Invalid chart type
        invalid_params = {
            "chart_type": "invalid_type",
            "data": {"values": [1, 2, 3]}
        }
        assert tool.validate_parameters(invalid_params) is False
        
        # Missing data
        invalid_params = {
            "chart_type": "line"
        }
        assert tool.validate_parameters(invalid_params) is False
    
    @pytest.mark.asyncio
    async def test_execute_line_chart(self, tool):
        """Test line chart generation"""
        result = await tool.execute({
            "chart_type": "line",
            "data": {"values": [1, 2, 3, 4, 5]},
            "title": "Test Line Chart",
            "x_label": "X Axis",
            "y_label": "Y Axis"
        })
        
        assert result["success"] is True
        assert result["chart_type"] == "line"
        assert "data" in result
    
    @pytest.mark.asyncio
    async def test_execute_bar_chart(self, tool):
        """Test bar chart generation"""
        result = await tool.execute({
            "chart_type": "bar",
            "data": {"values": [10, 20, 30, 40, 50]},
            "title": "Test Bar Chart"
        })
        
        assert result["success"] is True
        assert result["chart_type"] == "bar"
    
    @pytest.mark.asyncio
    async def test_execute_pie_chart(self, tool):
        """Test pie chart generation"""
        result = await tool.execute({
            "chart_type": "pie",
            "data": {"values": [30, 25, 20, 15, 10]},
            "title": "Test Pie Chart"
        })
        
        assert result["success"] is True
        assert result["chart_type"] == "pie"
    
    @pytest.mark.asyncio
    async def test_output_formats(self, tool):
        """Test different output formats"""
        params = {
            "chart_type": "line",
            "data": {"values": [1, 2, 3, 4, 5]},
            "output_format": "html"
        }
        
        result = await tool.execute(params)
        assert result["success"] is True
        assert result["output_format"] == "html"
        assert "data" in result
    
    def test_chart_generation_methods(self, tool):
        """Test individual chart generation methods"""
        data = {"values": [1, 2, 3, 4, 5]}
        
        line_chart = tool._generate_line_chart(data, "Title", "X", "Y", 800, 600)
        assert line_chart["type"] == "line"
        assert line_chart["title"] == "Title"
        
        bar_chart = tool._generate_bar_chart(data, "Title", "X", "Y", 800, 600)
        assert bar_chart["type"] == "bar"
        
        pie_chart = tool._generate_pie_chart(data, "Title", 800, 600)
        assert pie_chart["type"] == "pie"

class TestTextProcessorTool:
    """Test cases for TextProcessorTool"""
    
    @pytest.fixture
    def tool(self):
        return TextProcessorTool()
    
    def test_initialization(self, tool):
        """Test tool initialization"""
        assert tool.name == "text_processor"
        assert tool.tool_type == ToolType.TEXT_PROCESSOR
        assert "operation" in tool.parameters_schema
    
    def test_validate_parameters(self, tool):
        """Test parameter validation"""
        # Valid parameters
        valid_params = {
            "operation": "analyze",
            "text": "This is a test text."
        }
        assert tool.validate_parameters(valid_params) is True
        
        # Invalid operation
        invalid_params = {
            "operation": "invalid_operation",
            "text": "Test text"
        }
        assert tool.validate_parameters(invalid_params) is False
        
        # Empty text
        invalid_params = {
            "operation": "analyze",
            "text": ""
        }
        assert tool.validate_parameters(invalid_params) is False
    
    @pytest.mark.asyncio
    async def test_execute_analyze_text(self, tool):
        """Test text analysis operation"""
        result = await tool.execute({
            "operation": "analyze",
            "text": "This is a test sentence. It has multiple words.",
            "language": "en"
        })
        
        assert result["success"] is True
        assert result["operation"] == "analyze"
        assert "result" in result
        assert "statistics" in result["result"]
    
    @pytest.mark.asyncio
    async def test_execute_summarize_text(self, tool):
        """Test text summarization operation"""
        long_text = "This is a very long text that contains many words and should be summarized. " * 10
        
        result = await tool.execute({
            "operation": "summarize",
            "text": long_text,
            "max_length": 50
        })
        
        assert result["success"] is True
        assert result["operation"] == "summarize"
        assert len(result["result"]["summary"].split()) <= 50
    
    @pytest.mark.asyncio
    async def test_execute_extract_keywords(self, tool):
        """Test keyword extraction operation"""
        result = await tool.execute({
            "operation": "extract_keywords",
            "text": "The quick brown fox jumps over the lazy dog. The fox is quick and brown.",
            "language": "en"
        })
        
        assert result["success"] is True
        assert result["operation"] == "extract_keywords"
        assert "keywords" in result["result"]
        assert len(result["result"]["keywords"]) > 0
    
    @pytest.mark.asyncio
    async def test_execute_sentiment_analysis(self, tool):
        """Test sentiment analysis operation"""
        positive_text = "I love this product! It's amazing and wonderful."
        negative_text = "I hate this product. It's terrible and awful."
        
        positive_result = await tool.execute({
            "operation": "sentiment",
            "text": positive_text
        })
        
        negative_result = await tool.execute({
            "operation": "sentiment",
            "text": negative_text
        })
        
        assert positive_result["success"] is True
        assert negative_result["success"] is True
        
        # Check that sentiment scores are different
        positive_score = positive_result["result"]["sentiment_score"]
        negative_score = negative_result["result"]["sentiment_score"]
        assert positive_score > negative_score
    
    @pytest.mark.asyncio
    async def test_execute_clean_text(self, tool):
        """Test text cleaning operation"""
        dirty_text = "  This   text   has   extra   spaces   and   special   chars!@#$%   "
        
        result = await tool.execute({
            "operation": "clean",
            "text": dirty_text
        })
        
        assert result["success"] is True
        assert result["operation"] == "clean"
        cleaned_text = result["result"]["cleaned_text"]
        assert "  " not in cleaned_text  # No double spaces
    
    def test_text_analysis_methods(self, tool):
        """Test individual text analysis methods"""
        text = "This is a test text. It has multiple sentences and words."
        
        # Test text analysis
        analysis = tool._analyze_text(text, "en", True)
        assert "statistics" in analysis
        assert analysis["statistics"]["words"] == 12
        assert analysis["statistics"]["sentences"] == 2
        
        # Test keyword extraction
        keywords = tool._extract_keywords(text, "en", True)
        assert "keywords" in keywords
        assert len(keywords["keywords"]) > 0
        
        # Test sentiment analysis
        sentiment = tool._analyze_sentiment(text, True)
        assert "sentiment" in sentiment
        assert "sentiment_score" in sentiment

class TestToolIntegration:
    """Test cases for tool integration"""
    
    @pytest.mark.asyncio
    async def test_tool_timeout_handling(self):
        """Test tool timeout handling"""
        tool = DataFetcherTool()
        
        # Mock a slow operation
        async def slow_operation(params):
            await asyncio.sleep(2)
            return {"success": True}
        
        tool.execute = slow_operation
        
        with pytest.raises(asyncio.TimeoutError):
            await tool.execute_with_timeout({}, timeout=1)
    
    @pytest.mark.asyncio
    async def test_tool_error_handling(self):
        """Test tool error handling"""
        tool = DataFetcherTool()
        
        # Mock an operation that raises an exception
        async def error_operation(params):
            raise ValueError("Test error")
        
        tool.execute = error_operation
        
        with pytest.raises(ValueError, match="Test error"):
            await tool.execute_with_timeout({})
    
    def test_tool_health_check(self):
        """Test tool health checking"""
        tool = DataFetcherTool()
        assert tool.health_check() is True
        
        # Test unhealthy tool
        tool.is_available = False
        assert tool.health_check() is False

@pytest.mark.asyncio
async def test_tool_concurrent_execution():
    """Test concurrent tool execution"""
    tool = DataFetcherTool()
    
    # Mock the execute method to simulate work
    async def mock_execute(params):
        await asyncio.sleep(0.1)
        return {"success": True, "data": "test"}
    
    tool.execute = mock_execute
    
    # Execute multiple operations concurrently
    tasks = [
        tool.execute_with_timeout({"source_type": "http", "source": "test1"}),
        tool.execute_with_timeout({"source_type": "http", "source": "test2"}),
        tool.execute_with_timeout({"source_type": "http", "source": "test3"})
    ]
    
    results = await asyncio.gather(*tasks)
    
    assert len(results) == 3
    for result in results:
        assert result["success"] is True
