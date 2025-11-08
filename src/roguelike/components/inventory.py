"""Inventory component for entities."""

from typing import TYPE_CHECKING, List, Optional

from roguelike.components.component import Component
from roguelike.entities.item import Item
from roguelike.systems.inventory import Inventory, InventoryItem

if TYPE_CHECKING:
    from roguelike.components.entity import ComponentEntity


class InventoryComponent(Component):
    """Component for entity inventory management."""

    def __init__(self, capacity: int = 26):
        """Initialize inventory component.

        Args:
            capacity: Maximum number of items
        """
        super().__init__()
        self._inventory = Inventory(capacity=capacity)

    @property
    def capacity(self) -> int:
        """Maximum inventory capacity."""
        return self._inventory.capacity

    def add_item(self, item: InventoryItem) -> bool:
        """Add item to inventory.

        Args:
            item: Item to add (Item or ComponentEntity with CraftingComponent)

        Returns:
            True if item was added
        """
        return self._inventory.add(item)

    def remove_item(self, item: InventoryItem) -> bool:
        """Remove item from inventory.

        Args:
            item: Item to remove

        Returns:
            True if item was removed
        """
        return self._inventory.remove(item)

    def get_item_by_index(self, index: int) -> Optional[InventoryItem]:
        """Get item by index.

        Args:
            index: Item index

        Returns:
            Item or None if index is invalid
        """
        return self._inventory.get_item_by_index(index)

    def get_items(self) -> List[InventoryItem]:
        """Get all items in inventory.

        Returns:
            List of items (both Item objects and ComponentEntity with CraftingComponent)
        """
        return self._inventory.items.copy()

    def is_full(self) -> bool:
        """Check if inventory is full.

        Returns:
            True if inventory is at capacity
        """
        return self._inventory.is_full()

    def __len__(self) -> int:
        """Get number of items in inventory."""
        return len(self._inventory)
