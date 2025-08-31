# Multi-Agent Task Solver

A sophisticated backend system for orchestrating AI agents that can work together to solve complex tasks while maintaining isolation and enabling dynamic tool integration.

## 🏗️ Architecture Overview

The system is built with a modular, event-driven architecture that supports:

- **Agent Isolation**: Each agent runs in its own process/container
- **Dynamic Tool Integration**: Pluggable tools that agents can use
- **Concurrent Execution**: Multiple agents can run simultaneously
- **Fault Tolerance**: Retry logic, timeouts, and error handling
- **Scalable API**: RESTful interface for frontend consumption

## 🎯 Core Components

### 1. Agent Base Class
- Abstract base for all agents
- Standardized communication interface
- Tool integration capabilities

### 2. Agent Orchestrator
- Manages agent lifecycle
- Handles inter-agent communication
- Implements execution graph logic

### 3. Tool System
- Pluggable tool architecture
- Standardized tool interface
- Built-in tools (data fetcher, chart generator, etc.)

### 4. API Layer
- FastAPI-based REST endpoints
- Async request handling
- Real-time status updates

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Redis server
- Docker (optional)

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd Wand-AI_technical-challenge

# Install dependencies
pip install -r requirements.txt

# Start Redis (if not running)
redis-server

# Run the system
python -m uvicorn app.main:app --reload
```

### Basic Usage
```python
from app.orchestrator import AgentOrchestrator
from app.agents import DataFetcherAgent, ChartGeneratorAgent

# Create orchestrator
orchestrator = AgentOrchestrator()

# Define execution graph
execution_graph = {
    "data_fetcher": DataFetcherAgent,
    "chart_generator": ChartGeneratorAgent,
    "dependencies": [("data_fetcher", "chart_generator")]
}

# Execute task
result = await orchestrator.execute_task(
    "analyze_sales_data",
    execution_graph,
    {"query": "Q4 sales performance"}
)
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_orchestrator.py
```

## 📡 API Endpoints

- `POST /tasks` - Create and execute a new task
- `GET /tasks/{task_id}` - Get task status and results
- `GET /agents` - List available agents
- `GET /tools` - List available tools
- `POST /tools` - Register a new tool

## 🔧 Configuration

Environment variables:
- `REDIS_URL`: Redis connection string
- `MAX_CONCURRENT_AGENTS`: Maximum agents running simultaneously
- `AGENT_TIMEOUT`: Default agent timeout in seconds
- `RETRY_ATTEMPTS`: Number of retry attempts for failed agents

## 🏗️ Design Decisions & Trade-offs

### Made Due to 24h Constraint:
1. **Simplified Persistence**: Using Redis instead of a full database
2. **Basic Error Handling**: Focused on core functionality over edge cases
3. **Limited Tool Set**: Started with essential tools, extensible for more
4. **Async-First**: Chose asyncio for better concurrency handling

### Architecture Choices:
1. **Event-Driven**: Better scalability and loose coupling
2. **Tool Plugins**: Easy to extend without modifying core code
3. **Process Isolation**: Agents run separately for security and stability
4. **Graph-Based Execution**: Clear dependency management

## 🚀 Future Enhancements

- [ ] Kubernetes deployment support
- [ ] Advanced monitoring and metrics
- [ ] Machine learning-based agent optimization
- [ ] WebSocket support for real-time updates
- [ ] Advanced tool marketplace
- [ ] Multi-tenant support

## 📝 License

MIT License - see LICENSE file for details
