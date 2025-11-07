"""Tests for StartTargetingCommand."""

import pytest

from roguelike.commands.game_commands import StartTargetingCommand
from roguelike.components.factories import create_orc
from roguelike.systems.targeting import TargetingSystem
from roguelike.ui.message_log import MessageLog
from roguelike.utils.position import Position
from roguelike.world.fov import FOVMap
from roguelike.world.game_map import GameMap
from roguelike.world.tile import Tiles
from tests.test_helpers import create_test_player


def test_start_targeting_finds_visible_monsters():
    """StartTargetingCommand finds visible monsters and activates targeting."""
    game_map = GameMap(width=80, height=50)

    # Make a corridor of transparent walkable floor tiles from player to orc
    for x in range(5, 10):
        for y in range(5, 10):
            game_map.tiles[x, y] = Tiles.FLOOR

    fov_map = FOVMap(game_map)
    targeting_system = TargetingSystem()
    message_log = MessageLog()

    player = create_test_player(Position(5, 5))
    orc = create_orc(Position(8, 8))
    entities = [orc]

    # Make orc visible
    fov_map.compute_fov(player.position, radius=10)

    cmd = StartTargetingCommand(
        player=player,
        entities=entities,
        fov_map=fov_map,
        targeting_system=targeting_system,
        message_log=message_log,
        game_map=game_map,
    )

    result = cmd.execute()

    # Should succeed and signal targeting start
    assert result.success is True
    assert result.turn_consumed is False
    assert result.data is not None
    assert result.data.get("start_targeting") is True

    # Targeting system should be active
    assert targeting_system.is_active is True


def test_start_targeting_no_visible_monsters():
    """StartTargetingCommand fails when no visible monsters."""
    game_map = GameMap(width=80, height=50)
    fov_map = FOVMap(game_map)
    targeting_system = TargetingSystem()
    message_log = MessageLog()

    player = create_test_player(Position(5, 5))
    orc = create_orc(Position(50, 50))  # Far away, not visible
    entities = [orc]

    # Compute FOV but orc is too far
    fov_map.compute_fov(player.position, radius=10)

    cmd = StartTargetingCommand(
        player=player,
        entities=entities,
        fov_map=fov_map,
        targeting_system=targeting_system,
        message_log=message_log,
        game_map=game_map,
    )

    result = cmd.execute()

    # Should fail
    assert result.success is False
    assert result.turn_consumed is False

    # Targeting system should not be active
    assert targeting_system.is_active is False


def test_start_targeting_no_monsters():
    """StartTargetingCommand fails when no monsters in entities."""
    game_map = GameMap(width=80, height=50)
    fov_map = FOVMap(game_map)
    targeting_system = TargetingSystem()
    message_log = MessageLog()

    player = create_test_player(Position(5, 5))
    entities = []  # No monsters

    # Compute FOV
    fov_map.compute_fov(player.position, radius=10)

    cmd = StartTargetingCommand(
        player=player,
        entities=entities,
        fov_map=fov_map,
        targeting_system=targeting_system,
        message_log=message_log,
        game_map=game_map,
    )

    result = cmd.execute()

    # Should fail
    assert result.success is False
    assert result.turn_consumed is False

    # Targeting system should not be active
    assert targeting_system.is_active is False


def test_start_targeting_logs_message_on_success():
    """StartTargetingCommand logs message when targeting starts."""
    game_map = GameMap(width=80, height=50)

    # Make a corridor of transparent walkable floor tiles from player to orc
    for x in range(5, 10):
        for y in range(5, 10):
            game_map.tiles[x, y] = Tiles.FLOOR

    fov_map = FOVMap(game_map)
    targeting_system = TargetingSystem()
    message_log = MessageLog()

    player = create_test_player(Position(5, 5))
    orc = create_orc(Position(8, 8))
    entities = [orc]

    # Make orc visible
    fov_map.compute_fov(player.position, radius=10)

    cmd = StartTargetingCommand(
        player=player,
        entities=entities,
        fov_map=fov_map,
        targeting_system=targeting_system,
        message_log=message_log,
        game_map=game_map,
    )

    cmd.execute()

    # Should have logged a message
    assert len(message_log.messages) > 0
    assert "select" in str(message_log.messages[-1]).lower()


def test_start_targeting_logs_message_on_no_targets():
    """StartTargetingCommand logs message when no targets found."""
    game_map = GameMap(width=80, height=50)
    fov_map = FOVMap(game_map)
    targeting_system = TargetingSystem()
    message_log = MessageLog()

    player = create_test_player(Position(5, 5))
    entities = []

    # Compute FOV
    fov_map.compute_fov(player.position, radius=10)

    cmd = StartTargetingCommand(
        player=player,
        entities=entities,
        fov_map=fov_map,
        targeting_system=targeting_system,
        message_log=message_log,
        game_map=game_map,
    )

    cmd.execute()

    # Should have logged a message
    assert len(message_log.messages) > 0
    assert "no visible targets" in str(message_log.messages[-1]).lower()


def test_start_targeting_respects_range():
    """StartTargetingCommand respects max_range of 10."""
    game_map = GameMap(width=80, height=50)

    # Make a large area transparent floor so we can test range
    for x in range(5, 20):
        for y in range(5, 20):
            game_map.tiles[x, y] = Tiles.FLOOR

    fov_map = FOVMap(game_map)
    targeting_system = TargetingSystem()
    message_log = MessageLog()

    player = create_test_player(Position(5, 5))
    # Place orc at manhattan distance > 10 but still visible
    orc = create_orc(Position(17, 17))  # Distance = |17-5| + |17-5| = 24
    entities = [orc]

    # Make the whole map visible
    fov_map.compute_fov(player.position, radius=50)

    cmd = StartTargetingCommand(
        player=player,
        entities=entities,
        fov_map=fov_map,
        targeting_system=targeting_system,
        message_log=message_log,
        game_map=game_map,
    )

    result = cmd.execute()

    # Should fail because out of range
    assert result.success is False

    # Message should mention range
    assert len(message_log.messages) > 0
    assert "no targets in range" in str(message_log.messages[-1]).lower()
