#!/usr/bin/env python3
"""
Demo script for the Multi-Agent Task Solver
This script demonstrates the core functionality of the system.
"""

import asyncio
import json
from app.orchestrator import AgentOrchestrator
from app.agents import DataFetcherAgent, ChartGeneratorAgent, TextProcessorAgent

async def demo_basic_agents():
    """Demo basic agent functionality"""
    print("🚀 Starting Multi-Agent Task Solver Demo")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator(max_concurrent_agents=3, agent_timeout=30)
    
    print(f"✅ Orchestrator initialized with {len(orchestrator.agents)} agents")
    
    # List available agents
    agents = orchestrator.get_available_agents()
    print("\n📋 Available Agents:")
    for agent in agents:
        print(f"  • {agent['name']} ({agent['agent_type']}) - {agent['status']}")
    
    # List available tools
    tools = orchestrator.get_tools()
    print(f"\n🔧 Available Tools: {len(tools)}")
    
    return orchestrator

async def demo_data_analysis_pipeline(orchestrator):
    """Demo a complete data analysis pipeline"""
    print("\n📊 Demo: Data Analysis Pipeline")
    print("-" * 30)
    
    # Define execution graph for data analysis
    execution_graph = {
        "data_fetcher": {
            "agent_type": "data_fetcher",
            "parameters": {
                "source_type": "http",
                "source": "https://jsonplaceholder.typicode.com/posts/1"
            }
        },
        "chart_generator": {
            "agent_type": "chart_generator",
            "parameters": {
                "chart_type": "bar",
                "title": "Sample Data Analysis",
                "x_label": "Categories",
                "y_label": "Values"
            },
            "dependencies": ["data_fetcher"]
        }
    }
    
    print("🔄 Executing data analysis pipeline...")
    
    try:
        # Execute the task
        task_id = await orchestrator.execute_task(
            "Data Analysis Demo",
            execution_graph,
            {"description": "Demo pipeline for data fetching and visualization"}
        )
        
        print(f"✅ Task created with ID: {task_id}")
        
        # Wait for completion
        print("⏳ Waiting for task completion...")
        await asyncio.sleep(5)  # Give some time for execution
        
        # Get task status
        status = await orchestrator.get_task_status(task_id)
        print(f"📈 Task Status: {status['status']}")
        
        if status['status'] == 'completed':
            print("🎉 Task completed successfully!")
            print(f"📊 Results: {len(status.get('results', {}))} nodes completed")
        else:
            print(f"⚠️ Task status: {status['status']}")
            if 'error_message' in status:
                print(f"❌ Error: {status['error_message']}")
    
    except Exception as e:
        print(f"❌ Error executing pipeline: {e}")

async def demo_text_analysis(orchestrator):
    """Demo text analysis capabilities"""
    print("\n📝 Demo: Text Analysis")
    print("-" * 20)
    
    # Define execution graph for text analysis
    execution_graph = {
        "text_processor": {
            "agent_type": "text_processor",
            "parameters": {
                "task_type": "analyze_sentiment",
                "text": "I absolutely love this multi-agent system! It's amazing and wonderful to work with."
            }
        }
    }
    
    print("🔄 Executing text analysis...")
    
    try:
        task_id = await orchestrator.execute_task(
            "Text Analysis Demo",
            execution_graph,
            {"description": "Demo text sentiment analysis"}
        )
        
        print(f"✅ Task created with ID: {task_id}")
        
        # Wait for completion
        await asyncio.sleep(3)
        
        # Get results
        status = await orchestrator.get_task_status(task_id)
        if status['status'] == 'completed':
            print("🎉 Text analysis completed!")
            results = status.get('results', {})
            if 'text_processor' in results:
                result = results['text_processor']
                if result.get('success'):
                    sentiment_data = result.get('result', {})
                    print(f"😊 Sentiment: {sentiment_data.get('sentiment', 'unknown')}")
                    print(f"📊 Score: {sentiment_data.get('sentiment_score', 'N/A')}")
    
    except Exception as e:
        print(f"❌ Error in text analysis: {e}")

async def demo_concurrent_execution(orchestrator):
    """Demo concurrent task execution"""
    print("\n⚡ Demo: Concurrent Task Execution")
    print("-" * 35)
    
    # Create multiple simple tasks
    tasks = []
    for i in range(3):
        execution_graph = {
            "data_fetcher": {
                "agent_type": "data_fetcher",
                "parameters": {
                    "source_type": "http",
                    "source": f"https://jsonplaceholder.typicode.com/posts/{i+1}"
                }
            }
        }
        
        task_id = await orchestrator.execute_task(
            f"Concurrent Task {i+1}",
            execution_graph
        )
        tasks.append(task_id)
        print(f"✅ Created task {i+1}: {task_id}")
    
    print(f"\n🔄 Executing {len(tasks)} tasks concurrently...")
    
    # Wait for all tasks to complete
    await asyncio.sleep(8)
    
    # Check results
    print("\n📊 Task Results:")
    for i, task_id in enumerate(tasks):
        status = await orchestrator.get_task_status(task_id)
        print(f"  Task {i+1}: {status['status']}")

async def demo_agent_health_monitoring(orchestrator):
    """Demo agent health monitoring"""
    print("\n💚 Demo: Agent Health Monitoring")
    print("-" * 30)
    
    # Get agent health status
    health = orchestrator.get_agent_health()
    
    print("📊 Agent Health Status:")
    for agent_id, status in health.items():
        health_icon = "✅" if status['is_healthy'] else "❌"
        print(f"  {health_icon} {status['name']}: {status['status']}")
        print(f"    Last heartbeat: {status['last_heartbeat']}")
        print(f"    Current task: {status['current_task'] or 'None'}")
        print(f"    Tools: {status['tools_count']}")

async def main():
    """Main demo function"""
    try:
        # Initialize system
        orchestrator = await demo_basic_agents()
        
        # Run demos
        await demo_data_analysis_pipeline(orchestrator)
        await demo_text_analysis(orchestrator)
        await demo_concurrent_execution(orchestrator)
        await demo_agent_health_monitoring(orchestrator)
        
        print("\n🎉 Demo completed successfully!")
        print("\n💡 Key Features Demonstrated:")
        print("  • Multi-agent orchestration")
        print("  • Tool integration and execution")
        print("  • Concurrent task processing")
        print("  • Health monitoring")
        print("  • Error handling and retries")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if 'orchestrator' in locals():
            await orchestrator.shutdown()
            print("\n🧹 System shutdown complete")

if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())
