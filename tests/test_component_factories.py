"""Tests for component-based entity factories."""

from roguelike.components.combat import CombatComponent
from roguelike.components.factories import (
    create_component_orc,
    create_component_player,
    create_component_troll,
)
from roguelike.components.health import HealthComponent
from roguelike.components.inventory import InventoryComponent
from roguelike.components.level import LevelComponent
from roguelike.utils.position import Position


def test_create_component_player():
    """Can create player with components."""
    player = create_component_player(Position(10, 10))

    assert player.name == "Player"
    assert player.position == Position(10, 10)
    assert player.char == "@"
    assert player.blocks_movement


def test_component_player_has_health():
    """Component player has HealthComponent."""
    player = create_component_player(Position(10, 10))

    health = player.get_component(HealthComponent)
    assert health is not None
    assert health.max_hp == 30
    assert health.hp == 30


def test_component_player_has_combat():
    """Component player has CombatComponent."""
    player = create_component_player(Position(10, 10))

    combat = player.get_component(CombatComponent)
    assert combat is not None
    assert combat.power == 5
    assert combat.defense == 2


def test_component_player_has_level():
    """Component player has LevelComponent."""
    player = create_component_player(Position(10, 10))

    level = player.get_component(LevelComponent)
    assert level is not None
    assert level.level == 1
    assert level.xp == 0


def test_component_player_has_inventory():
    """Component player has InventoryComponent."""
    player = create_component_player(Position(10, 10))

    inventory = player.get_component(InventoryComponent)
    assert inventory is not None


def test_component_player_inventory_capacity():
    """Component player inventory has default capacity of 26."""
    player = create_component_player(Position(10, 10))

    inventory = player.get_component(InventoryComponent)
    assert inventory.capacity == 26


def test_create_component_orc():
    """Can create orc with components."""
    orc = create_component_orc(Position(5, 5))

    assert orc.name == "Orc"
    assert orc.position == Position(5, 5)
    assert orc.char == "o"


def test_component_orc_has_health():
    """Component orc has HealthComponent."""
    orc = create_component_orc(Position(5, 5))

    health = orc.get_component(HealthComponent)
    assert health is not None
    assert health.max_hp == 10


def test_component_orc_has_combat():
    """Component orc has CombatComponent."""
    orc = create_component_orc(Position(5, 5))

    combat = orc.get_component(CombatComponent)
    assert combat is not None
    assert combat.power == 3
    assert combat.defense == 0


def test_component_orc_has_level():
    """Component orc has LevelComponent."""
    orc = create_component_orc(Position(5, 5))

    level = orc.get_component(LevelComponent)
    assert level is not None
    assert level.xp_value == 35


def test_create_component_troll():
    """Can create troll with components."""
    troll = create_component_troll(Position(5, 5))

    assert troll.name == "Troll"
    assert troll.position == Position(5, 5)
    assert troll.char == "T"


def test_component_troll_has_health():
    """Component troll has HealthComponent."""
    troll = create_component_troll(Position(5, 5))

    health = troll.get_component(HealthComponent)
    assert health is not None
    assert health.max_hp == 16


def test_component_troll_has_combat():
    """Component troll has CombatComponent."""
    troll = create_component_troll(Position(5, 5))

    combat = troll.get_component(CombatComponent)
    assert combat is not None
    assert combat.power == 4
    assert combat.defense == 1


def test_component_troll_has_level():
    """Component troll has LevelComponent."""
    troll = create_component_troll(Position(5, 5))

    level = troll.get_component(LevelComponent)
    assert level is not None
    assert level.xp_value == 100


def test_component_player_can_take_damage():
    """Component player can take damage via HealthComponent."""
    player = create_component_player(Position(10, 10))
    health = player.get_component(HealthComponent)

    damage = health.take_damage(10)

    assert damage == 10
    assert health.hp == 20


def test_component_orc_can_die():
    """Component orc dies when health reaches 0."""
    orc = create_component_orc(Position(5, 5))
    health = orc.get_component(HealthComponent)

    health.take_damage(10)

    assert health.hp == 0
    assert not health.is_alive
