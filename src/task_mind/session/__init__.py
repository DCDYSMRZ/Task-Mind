"""
Task-Mind Session Module - Agent Session Monitoring and Data Persistence

Provides real-time monitoring and data storage capabilities for Agent tool execution sessions
such as Claude Code.

Core components:
- models: Session data models (MonitoredSession, SessionStep, ToolCallRecord, SessionSummary)
- parser: JSONL incremental parser
- storage: Session data persistent storage
- formatter: Terminal output formatter
- monitor: File system monitoring and session tracking

Environment variables:
- TASK_MIND_SESSION_DIR: Custom session storage directory (default ~/.task-mind/sessions/)
- TASK_MIND_CLAUDE_DIR: Custom Claude Code session directory (default ~/.claude/projects/)
- TASK_MIND_MONITOR_ENABLED: Whether to enable monitoring (default 1, set to 0 to disable)
"""

from task_mind.session.models import (
    AgentType,
    MonitoredSession,
    SessionStatus,
    SessionStep,
    SessionSummary,
    StepType,
    ToolCallRecord,
    ToolCallStatus,
)

__all__ = [
    # Enum types
    "AgentType",
    "SessionStatus",
    "StepType",
    "ToolCallStatus",
    # Data models
    "MonitoredSession",
    "SessionStep",
    "ToolCallRecord",
    "SessionSummary",
]
