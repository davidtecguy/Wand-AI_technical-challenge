import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from app.orchestrator import AgentOrchestrator
from app.agents import DataFetcherAgent, ChartGeneratorAgent, TextProcessorAgent
from app.models import TaskStatus, AgentStatus

@pytest.fixture
def orchestrator():
    """Create a test orchestrator instance"""
    return AgentOrchestrator(max_concurrent_agents=2, agent_timeout=10)

@pytest.fixture
def sample_execution_graph():
    """Sample execution graph for testing"""
    return {
        "data_fetcher": {
            "agent_type": "data_fetcher",
            "parameters": {"source": "test://data"},
            "dependencies": []
        },
        "chart_generator": {
            "agent_type": "chart_generator",
            "parameters": {"chart_type": "line"},
            "dependencies": ["data_fetcher"]
        }
    }

class TestAgentOrchestrator:
    """Test cases for AgentOrchestrator"""
    
    def test_initialization(self, orchestrator):
        """Test orchestrator initialization"""
        assert orchestrator.max_concurrent_agents == 2
        assert orchestrator.agent_timeout == 10
        assert len(orchestrator.agents) == 3  # Default agents
        assert orchestrator.semaphore._value == 2
    
    def test_register_agent(self, orchestrator):
        """Test agent registration"""
        mock_agent = Mock()
        mock_agent.id = "test-agent"
        mock_agent.name = "TestAgent"
        
        orchestrator.register_agent(mock_agent)
        assert "test-agent" in orchestrator.agents
        assert orchestrator.agents["test-agent"] == mock_agent
    
    def test_parse_execution_graph(self, orchestrator, sample_execution_graph):
        """Test execution graph parsing"""
        parsed_graph = orchestrator._parse_execution_graph(sample_execution_graph)
        
        assert len(parsed_graph.nodes) == 2
        assert "data_fetcher" in parsed_graph.nodes
        assert "chart_generator" in parsed_graph.nodes
        assert len(parsed_graph.edges) == 1
        assert parsed_graph.entry_points == ["data_fetcher"]
        assert parsed_graph.exit_points == ["chart_generator"]
    
    def test_find_agent_by_type(self, orchestrator):
        """Test finding agents by type"""
        agent = orchestrator._find_agent_by_type("data_fetcher")
        assert agent is not None
        assert agent.agent_type == "data_fetcher"
        
        # Test with non-existent type
        agent = orchestrator._find_agent_by_type("non_existent")
        assert agent is None
    
    @pytest.mark.asyncio
    async def test_execute_task(self, orchestrator, sample_execution_graph):
        """Test task execution"""
        task_id = await orchestrator.execute_task(
            "test_task",
            sample_execution_graph,
            {"param": "value"}
        )
        
        assert task_id in orchestrator.tasks
        assert orchestrator.tasks[task_id].name == "test_task"
        assert orchestrator.tasks[task_id].status == TaskStatus.PENDING
    
    @pytest.mark.asyncio
    async def test_get_task_status(self, orchestrator, sample_execution_graph):
        """Test getting task status"""
        task_id = await orchestrator.execute_task("test_task", sample_execution_graph)
        
        # Wait a bit for task to start
        await asyncio.sleep(0.1)
        
        status = await orchestrator.get_task_status(task_id)
        assert status is not None
        assert status["task_id"] == task_id
        assert status["name"] == "test_task"
    
    def test_get_available_agents(self, orchestrator):
        """Test getting available agents"""
        agents = orchestrator.get_available_agents()
        assert len(agents) == 3
        
        # Check that all agents have required fields
        for agent in agents:
            assert "id" in agent
            assert "name" in agent
            assert "agent_type" in agent
            assert "status" in agent
    
    def test_get_agent_health(self, orchestrator):
        """Test getting agent health status"""
        health = orchestrator.get_agent_health()
        assert len(health) == 3
        
        for agent_id, status in health.items():
            assert "agent_id" in status
            assert "name" in status
            assert "status" in status
            assert "is_healthy" in status
    
    @pytest.mark.asyncio
    async def test_send_message(self, orchestrator):
        """Test sending messages between agents"""
        message_id = await orchestrator.send_message(
            "agent1",
            "agent2",
            "test_message",
            {"data": "test"}
        )
        
        assert message_id is not None
        assert isinstance(message_id, str)
    
    @pytest.mark.asyncio
    async def test_shutdown(self, orchestrator):
        """Test orchestrator shutdown"""
        await orchestrator.shutdown()
        # Should complete without errors

class TestExecutionGraph:
    """Test cases for execution graph functionality"""
    
    def test_simple_dependency_graph(self, orchestrator):
        """Test simple dependency graph"""
        graph = {
            "step1": "data_fetcher",
            "step2": {
                "agent_type": "chart_generator",
                "dependencies": ["step1"]
            }
        }
        
        parsed = orchestrator._parse_execution_graph(graph)
        assert len(parsed.nodes) == 2
        assert len(parsed.edges) == 1
        assert parsed.entry_points == ["step1"]
        assert parsed.exit_points == ["step2"]
    
    def test_complex_dependency_graph(self, orchestrator):
        """Test complex dependency graph"""
        graph = {
            "fetch": "data_fetcher",
            "process": {
                "agent_type": "text_processor",
                "dependencies": ["fetch"]
            },
            "visualize": {
                "agent_type": "chart_generator",
                "dependencies": ["fetch", "process"]
            }
        }
        
        parsed = orchestrator._parse_execution_graph(graph)
        assert len(parsed.nodes) == 3
        assert len(parsed.edges) == 3
        assert parsed.entry_points == ["fetch"]
        assert "visualize" in parsed.exit_points
    
    def test_circular_dependency_detection(self, orchestrator):
        """Test circular dependency detection"""
        graph = {
            "step1": {
                "agent_type": "data_fetcher",
                "dependencies": ["step2"]
            },
            "step2": {
                "agent_type": "chart_generator",
                "dependencies": ["step1"]
            }
        }
        
        # This should raise an error due to circular dependency
        with pytest.raises(ValueError, match="Circular dependency"):
            orchestrator._parse_execution_graph(graph)

class TestAgentIntegration:
    """Test cases for agent integration"""
    
    @pytest.mark.asyncio
    async def test_data_fetcher_agent_integration(self, orchestrator):
        """Test data fetcher agent integration"""
        agent = orchestrator.agents[list(orchestrator.agents.keys())[0]]
        assert isinstance(agent, DataFetcherAgent)
        
        # Test agent capabilities
        assert agent.can_handle_task("fetch_data")
        assert not agent.can_handle_task("invalid_task")
        
        # Test tool registration
        assert "data_fetcher" in agent.tools
    
    @pytest.mark.asyncio
    async def test_chart_generator_agent_integration(self, orchestrator):
        """Test chart generator agent integration"""
        chart_agents = [a for a in orchestrator.agents.values() if isinstance(a, ChartGeneratorAgent)]
        assert len(chart_agents) == 1
        
        agent = chart_agents[0]
        assert agent.can_handle_task("generate_chart")
        assert "chart_generator" in agent.tools
    
    @pytest.mark.asyncio
    async def test_text_processor_agent_integration(self, orchestrator):
        """Test text processor agent integration"""
        text_agents = [a for a in orchestrator.agents.values() if isinstance(a, TextProcessorAgent)]
        assert len(text_agents) == 1
        
        agent = text_agents[0]
        assert agent.can_handle_task("analyze_text")
        assert "text_processor" in agent.tools

@pytest.mark.asyncio
async def test_concurrent_task_execution(orchestrator):
    """Test concurrent task execution"""
    # Create multiple simple tasks
    tasks = []
    for i in range(3):
        task_id = await orchestrator.execute_task(
            f"concurrent_task_{i}",
            {"step": "data_fetcher"}
        )
        tasks.append(task_id)
    
    # Wait for tasks to start
    await asyncio.sleep(0.1)
    
    # Check that tasks are created
    for task_id in tasks:
        assert task_id in orchestrator.tasks
    
    # Clean up
    await orchestrator.shutdown()

@pytest.mark.asyncio
async def test_task_with_parameters(orchestrator):
    """Test task execution with parameters"""
    execution_graph = {
        "data_fetcher": {
            "agent_type": "data_fetcher",
            "parameters": {
                "source_type": "http",
                "source": "https://api.example.com/data"
            }
        }
    }
    
    task_id = await orchestrator.execute_task(
        "parameterized_task",
        execution_graph,
        {"custom_param": "value"}
    )
    
    task = orchestrator.tasks[task_id]
    assert task.parameters == {"custom_param": "value"}
    
    # Clean up
    await orchestrator.shutdown()
