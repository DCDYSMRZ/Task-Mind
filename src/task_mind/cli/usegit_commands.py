"""use-git command group - Sync Task-Mind resources via Git

Treat ~/.task-mind/ as a Git repository, sync resources to remote repository for multi-device sharing.
"""

import click

from .agent_friendly import AgentFriendlyGroup
from .sync_command import sync_cmd


@click.group(name="use-git", cls=AgentFriendlyGroup, hidden=True)
def usegit_group():
    """
    [Deprecated] Sync Task-Mind resources via Git

    This command is deprecated, please use `task-mind sync` instead.

    \b
    New commands:
      task-mind sync --set-repo git@github.com:user/my-resources.git  # First time use
      task-mind sync              # Sync resources
      task-mind sync --dry-run    # Preview content to be synced

    \b
    Sync content:
      ~/.claude/commands/task-mind.*.md   # Command files
      ~/.claude/skills/task-mind-*        # Skills
      ~/.task-mind/recipes/               # Recipes
    """
    click.echo("[!]  'task-mind use-git' command is deprecated, please use 'task-mind sync'", err=True)


# Register subcommand
usegit_group.add_command(sync_cmd, name="sync")
