"""Factory functions for creating component-based entities."""

from roguelike.components.combat import CombatComponent
from roguelike.components.entity import ComponentEntity
from roguelike.components.equipment import EquipmentComponent, EquipmentSlot, EquipmentStats
from roguelike.components.health import HealthComponent
from roguelike.components.inventory import InventoryComponent
from roguelike.components.level import LevelComponent
from roguelike.utils.position import Position


def create_component_player(position: Position) -> ComponentEntity:
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
    player.add_component(EquipmentComponent())

    return player


def create_component_orc(position: Position) -> ComponentEntity:
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


def create_component_troll(position: Position) -> ComponentEntity:
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


# Equipment Factory Functions

def create_wooden_club(position: Position) -> ComponentEntity:
    """Create a wooden club weapon."""
    item = ComponentEntity(position=position, char="\\", name="Wooden Club", blocks_movement=False)
    item.add_component(EquipmentStats(slot=EquipmentSlot.WEAPON, power_bonus=2))
    return item


def create_iron_sword(position: Position) -> ComponentEntity:
    """Create an iron sword weapon."""
    item = ComponentEntity(position=position, char="/", name="Iron Sword", blocks_movement=False)
    item.add_component(EquipmentStats(slot=EquipmentSlot.WEAPON, power_bonus=3))
    return item


def create_steel_sword(position: Position) -> ComponentEntity:
    """Create a steel sword weapon."""
    item = ComponentEntity(position=position, char="/", name="Steel Sword", blocks_movement=False)
    item.add_component(EquipmentStats(slot=EquipmentSlot.WEAPON, power_bonus=5))
    return item


def create_enchanted_blade(position: Position) -> ComponentEntity:
    """Create an enchanted blade weapon."""
    item = ComponentEntity(position=position, char="/", name="Enchanted Blade", blocks_movement=False)
    item.add_component(EquipmentStats(slot=EquipmentSlot.WEAPON, power_bonus=7, defense_bonus=1))
    return item


def create_battle_axe(position: Position) -> ComponentEntity:
    """Create a battle axe weapon."""
    item = ComponentEntity(position=position, char="/", name="Battle Axe", blocks_movement=False)
    item.add_component(EquipmentStats(slot=EquipmentSlot.WEAPON, power_bonus=8, defense_bonus=-1))
    return item


def create_leather_armor(position: Position) -> ComponentEntity:
    """Create leather armor."""
    item = ComponentEntity(position=position, char="[", name="Leather Armor", blocks_movement=False)
    item.add_component(EquipmentStats(slot=EquipmentSlot.ARMOR, defense_bonus=2))
    return item


def create_chainmail(position: Position) -> ComponentEntity:
    """Create chainmail armor."""
    item = ComponentEntity(position=position, char="[", name="Chainmail", blocks_movement=False)
    item.add_component(EquipmentStats(slot=EquipmentSlot.ARMOR, defense_bonus=4))
    return item


def create_plate_armor(position: Position) -> ComponentEntity:
    """Create plate armor."""
    item = ComponentEntity(position=position, char="[", name="Plate Armor", blocks_movement=False)
    item.add_component(EquipmentStats(slot=EquipmentSlot.ARMOR, defense_bonus=6, max_hp_bonus=5))
    return item


def create_dragon_scale_armor(position: Position) -> ComponentEntity:
    """Create dragon scale armor."""
    item = ComponentEntity(position=position, char="[", name="Dragon Scale Armor", blocks_movement=False)
    item.add_component(EquipmentStats(slot=EquipmentSlot.ARMOR, power_bonus=1, defense_bonus=8, max_hp_bonus=10))
    return item


def create_leather_helmet(position: Position) -> ComponentEntity:
    """Create a leather helmet."""
    item = ComponentEntity(position=position, char="^", name="Leather Helmet", blocks_movement=False)
    item.add_component(EquipmentStats(slot=EquipmentSlot.HELMET, defense_bonus=1, max_hp_bonus=2))
    return item


def create_steel_helmet(position: Position) -> ComponentEntity:
    """Create a steel helmet."""
    item = ComponentEntity(position=position, char="^", name="Steel Helmet", blocks_movement=False)
    item.add_component(EquipmentStats(slot=EquipmentSlot.HELMET, defense_bonus=2, max_hp_bonus=5))
    return item


def create_crown_of_kings(position: Position) -> ComponentEntity:
    """Create crown of kings helmet."""
    item = ComponentEntity(position=position, char="^", name="Crown of Kings", blocks_movement=False)
    item.add_component(EquipmentStats(slot=EquipmentSlot.HELMET, power_bonus=2, defense_bonus=3, max_hp_bonus=10))
    return item


def create_leather_boots(position: Position) -> ComponentEntity:
    """Create leather boots."""
    item = ComponentEntity(position=position, char="]", name="Leather Boots", blocks_movement=False)
    item.add_component(EquipmentStats(slot=EquipmentSlot.BOOTS, defense_bonus=1))
    return item


def create_steel_boots(position: Position) -> ComponentEntity:
    """Create steel boots."""
    item = ComponentEntity(position=position, char="]", name="Steel Boots", blocks_movement=False)
    item.add_component(EquipmentStats(slot=EquipmentSlot.BOOTS, power_bonus=1, defense_bonus=2))
    return item


def create_boots_of_speed(position: Position) -> ComponentEntity:
    """Create boots of speed."""
    item = ComponentEntity(position=position, char="]", name="Boots of Speed", blocks_movement=False)
    item.add_component(EquipmentStats(slot=EquipmentSlot.BOOTS, defense_bonus=1, max_hp_bonus=5))
    return item


def create_leather_gloves(position: Position) -> ComponentEntity:
    """Create leather gloves."""
    item = ComponentEntity(position=position, char=")", name="Leather Gloves", blocks_movement=False)
    item.add_component(EquipmentStats(slot=EquipmentSlot.GLOVES, power_bonus=1))
    return item


def create_gauntlets(position: Position) -> ComponentEntity:
    """Create gauntlets."""
    item = ComponentEntity(position=position, char=")", name="Gauntlets", blocks_movement=False)
    item.add_component(EquipmentStats(slot=EquipmentSlot.GLOVES, power_bonus=2, defense_bonus=1))
    return item


def create_ring_of_power(position: Position) -> ComponentEntity:
    """Create ring of power."""
    item = ComponentEntity(position=position, char="=", name="Ring of Power", blocks_movement=False)
    item.add_component(EquipmentStats(slot=EquipmentSlot.RING, power_bonus=3))
    return item


def create_ring_of_protection(position: Position) -> ComponentEntity:
    """Create ring of protection."""
    item = ComponentEntity(position=position, char="=", name="Ring of Protection", blocks_movement=False)
    item.add_component(EquipmentStats(slot=EquipmentSlot.RING, defense_bonus=3))
    return item


def create_ring_of_vitality(position: Position) -> ComponentEntity:
    """Create ring of vitality."""
    item = ComponentEntity(position=position, char="=", name="Ring of Vitality", blocks_movement=False)
    item.add_component(EquipmentStats(slot=EquipmentSlot.RING, max_hp_bonus=15))
    return item


def create_amulet_of_strength(position: Position) -> ComponentEntity:
    """Create amulet of strength."""
    item = ComponentEntity(position=position, char='"', name="Amulet of Strength", blocks_movement=False)
    item.add_component(EquipmentStats(slot=EquipmentSlot.AMULET, power_bonus=4))
    return item


def create_amulet_of_defense(position: Position) -> ComponentEntity:
    """Create amulet of defense."""
    item = ComponentEntity(position=position, char='"', name="Amulet of Defense", blocks_movement=False)
    item.add_component(EquipmentStats(slot=EquipmentSlot.AMULET, defense_bonus=4))
    return item


def create_amulet_of_life(position: Position) -> ComponentEntity:
    """Create amulet of life."""
    item = ComponentEntity(position=position, char='"', name="Amulet of Life", blocks_movement=False)
    item.add_component(EquipmentStats(slot=EquipmentSlot.AMULET, max_hp_bonus=20))
    return item
