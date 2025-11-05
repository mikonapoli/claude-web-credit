"""Tests for Entity class."""

from roguelike.entities.entity import Entity
from roguelike.utils.position import Position


def test_entity_creation():
    """Entity can be created with required attributes."""
    pos = Position(5, 10)
    entity = Entity(position=pos, char="@", name="Test")
    assert entity.name == "Test"


def test_entity_position():
    """Entity stores position correctly."""
    pos = Position(5, 10)
    entity = Entity(position=pos, char="@", name="Test")
    assert entity.position == pos


def test_entity_char():
    """Entity stores display character correctly."""
    entity = Entity(position=Position(0, 0), char="@", name="Test")
    assert entity.char == "@"


def test_entity_blocks_movement_default():
    """Entity does not block movement by default."""
    entity = Entity(position=Position(0, 0), char="@", name="Test")
    assert not entity.blocks_movement


def test_entity_blocks_movement_true():
    """Entity can be set to block movement."""
    entity = Entity(position=Position(0, 0), char="@", name="Test", blocks_movement=True)
    assert entity.blocks_movement


def test_entity_move_relative():
    """Entity can move by relative offset."""
    entity = Entity(position=Position(5, 5), char="@", name="Test")
    entity.move(2, 3)
    assert entity.position == Position(7, 8)


def test_entity_move_to_absolute():
    """Entity can move to absolute position."""
    entity = Entity(position=Position(5, 5), char="@", name="Test")
    entity.move_to(Position(10, 15))
    assert entity.position == Position(10, 15)


def test_entity_repr():
    """Entity has useful string representation."""
    entity = Entity(position=Position(5, 5), char="@", name="Player")
    repr_str = repr(entity)
    assert "Entity" in repr_str
    assert "Player" in repr_str
