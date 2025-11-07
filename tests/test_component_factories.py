"""Tests for component-based entity factories."""

from roguelike.components.combat import CombatComponent
from roguelike.components.factories import (
    create_orc,
    create_player,
    create_troll,
)
from roguelike.components.health import HealthComponent
from roguelike.components.inventory import InventoryComponent
from roguelike.components.level import LevelComponent
from roguelike.utils.position import Position


def test_create_player():
    """Can create player with components."""
    player = create_player(Position(10, 10))

    assert player.name == "Player"
    assert player.position == Position(10, 10)
    assert player.char == "@"
    assert player.blocks_movement


def test_player_has_health():
    """Player has HealthComponent."""
    player = create_player(Position(10, 10))

    health = player.get_component(HealthComponent)
    assert health is not None
    assert health.max_hp == 30
    assert health.hp == 30


def test_player_has_combat():
    """Player has CombatComponent."""
    player = create_player(Position(10, 10))

    combat = player.get_component(CombatComponent)
    assert combat is not None
    assert combat.power == 5
    assert combat.defense == 2


def test_player_has_level():
    """Player has LevelComponent."""
    player = create_player(Position(10, 10))

    level = player.get_component(LevelComponent)
    assert level is not None
    assert level.level == 1
    assert level.xp == 0


def test_player_has_inventory():
    """Player has InventoryComponent."""
    player = create_player(Position(10, 10))

    inventory = player.get_component(InventoryComponent)
    assert inventory is not None


def test_player_inventory_capacity():
    """Player inventory has default capacity of 26."""
    player = create_player(Position(10, 10))

    inventory = player.get_component(InventoryComponent)
    assert inventory.capacity == 26


def test_create_orc():
    """Can create orc with components."""
    orc = create_orc(Position(5, 5))

    assert orc.name == "Orc"
    assert orc.position == Position(5, 5)
    assert orc.char == "o"


def test_orc_has_health():
    """Orc has HealthComponent."""
    orc = create_orc(Position(5, 5))

    health = orc.get_component(HealthComponent)
    assert health is not None
    assert health.max_hp == 10


def test_orc_has_combat():
    """Orc has CombatComponent."""
    orc = create_orc(Position(5, 5))

    combat = orc.get_component(CombatComponent)
    assert combat is not None
    assert combat.power == 3
    assert combat.defense == 0


def test_orc_has_level():
    """Orc has LevelComponent."""
    orc = create_orc(Position(5, 5))

    level = orc.get_component(LevelComponent)
    assert level is not None
    assert level.xp_value == 35


def test_create_troll():
    """Can create troll with components."""
    troll = create_troll(Position(5, 5))

    assert troll.name == "Troll"
    assert troll.position == Position(5, 5)
    assert troll.char == "T"


def test_troll_has_health():
    """Troll has HealthComponent."""
    troll = create_troll(Position(5, 5))

    health = troll.get_component(HealthComponent)
    assert health is not None
    assert health.max_hp == 16


def test_troll_has_combat():
    """Troll has CombatComponent."""
    troll = create_troll(Position(5, 5))

    combat = troll.get_component(CombatComponent)
    assert combat is not None
    assert combat.power == 4
    assert combat.defense == 1


def test_troll_has_level():
    """Troll has LevelComponent."""
    troll = create_troll(Position(5, 5))

    level = troll.get_component(LevelComponent)
    assert level is not None
    assert level.xp_value == 100


def test_player_can_take_damage():
    """Player can take damage via HealthComponent."""
    player = create_player(Position(10, 10))
    health = player.get_component(HealthComponent)

    damage = health.take_damage(10)

    assert damage == 10
    assert health.hp == 20


def test_orc_can_die():
    """Orc dies when health reaches 0."""
    orc = create_orc(Position(5, 5))
    health = orc.get_component(HealthComponent)

    health.take_damage(10)

    assert health.hp == 0
    assert not health.is_alive
