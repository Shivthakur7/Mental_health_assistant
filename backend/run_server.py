#!/usr/bin/env python3
"""
Mental Health Assistant Backend Server
Run this script to start the FastAPI server
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Get the backend directory
    backend_dir = Path(__file__).parent
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Add backend to Python path
    sys.path.insert(0, str(backend_dir))
    
    print("Mental Health Assistant Backend")
    print("=" * 40)
    print(f"Backend directory: {backend_dir}")
    print(f"Server will run on: http://localhost:8000")
    print(f"API docs will be at: http://localhost:8000/docs")
    print("=" * 40)
    
    # Check if requirements are installed
    try:
        import fastapi
        import uvicorn
        print("Dependencies found")
    except ImportError:
        print("Missing dependencies. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Start the server
    try:
        print("Starting server...")
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "api.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Error starting server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
