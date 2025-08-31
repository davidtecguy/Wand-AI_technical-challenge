from typing import Dict, Any, List, Optional, Type
from app.models import Task, TaskStatus, ExecutionGraph, ExecutionNode, AgentMessage, AgentStatus
from app.agents import BaseAgent, DataFetcherAgent, ChartGeneratorAgent, TextProcessorAgent
from app.tools import BaseTool
import asyncio
import logging
from datetime import datetime
import uuid
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Orchestrates the execution of tasks across multiple agents"""
    
    def __init__(self, max_concurrent_agents: int = 5, agent_timeout: int = 300):
        self.max_concurrent_agents = max_concurrent_agents
        self.agent_timeout = agent_timeout
        self.agents: Dict[str, BaseAgent] = {}
        self.tasks: Dict[str, Task] = {}
        self.execution_graphs: Dict[str, ExecutionGraph] = {}
        self.agent_assignments: Dict[str, str] = {}  # task_id -> agent_id
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.semaphore = asyncio.Semaphore(max_concurrent_agents)
        
        # Initialize default agents
        self._initialize_default_agents()
        
        logger.info(f"AgentOrchestrator initialized with max {max_concurrent_agents} concurrent agents")
    
    def get_tools(self) -> list[dict]:
        """Return all tools across agents with basic metadata"""
        tools: list[dict] = []
        for agent in self.agents.values():
            for tool in agent.tools.values():
                info = tool.get_tool_info().dict()
                info["agent_id"] = agent.id
                info["agent_name"] = agent.name
                tools.append(info)
        return tools

    def _initialize_default_agents(self):
        """Initialize the default set of agents"""
        default_agents = [
            DataFetcherAgent(),
            ChartGeneratorAgent(),
            TextProcessorAgent()
        ]
        
        for agent in default_agents:
            self.register_agent(agent)
    
    def register_agent(self, agent: BaseAgent):
        """Register a new agent with the orchestrator"""
        self.agents[agent.id] = agent
        logger.info(f"Agent {agent.name} ({agent.id}) registered with orchestrator")
    
    def register_tool(self, tool: BaseTool):
        """Register a tool with all agents that can use it"""
        for agent in self.agents.values():
            if tool.tool_type.value in agent.capabilities:
                agent.register_tool(tool)
                logger.info(f"Tool {tool.name} registered with agent {agent.name}")
    
    async def execute_task(self, task_name: str, execution_graph: Dict[str, Any], 
                          parameters: Dict[str, Any] = None, timeout: int = None) -> str:
        """Execute a task using the specified execution graph"""
        try:
            # Create task
            task = Task(
                name=task_name,
                execution_graph=execution_graph,
                parameters=parameters or {},
                max_retries=3
            )
            
            self.tasks[task.id] = task
            logger.info(f"Task {task.id} created: {task_name}")
            
            # Parse execution graph
            parsed_graph = self._parse_execution_graph(execution_graph)
            self.execution_graphs[task.id] = parsed_graph
            
            # Start task execution
            asyncio.create_task(self._execute_task_graph(task.id, parsed_graph))
            
            return task.id
            
        except Exception as e:
            logger.error(f"Error creating task {task_name}: {e}")
            raise
    
    def _parse_execution_graph(self, execution_graph: Dict[str, Any]) -> ExecutionGraph:
        """Parse the execution graph into a structured format"""
        nodes = {}
        edges = []
        entry_points = []
        exit_points = []
        
        # Parse nodes
        for node_name, node_config in execution_graph.items():
            if node_name == "dependencies":
                continue
                
            if isinstance(node_config, dict):
                # Node with configuration
                agent_type = node_config.get("agent_type", "unknown")
                node_params = node_config.get("parameters", {})
                dependencies = node_config.get("dependencies", [])
            else:
                # Simple agent type string
                agent_type = node_config
                node_params = {}
                dependencies = []
            
            # Find agent of this type
            agent = self._find_agent_by_type(agent_type)
            if not agent:
                raise ValueError(f"No agent found for type: {agent_type}")
            
            node = ExecutionNode(
                agent_id=agent.id,
                agent_type=agent_type,
                dependencies=dependencies,
                parameters=node_params
            )
            
            nodes[node_name] = node
            edges.extend([(dep, node_name) for dep in dependencies])
        
        # Find entry and exit points
        all_nodes = set(nodes.keys())
        dependent_nodes = set()
        for edge in edges:
            dependent_nodes.add(edge[1])
        
        entry_points = list(all_nodes - dependent_nodes)
        exit_points = list(all_nodes - {edge[0] for edge in edges})
        
        return ExecutionGraph(
            nodes=nodes,
            edges=edges,
            entry_points=entry_points,
            exit_points=exit_points
        )
    
    def _find_agent_by_type(self, agent_type: str) -> Optional[BaseAgent]:
        """Find an available agent of the specified type"""
        for agent in self.agents.values():
            if agent.agent_type == agent_type and agent.status in [AgentStatus.IDLE, AgentStatus.ERROR]:
                return agent
        return None
    
    async def _execute_task_graph(self, task_id: str, execution_graph: ExecutionGraph):
        """Execute the task graph"""
        task = self.tasks[task_id]
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        
        try:
            # Execute nodes in dependency order
            completed_nodes = set()
            node_results = {}
            
            while len(completed_nodes) < len(execution_graph.nodes):
                # Find nodes ready to execute
                ready_nodes = []
                for node_name, node in execution_graph.nodes.items():
                    if node_name in completed_nodes:
                        continue
                    
                    # Check if all dependencies are completed
                    if all(dep in completed_nodes for dep in node.dependencies):
                        ready_nodes.append((node_name, node))
                
                if not ready_nodes:
                    # Check for circular dependencies
                    if len(completed_nodes) == 0:
                        raise ValueError("Circular dependency detected in execution graph")
                    break
                
                # Execute ready nodes concurrently
                execution_tasks = []
                for node_name, node in ready_nodes:
                    execution_task = asyncio.create_task(
                        self._execute_node(task_id, node_name, node, node_results)
                    )
                    execution_tasks.append((node_name, execution_task))
                
                # Wait for all ready nodes to complete
                for node_name, execution_task in execution_tasks:
                    try:
                        result = await execution_task
                        node_results[node_name] = result
                        completed_nodes.add(node_name)
                        
                        # Update execution graph
                        execution_graph.nodes[node_name].status = TaskStatus.COMPLETED
                        execution_graph.nodes[node_name].result = result
                        execution_graph.nodes[node_name].completed_at = datetime.utcnow()
                        
                    except Exception as e:
                        logger.error(f"Node {node_name} execution failed: {e}")
                        execution_graph.nodes[node_name].status = TaskStatus.FAILED
                        execution_graph.nodes[node_name].error = str(e)
                        
                        # Handle retry logic
                        if task.retry_count < task.max_retries:
                            task.retry_count += 1
                            logger.info(f"Retrying task {task_id}, attempt {task.retry_count}")
                            # Could implement retry logic here
                        else:
                            raise e
            
            # Task completed successfully
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.results = node_results
            
            logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task_id} execution failed: {e}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
    
    async def _execute_node(self, task_id: str, node_name: str, node: ExecutionNode, 
                           node_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single node in the execution graph"""
        async with self.semaphore:
            try:
                agent = self.agents[node.agent_id]
                
                # Mark node as running
                node.status = TaskStatus.RUNNING
                node.started_at = datetime.utcnow()
                
                # Prepare task data with dependencies
                task_data = {
                    "task_type": "fetch_data" if node.agent_type == "data_fetcher" else "generate_chart" if node.agent_type == "chart_generator" else "analyze_text",
                    "parameters": node.parameters,
                    "dependencies": node_results
                }
                
                # Start agent task
                await agent.start_task(task_id)
                
                # Execute with timeout
                result = await asyncio.wait_for(
                    agent.process_task(task_data),
                    timeout=self.agent_timeout
                )
                
                # Complete agent task
                await agent.complete_task(task_id)
                
                return result
                
            except asyncio.TimeoutError:
                logger.error(f"Node {node_name} execution timed out")
                await agent.fail_task(task_id, "Execution timeout")
                raise
            except Exception as e:
                logger.error(f"Node {node_name} execution failed: {e}")
                await agent.fail_task(task_id, str(e))
                raise
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a task"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        execution_graph = self.execution_graphs.get(task_id)
        
        status_info = {
            "task_id": task_id,
            "name": task.name,
            "status": task.status,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "error_message": task.error_message,
            "retry_count": task.retry_count,
            "max_retries": task.max_retries
        }
        
        if execution_graph:
            status_info["execution_graph"] = {
                "total_nodes": len(execution_graph.nodes),
                "completed_nodes": len([n for n in execution_graph.nodes.values() if n.status == TaskStatus.COMPLETED]),
                "failed_nodes": len([n for n in execution_graph.nodes.values() if n.status == TaskStatus.FAILED]),
                "running_nodes": len([n for n in execution_graph.nodes.values() if n.status == TaskStatus.RUNNING]),
                "node_statuses": {
                    name: {
                        "status": node.status,
                        "started_at": node.started_at,
                        "completed_at": node.completed_at,
                        "error": node.error
                    }
                    for name, node in execution_graph.nodes.items()
                }
            }
        
        if task.status == TaskStatus.COMPLETED:
            status_info["results"] = task.results
        
        return status_info
    
    def get_available_agents(self) -> List[Dict[str, Any]]:
        """Get information about all available agents"""
        return [agent.get_agent_info().dict() for agent in self.agents.values()]
    
    def get_agent_health(self) -> Dict[str, Any]:
        """Get health status of all agents"""
        health_status = {}
        for agent_id, agent in self.agents.items():
            health_status[agent_id] = agent.get_health_status()
        return health_status
    
    async def send_message(self, from_agent: str, to_agent: str, message_type: str, 
                          payload: Dict[str, Any]) -> str:
        """Send a message between agents"""
        message = AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload
        )
        
        # In a real implementation, you might use a message queue here
        logger.info(f"Message sent from {from_agent} to {to_agent}: {message_type}")
        
        return message.correlation_id or str(uuid.uuid4())
    
    async def shutdown(self):
        """Shutdown the orchestrator and all agents"""
        logger.info("Shutting down AgentOrchestrator")
        
        # Cancel all running tasks
        for task_id, running_task in self.running_tasks.items():
            running_task.cancel()
        
        # Wait for tasks to complete
        if self.running_tasks:
            await asyncio.gather(*self.running_tasks.values(), return_exceptions=True)
        
        logger.info("AgentOrchestrator shutdown complete")

