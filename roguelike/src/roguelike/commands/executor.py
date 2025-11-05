"""Command executor for managing command execution and history."""

from typing import List

from roguelike.commands.command import Command, CommandResult


class CommandExecutor:
    """Executes commands and maintains history for undo/redo."""

    def __init__(self, max_history: int = 100):
        """Initialize command executor.

        Args:
            max_history: Maximum number of commands to keep in history
        """
        self.max_history = max_history
        self.history: List[Command] = []
        self.current_index = -1

    def execute(self, command: Command) -> CommandResult:
        """Execute a command and add to history if successful.

        Args:
            command: Command to execute

        Returns:
            Result of command execution
        """
        result = command.execute()

        if result.success and command.can_undo():
            # Remove any commands after current index (for redo)
            self.history = self.history[: self.current_index + 1]

            # Add command to history
            self.history.append(command)

            # Trim history if needed
            if len(self.history) > self.max_history:
                self.history.pop(0)
            else:
                self.current_index += 1

        return result

    def can_undo(self) -> bool:
        """Check if undo is available.

        Returns:
            True if there are commands to undo
        """
        return self.current_index >= 0

    def undo(self) -> bool:
        """Undo the last command.

        Returns:
            True if undo was successful
        """
        if not self.can_undo():
            return False

        command = self.history[self.current_index]
        command.undo()
        self.current_index -= 1
        return True

    def can_redo(self) -> bool:
        """Check if redo is available.

        Returns:
            True if there are commands to redo
        """
        return self.current_index < len(self.history) - 1

    def redo(self) -> bool:
        """Redo the next command.

        Returns:
            True if redo was successful
        """
        if not self.can_redo():
            return False

        self.current_index += 1
        command = self.history[self.current_index]
        command.execute()
        return True

    def clear_history(self) -> None:
        """Clear all command history."""
        self.history.clear()
        self.current_index = -1

    def get_history_size(self) -> int:
        """Get the number of commands in history.

        Returns:
            Size of command history
        """
        return len(self.history)
