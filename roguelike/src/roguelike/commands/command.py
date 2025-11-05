"""Base command interface for actions."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class CommandResult:
    """Result of executing a command."""

    success: bool
    turn_consumed: bool
    should_quit: bool = False
    data: Any = None


class Command(ABC):
    """Base class for all commands."""

    @abstractmethod
    def execute(self) -> CommandResult:
        """Execute the command.

        Returns:
            Result of command execution
        """
        pass

    def can_undo(self) -> bool:
        """Check if this command can be undone.

        Returns:
            True if command supports undo
        """
        return False

    def undo(self) -> None:
        """Undo the command.

        Should only be called if can_undo() returns True.
        """
        raise NotImplementedError("Command does not support undo")
