"""Tests for GameEngine."""

from roguelike.engine.game_engine import GameEngine
from roguelike.entities.player import Player
from roguelike.ui.input_handler import Action
from roguelike.utils.position import Position
from roguelike.world.game_map import GameMap
from roguelike.world.tile import Tiles


def test_engine_creation():
    """Engine can be created with map and player."""
    game_map = GameMap(20, 20)
    player = Player(Position(10, 10))
    engine = GameEngine(game_map, player)
    assert engine.player == player


def test_engine_quit_action_stops_running():
    """Quit action sets running to False."""
    game_map = GameMap(20, 20)
    player = Player(Position(10, 10))
    engine = GameEngine(game_map, player)
    engine.running = True
    engine.handle_action(Action.QUIT)
    assert not engine.running


def test_engine_wait_action_consumes_turn():
    """Wait action consumes a turn."""
    game_map = GameMap(20, 20)
    player = Player(Position(10, 10))
    engine = GameEngine(game_map, player)
    turn_taken = engine.handle_action(Action.WAIT)
    assert turn_taken


def test_move_player_to_floor():
    """Player can move to floor tile."""
    game_map = GameMap(20, 20)
    game_map.set_tile(Position(10, 10), Tiles.FLOOR)
    game_map.set_tile(Position(10, 11), Tiles.FLOOR)
    player = Player(Position(10, 10))
    engine = GameEngine(game_map, player)
    success = engine.try_move_player(0, 1)
    assert success


def test_move_player_updates_position():
    """Player position updates after successful move."""
    game_map = GameMap(20, 20)
    game_map.set_tile(Position(10, 10), Tiles.FLOOR)
    game_map.set_tile(Position(10, 11), Tiles.FLOOR)
    player = Player(Position(10, 10))
    engine = GameEngine(game_map, player)
    engine.try_move_player(0, 1)
    assert player.position == Position(10, 11)


def test_cannot_move_into_wall():
    """Player cannot move into wall."""
    game_map = GameMap(20, 20)
    game_map.set_tile(Position(10, 10), Tiles.FLOOR)
    # Position(10, 11) is a wall (default)
    player = Player(Position(10, 10))
    engine = GameEngine(game_map, player)
    success = engine.try_move_player(0, 1)
    assert not success


def test_player_position_unchanged_after_blocked_move():
    """Player position unchanged after blocked move."""
    game_map = GameMap(20, 20)
    game_map.set_tile(Position(10, 10), Tiles.FLOOR)
    player = Player(Position(10, 10))
    engine = GameEngine(game_map, player)
    engine.try_move_player(0, 1)  # Try to move into wall
    assert player.position == Position(10, 10)
