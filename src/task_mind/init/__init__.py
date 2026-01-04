"""
Task-Mind Environment Initialization Module

This module provides complete functionality for the `task-mind init` command, including:
- Parallel dependency checking (Node.js, Claude Code)
- Smart installation of missing components
- Authentication configuration (official login vs custom API endpoint)
- Optional Claude Code Router integration
- Configuration persistence and state recovery
"""

from task_mind.init.models import (
    Config,
    APIEndpoint,
    TemporaryState,
    InstallationStep,
    StepStatus,
    DependencyCheckResult,
)
from task_mind.init.exceptions import CommandError, InitErrorCode
from task_mind.init.checker import (
    check_node,
    check_claude_code,
    parallel_dependency_check,
    compare_versions,
)
from task_mind.init.installer import (
    run_external_command,
    install_node,
    install_claude_code,
    get_installation_order,
)
from task_mind.init.config_manager import load_config, save_config
from task_mind.init.configurator import (
    config_exists,
    get_config_path,
    display_config_summary,
    prompt_auth_method,
    configure_official_auth,
    configure_custom_endpoint,
    run_auth_configuration,
    # Phase 6: Custom endpoint configuration
    PRESET_ENDPOINTS,
    validate_endpoint_url,
    prompt_endpoint_type,
    prompt_api_key,
    prompt_custom_endpoint_url,
    # Phase 8: Configuration summary
    format_final_summary,
    suggest_next_steps,
    display_next_steps,
    # claude.json management
    check_claude_json_exists,
    ensure_claude_json_for_custom_auth,
)

__all__ = [
    # Data models
    "Config",
    "APIEndpoint",
    "TemporaryState",
    "InstallationStep",
    "StepStatus",
    "DependencyCheckResult",
    # Exceptions
    "CommandError",
    "InitErrorCode",
    # Checkers
    "check_node",
    "check_claude_code",
    "parallel_dependency_check",
    "compare_versions",
    # Installers
    "run_external_command",
    "install_node",
    "install_claude_code",
    "get_installation_order",
    # Configurators
    "load_config",
    "save_config",
    "config_exists",
    "get_config_path",
    "display_config_summary",
    "prompt_auth_method",
    "configure_official_auth",
    "configure_custom_endpoint",
    "run_auth_configuration",
    # Phase 6: Custom endpoint configuration
    "PRESET_ENDPOINTS",
    "validate_endpoint_url",
    "prompt_endpoint_type",
    "prompt_api_key",
    "prompt_custom_endpoint_url",
    # Phase 8: Configuration summary
    "format_final_summary",
    "suggest_next_steps",
    "display_next_steps",
    # claude.json management
    "check_claude_json_exists",
    "ensure_claude_json_for_custom_auth",
]
