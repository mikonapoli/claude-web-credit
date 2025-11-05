"""Items that can be picked up and used."""

from enum import Enum

from roguelike.entities.entity import Entity
from roguelike.utils.position import Position


class ItemType(Enum):
    """Types of items."""

    HEALING_POTION = "healing_potion"


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
