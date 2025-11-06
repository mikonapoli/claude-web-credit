"""Tests for targeting system."""

import pytest

from roguelike.entities.monster import create_orc, create_troll
from roguelike.systems.targeting import TargetingSystem
from roguelike.utils.position import Position


def test_start_targeting_with_no_targets():
    """Starting targeting with no valid targets returns False."""
    system = TargetingSystem()
    result = system.start_targeting(
        origin=Position(5, 5), max_range=10, valid_targets=[]
    )
    assert result is False


def test_start_targeting_with_valid_targets():
    """Starting targeting with valid targets returns True."""
    system = TargetingSystem()
    orc = create_orc(Position(7, 7))
    result = system.start_targeting(
        origin=Position(5, 5), max_range=10, valid_targets=[orc]
    )
    assert result is True


def test_start_targeting_filters_out_of_range_targets():
    """Starting targeting filters out targets beyond max_range."""
    system = TargetingSystem()
    near_orc = create_orc(Position(7, 7))  # Distance 4
    far_orc = create_orc(Position(20, 20))  # Distance 30

    system.start_targeting(
        origin=Position(5, 5), max_range=10, valid_targets=[near_orc, far_orc]
    )

    valid_targets = system.get_valid_targets()
    assert len(valid_targets) == 1
    assert valid_targets[0] == near_orc


def test_start_targeting_filters_dead_targets():
    """Starting targeting filters out dead targets."""
    system = TargetingSystem()
    alive_orc = create_orc(Position(7, 7))
    dead_orc = create_orc(Position(8, 8))
    dead_orc.take_damage(100)  # Kill it

    system.start_targeting(
        origin=Position(5, 5), max_range=10, valid_targets=[alive_orc, dead_orc]
    )

    valid_targets = system.get_valid_targets()
    assert len(valid_targets) == 1
    assert valid_targets[0] == alive_orc


def test_cursor_starts_at_first_target():
    """Cursor position starts at first valid target."""
    system = TargetingSystem()
    orc = create_orc(Position(7, 7))

    system.start_targeting(
        origin=Position(5, 5), max_range=10, valid_targets=[orc]
    )

    assert system.get_cursor_position() == Position(7, 7)


def test_get_current_target_returns_target_at_cursor():
    """get_current_target returns actor at cursor position."""
    system = TargetingSystem()
    orc = create_orc(Position(7, 7))

    system.start_targeting(
        origin=Position(5, 5), max_range=10, valid_targets=[orc]
    )

    target = system.get_current_target()
    assert target == orc


def test_cycle_target_moves_to_next_target():
    """cycle_target moves cursor to next target."""
    system = TargetingSystem()
    orc = create_orc(Position(7, 7))
    troll = create_troll(Position(10, 10))

    system.start_targeting(
        origin=Position(5, 5), max_range=10, valid_targets=[orc, troll]
    )

    assert system.get_cursor_position() == Position(7, 7)

    system.cycle_target(1)
    assert system.get_cursor_position() == Position(10, 10)


def test_cycle_target_wraps_around():
    """cycle_target wraps from last to first target."""
    system = TargetingSystem()
    orc = create_orc(Position(7, 7))
    troll = create_troll(Position(10, 10))

    system.start_targeting(
        origin=Position(5, 5), max_range=10, valid_targets=[orc, troll]
    )

    system.cycle_target(1)  # Move to troll
    system.cycle_target(1)  # Wrap to orc
    assert system.get_cursor_position() == Position(7, 7)


def test_cycle_target_backwards():
    """cycle_target with -1 moves to previous target."""
    system = TargetingSystem()
    orc = create_orc(Position(7, 7))
    troll = create_troll(Position(10, 10))

    system.start_targeting(
        origin=Position(5, 5), max_range=10, valid_targets=[orc, troll]
    )

    system.cycle_target(-1)  # Wrap to troll
    assert system.get_cursor_position() == Position(10, 10)


def test_move_cursor_within_range():
    """move_cursor moves cursor to new position within range."""
    system = TargetingSystem()
    orc = create_orc(Position(7, 7))

    system.start_targeting(
        origin=Position(5, 5), max_range=10, valid_targets=[orc]
    )

    system.move_cursor(1, 0)  # Move right
    assert system.get_cursor_position() == Position(8, 7)


def test_move_cursor_beyond_range_is_ignored():
    """move_cursor beyond max_range is ignored."""
    system = TargetingSystem()
    orc = create_orc(Position(7, 7))

    system.start_targeting(
        origin=Position(5, 5), max_range=5, valid_targets=[orc]
    )

    # Try to move way beyond range
    system.move_cursor(20, 20)
    # Should still be at original position
    assert system.get_cursor_position() == Position(7, 7)


def test_select_target_returns_target_and_exits():
    """select_target returns target at cursor and exits targeting mode."""
    system = TargetingSystem()
    orc = create_orc(Position(7, 7))

    system.start_targeting(
        origin=Position(5, 5), max_range=10, valid_targets=[orc]
    )

    target = system.select_target()
    assert target == orc
    assert system.is_active is False


def test_select_target_with_no_target_at_cursor():
    """select_target with no target at cursor returns None."""
    system = TargetingSystem()
    orc = create_orc(Position(7, 7))

    system.start_targeting(
        origin=Position(5, 5), max_range=10, valid_targets=[orc]
    )

    # Move cursor away from target
    system.move_cursor(5, 0)

    target = system.select_target()
    assert target is None


def test_cancel_targeting_exits_targeting_mode():
    """cancel_targeting exits targeting mode."""
    system = TargetingSystem()
    orc = create_orc(Position(7, 7))

    system.start_targeting(
        origin=Position(5, 5), max_range=10, valid_targets=[orc]
    )

    system.cancel_targeting()
    assert system.is_active is False
    assert system.get_cursor_position() is None
