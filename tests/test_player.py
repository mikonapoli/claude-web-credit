"""Tests for Player class."""

from roguelike.entities.player import Player
from roguelike.utils.position import Position


def test_player_creation():
    """Player can be created at a position."""
    player = Player(Position(10, 10))
    assert player.name == "Player"


def test_player_has_combat_stats():
    """Player has appropriate combat stats."""
    player = Player(Position(10, 10))
    assert player.max_hp == 30


def test_player_char_is_at_symbol():
    """Player is represented by @ symbol."""
    player = Player(Position(10, 10))
    assert player.char == "@"


def test_player_blocks_movement():
    """Player blocks movement."""
    player = Player(Position(10, 10))
    assert player.blocks_movement
