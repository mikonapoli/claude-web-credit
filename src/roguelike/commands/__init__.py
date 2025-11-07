"""Command pattern for game actions."""

from roguelike.commands.command import Command, CommandResult
from roguelike.commands.executor import CommandExecutor
from roguelike.commands.game_commands import (
    MoveCommand,
    WaitCommand,
    QuitCommand,
    DescendStairsCommand,
    PickupItemCommand,
    StartTargetingCommand,
    TargetingMoveCommand,
    TargetingSelectCommand,
    TargetingCancelCommand,
    TargetingCycleCommand,
)

__all__ = [
    "Command",
    "CommandResult",
    "CommandExecutor",
    "MoveCommand",
    "WaitCommand",
    "QuitCommand",
    "DescendStairsCommand",
    "PickupItemCommand",
    "StartTargetingCommand",
    "TargetingMoveCommand",
    "TargetingSelectCommand",
    "TargetingCancelCommand",
    "TargetingCycleCommand",
]
