"""Task-Mind serve command - Web service GUI.

Starts a local HTTP web server for the Task-Mind GUI,
allowing access through any modern browser.
"""

import click

from task_mind.server.utils import SERVER_PORT, SERVER_HOST


@click.command("serve")
@click.option(
    "--port",
    "-p",
    type=int,
    default=SERVER_PORT,
    help=f"Port to listen on (default: {SERVER_PORT})",
)
@click.option(
    "--host",
    "-h",
    type=str,
    default=SERVER_HOST,
    help=f"Host to bind to (default: {SERVER_HOST} for security)",
)
@click.option(
    "--open/--no-open",
    default=True,
    help="Auto-open browser (default: --open)",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug mode with verbose logging",
)
def serve(port: int, host: str, open: bool, debug: bool) -> None:
    """Start the Task-Mind web service GUI.

    DEPRECATED: Use 'task-mind server' instead for background daemon mode.

    Launches a local HTTP server that serves the Task-Mind GUI
    through your web browser. This replaces the need for
    platform-specific GUI dependencies.

    \b
    Examples:
        task-mind serve              # Start on default port 8093
        task-mind serve -p 3000      # Start on port 3000
        task-mind serve --no-open    # Don't auto-open browser

    \b
    The server binds to 127.0.0.1 by default for security.
    Access the GUI at: http://127.0.0.1:8093
    """
    import click
    click.echo(
        click.style("Warning: ", fg="yellow", bold=True) +
        "'task-mind serve' is deprecated. Use 'task-mind server' for background daemon mode.",
        err=True
    )
    click.echo()

    from task_mind.server.runner import run_server

    log_level = "debug" if debug else "info"

    run_server(
        host=host,
        port=port,
        auto_open=open,
        auto_port=True,  # Find available port if specified is in use
        log_level=log_level,
    )
