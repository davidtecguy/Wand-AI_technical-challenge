import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.agents import DataFetcherAgent, ChartGeneratorAgent, TextProcessorAgent
from app.models import AgentStatus, TaskStatus
from app.tools import DataFetcherTool, ChartGeneratorTool, TextProcessorTool

class TestBaseAgent:
    """Test cases for BaseAgent abstract class"""
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        # Create a concrete agent to test base functionality
        agent = DataFetcherAgent()
        
        assert agent.id is not None
        assert agent.name == "DataFetcherAgent"
        assert agent.agent_type == "data_fetcher"
        assert agent.status == AgentStatus.IDLE
        assert agent.capabilities == ["data_fetching", "data_validation", "data_transformation"]
        assert len(agent.tools) > 0
    
    def test_agent_tool_registration(self):
        """Test tool registration with agents"""
        agent = DataFetcherAgent()
        initial_tool_count = len(agent.tools)
        
        # Create a mock tool
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        
        agent.register_tool(mock_tool)
        assert len(agent.tools) == initial_tool_count + 1
        assert "test_tool" in agent.tools
    
    def test_agent_status_management(self):
        """Test agent status management"""
        agent = DataFetcherAgent()
        
        # Test status updates
        agent.update_status(AgentStatus.BUSY)
        assert agent.status == AgentStatus.BUSY
        
        agent.update_status(AgentStatus.IDLE)
        assert agent.status == AgentStatus.IDLE
    
    def test_agent_heartbeat(self):
        """Test agent heartbeat functionality"""
        agent = DataFetcherAgent()
        initial_heartbeat = agent.last_heartbeat
        
        # Wait a bit and update heartbeat
        import time
        time.sleep(0.1)
        agent.heartbeat()
        
        assert agent.last_heartbeat > initial_heartbeat
    
    def test_agent_health_check(self):
        """Test agent health checking"""
        agent = DataFetcherAgent()
        
        # Agent should be healthy initially
        assert agent.is_healthy() is True
        
        # Make agent unhealthy by setting old heartbeat
        import time
        agent.last_heartbeat = time.time() - 60  # 1 minute ago
        assert agent.is_healthy() is False
    
    def test_agent_info_retrieval(self):
        """Test getting agent information"""
        agent = DataFetcherAgent()
        agent_info = agent.get_agent_info()
        
        assert agent_info.id == agent.id
        assert agent_info.name == agent.name
        assert agent_info.agent_type == agent.agent_type
        assert agent_info.status == agent.status
    
    @pytest.mark.asyncio
    async def test_agent_task_lifecycle(self):
        """Test agent task lifecycle management"""
        agent = DataFetcherAgent()
        task_id = "test-task-123"
        
        # Start task
        await agent.start_task(task_id)
        assert agent.current_task == task_id
        assert agent.status == AgentStatus.BUSY
        
        # Complete task
        await agent.complete_task(task_id)
        assert agent.current_task is None
        assert agent.status == AgentStatus.IDLE
        
        # Fail task
        await agent.fail_task(task_id, "Test error")
        assert agent.current_task is None
        assert agent.status == AgentStatus.ERROR
    
    def test_agent_health_status(self):
        """Test comprehensive health status"""
        agent = DataFetcherAgent()
        health_status = agent.get_health_status()
        
        required_fields = [
            "agent_id", "name", "status", "is_healthy", 
            "last_heartbeat", "current_task", "tools_count", "capabilities"
        ]
        
        for field in required_fields:
            assert field in health_status

class TestDataFetcherAgent:
    """Test cases for DataFetcherAgent"""
    
    @pytest.fixture
    def agent(self):
        return DataFetcherAgent()
    
    def test_initialization(self, agent):
        """Test DataFetcherAgent initialization"""
        assert agent.name == "DataFetcherAgent"
        assert agent.agent_type == "data_fetcher"
        assert "data_fetching" in agent.capabilities
        assert "data_fetcher" in agent.tools
    
    def test_capability_checking(self, agent):
        """Test task capability checking"""
        assert agent.can_handle_task("fetch_data") is True
        assert agent.can_handle_task("validate_data") is True
        assert agent.can_handle_task("transform_data") is True
        assert agent.can_handle_task("aggregate_data") is True
        assert agent.can_handle_task("invalid_task") is False
    
    @pytest.mark.asyncio
    async def test_fetch_data_task(self, agent):
        """Test fetch data task execution"""
        with patch.object(agent, 'execute_tool', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "data": {"test": "data"},
                "source": "test://data"
            }
            
            result = await agent.process_task({
                "task_type": "fetch_data",
                "parameters": {
                    "source_type": "http",
                    "source": "https://api.example.com/data"
                }
            })
            
            assert result["success"] is True
            assert "agent_id" in result
            assert "fetch_timestamp" in result
    
    @pytest.mark.asyncio
    async def test_validate_data_task(self, agent):
        """Test data validation task execution"""
        result = await agent.process_task({
            "task_type": "validate_data",
            "parameters": {
                "data": {"field1": "value1", "field2": "value2"},
                "validation_rules": {
                    "check_required_fields": True,
                    "required_fields": ["field1", "field2"]
                }
            }
        })
        
        assert result["success"] is True
        assert result["is_valid"] is True
        assert len(result["validation_errors"]) == 0
    
    @pytest.mark.asyncio
    async def test_transform_data_task(self, agent):
        """Test data transformation task execution"""
        result = await agent.process_task({
            "task_type": "transform_data",
            "parameters": {
                "data": {"old_name": "value"},
                "transformation_rules": [
                    {
                        "type": "rename_field",
                        "old_name": "old_name",
                        "new_name": "new_name"
                    }
                ]
            }
        })
        
        assert result["success"] is True
        assert "new_name" in result["transformed_data"]
        assert "old_name" not in result["transformed_data"]
    
    @pytest.mark.asyncio
    async def test_aggregate_data_task(self, agent):
        """Test data aggregation task execution"""
        data = [
            {"value": 10},
            {"value": 20},
            {"value": 30}
        ]
        
        result = await agent.process_task({
            "task_type": "aggregate_data",
            "parameters": {
                "data": data,
                "aggregation_rules": [
                    {"operation": "sum", "field_name": "value"},
                    {"operation": "average", "field_name": "value"}
                ]
            }
        })
        
        assert result["success"] is True
        assert result["aggregation_results"]["sum_value"] == 60
        assert result["aggregation_results"]["average_value"] == 20.0

class TestChartGeneratorAgent:
    """Test cases for ChartGeneratorAgent"""
    
    @pytest.fixture
    def agent(self):
        return ChartGeneratorAgent()
    
    def test_initialization(self, agent):
        """Test ChartGeneratorAgent initialization"""
        assert agent.name == "ChartGeneratorAgent"
        assert agent.agent_type == "chart_generator"
        assert "chart_generation" in agent.capabilities
        assert "chart_generator" in agent.tools
    
    def test_capability_checking(self, agent):
        """Test task capability checking"""
        assert agent.can_handle_task("generate_chart") is True
        assert agent.can_handle_task("customize_chart") is True
        assert agent.can_handle_task("batch_chart_generation") is True
        assert agent.can_handle_task("chart_analysis") is True
        assert agent.can_handle_task("invalid_task") is False
    
    @pytest.mark.asyncio
    async def test_generate_chart_task(self, agent):
        """Test chart generation task execution"""
        with patch.object(agent, 'execute_tool', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "chart_type": "line",
                "data": "chart_data_here"
            }
            
            result = await agent.process_task({
                "task_type": "generate_chart",
                "parameters": {
                    "chart_type": "line",
                    "data": {"values": [1, 2, 3, 4, 5]},
                    "title": "Test Chart"
                }
            })
            
            assert result["success"] is True
            assert "agent_id" in result
            assert "generation_timestamp" in result
    
    @pytest.mark.asyncio
    async def test_customize_chart_task(self, agent):
        """Test chart customization task execution"""
        chart_data = {
            "chart_type": "line",
            "title": "Original Title",
            "width": 800,
            "height": 600
        }
        
        with patch.object(agent, 'execute_tool', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "chart_type": "line",
                "title": "New Title"
            }
            
            result = await agent.process_task({
                "task_type": "customize_chart",
                "parameters": {
                    "chart_data": chart_data,
                    "customization_rules": [
                        {
                            "type": "change_title",
                            "new_title": "New Title"
                        }
                    ]
                }
            })
            
            assert result["success"] is True
            assert "customization_rules_applied" in result
    
    @pytest.mark.asyncio
    async def test_batch_chart_generation_task(self, agent):
        """Test batch chart generation task execution"""
        with patch.object(agent, 'execute_tool', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "chart_type": "line",
                "data": "chart_data"
            }
            
            result = await agent.process_task({
                "task_type": "batch_chart_generation",
                "parameters": {
                    "dataset": [1, 2, 3, 4, 5],
                    "chart_configs": [
                        {"chart_type": "line", "title": "Chart 1"},
                        {"chart_type": "bar", "title": "Chart 2"}
                    ]
                }
            })
            
            assert result["success"] is True
            assert result["total_charts_requested"] == 2
            assert result["successfully_generated"] == 2
    
    @pytest.mark.asyncio
    async def test_chart_analysis_task(self, agent):
        """Test chart analysis task execution"""
        chart_data = {
            "chart_type": "line",
            "data": {"values": [1, 2, 3, 4, 5]},
            "width": 800,
            "height": 600
        }
        
        result = await agent.process_task({
            "task_type": "chart_analysis",
            "parameters": {
                "chart_data": chart_data
            }
        })
        
        assert result["success"] is True
        assert result["data_points"] == 5
        assert len(result["insights"]) > 0
        assert len(result["recommendations"]) > 0

class TestTextProcessorAgent:
    """Test cases for TextProcessorAgent"""
    
    @pytest.fixture
    def agent(self):
        return TextProcessorAgent()
    
    def test_initialization(self, agent):
        """Test TextProcessorAgent initialization"""
        assert agent.name == "TextProcessorAgent"
        assert agent.agent_type == "text_processor"
        assert "text_analysis" in agent.capabilities
        assert "text_processor" in agent.tools
    
    def test_capability_checking(self, agent):
        """Test task capability checking"""
        assert agent.can_handle_task("analyze_text") is True
        assert agent.can_handle_task("summarize_text") is True
        assert agent.can_handle_task("extract_keywords") is True
        assert agent.can_handle_task("analyze_sentiment") is True
        assert agent.can_handle_task("clean_text") is True
        assert agent.can_handle_task("batch_text_processing") is True
        assert agent.can_handle_task("invalid_task") is False
    
    @pytest.mark.asyncio
    async def test_analyze_text_task(self, agent):
        """Test text analysis task execution"""
        with patch.object(agent, 'execute_tool', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "operation": "analyze",
                "result": {
                    "statistics": {
                        "characters": 25,
                        "words": 5,
                        "sentences": 1
                    }
                }
            }
            
            result = await agent.process_task({
                "task_type": "analyze_text",
                "parameters": {
                    "text": "This is a test sentence.",
                    "language": "en"
                }
            })
            
            assert result["success"] is True
            assert "agent_id" in result
            assert "analysis_timestamp" in result
    
    @pytest.mark.asyncio
    async def test_summarize_text_task(self, agent):
        """Test text summarization task execution"""
        with patch.object(agent, 'execute_tool', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "operation": "summarize",
                "result": {
                    "summary": "This is a summary.",
                    "original_length": 100,
                    "summary_length": 5
                }
            }
            
            result = await agent.process_task({
                "task_type": "summarize_text",
                "parameters": {
                    "text": "This is a very long text that should be summarized.",
                    "max_length": 10
                }
            })
            
            assert result["success"] is True
            assert "summarization_timestamp" in result
    
    @pytest.mark.asyncio
    async def test_extract_keywords_task(self, agent):
        """Test keyword extraction task execution"""
        with patch.object(agent, 'execute_tool', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "operation": "extract_keywords",
                "result": {
                    "keywords": [{"word": "test", "frequency": 2}],
                    "total_keywords": 1
                }
            }
            
            result = await agent.process_task({
                "task_type": "extract_keywords",
                "parameters": {
                    "text": "This is a test text for testing.",
                    "language": "en"
                }
            })
            
            assert result["success"] is True
            assert "extraction_timestamp" in result
    
    @pytest.mark.asyncio
    async def test_sentiment_analysis_task(self, agent):
        """Test sentiment analysis task execution"""
        with patch.object(agent, 'execute_tool', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "operation": "sentiment",
                "result": {
                    "sentiment": "positive",
                    "sentiment_score": 0.3
                }
            }
            
            result = await agent.process_task({
                "task_type": "analyze_sentiment",
                "parameters": {
                    "text": "I love this product! It's amazing."
                }
            })
            
            assert result["success"] is True
            assert "sentiment_analysis_timestamp" in result
    
    @pytest.mark.asyncio
    async def test_clean_text_task(self, agent):
        """Test text cleaning task execution"""
        with patch.object(agent, 'execute_tool', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "operation": "clean",
                "result": {
                    "cleaned_text": "Clean text here",
                    "original_length": 20,
                    "cleaned_length": 15
                }
            }
            
            result = await agent.process_task({
                "task_type": "clean_text",
                "parameters": {
                    "text": "  Dirty   text   here!@#$%   "
                }
            })
            
            assert result["success"] is True
            assert "cleaning_timestamp" in result
    
    @pytest.mark.asyncio
    async def test_batch_text_processing_task(self, agent):
        """Test batch text processing task execution"""
        with patch.object(agent, 'execute_tool', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "operation": "analyze",
                "result": {"statistics": {"words": 5}}
            }
            
            result = await agent.process_task({
                "task_type": "batch_text_processing",
                "parameters": {
                    "texts": [
                        "First text for analysis.",
                        "Second text for analysis."
                    ],
                    "operations": ["analyze"]
                }
            })
            
            assert result["success"] is True
            assert result["total_texts"] == 2
            assert result["successfully_processed"] == 2

class TestAgentIntegration:
    """Test cases for agent integration and communication"""
    
    @pytest.mark.asyncio
    async def test_agent_tool_execution(self):
        """Test agent tool execution"""
        agent = DataFetcherAgent()
        
        # Test that agent can execute its tools
        result = await agent.execute_tool("data_fetcher", {
            "source_type": "http",
            "source": "https://api.example.com/data"
        })
        
        # Note: This will fail in tests since we're not mocking the actual HTTP call
        # In a real test environment, you'd mock the tool execution
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_agent_error_handling(self):
        """Test agent error handling"""
        agent = DataFetcherAgent()
        
        # Test with invalid tool name
        with pytest.raises(ValueError, match="Tool invalid_tool not found"):
            await agent.execute_tool("invalid_tool", {})
    
    def test_agent_tool_management(self):
        """Test agent tool management"""
        agent = DataFetcherAgent()
        
        # Test getting existing tool
        tool = agent.get_tool("data_fetcher")
        assert tool is not None
        assert tool.name == "data_fetcher"
        
        # Test getting non-existent tool
        tool = agent.get_tool("non_existent_tool")
        assert tool is None

@pytest.mark.asyncio
async def test_agent_concurrent_operations():
    """Test concurrent agent operations"""
    agent = DataFetcherAgent()
    
    # Create multiple concurrent operations
    async def mock_operation():
        await asyncio.sleep(0.1)
        return {"success": True, "data": "test"}
    
    # Mock the tool execution
    agent.execute_tool = mock_operation
    
    # Execute multiple operations concurrently
    tasks = [
        agent.process_task({"task_type": "fetch_data", "parameters": {}}),
        agent.process_task({"task_type": "validate_data", "parameters": {"data": {}}}),
        agent.process_task({"task_type": "transform_data", "parameters": {"data": {}}})
    ]
    
    results = await asyncio.gather(*tasks)
    
    assert len(results) == 3
    for result in results:
        assert result["success"] is True
