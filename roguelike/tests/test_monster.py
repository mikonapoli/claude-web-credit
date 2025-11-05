"""Tests for Monster class."""

from roguelike.entities.monster import create_orc, create_troll, Monster
from roguelike.utils.position import Position


def test_monster_creation():
    """Monster can be created with stats."""
    monster = Monster(
        position=Position(5, 5),
        char="m",
        name="Goblin",
        max_hp=8,
        defense=0,
        power=2,
        xp_value=25
    )
    assert monster.name == "Goblin"


def test_create_orc():
    """Orc factory creates orc with correct stats."""
    orc = create_orc(Position(10, 10))
    assert orc.name == "Orc"


def test_orc_char():
    """Orc is represented by 'o' character."""
    orc = create_orc(Position(10, 10))
    assert orc.char == "o"


def test_orc_stats():
    """Orc has expected combat stats."""
    orc = create_orc(Position(10, 10))
    assert orc.max_hp == 10 and orc.power == 3


def test_create_troll():
    """Troll factory creates troll with correct stats."""
    troll = create_troll(Position(10, 10))
    assert troll.name == "Troll"


def test_troll_char():
    """Troll is represented by 'T' character."""
    troll = create_troll(Position(10, 10))
    assert troll.char == "T"


def test_troll_stronger_than_orc():
    """Troll has more HP than orc."""
    orc = create_orc(Position(10, 10))
    troll = create_troll(Position(10, 10))
    assert troll.max_hp > orc.max_hp
