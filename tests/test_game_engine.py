"""Tests for GameEngine."""

from roguelike.engine.game_engine import GameEngine
from tests.test_helpers import create_test_player
from roguelike.ui.input_handler import Action
from roguelike.utils.position import Position
from roguelike.world.game_map import GameMap
from roguelike.world.tile import Tiles


def test_engine_creation():
    """Engine can be created with map and player."""
    game_map = GameMap(20, 20)
    player = create_test_player(Position(10, 10))
    engine = GameEngine(game_map, player)
    assert engine.player == player


def test_engine_quit_action_stops_running():
    """Quit action sets running to False via TurnManager."""
    game_map = GameMap(20, 20)
    player = create_test_player(Position(10, 10))
    engine = GameEngine(game_map, player)
    engine.running = True
    continue_game = engine.turn_manager.process_turn(
        Action.QUIT, player, [player], game_map, engine.fov_map, engine.fov_radius
    )
    assert not continue_game


def test_engine_wait_action_consumes_turn():
    """Wait action consumes a turn via TurnManager."""
    game_map = GameMap(20, 20)
    player = create_test_player(Position(10, 10))
    engine = GameEngine(game_map, player)
    turn_consumed, should_quit = engine.turn_manager.handle_player_action(
        Action.WAIT, player, [player], game_map, engine.fov_map, engine.fov_radius
    )
    assert turn_consumed


def test_move_player_to_floor():
    """Player can move to floor tile via TurnManager."""
    game_map = GameMap(20, 20)
    game_map.set_tile(Position(10, 10), Tiles.FLOOR)
    game_map.set_tile(Position(10, 11), Tiles.FLOOR)
    player = create_test_player(Position(10, 10))
    engine = GameEngine(game_map, player)
    turn_consumed, should_quit = engine.turn_manager.handle_player_action(
        Action.MOVE_DOWN, player, [player], game_map, engine.fov_map, engine.fov_radius
    )
    assert turn_consumed


def test_move_player_updates_position():
    """Player position updates after successful move via TurnManager."""
    game_map = GameMap(20, 20)
    game_map.set_tile(Position(10, 10), Tiles.FLOOR)
    game_map.set_tile(Position(10, 11), Tiles.FLOOR)
    player = create_test_player(Position(10, 10))
    engine = GameEngine(game_map, player)
    engine.turn_manager.handle_player_action(
        Action.MOVE_DOWN, player, [player], game_map, engine.fov_map, engine.fov_radius
    )
    assert player.position == Position(10, 11)


def test_cannot_move_into_wall():
    """Player cannot move into wall via TurnManager."""
    game_map = GameMap(20, 20)
    game_map.set_tile(Position(10, 10), Tiles.FLOOR)
    # Position(10, 11) is a wall (default)
    player = create_test_player(Position(10, 10))
    engine = GameEngine(game_map, player)
    turn_consumed, should_quit = engine.turn_manager.handle_player_action(
        Action.MOVE_DOWN, player, [player], game_map, engine.fov_map, engine.fov_radius
    )
    assert not turn_consumed


def test_player_position_unchanged_after_blocked_move():
    """Player position unchanged after blocked move via TurnManager."""
    game_map = GameMap(20, 20)
    game_map.set_tile(Position(10, 10), Tiles.FLOOR)
    player = create_test_player(Position(10, 10))
    engine = GameEngine(game_map, player)
    engine.turn_manager.handle_player_action(
        Action.MOVE_DOWN, player, [player], game_map, engine.fov_map, engine.fov_radius
    )
    assert player.position == Position(10, 10)
