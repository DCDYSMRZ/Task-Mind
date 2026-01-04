"""CLI commands for managing task-mind server autostart."""

import click

from task_mind.autostart import get_autostart_manager


@click.group("autostart")
def autostart_group():
    """Manage task-mind server autostart on system boot.

    Configure the task-mind web server to start automatically when you log in.

    \b
    Examples:
        task-mind autostart enable    # Enable autostart
        task-mind autostart disable   # Disable autostart
        task-mind autostart status    # Check current status
    """
    pass


@autostart_group.command("enable")
def enable():
    """Enable task-mind server autostart on system boot."""
    try:
        manager = get_autostart_manager()
        success, message = manager.enable()

        if success:
            click.echo(click.style("✓ ", fg="green") + message)
        else:
            click.echo(click.style("✗ ", fg="red") + message)
            raise SystemExit(1)

    except NotImplementedError as e:
        click.echo(click.style("✗ ", fg="red") + str(e))
        raise SystemExit(1)


@autostart_group.command("disable")
def disable():
    """Disable task-mind server autostart on system boot."""
    try:
        manager = get_autostart_manager()
        success, message = manager.disable()

        if success:
            click.echo(click.style("✓ ", fg="green") + message)
        else:
            click.echo(click.style("✗ ", fg="red") + message)
            raise SystemExit(1)

    except NotImplementedError as e:
        click.echo(click.style("✗ ", fg="red") + str(e))
        raise SystemExit(1)


@autostart_group.command("status")
def status():
    """Show current autostart configuration status."""
    try:
        manager = get_autostart_manager()
        status = manager.get_status()

        if status.enabled:
            click.echo(f"Autostart: {click.style('enabled', fg='green')}")
            click.echo(f"Platform:  {status.platform}")
            if status.config_path:
                click.echo(f"Config:    {status.config_path}")
        else:
            click.echo(f"Autostart: {click.style('disabled', fg='yellow')}")
            click.echo(f"Platform:  {status.platform}")

    except NotImplementedError as e:
        click.echo(click.style("✗ ", fg="red") + str(e))
        raise SystemExit(1)
