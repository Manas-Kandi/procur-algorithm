#!/usr/bin/env python
"""Run the Procur FastAPI server."""

import os
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

from src.procur.api.config import get_api_config

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded environment variables from {env_path}")
else:
    print(f"Warning: .env file not found at {env_path}")


def main():
    """Run the API server."""
    config = get_api_config()
    
    uvicorn.run(
        "src.procur.api.app:app",
        host=config.host,
        port=config.port,
        reload=config.reload,
        workers=1 if config.reload else config.workers,
        log_level="info",
    )


if __name__ == "__main__":
    main()
