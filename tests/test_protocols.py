"""Tests for protocol interfaces."""

from tests.test_helpers import create_test_entity, create_test_player, create_test_monster
from roguelike.entities.monster import create_orc
# from roguelike.entities.player import Player
from roguelike.utils.position import Position
from roguelike.utils.protocols import (
    AIControlled,
    Combatant,
    Levelable,
    Positionable,
    XPSource,
)


def test_actor_implements_combatant():
    """Actor implements Combatant protocol."""
    actor = Actor(
        position=Position(0, 0),
        char="@",
        name="TestActor",
        max_hp=10,
        defense=1,
        power=5,
    )
    # Type check - this will fail at type-check time if protocol not satisfied
    combatant: Combatant = actor
    assert combatant.name == "TestActor"


def test_actor_implements_positionable():
    """Actor implements Positionable protocol."""
    actor = Actor(
        position=Position(0, 0),
        char="@",
        name="TestActor",
        max_hp=10,
        defense=1,
        power=5,
    )
    positionable: Positionable = actor
    assert positionable.position == Position(0, 0)


def test_monster_implements_ai_controlled():
    """Monster implements AIControlled protocol."""
    monster = create_orc(Position(5, 5))
    ai_controlled: AIControlled = monster
    assert ai_controlled.is_alive


def test_monster_implements_xp_source():
    """Monster implements XPSource protocol."""
    monster = create_orc(Position(5, 5))
    xp_source: XPSource = monster
    assert xp_source.xp_value == 35


def test_player_implements_levelable():
    """Player implements Levelable protocol."""
    player = create_test_player(Position(10, 10))
    levelable: Levelable = player
    assert levelable.level == 1
