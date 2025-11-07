"""Inventory system."""

from typing import TYPE_CHECKING, List, Optional, Union

from roguelike.entities.item import Item, ItemType

if TYPE_CHECKING:
    from roguelike.components.entity import ComponentEntity

# Type alias for items that can be stored in inventory
InventoryItem = Union[Item, "ComponentEntity"]


class Inventory:
    """Manages items carried by an actor."""

    def __init__(self, capacity: int = 26):
        """Initialize inventory.

        Args:
            capacity: Maximum number of items
        """
        self.capacity = capacity
        self.items: List[InventoryItem] = []

    def add(self, item: InventoryItem) -> bool:
        """Add item to inventory.

        Args:
            item: Item to add (Item or ComponentEntity with CraftingComponent)

        Returns:
            True if item was added
        """
        if len(self.items) >= self.capacity:
            return False
        self.items.append(item)
        return True

    def remove(self, item: InventoryItem) -> bool:
        """Remove item from inventory.

        Args:
            item: Item to remove

        Returns:
            True if item was removed
        """
        if item in self.items:
            self.items.remove(item)
            return True
        return False

    def get_item_by_index(self, index: int) -> Optional[InventoryItem]:
        """Get item by index.

        Args:
            index: Item index

        Returns:
            Item or None if index is invalid
        """
        if 0 <= index < len(self.items):
            return self.items[index]
        return None

    def is_full(self) -> bool:
        """Check if inventory is full.

        Returns:
            True if inventory is at capacity
        """
        return len(self.items) >= self.capacity

    def __len__(self) -> int:
        """Get number of items in inventory."""
        return len(self.items)
