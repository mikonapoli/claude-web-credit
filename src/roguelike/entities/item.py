"""Items that can be picked up and used."""

from enum import Enum

from roguelike.entities.entity import Entity
from roguelike.utils.position import Position


class ItemType(Enum):
    """Types of items."""

    # Healing items
    HEALING_POTION = "healing_potion"
    GREATER_HEALING_POTION = "greater_healing_potion"
    CHEESE_WHEEL = "cheese_wheel"

    # Buff potions
    STRENGTH_POTION = "strength_potion"
    DEFENSE_POTION = "defense_potion"
    SPEED_POTION = "speed_potion"
    INVISIBILITY_POTION = "invisibility_potion"
    GIGANTISM_POTION = "gigantism_potion"
    SHRINKING_POTION = "shrinking_potion"

    # Combat scrolls
    SCROLL_FIREBALL = "scroll_fireball"
    SCROLL_LIGHTNING = "scroll_lightning"
    SCROLL_CONFUSION = "scroll_confusion"

    # Utility scrolls
    SCROLL_TELEPORT = "scroll_teleport"
    SCROLL_MAGIC_MAPPING = "scroll_magic_mapping"

    # Quirky items
    COFFEE = "coffee"
    LUCKY_COIN = "lucky_coin"
    BANANA_PEEL = "banana_peel"
    RUBBER_CHICKEN = "rubber_chicken"
    CURSED_RING = "cursed_ring"


class Item(Entity):
    """An item that can be picked up."""

    def __init__(
        self,
        position: Position,
        char: str,
        name: str,
        item_type: ItemType,
        value: int = 0,
    ):
        """Initialize an item.

        Args:
            position: Item position
            char: Display character
            name: Item name
            item_type: Type of item
            value: Item's effect value (e.g., healing amount)
        """
        super().__init__(position=position, char=char, name=name, blocks_movement=False)
        self.item_type = item_type
        self.value = value


def create_healing_potion(position: Position) -> Item:
    """Create a healing potion.

    Args:
        position: Item position

    Returns:
        Healing potion item
    """
    return Item(
        position=position,
        char="!",
        name="Healing Potion",
        item_type=ItemType.HEALING_POTION,
        value=20,
    )


def create_greater_healing_potion(position: Position) -> Item:
    """Create a greater healing potion.

    Args:
        position: Item position

    Returns:
        Greater healing potion item
    """
    return Item(
        position=position,
        char="!",
        name="Greater Healing Potion",
        item_type=ItemType.GREATER_HEALING_POTION,
        value=40,
    )


def create_cheese_wheel(position: Position) -> Item:
    """Create a cheese wheel.

    Args:
        position: Item position

    Returns:
        Cheese wheel item (large heal)
    """
    return Item(
        position=position,
        char="%",
        name="Cheese Wheel",
        item_type=ItemType.CHEESE_WHEEL,
        value=50,
    )


def create_strength_potion(position: Position) -> Item:
    """Create a strength potion.

    Args:
        position: Item position

    Returns:
        Strength potion item
    """
    return Item(
        position=position,
        char="!",
        name="Potion of Strength",
        item_type=ItemType.STRENGTH_POTION,
        value=3,  # +3 power for duration
    )


def create_defense_potion(position: Position) -> Item:
    """Create a defense potion.

    Args:
        position: Item position

    Returns:
        Defense potion item
    """
    return Item(
        position=position,
        char="!",
        name="Potion of Defense",
        item_type=ItemType.DEFENSE_POTION,
        value=3,  # +3 defense for duration
    )


def create_speed_potion(position: Position) -> Item:
    """Create a speed potion.

    Args:
        position: Item position

    Returns:
        Speed potion item
    """
    return Item(
        position=position,
        char="!",
        name="Potion of Speed",
        item_type=ItemType.SPEED_POTION,
        value=5,  # 5 turns of double actions
    )


def create_invisibility_potion(position: Position) -> Item:
    """Create an invisibility potion.

    Args:
        position: Item position

    Returns:
        Invisibility potion item
    """
    return Item(
        position=position,
        char="!",
        name="Potion of Invisibility",
        item_type=ItemType.INVISIBILITY_POTION,
        value=10,  # 10 turns invisible
    )


def create_gigantism_potion(position: Position) -> Item:
    """Create a gigantism potion.

    Args:
        position: Item position

    Returns:
        Gigantism potion item
    """
    return Item(
        position=position,
        char="!",
        name="Potion of Gigantism",
        item_type=ItemType.GIGANTISM_POTION,
        value=5,  # +5 power for duration
    )


def create_shrinking_potion(position: Position) -> Item:
    """Create a shrinking potion.

    Args:
        position: Item position

    Returns:
        Shrinking potion item
    """
    return Item(
        position=position,
        char="!",
        name="Potion of Shrinking",
        item_type=ItemType.SHRINKING_POTION,
        value=3,  # +3 defense for duration
    )


def create_scroll_fireball(position: Position) -> Item:
    """Create a fireball scroll.

    Args:
        position: Item position

    Returns:
        Fireball scroll item
    """
    return Item(
        position=position,
        char="?",
        name="Scroll of Fireball",
        item_type=ItemType.SCROLL_FIREBALL,
        value=25,  # 25 damage in area
    )


def create_scroll_lightning(position: Position) -> Item:
    """Create a lightning scroll.

    Args:
        position: Item position

    Returns:
        Lightning scroll item
    """
    return Item(
        position=position,
        char="?",
        name="Scroll of Lightning",
        item_type=ItemType.SCROLL_LIGHTNING,
        value=20,  # 20 damage single target
    )


def create_scroll_confusion(position: Position) -> Item:
    """Create a confusion scroll.

    Args:
        position: Item position

    Returns:
        Confusion scroll item
    """
    return Item(
        position=position,
        char="?",
        name="Scroll of Confusion",
        item_type=ItemType.SCROLL_CONFUSION,
        value=10,  # 10 turns confused
    )


def create_scroll_teleport(position: Position) -> Item:
    """Create a teleport scroll.

    Args:
        position: Item position

    Returns:
        Teleport scroll item
    """
    return Item(
        position=position,
        char="?",
        name="Scroll of Teleportation",
        item_type=ItemType.SCROLL_TELEPORT,
        value=0,  # Random teleport
    )


def create_scroll_magic_mapping(position: Position) -> Item:
    """Create a magic mapping scroll.

    Args:
        position: Item position

    Returns:
        Magic mapping scroll item
    """
    return Item(
        position=position,
        char="?",
        name="Scroll of Magic Mapping",
        item_type=ItemType.SCROLL_MAGIC_MAPPING,
        value=0,  # Reveals map
    )


def create_coffee(position: Position) -> Item:
    """Create a coffee.

    Args:
        position: Item position

    Returns:
        Coffee item
    """
    return Item(
        position=position,
        char="~",
        name="Coffee",
        item_type=ItemType.COFFEE,
        value=3,  # 3 turns of speed boost
    )


def create_lucky_coin(position: Position) -> Item:
    """Create a lucky coin.

    Args:
        position: Item position

    Returns:
        Lucky coin item
    """
    return Item(
        position=position,
        char="$",
        name="Lucky Coin",
        item_type=ItemType.LUCKY_COIN,
        value=50,  # 50% XP bonus for duration
    )


def create_banana_peel(position: Position) -> Item:
    """Create a banana peel.

    Args:
        position: Item position

    Returns:
        Banana peel item
    """
    return Item(
        position=position,
        char=")",
        name="Banana Peel",
        item_type=ItemType.BANANA_PEEL,
        value=0,  # Throwable trap item
    )


def create_rubber_chicken(position: Position) -> Item:
    """Create a rubber chicken.

    Args:
        position: Item position

    Returns:
        Rubber chicken item
    """
    return Item(
        position=position,
        char="&",
        name="Rubber Chicken",
        item_type=ItemType.RUBBER_CHICKEN,
        value=1,  # Weak comedic weapon
    )


def create_cursed_ring(position: Position) -> Item:
    """Create a cursed ring.

    Args:
        position: Item position

    Returns:
        Cursed ring item
    """
    return Item(
        position=position,
        char="=",
        name="Cursed Ring",
        item_type=ItemType.CURSED_RING,
        value=0,  # Random effect
    )
