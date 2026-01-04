"""Terminal service for interactive PTY sessions."""

import asyncio
import fcntl
import logging
import os
import pty
import select
import shutil
import struct
import termios
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from task_mind.compat import prepare_command_for_windows
from task_mind.server.services.base import get_utf8_env

logger = logging.getLogger(__name__)


class TerminalSession:
    """Manages a PTY-based terminal session."""

    def __init__(self, session_id: str, command: list[str], cwd: Optional[str] = None):
        self.session_id = session_id
        self.command = command
        self.cwd = cwd or str(Path.home())
        self.master_fd: Optional[int] = None
        self.pid: Optional[int] = None
        self._running = False
        self._reader_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start the terminal session."""
        loop = asyncio.get_event_loop()
        
        # Fork PTY in executor to avoid blocking
        self.pid, self.master_fd = await loop.run_in_executor(
            None, self._fork_pty
        )
        
        self._running = True
        logger.info(f"Terminal session {self.session_id[:8]} started (PID: {self.pid})")

    def _fork_pty(self) -> tuple[int, int]:
        """Fork a PTY process."""
        pid, master_fd = pty.fork()
        
        if pid == 0:  # Child process
            # Change to working directory
            os.chdir(self.cwd)
            
            # Execute command
            env = get_utf8_env()
            env["TERM"] = "xterm-256color"
            env["COLORTERM"] = "truecolor"
            os.execvpe(self.command[0], self.command, env)
        
        # Parent process
        return pid, master_fd

    async def write(self, data: str) -> None:
        """Write data to terminal."""
        if self.master_fd is None:
            return
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, os.write, self.master_fd, data.encode('utf-8')
        )

    async def read(self) -> Optional[str]:
        """Read data from terminal (non-blocking)."""
        if self.master_fd is None:
            return None
        
        loop = asyncio.get_event_loop()
        
        try:
            # Check if data is available
            ready, _, _ = await loop.run_in_executor(
                None, select.select, [self.master_fd], [], [], 0.1
            )
            
            if not ready:
                return None
            
            # Read data
            data = await loop.run_in_executor(
                None, os.read, self.master_fd, 4096
            )
            
            if not data:
                # EOF reached (process exited)
                raise EOFError("PTY closed")
            
            return data.decode('utf-8', errors='replace')
        
        except (OSError, EOFError):
            raise EOFError("PTY closed")

    async def resize(self, rows: int, cols: int) -> None:
        """Resize terminal."""
        if self.master_fd is None:
            return
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, self._do_resize, rows, cols
        )

    def _do_resize(self, rows: int, cols: int) -> None:
        """Perform terminal resize."""
        if self.master_fd is None:
            return
        
        winsize = struct.pack('HHHH', rows, cols, 0, 0)
        fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, winsize)

    async def stop(self) -> None:
        """Stop the terminal session."""
        self._running = False
        
        if self.master_fd is not None:
            try:
                os.close(self.master_fd)
            except OSError:
                pass
        
        if self.pid is not None:
            try:
                os.kill(self.pid, 9)
                os.waitpid(self.pid, 0)
            except (OSError, ChildProcessError):
                pass
        
        logger.info(f"Terminal session {self.session_id[:8]} stopped")


class TerminalService:
    """Service for managing terminal sessions."""

    def __init__(self):
        self._sessions: Dict[str, TerminalSession] = {}
        self._claude_to_terminal: Dict[str, str] = {}  # Map Claude session_id to terminal session_id

    async def create_session(
        self, prompt: str, project_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new terminal session running task-mind agent.
        
        Args:
            prompt: Task prompt
            project_path: Optional project path
            
        Returns:
            Session info dictionary
        """
        session_id = str(uuid.uuid4())
        
        # Find task-mind executable
        task_mind_path = shutil.which("task-mind")
        if not task_mind_path:
            return {
                "status": "error",
                "error": "task-mind command not found",
            }

        # Check if project path exists
        if project_path and not os.path.isdir(project_path):
            return {
                "status": "error", 
                "error": f"Project path does not exist: {project_path}"
            }
        
        # Build command
        cmd = [task_mind_path, "agent", "--yes", "--source", "web"]
        if project_path:
            cmd.extend(["--project", project_path])
        cmd.append(prompt)
        
        # Create session
        session = TerminalSession(session_id, cmd, project_path)
        
        try:
            await session.start()
            self._sessions[session_id] = session
            
            # Store mapping for later (will be updated when Claude session is detected)
            logger.info(f"Created PTY session {session_id[:8]}, waiting for Claude session...")
            
            return {
                "status": "ok",
                "session_id": session_id,
                "project_path": project_path,
            }
        
        except Exception as e:
            logger.error(f"Failed to create terminal session: {e}")
            return {
                "status": "error",
                "error": str(e),
            }

    async def start_pty_session(
        self,
        command: list,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start a generic PTY session with custom command.
        
        Args:
            command: Command to execute
            cwd: Working directory
            env: Environment variables (currently unused)
            session_id: Optional session ID
            
        Returns:
            Session info dictionary
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        # Check if working directory exists
        if cwd and not os.path.isdir(cwd):
            return {
                "status": "error",
                "error": f"Working directory does not exist: {cwd}"
            }
        
        session = TerminalSession(session_id, command, cwd)
        
        try:
            await session.start()
            self._sessions[session_id] = session
            
            logger.info(f"Started PTY session {session_id[:8]}")
            
            return {
                "status": "ok",
                "session_id": session_id,
            }
        
        except Exception as e:
            logger.error(f"Failed to start PTY session: {e}")
            return {
                "status": "error",
                "error": str(e),
            }

    def get_session(self, session_id: str) -> Optional[TerminalSession]:
        """Get terminal session by ID (supports both terminal and Claude session IDs)."""
        # Try direct lookup
        session = self._sessions.get(session_id)
        if session:
            return session
        
        # Try Claude session ID mapping
        terminal_id = self._claude_to_terminal.get(session_id)
        if terminal_id:
            return self._sessions.get(terminal_id)
        
        return None

    async def close_session(self, session_id: str) -> None:
        """Close terminal session."""
        session = self._sessions.pop(session_id, None)
        if session:
            await session.stop()


# Global instance
terminal_service = TerminalService()
