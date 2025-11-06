"""Inventory UI for displaying and interacting with items."""

from typing import List, Optional

from roguelike.entities.item import Item


class InventoryUI:
    """UI for displaying inventory items."""

    def __init__(self, width: int = 50, height: int = 30):
        """Initialize inventory UI.

        Args:
            width: Width of inventory panel
            height: Height of inventory panel
        """
        self.width = width
        self.height = height
        self.selected_index: Optional[int] = None

    def get_item_letters(self, items: List[Item]) -> dict[str, int]:
        """Get letter-to-index mapping for items.

        Args:
            items: List of items

        Returns:
            Dictionary mapping letters (a-z) to item indices
        """
        letter_map = {}
        for i, item in enumerate(items[:26]):  # Limit to 26 items (a-z)
            letter = chr(ord('a') + i)
            letter_map[letter] = i
        return letter_map

    def get_item_by_letter(self, items: List[Item], letter: str) -> Optional[Item]:
        """Get item by its letter key.

        Args:
            items: List of items
            letter: Letter key (a-z)

        Returns:
            Item or None if letter is invalid
        """
        letter_map = self.get_item_letters(items)
        if letter in letter_map:
            index = letter_map[letter]
            return items[index]
        return None

    def get_display_lines(self, items: List[Item]) -> List[str]:
        """Get display lines for inventory items.

        Args:
            items: List of items to display

        Returns:
            List of formatted display lines
        """
        if not items:
            return ["Your inventory is empty."]

        lines = []
        letter_map = self.get_item_letters(items)

        for letter, index in sorted(letter_map.items()):
            item = items[index]
            # Format: (a) Item Name
            lines.append(f"({letter}) {item.name}")

        return lines

    def calculate_position(self, screen_width: int, screen_height: int) -> tuple[int, int]:
        """Calculate centered position for inventory panel.

        Args:
            screen_width: Screen width
            screen_height: Screen height

        Returns:
            Tuple of (x, y) position for top-left corner
        """
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        return x, y
