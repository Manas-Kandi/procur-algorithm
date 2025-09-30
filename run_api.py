#!/usr/bin/env python
"""Run the Procur FastAPI server."""

import uvicorn

from src.procur.api.config import get_api_config


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
