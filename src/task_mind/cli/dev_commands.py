"""dev command group - Task-Mind developer commands

Contains:
  - pack: User directory → Package resources
"""

import click

from .pack_command import dev_pack
from .agent_friendly import AgentFriendlyGroup


@click.group(name="dev", cls=AgentFriendlyGroup)
def dev_group():
    """
    Task-Mind developer commands

    For Task-Mind project development and testing.

    \b
    Subcommands:
      pack     User directory → Package resources (src/task-mind/resources/)

    \b
    Data flow:
      User directory (~/.claude/, ~/.task-mind/)
          ↓ pack
      Package resources (src/task-mind/resources/)
          ↓ (PyPI release)
      User installation (task-mind init)
          ↓
      User directory (~/.claude/, ~/.task-mind/)

    \b
    Examples:
      task-mind dev pack              # Package user directory resources
      task-mind dev pack --dry-run    # Preview files to be synced
      task-mind dev pack --all        # Ignore manifest, sync all
    """
    pass


# Register subcommand
dev_group.add_command(dev_pack, name="pack")
