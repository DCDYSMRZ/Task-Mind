"""
task-mind - Automated visual management system CDP control library

Provides Python wrapper for Chrome DevTools Protocol,
for browser automation control and visual management.
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("task-mind-cli")
except PackageNotFoundError:
    __version__ = "0.0.0"  # Fallback value when not installed in development mode
__author__ = "Jamey Tsai"
__email__ = "caijia@task-mind.ai"

# Recommended to use explicit imports:
# from task_mind.recipes import RecipeRegistry, RecipeRunner
# from task_mind.run import RunInstance, RunManager
# from task_mind.cdp import CDPClient, CDPSession
# from task_mind.cli import cli

# Submodules accessed via path (avoid top-level namespace pollution)
# Example: import task_mind.recipes, import task_mind.run

__all__ = [
    "__version__",
    "__author__",
    "__email__",
]