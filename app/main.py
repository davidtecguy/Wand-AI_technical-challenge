from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.models import TaskRequest, TaskResponse
from app.orchestrator import AgentOrchestrator
from app.tools import BaseTool
import logging
import asyncio
from contextlib import asynccontextmanager
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global orchestrator instance
orchestrator: AgentOrchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    global orchestrator
    
    # Startup
    logger.info("Starting Multi-Agent Task Solver...")
    
    # Initialize orchestrator
    max_concurrent = int(os.getenv("MAX_CONCURRENT_AGENTS", "5"))
    agent_timeout = int(os.getenv("AGENT_TIMEOUT", "300"))
    
    orchestrator = AgentOrchestrator(
        max_concurrent_agents=max_concurrent,
        agent_timeout=agent_timeout
    )
    
    logger.info(f"Orchestrator initialized with {max_concurrent} max concurrent agents")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Multi-Agent Task Solver...")
    if orchestrator:
        await orchestrator.shutdown()

# Create FastAPI app
app = FastAPI(
    title="Multi-Agent Task Solver",
    description="A sophisticated system for orchestrating AI agents to solve complex tasks",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "Multi-Agent Task Solver API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "tasks": "/tasks",
            "agents": "/agents",
            "tools": "/tools",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """System health check"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    try:
        agent_health = orchestrator.get_agent_health()
        total_agents = len(agent_health)
        healthy_agents = sum(1 for status in agent_health.values() if status["is_healthy"])
        
        return {
            "status": "healthy",
            "orchestrator": "running",
            "agents": {
                "total": total_agents,
                "healthy": healthy_agents,
                "unhealthy": total_agents - healthy_agents
            },
            "timestamp": str(datetime.utcnow())
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@app.post("/tasks", response_model=TaskResponse)
async def create_task(task_request: TaskRequest, background_tasks: BackgroundTasks):
    """Create and execute a new task"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    try:
        # Execute task in background
        task_id = await orchestrator.execute_task(
            task_name=task_request.name,
            execution_graph=task_request.execution_graph,
            parameters=task_request.parameters,
            timeout=task_request.timeout
        )
        
        return TaskResponse(
            task_id=task_id,
            status="pending",
            message=f"Task '{task_request.name}' created successfully",
            estimated_completion=None
        )
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get task status and results"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    try:
        status = await orchestrator.get_task_status(task_id)
        if not status:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks")
async def list_tasks():
    """List all tasks"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    try:
        tasks = []
        for task_id, task in orchestrator.tasks.items():
            task_info = {
                "task_id": task_id,
                "name": task.name,
                "status": task.status,
                "created_at": task.created_at,
                "started_at": task.started_at,
                "completed_at": task.completed_at
            }
            tasks.append(task_info)
        
        return {"tasks": tasks, "total": len(tasks)}
        
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents")
async def list_agents():
    """List all available agents"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    try:
        agents = orchestrator.get_available_agents()
        return {"agents": agents, "total": len(agents)}
        
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/{agent_id}")
async def get_agent_details(agent_id: str):
    """Get detailed information about a specific agent"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    try:
        agents = orchestrator.get_available_agents()
        agent = next((a for a in agents if a["id"] == agent_id), None)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools")
async def list_tools():
    """List all available tools"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    try:
        tools = []
        for agent in orchestrator.agents.values():
            for tool_name, tool in agent.tools.items():
                tool_info = tool.get_tool_info().dict()
                tool_info["agent_id"] = agent.id
                tool_info["agent_name"] = agent.name
                tools.append(tool_info)
        
        return {"tools": tools, "total": len(tools)}
        
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools")
async def register_tool(tool_data: dict):
    """Register a new tool with the system"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    try:
        # This is a simplified tool registration
        # In production, you'd want proper tool validation and instantiation
        logger.info(f"Tool registration requested: {tool_data}")
        
        return {
            "message": "Tool registration endpoint - implement custom tool logic here",
            "tool_data": tool_data
        }
        
    except Exception as e:
        logger.error(f"Error registering tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/examples")
async def get_examples():
    """Get example task configurations"""
    examples = {
        "data_analysis_pipeline": {
            "name": "Data Analysis Pipeline",
            "description": "Fetch data, analyze it, and generate charts",
            "execution_graph": {
                "data_fetcher": {
                    "agent_type": "data_fetcher",
                    "parameters": {
                        "source_type": "http",
                        "source": "https://api.example.com/data"
                    }
                },
                "chart_generator": {
                    "agent_type": "chart_generator",
                    "parameters": {
                        "chart_type": "line",
                        "title": "Data Analysis Chart"
                    },
                    "dependencies": ["data_fetcher"]
                }
            }
        },
        "text_analysis": {
            "name": "Text Analysis",
            "description": "Analyze text sentiment and extract keywords",
            "execution_graph": {
                "text_processor": {
                    "agent_type": "text_processor",
                    "parameters": {
                        "task_type": "analyze_sentiment",
                        "text": "This is a sample text for analysis"
                    }
                }
            }
        }
    }
    
    return {"examples": examples}

@app.post("/execute-example/{example_name}")
async def execute_example(example_name: str):
    """Execute a predefined example task"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    try:
        examples = await get_examples()
        example = examples["examples"].get(example_name)
        
        if not example:
            raise HTTPException(status_code=404, detail="Example not found")
        
        # Execute the example
        task_id = await orchestrator.execute_task(
            task_name=example["name"],
            execution_graph=example["execution_graph"],
            parameters={}
        )
        
        return {
            "message": f"Example '{example_name}' executed successfully",
            "task_id": task_id,
            "example": example
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing example: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

