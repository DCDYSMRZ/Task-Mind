"""Task-Mind Web Service Server Module.

This module provides a local HTTP web service for the Task-Mind GUI,
replacing the pywebview-based implementation with a browser-accessible
web application.

Key components:
- app: FastAPI application factory
- runner: Uvicorn server runner
- routes/: API endpoint handlers
- websocket: Real-time update manager

Usage:
    from task_mind.server.app import create_app
    from task_mind.server.runner import run_server
"""

# Lazy imports to avoid circular dependency issues
# Users should import directly from submodules:
#   from task_mind.server.app import create_app
#   from task_mind.server.runner import run_server

__all__ = ["create_app", "run_server"]


def __getattr__(name: str):
    """Lazy import to avoid circular dependencies."""
    if name == "create_app":
        from task_mind.server.app import create_app
        return create_app
    if name == "run_server":
        from task_mind.server.runner import run_server
        return run_server
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
