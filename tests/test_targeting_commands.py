"""Tests for targeting commands."""

import pytest

from roguelike.commands.game_commands import (
    TargetingCancelCommand,
    TargetingCycleCommand,
    TargetingMoveCommand,
    TargetingSelectCommand,
)
from roguelike.components.factories import create_orc
from roguelike.systems.targeting import TargetingSystem
from roguelike.utils.position import Position


def test_targeting_cancel_command_calls_cancel_targeting():
    """TargetingCancelCommand calls cancel_targeting() on TargetingSystem."""
    targeting_system = TargetingSystem()
    orc = create_orc(Position(10, 10))

    # Start targeting
    targeting_system.start_targeting(
        origin=Position(5, 5),
        max_range=10,
        valid_targets=[orc],
        map_width=80,
        map_height=50,
    )
    assert targeting_system.is_active is True

    # Execute cancel command
    cmd = TargetingCancelCommand(targeting_system)
    result = cmd.execute()

    # Verify targeting was cancelled
    assert targeting_system.is_active is False
    assert result.success is True
    assert result.turn_consumed is False


def test_targeting_cycle_forward_command_calls_cycle_target():
    """TargetingCycleCommand with forward=True calls cycle_target(1)."""
    targeting_system = TargetingSystem()
    orc1 = create_orc(Position(6, 6))
    orc2 = create_orc(Position(8, 8))

    # Start targeting with two targets
    targeting_system.start_targeting(
        origin=Position(5, 5),
        max_range=10,
        valid_targets=[orc1, orc2],
        map_width=80,
        map_height=50,
    )

    # Should start at first target
    assert targeting_system.get_cursor_position() == Position(6, 6)

    # Execute cycle forward command
    cmd = TargetingCycleCommand(targeting_system, forward=True)
    result = cmd.execute()

    # Should move to second target
    assert targeting_system.get_cursor_position() == Position(8, 8)
    assert result.success is True
    assert result.turn_consumed is False


def test_targeting_cycle_backward_command_calls_cycle_target():
    """TargetingCycleCommand with forward=False calls cycle_target(-1)."""
    targeting_system = TargetingSystem()
    orc1 = create_orc(Position(6, 6))
    orc2 = create_orc(Position(8, 8))

    # Start targeting with two targets
    targeting_system.start_targeting(
        origin=Position(5, 5),
        max_range=10,
        valid_targets=[orc1, orc2],
        map_width=80,
        map_height=50,
    )

    # Should start at first target
    assert targeting_system.get_cursor_position() == Position(6, 6)

    # Execute cycle backward command (should wrap to last target)
    cmd = TargetingCycleCommand(targeting_system, forward=False)
    result = cmd.execute()

    # Should wrap to second target
    assert targeting_system.get_cursor_position() == Position(8, 8)
    assert result.success is True
    assert result.turn_consumed is False


def test_targeting_move_command_moves_cursor():
    """TargetingMoveCommand moves cursor correctly."""
    targeting_system = TargetingSystem()
    orc = create_orc(Position(8, 8))

    # Start targeting with larger range
    targeting_system.start_targeting(
        origin=Position(5, 5),
        max_range=15,
        valid_targets=[orc],
        map_width=80,
        map_height=50,
    )

    # Initial cursor position at target (8, 8)
    assert targeting_system.get_cursor_position() == Position(8, 8)

    # Execute move command (move right - within range)
    cmd = TargetingMoveCommand(targeting_system, dx=1, dy=0)
    result = cmd.execute()

    # Cursor should move to (9, 8)
    # Manhattan distance from (5,5) to (9,8) is |9-5| + |8-5| = 4 + 3 = 7, within range
    assert targeting_system.get_cursor_position() == Position(9, 8)
    assert result.success is True
    assert result.turn_consumed is False


def test_targeting_select_command_signals_selection():
    """TargetingSelectCommand signals that targeting selection occurred."""
    targeting_system = TargetingSystem()
    orc = create_orc(Position(10, 10))

    # Start targeting
    targeting_system.start_targeting(
        origin=Position(5, 5),
        max_range=10,
        valid_targets=[orc],
        map_width=80,
        map_height=50,
    )

    # Execute select command
    cmd = TargetingSelectCommand(targeting_system)
    result = cmd.execute()

    # Should signal targeting selection (game engine handles actual target retrieval)
    assert result.success is True
    assert result.turn_consumed is False
    assert result.data is not None
    assert result.data.get("targeting_select") is True


def test_targeting_cycle_with_no_targets_does_not_crash():
    """TargetingCycleCommand with no targets doesn't crash."""
    targeting_system = TargetingSystem()

    # Don't start targeting - system is inactive
    assert targeting_system.is_active is False

    # Execute cycle command - should not crash
    cmd = TargetingCycleCommand(targeting_system, forward=True)
    result = cmd.execute()

    assert result.success is True
    assert result.turn_consumed is False
