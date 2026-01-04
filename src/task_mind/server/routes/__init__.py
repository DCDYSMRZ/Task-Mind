"""API route handlers for Task-Mind Web Service.

This package contains FastAPI routers for different API domains:
- system: Server status and info endpoints
- dashboard: Dashboard overview data
- recipes: Recipe listing and execution
- tasks: Task/session management
- config: User configuration
- agent: Agent task execution
- skills: Claude Code skills
- settings: Main config, env vars, GitHub integration
- sync: Multi-device sync via GitHub
- init: Web-based initialization (dependency check, resource install)
- viewer: Content preview file serving
"""

from task_mind.server.routes.system import router as system_router
from task_mind.server.routes.dashboard import router as dashboard_router
from task_mind.server.routes.recipes import router as recipes_router
from task_mind.server.routes.tasks import router as tasks_router
from task_mind.server.routes.agent import router as agent_router
from task_mind.server.routes.config import router as config_router
from task_mind.server.routes.skills import router as skills_router
from task_mind.server.routes.settings import router as settings_router
from task_mind.server.routes.sync import router as sync_router
from task_mind.server.routes.console import router as console_router
from task_mind.server.routes.init import router as init_router
from task_mind.server.routes.viewer import router as viewer_router
from task_mind.server.routes.files import router as files_router
from task_mind.server.routes.logs import router as logs_router
from task_mind.server.routes.terminal import router as terminal_router

__all__ = [
    "system_router",
    "dashboard_router",
    "recipes_router",
    "tasks_router",
    "agent_router",
    "config_router",
    "skills_router",
    "settings_router",
    "sync_router",
    "console_router",
    "init_router",
    "viewer_router",
    "files_router",
    "logs_router",
    "terminal_router",
]
