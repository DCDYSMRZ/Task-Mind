"""Terminal service for interactive PTY sessions."""

import asyncio
import collections
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
from typing import Any, Dict, Optional, Set

from task_mind.compat import prepare_command_for_windows
from task_mind.server.services.base import get_utf8_env

logger = logging.getLogger(__name__)


class TerminalSession:
    """Manages a PTY-based terminal session."""

    def __init__(self, session_id: str, command: list[str], cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None):
        self.session_id = session_id
        self.command = command
        self.cwd = cwd or str(Path.home())
        self.env = env
        self.master_fd: Optional[int] = None
        self.pid: Optional[int] = None
        self._running = False
        self._reader_task: Optional[asyncio.Task] = None
        # Ring buffer for output history (100KB should be enough for recent context)
        self._history = collections.deque(maxlen=100000)
        # Active listeners (queues)
        self._listeners: Set[asyncio.Queue] = set()

    async def start(self) -> None:
        """Start the terminal session."""
        loop = asyncio.get_event_loop()
        
        # Fork PTY in executor to avoid blocking
        self.pid, self.master_fd = await loop.run_in_executor(
            None, self._fork_pty
        )
        
        self._running = True
        # Start background reader
        self._reader_task = asyncio.create_task(self._read_loop())
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
            
            # Merge custom env if provided
            if self.env:
                env.update(self.env)
            
            os.execvpe(self.command[0], self.command, env)
        
        # Parent process
        return pid, master_fd

    async def _read_loop(self) -> None:
        """Background loop to drain PTY and broadcast to listeners."""
        if self.master_fd is None:
            return
            
        loop = asyncio.get_event_loop()
        
        while self._running:
            try:
                # Check if data is available
                ready, _, _ = await loop.run_in_executor(
                    None, select.select, [self.master_fd], [], [], 0.1
                )
                
                if not ready:
                    continue
                
                # Read data
                data = await loop.run_in_executor(
                    None, os.read, self.master_fd, 4096
                )
                
                if not data:
                    # EOF reached
                    break
                
                # Update history
                self._history.append(data)
                
                # Broadcast to listeners
                for queue in list(self._listeners):
                    try:
                        queue.put_nowait(data)
                    except Exception:
                        # Should not happen with unbounded queue, but playing safe
                        pass
                        
            except (OSError, EOFError, ValueError):
                break
            except Exception as e:
                logger.error(f"Error in PTY read loop: {e}")
                break
        
        # Signal EOF to listeners
        for queue in list(self._listeners):
             queue.put_nowait(b"") # Empty bytes serves as EOF signal
        
        self._running = False
        logger.info(f"PTY read loop ended for {self.session_id[:8]}")

    async def write(self, data: str) -> None:
        """Write data to terminal."""
        if self.master_fd is None:
            return
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, os.write, self.master_fd, data.encode('utf-8')
        )

    def subscribe(self) -> asyncio.Queue:
        """Subscribe to terminal output."""
        queue = asyncio.Queue()
        self._listeners.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        """Unsubscribe from terminal output."""
        if queue in self._listeners:
            self._listeners.remove(queue)

    def get_history(self) -> bytes:
        """Get full history as bytes."""
        return b''.join(self._history)

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
        
        if self._reader_task:
            self._reader_task.cancel()
            try:
                await self._reader_task
            except asyncio.CancelledError:
                pass
        
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
        # Map Claude session_id (task ID) to terminal session_id (Active PTY ID)
        self._task_to_terminal: Dict[str, str] = {} 

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
            
            # Store mapping so we can find this PTY later using the task ID? 
            # Actually for 'create_session', the session_id returned IS the task_id usually used by frontend.
            # But the agent runner will have its own internal ID. 
            # In this app architecture, it seems 'create_session' returns a session_id which IS the main handle.
            
            # Let's just track it directly.
            # However, if CLI is running, we might want to map it.
            # For now, simplistic: session_id is the key.
            
            logger.info(f"Created PTY session {session_id[:8]}")
            
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
            session_id: Optional session ID (usually the Task ID for resume sessions)
            
        Returns:
            Session info dictionary
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        # Check if session exists and is running
        existing_session = self.get_session(session_id)
        if existing_session and existing_session._running:
             logger.info(f"Reusing existing PTY session {session_id[:8]}")
             return {
                "status": "ok",
                "session_id": session_id,
            }

        # Check if working directory exists
        if cwd and not os.path.isdir(cwd):
            return {
                "status": "error",
                "error": f"Working directory does not exist: {cwd}"
            }
        
        session = TerminalSession(session_id, command, cwd, env)
        
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
        """Get terminal session by ID."""
        # Check process-level mapping first
        real_sid = self._task_to_terminal.get(session_id, session_id)
        return self._sessions.get(real_sid)

    def register_mapping(self, task_id: str, terminal_id: str) -> None:
        """Register a mapping from a task/frontend ID to a real PTY session ID."""
        self._task_to_terminal[task_id] = terminal_id

    async def close_session(self, session_id: str) -> None:
        """Close terminal session."""
        real_sid = self._task_to_terminal.get(session_id, session_id)
        session = self._sessions.pop(real_sid, None)
        
        if session:
            await session.stop()
            
        # Clean up mapping if exists
        if session_id in self._task_to_terminal:
            del self._task_to_terminal[session_id]


# Global instance
terminal_service = TerminalService()
