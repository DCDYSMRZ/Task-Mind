"""Terminal WebSocket endpoints."""

import asyncio
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from task_mind.server.services.terminal_service import TerminalService

logger = logging.getLogger(__name__)

router = APIRouter()

# Global terminal service instance
terminal_service = TerminalService()


@router.websocket("/terminal/{session_id}")
async def terminal_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for terminal I/O.
    
    Protocol:
    - Client -> Server: {"type": "input", "data": "..."}
    - Client -> Server: {"type": "resize", "rows": 24, "cols": 80}
    - Server -> Client (binary): raw PTY bytes (ANSI + UTF-8 text mixed)
    - Server -> Client (json): {"type": "error", "message": "..."}
    """
    try:
        logger.info(f"WebSocket connection attempt for session {session_id[:8]}")
        await websocket.accept()
        logger.info(f"WebSocket accepted for session {session_id[:8]}")
        
        session = terminal_service.get_session(session_id)
        logger.info(f"Session lookup result: {session is not None}")
    except Exception as e:
        logger.error(f"Error in WebSocket setup: {e}", exc_info=True)
        try:
            await websocket.close()
        except:
            pass
        return
    
    # If no session exists, this might be a request to RESUME/CONNECT to a finished task
    if not session:
        from pathlib import Path
        import json
        
        # Check if this is a Claude session that exists but isn't running
        # NOTE: session_id here might be the task ID
        # Let's check if we can resume it
        
        metadata_file = Path.home() / ".task-mind" / "sessions" / "claude" / session_id / "metadata.json"
        
        if metadata_file.exists():
            # This is a completed (or existing) session, start a resume session
            logger.info(f"Starting resume session for task {session_id[:8]}")
            
            try:
                with open(metadata_file) as f:
                    metadata = json.load(f)
                project_path = metadata.get("project_path")
            except Exception:
                project_path = None
            
            # Find claude executable
            import shutil
            claude_path = shutil.which("claude")
            if not claude_path:
                await websocket.send_json({"type": "error", "message": "claude command not found"})
                await websocket.close()
                return
            
            # Start a resume session in PTY (direct claude CLI)
            # Use 'resume-{session_id}' as the PTY ID
            pty_session_id = f"resume-{session_id}"
            cmd = [claude_path, "--resume", session_id]
            
            # Check if project_path exists
            if project_path:
                from pathlib import Path
                project_dir = Path(project_path)
                if not project_dir.exists():
                    await websocket.send_json({
                        "type": "error", 
                        "message": f"Project directory does not exist: {project_path}. Please check if the directory has been moved or deleted."
                    })
                    await websocket.close()
                    return
            
            # Force color output
            import os
            color_env = os.environ.copy()
            color_env.update({
                'FORCE_COLOR': '1',
                'CLICOLOR_FORCE': '1',
                'TERM': 'xterm-256color',
                'COLORTERM': 'truecolor',
                'LS_COLORS': 'di=34:ln=35:so=32:pi=33:ex=31:bd=34;46:cd=34;43:su=30;41:sg=30;46:tw=30;42:ow=30;43',
            })
            
            # Track the mapping: task session_id -> pty_session_id
            # NOTE: terminal_service.start_pty_session handles session reuse if pty_session_id exists
            result = await terminal_service.start_pty_session(
                command=cmd,
                cwd=project_path,
                env=color_env,
                session_id=pty_session_id
            )
            
            if result.get('status') != 'ok':
                error_msg = result.get('error', 'Failed to start resume session')
                await websocket.send_json({"type": "error", "message": error_msg})
                await websocket.close()
                return
            
            # Register the mapping so future calls to get_session(session_id) work
            terminal_service.register_mapping(session_id, pty_session_id)
            
            session = terminal_service.get_session(pty_session_id)
        else:
            # No task session found, create a standalone shell
            # This is for "Live PTY" on something that isn't a task? Or maybe a generic ID?
            logger.info(f"No task found for {session_id[:8]}, creating/connecting schema shell")
            shell_session_id = f"shell-{session_id}"
            
            import os
            shell = os.environ.get('SHELL', '/bin/bash')
            
            # Force color output
            color_env = os.environ.copy()
            color_env.pop('NO_COLOR', None)  # Remove NO_COLOR to avoid conflict
            color_env.update({
                'FORCE_COLOR': '1',
                'TERM': 'xterm-256color',
                'COLORTERM': 'truecolor',
            })
            
            result = await terminal_service.start_pty_session(
                command=[shell],
                cwd=None,
                env=color_env,
                session_id=shell_session_id
            )
            
            if result.get('status') != 'ok':
                await websocket.send_json({"type": "error", "message": "Failed to create shell session"})
                await websocket.close()
                return
            
            # Register mapping
            terminal_service.register_mapping(session_id, shell_session_id)
            
            session = terminal_service.get_session(shell_session_id)
        
        if not session:
            await websocket.send_json({"type": "error", "message": "Session creation failed"})
            await websocket.close()
            return
    
    logger.info(f"Terminal WebSocket connected for session {session.session_id[:8]}")
    
    # Send history buffer immediately
    history = session.get_history()
    if history:
        await websocket.send_bytes(history)
    
    # Subscribe to new output
    output_queue = session.subscribe()
    
    # Task for reading from PTY and sending to client
    async def read_loop():
        try:
            while True:
                data = await output_queue.get()
                if data:
                    await websocket.send_bytes(data)
                else:
                    # EOF signal
                    logger.info(f"Terminal session {session_id[:8]} ended (EOF signal)")
                    try:
                        await websocket.send_bytes(b"\r\n[Session ended]\r\n")
                        await websocket.close()
                    except:
                        pass
                    break
        except Exception as e:
            logger.error(f"Error in terminal read loop: {e}")
            
    read_task = asyncio.create_task(read_loop())
    
    try:
        # Handle client messages
        while True:
            message = await websocket.receive_json()
            
            if message.get("type") == "input":
                data = message.get("data", "")
                await session.write(data)
            
            elif message.get("type") == "resize":
                rows = message.get("rows", 24)
                cols = message.get("cols", 80)
                await session.resize(rows, cols)
    
    except WebSocketDisconnect:
        logger.info(f"Terminal WebSocket disconnected for session {session_id[:8]}")
    
    except Exception as e:
        logger.error(f"Terminal WebSocket error: {e}")
    
    finally:
        read_task.cancel()
        session.unsubscribe(output_queue)
        try:
            await read_task
        except asyncio.CancelledError:
            pass


@router.post("/terminal/create")
async def create_terminal(prompt: str, project_path: str = None):
    """Create a new terminal session.
    
    Args:
        prompt: Task prompt
        project_path: Optional project path
        
    Returns:
        Session info
    """
    result = await terminal_service.create_session(prompt, project_path)
    return result


@router.delete("/terminal/{session_id}")
async def close_terminal(session_id: str):
    """Close a terminal session."""
    await terminal_service.close_session(session_id)
    return {"status": "ok"}

