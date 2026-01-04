"""Log streaming endpoints."""

import asyncio
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/logs/agent/{session_id}/stream")
async def stream_agent_log(session_id: str):
    """Stream agent log file in real-time.
    
    Args:
        session_id: Session ID to stream logs for
        
    Returns:
        StreamingResponse with log content
    """
    log_dir = Path.home() / ".task-mind" / "logs"
    
    # Try multiple log file patterns
    log_files = [
        log_dir / f"agent-{session_id[:8]}.log",
        log_dir / f"agent-resume-{session_id[:8]}.log",
    ]
    
    log_file: Optional[Path] = None
    for f in log_files:
        if f.exists():
            log_file = f
            break
    
    if not log_file:
        raise HTTPException(status_code=404, detail="Log file not found")
    
    async def generate():
        """Generate log content as it's written."""
        try:
            with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                # Send existing content
                content = f.read()
                if content:
                    yield content
                
                # Tail new content
                while True:
                    line = f.readline()
                    if line:
                        yield line
                    else:
                        await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Error streaming log: {e}")
            yield f"\n[Error reading log: {e}]\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

