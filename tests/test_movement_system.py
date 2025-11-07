"""Tests for MovementSystem."""

from roguelike.components.factories import create_orc
from tests.test_helpers import create_test_entity, create_test_player, create_test_monster
from roguelike.systems.movement_system import MovementSystem
from roguelike.utils.position import Position
from roguelike.world.fov import FOVMap
from roguelike.world.game_map import GameMap
from roguelike.world.tile import Tiles


def test_movement_system_creation():
    """MovementSystem can be created with game map."""
    game_map = GameMap(20, 20)
    system = MovementSystem(game_map)
    assert system.game_map == game_map


def test_can_move_to_floor():
    """Can move to floor tile."""
    game_map = GameMap(20, 20)
    game_map.set_tile(Position(5, 5), Tiles.FLOOR)
    system = MovementSystem(game_map)

    assert system.can_move_to(Position(5, 5), [])


def test_cannot_move_to_wall():
    """Cannot move to wall tile."""
    game_map = GameMap(20, 20)
    system = MovementSystem(game_map)

    assert not system.can_move_to(Position(5, 5), [])


def test_cannot_move_to_blocking_entity():
    """Cannot move to position with blocking entity."""
    game_map = GameMap(20, 20)
    game_map.set_tile(Position(5, 5), Tiles.FLOOR)
    system = MovementSystem(game_map)

    orc = create_orc(Position(5, 5))
    assert not system.can_move_to(Position(5, 5), [orc])


def test_can_move_ignoring_self():
    """Can move to own position when ignoring self."""
    game_map = GameMap(20, 20)
    game_map.set_tile(Position(5, 5), Tiles.FLOOR)
    system = MovementSystem(game_map)

    player = create_test_player(Position(5, 5))
    assert system.can_move_to(Position(5, 5), [player], ignore_entity=player)


def test_get_blocking_entity_finds_blocker():
    """Get blocking entity finds entity at position."""
    game_map = GameMap(20, 20)
    system = MovementSystem(game_map)

    orc = create_orc(Position(5, 5))
    blocker = system.get_blocking_entity(Position(5, 5), [orc])

    assert blocker == orc


def test_get_blocking_entity_returns_none():
    """Get blocking entity returns None when no blocker."""
    game_map = GameMap(20, 20)
    system = MovementSystem(game_map)

    blocker = system.get_blocking_entity(Position(5, 5), [])
    assert blocker is None


def test_move_entity_success():
    """Move entity succeeds on valid move."""
    game_map = GameMap(20, 20)
    game_map.set_tile(Position(5, 5), Tiles.FLOOR)
    game_map.set_tile(Position(5, 6), Tiles.FLOOR)
    system = MovementSystem(game_map)

    player = create_test_player(Position(5, 5))
    success = system.move_entity(player, 0, 1, [player])

    assert success
    assert player.position == Position(5, 6)


def test_move_entity_blocked_by_wall():
    """Move entity fails when blocked by wall."""
    game_map = GameMap(20, 20)
    game_map.set_tile(Position(5, 5), Tiles.FLOOR)
    system = MovementSystem(game_map)

    player = create_test_player(Position(5, 5))
    success = system.move_entity(player, 0, 1, [player])

    assert not success
    assert player.position == Position(5, 5)


def test_move_entity_blocked_by_entity():
    """Move entity fails when blocked by another entity."""
    game_map = GameMap(20, 20)
    game_map.set_tile(Position(5, 5), Tiles.FLOOR)
    game_map.set_tile(Position(5, 6), Tiles.FLOOR)
    system = MovementSystem(game_map)

    player = create_test_player(Position(5, 5))
    orc = create_orc(Position(5, 6))

    success = system.move_entity(player, 0, 1, [player, orc])

    assert not success
    assert player.position == Position(5, 5)


def test_move_entity_to_absolute_position():
    """Move entity to absolute position succeeds."""
    game_map = GameMap(20, 20)
    game_map.set_tile(Position(5, 5), Tiles.FLOOR)
    game_map.set_tile(Position(10, 10), Tiles.FLOOR)
    system = MovementSystem(game_map)

    player = create_test_player(Position(5, 5))
    success = system.move_entity_to(player, Position(10, 10), [player])

    assert success
    assert player.position == Position(10, 10)


def test_update_fov():
    """Update FOV computes field of view."""
    game_map = GameMap(20, 20)
    for y in range(20):
        for x in range(20):
            game_map.set_tile(Position(x, y), Tiles.FLOOR)

    system = MovementSystem(game_map)
    fov_map = FOVMap(game_map)

    system.update_fov(fov_map, Position(10, 10), radius=5)

    # Should be able to see center position
    assert fov_map.is_visible(Position(10, 10))


def test_update_fov_with_different_radius():
    """Update FOV respects radius parameter."""
    game_map = GameMap(20, 20)
    for y in range(20):
        for x in range(20):
            game_map.set_tile(Position(x, y), Tiles.FLOOR)

    system = MovementSystem(game_map)
    fov_map = FOVMap(game_map)

    system.update_fov(fov_map, Position(10, 10), radius=3)

    # Should see nearby positions
    assert fov_map.is_visible(Position(10, 11))
    # Should not see far positions (beyond radius)
    assert not fov_map.is_visible(Position(10, 15))
