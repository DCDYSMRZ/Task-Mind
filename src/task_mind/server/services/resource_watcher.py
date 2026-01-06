"""Resource file watcher service.

Monitors recipe and skill directories for changes and triggers cache refresh.
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

logger = logging.getLogger(__name__)


class ResourceChangeHandler(FileSystemEventHandler):
    """Handler for recipe/skill file changes."""

    def __init__(self, cache_service):
        self.cache_service = cache_service
        self._debounce_task: Optional[asyncio.Task] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        """Set the event loop for async operations."""
        self._loop = loop

    def on_any_event(self, event: FileSystemEvent):
        """Handle any file system event."""
        if event.is_directory:
            return

        # Only care about recipe/skill files
        path = Path(event.src_path)
        if path.suffix not in ['.js', '.py', '.sh', '.md', '.yaml', '.yml']:
            return

        logger.debug(f"Resource change detected: {event.event_type} - {path.name}")
        
        # Debounce: wait 1 second before refreshing
        if self._loop and self._loop.is_running():
            if self._debounce_task and not self._debounce_task.done():
                self._debounce_task.cancel()
            
            self._debounce_task = asyncio.run_coroutine_threadsafe(
                self._refresh_after_delay(),
                self._loop
            )

    async def _refresh_after_delay(self):
        """Refresh cache after a short delay."""
        await asyncio.sleep(1)
        logger.info("Refreshing resources due to file changes")
        await self.cache_service.refresh_recipes(broadcast=True)
        await self.cache_service.refresh_skills(broadcast=True)


class ResourceWatcher:
    """Watches recipe and skill directories for changes."""

    _instance: Optional["ResourceWatcher"] = None

    def __init__(self):
        self._observer: Optional[Observer] = None
        self._handler: Optional[ResourceChangeHandler] = None
        self._cache_service = None

    @classmethod
    def get_instance(cls) -> "ResourceWatcher":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def start(self, cache_service, loop: asyncio.AbstractEventLoop):
        """Start watching resource directories.
        
        Args:
            cache_service: CacheService instance
            loop: Event loop for async operations
        """
        if self._observer is not None:
            logger.warning("Resource watcher already running")
            return

        self._cache_service = cache_service
        self._handler = ResourceChangeHandler(cache_service)
        self._handler.set_loop(loop)
        self._observer = Observer()

        # Watch recipe directories
        recipe_dirs = [
            Path.home() / ".task-mind" / "recipes",
        ]

        # Watch skill directories
        skill_dirs = [
            Path.home() / ".claude" / "skills",
        ]

        watch_dirs = recipe_dirs + skill_dirs
        
        for watch_dir in watch_dirs:
            if watch_dir.exists():
                self._observer.schedule(self._handler, str(watch_dir), recursive=True)
                logger.info(f"Watching directory: {watch_dir}")

        self._observer.start()
        logger.info("Resource watcher started")

    def stop(self):
        """Stop watching."""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None
            logger.info("Resource watcher stopped")

