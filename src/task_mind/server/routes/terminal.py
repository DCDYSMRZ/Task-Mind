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
    - Server -> Client: {"type": "output", "data": "..."}
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
    
    # If no session exists, check if it's a completed Claude session
    if not session:
        from pathlib import Path
        import json
        
        # Check if this is a Claude session that exists but isn't running
        metadata_file = Path.home() / ".task-mind" / "sessions" / "claude" / session_id / "metadata.json"
        
        if metadata_file.exists():
            # This is a completed session, start a resume session
            logger.info(f"Starting resume session for completed task {session_id[:8]}")
            
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
            resume_session_id = f"resume-{session_id}"
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
            
            result = await terminal_service.start_pty_session(
                command=cmd,
                cwd=project_path,
                env=color_env,
                session_id=resume_session_id
            )
            
            if result.get('status') != 'ok':
                error_msg = result.get('error', 'Failed to start resume session')
                await websocket.send_json({"type": "error", "message": error_msg})
                await websocket.close()
                return
            
            session = terminal_service.get_session(resume_session_id)
        else:
            # No session found, create a standalone shell
            logger.info(f"No session found for {session_id[:8]}, creating standalone shell")
            shell_session_id = f"shell-{session_id}"
            
            import os
            shell = os.environ.get('SHELL', '/bin/bash')
            
            # Force color output
            color_env = os.environ.copy()
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
            
            session = terminal_service.get_session(shell_session_id)
        
        if not session:
            await websocket.send_json({"type": "error", "message": "Session creation failed"})
            await websocket.close()
            return
    
    logger.info(f"Terminal WebSocket connected for session {session.session_id[:8]}")
    
    # Task for reading from PTY and sending to client
    async def read_loop():
        while True:
            try:
                data = await session.read()
                if data:
                    await websocket.send_json({"type": "output", "data": data})
                else:
                    await asyncio.sleep(0.05)
            except EOFError:
                logger.info(f"Terminal session {session_id[:8]} ended (EOF)")
                try:
                    await websocket.send_json({"type": "output", "data": "\r\n[Session ended]\r\n"})
                    await websocket.close()
                except:
                    pass
                break
            except Exception as e:
                logger.error(f"Error reading from terminal: {e}")
                break
    
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

