"""Agent task execution service.

Provides functionality for starting and continuing agent tasks.
"""

import logging
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from task_mind.compat import prepare_command_for_windows
from task_mind.server.services.base import get_utf8_env

logger = logging.getLogger(__name__)


class AgentService:
    """Service for agent task execution."""

    @staticmethod
    async def start_task(prompt: str, project_path: Optional[str] = None, use_pty: bool = True) -> Dict[str, Any]:
        """Start agent task.

        Args:
            prompt: Task description/prompt.
            project_path: Optional project path context.
            use_pty: Whether to use PTY (for interactive terminal support).

        Returns:
            Dictionary with status, task_id, session_id, and message or error.
        """
        if not prompt or not prompt.strip():
            return {"status": "error", "error": "Task description cannot be empty"}

        prompt = prompt.strip()

        # Use PTY if requested
        if use_pty:
            from task_mind.server.services.terminal_service import terminal_service
            result = await terminal_service.create_session(prompt, project_path)
            if result["status"] == "ok":
                return {
                    "status": "ok",
                    "id": result["session_id"],
                    "session_id": result["session_id"],
                    "title": prompt[:50] + "..." if len(prompt) > 50 else prompt,
                    "project_path": project_path,
                    "agent_type": "claude",
                    "started_at": datetime.now(timezone.utc).isoformat(),
                    "message": f"Task started: {prompt[:50]}",
                    "has_pty": True,
                }
            # Fallback to subprocess if PTY fails
            logger.warning(f"PTY creation failed: {result.get('error')}, falling back to subprocess")

        # Fallback: use subprocess (no PTY)
        task_id = str(uuid.uuid4())

        try:
            # Find task-mind executable
            task_mind_path = shutil.which("task-mind")
            if not task_mind_path:
                return {
                    "status": "error",
                    "error": "task-mind command not found, please ensure it's properly installed and in PATH",
                }

            # Prepare log directory
            log_dir = Path.home() / ".task-mind" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"agent-{task_id[:8]}.log"

            # Use temp file to pass prompt (Windows compatibility)
            prompt_file = log_dir / f"prompt-{task_id[:8]}.txt"
            prompt_file.write_text(prompt, encoding="utf-8")

            # Build command
            cmd = [task_mind_path, "agent", "--yes", "--source", "web", "--prompt-file", str(prompt_file)]

            # Start process in background
            with open(log_file, "w", encoding="utf-8") as f:
                subprocess.Popen(
                    prepare_command_for_windows(cmd),
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                    cwd=project_path if project_path else None,
                    env=get_utf8_env(),
                )

            title = prompt[:50] + "..." if len(prompt) > 50 else prompt

            return {
                "status": "ok",
                "id": task_id,
                "title": title,
                "project_path": project_path,
                "agent_type": "claude",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "message": f"Task started: {title}",
                "has_pty": False,
            }

        except FileNotFoundError:
            return {
                "status": "error",
                "error": "task-mind command not found, please ensure it's properly installed",
            }
        except Exception as e:
            logger.error("Failed to start agent task: %s", e)
            return {
                "status": "error",
                "error": f"Failed to start task: {str(e)}",
            }

    @staticmethod
    async def continue_task(session_id: str, prompt: str) -> Dict[str, Any]:
        """Continue conversation in specified session.

        Args:
            session_id: Session ID to continue.
            prompt: User's new prompt.

        Returns:
            Dictionary with status and message or error.
        """
        if not session_id:
            return {"status": "error", "error": "session_id cannot be empty"}
        if not prompt or not prompt.strip():
            return {"status": "error", "error": "Task description cannot be empty"}

        prompt = prompt.strip()

        try:
            # Find task-mind executable
            task_mind_path = shutil.which("task-mind")
            if not task_mind_path:
                return {
                    "status": "error",
                    "error": "task-mind command not found, please ensure it's properly installed and in PATH",
                }

            # Prepare log directory
            log_dir = Path.home() / ".task-mind" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"agent-resume-{session_id[:8]}.log"

            # Use temp file to pass prompt
            prompt_file = log_dir / f"prompt-resume-{session_id[:8]}.txt"
            prompt_file.write_text(prompt, encoding="utf-8")

            # Read original project_path from metadata
            metadata_file = Path.home() / ".task-mind" / "sessions" / "claude" / session_id / "metadata.json"
            project_path = None
            if metadata_file.exists():
                import json
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    project_path = metadata.get("project_path")
                
                # Update status to RUNNING so the UI reflects the change immediately
                try:
                    from task_mind.session.models import AgentType, SessionStatus
                    from task_mind.session.storage import update_metadata, read_metadata
                    
                    # Force read to ensure we have the object
                    current_session = read_metadata(session_id, AgentType.CLAUDE)
                    if current_session:
                        update_metadata(
                            session_id, 
                            AgentType.CLAUDE, 
                            status=SessionStatus.RUNNING,
                            ended_at=None,
                            last_activity=datetime.now(timezone.utc)
                        )
                        logger.info(f"Reset session {session_id[:8]} status to RUNNING")
                except Exception as e:
                    logger.warning(f"Failed to update session status: {e}")

            # Build command
            cmd = [
                task_mind_path,
                "agent",
                "--resume",
                session_id,
                "--yes",
                "--prompt-file",
                str(prompt_file),
            ]

            # Build command
            cmd = [
                task_mind_path,
                "agent",
                "--resume",
                session_id,
                "--yes",
                "--prompt-file",
                str(prompt_file),
            ]

            # Use TerminalService to start process in PTY
            # This allows "Live PTY" to attach to it and view output
            from task_mind.server.services.terminal_service import terminal_service
            
            # Use a deterministic PTY ID so we can map it easily
            pty_session_id = f"resume-{session_id}"
            
            # Start PTY session
            # Note: We don't need to redirect stdout to log_file manually because 
            # TerminalSession captures PTY output. However, for logging persistence,
            # we might want to tail it or rely on the agent's internal logging.
            # task-mind agent logs to --log-file separately anyway if configured, 
            # or we rely on the implementation above that sets up logging.
            # actually task-mind agent usually logs to stderr/stdout
            
            # IMPORTANT: The original implementation redirected stdout/stderr to a log file.
            # TerminalService captures stdout/stderr. 
            # We can rely on TerminalSession history for the "Console" view.
            
            result = await terminal_service.start_pty_session(
                command=cmd,
                cwd=project_path if project_path else None,
                env=get_utf8_env(),
                session_id=pty_session_id
            )
            
            if result.get("status") == "ok":
                # Register mapping so Live PTY finds it via task ID
                terminal_service.register_mapping(session_id, pty_session_id)
                logger.info(f"Started resume task {session_id[:8]} in PTY {pty_session_id}")
            else:
                logger.error(f"Failed to start PTY for resume: {result.get('error')}")
                return {
                    "status": "error",
                    "error": f"Failed to start PTY: {result.get('error')}"
                }

            title = prompt[:50] + "..." if len(prompt) > 50 else prompt

            return {
                "status": "ok",
                "message": f"Continued in session {session_id[:8]}...: {title}",
            }

        except FileNotFoundError:
            return {
                "status": "error",
                "error": "task-mind command not found, please ensure it's properly installed",
            }
        except Exception as e:
            logger.error("Failed to continue agent task: %s", e)
            return {
                "status": "error",
                "error": f"Failed to continue task: {str(e)}",
            }
