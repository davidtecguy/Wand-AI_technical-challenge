#!/usr/bin/env python3
"""
Startup script for the Multi-Agent Task Solver
"""

import uvicorn
import os
from app.config import get_settings

def main():
    """Main startup function"""
    settings = get_settings()
    
    print("🚀 Starting Multi-Agent Task Solver...")
    print(f"📊 Version: {settings.app_version}")
    print(f"🌐 Host: {settings.host}")
    print(f"🔌 Port: {settings.port}")
    print(f"⚡ Max Concurrent Agents: {settings.max_concurrent_agents}")
    print(f"⏱️ Agent Timeout: {settings.agent_timeout}s")
    print("=" * 50)
    
    # Start the FastAPI server
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

if __name__ == "__main__":
    main()
