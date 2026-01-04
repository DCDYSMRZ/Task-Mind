"""Background task to map Claude sessions to PTY sessions."""

import asyncio
import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


class SessionMapper:
    """Maps Claude session IDs to PTY session IDs."""
    
    def __init__(self, terminal_service):
        self.terminal_service = terminal_service
        self._running = False
        self._task = None
    
    async def start(self):
        """Start the mapping task."""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._map_sessions())
        logger.info("Session mapper started")
    
    async def stop(self):
        """Stop the mapping task."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Session mapper stopped")
    
    async def _map_sessions(self):
        """Periodically scan for new Claude sessions and map them."""
        sessions_dir = Path.home() / ".task-mind" / "sessions" / "claude"
        known_sessions = set()
        
        while self._running:
            try:
                if not sessions_dir.exists():
                    await asyncio.sleep(2)
                    continue
                
                # Find all Claude sessions
                for session_path in sessions_dir.iterdir():
                    if not session_path.is_dir():
                        continue
                    
                    claude_id = session_path.name
                    
                    # Skip if already mapped
                    if claude_id in known_sessions:
                        continue
                    
                    # Check if this is a web-sourced session
                    metadata_file = session_path / "metadata.json"
                    if not metadata_file.exists():
                        continue
                    
                    try:
                        import json
                        with open(metadata_file) as f:
                            metadata = json.load(f)
                        
                        # Only map web-sourced sessions
                        if metadata.get("source") != "web":
                            known_sessions.add(claude_id)
                            continue
                        
                        # Find the most recent PTY session (heuristic: created within last 10 seconds)
                        import time
                        current_time = time.time()
                        
                        for pty_id, session in list(self.terminal_service._sessions.items()):
                            # Check if this PTY session is unmapped and recent
                            if pty_id not in self.terminal_service._claude_to_terminal.values():
                                # Map it
                                self.terminal_service._claude_to_terminal[claude_id] = pty_id
                                logger.info(f"Mapped Claude session {claude_id[:8]} -> PTY {pty_id[:8]}")
                                known_sessions.add(claude_id)
                                break
                    
                    except Exception as e:
                        logger.error(f"Error mapping session {claude_id}: {e}")
                
                await asyncio.sleep(2)
            
            except Exception as e:
                logger.error(f"Error in session mapper: {e}")
                await asyncio.sleep(5)


# Global instance
session_mapper = None


def get_session_mapper(terminal_service):
    """Get or create session mapper instance."""
    global session_mapper
    if session_mapper is None:
        session_mapper = SessionMapper(terminal_service)
    return session_mapper

