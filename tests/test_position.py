"""Tests for Position utility."""

from roguelike.utils.position import Position


def test_position_creation():
    """Position can be created with x and y coordinates."""
    pos = Position(5, 10)
    assert pos.x == 5


def test_position_y_coordinate():
    """Position stores y coordinate correctly."""
    pos = Position(5, 10)
    assert pos.y == 10


def test_position_addition():
    """Two positions can be added together."""
    pos1 = Position(1, 2)
    pos2 = Position(3, 4)
    result = pos1 + pos2
    assert result == Position(4, 6)


def test_position_subtraction():
    """One position can be subtracted from another."""
    pos1 = Position(5, 8)
    pos2 = Position(2, 3)
    result = pos1 - pos2
    assert result == Position(3, 5)


def test_euclidean_distance():
    """Distance between positions is calculated correctly."""
    pos1 = Position(0, 0)
    pos2 = Position(3, 4)
    assert pos1.distance_to(pos2) == 5.0


def test_manhattan_distance():
    """Manhattan distance is calculated correctly."""
    pos1 = Position(0, 0)
    pos2 = Position(3, 4)
    assert pos1.manhattan_distance_to(pos2) == 7


def test_neighbors_without_diagonals():
    """Neighbors without diagonals returns 4 positions."""
    pos = Position(5, 5)
    neighbors = list(pos.neighbors(include_diagonals=False))
    assert len(neighbors) == 4


def test_neighbors_with_diagonals():
    """Neighbors with diagonals returns 8 positions."""
    pos = Position(5, 5)
    neighbors = list(pos.neighbors(include_diagonals=True))
    assert len(neighbors) == 8


def test_position_immutable():
    """Position is immutable (frozen dataclass)."""
    pos = Position(1, 2)
    try:
        pos.x = 5
        assert False, "Position should be immutable"
    except AttributeError:
        pass
