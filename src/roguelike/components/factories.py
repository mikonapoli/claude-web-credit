"""Factory functions for creating component-based entities."""

from roguelike.components.combat import CombatComponent
from roguelike.components.entity import ComponentEntity
from roguelike.components.health import HealthComponent
from roguelike.components.inventory import InventoryComponent
from roguelike.components.level import LevelComponent
from roguelike.utils.position import Position


def create_player(position: Position) -> ComponentEntity:
    """Create a player entity using components.

    Args:
        position: Starting position

    Returns:
        Player entity with components
    """
    player = ComponentEntity(
        position=position,
        char="@",
        name="Player",
        blocks_movement=True,
    )

    # Add components
    player.add_component(HealthComponent(max_hp=30))
    player.add_component(CombatComponent(power=5, defense=2))
    player.add_component(LevelComponent(level=1, xp=0, xp_value=0))
    player.add_component(InventoryComponent(capacity=26))

    return player


def create_orc(position: Position) -> ComponentEntity:
    """Create an orc entity using components.

    Args:
        position: Starting position

    Returns:
        Orc entity with components
    """
    orc = ComponentEntity(
        position=position,
        char="o",
        name="Orc",
        blocks_movement=True,
    )

    # Add components
    orc.add_component(HealthComponent(max_hp=10))
    orc.add_component(CombatComponent(power=3, defense=0))
    orc.add_component(LevelComponent(level=1, xp=0, xp_value=35))

    return orc


def create_troll(position: Position) -> ComponentEntity:
    """Create a troll entity using components.

    Args:
        position: Starting position

    Returns:
        Troll entity with components
    """
    troll = ComponentEntity(
        position=position,
        char="T",
        name="Troll",
        blocks_movement=True,
    )

    # Add components
    troll.add_component(HealthComponent(max_hp=16))
    troll.add_component(CombatComponent(power=4, defense=1))
    troll.add_component(LevelComponent(level=2, xp=0, xp_value=100))

    return troll


# Backward compatibility aliases
create_component_player = create_player
create_component_orc = create_orc
create_component_troll = create_troll
