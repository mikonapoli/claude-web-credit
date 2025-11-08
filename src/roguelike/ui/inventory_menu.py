"""Inventory menu UI for displaying and interacting with inventory items."""

from typing import List, Optional

from roguelike.systems.inventory import InventoryItem


class InventoryMenu:
    """Handles inventory menu display and selection."""

    def __init__(self):
        """Initialize inventory menu."""
        self.is_open = False
        self.items: List[InventoryItem] = []
        self.selected_index = 0
        self.mode = "use"  # "use", "drop", or "examine"

    def open(self, items: List[InventoryItem]) -> None:
        """Open the inventory menu with available items.

        Args:
            items: List of inventory items to display
        """
        self.is_open = True
        self.items = items
        self.selected_index = 0 if items else 0
        self.mode = "use"

    def close(self) -> None:
        """Close the inventory menu."""
        self.is_open = False
        self.items = []
        self.selected_index = 0
        self.mode = "use"

    def select_next(self) -> None:
        """Move selection down."""
        if self.items:
            self.selected_index = (self.selected_index + 1) % len(self.items)

    def select_previous(self) -> None:
        """Move selection up."""
        if self.items:
            self.selected_index = (self.selected_index - 1) % len(self.items)

    def set_mode(self, mode: str) -> None:
        """Set the current mode.

        Args:
            mode: Mode to set ("use", "drop", or "examine")
        """
        if mode in ("use", "drop", "examine"):
            self.mode = mode

    def get_selected_item(self) -> Optional[InventoryItem]:
        """Get the currently selected item.

        Returns:
            Selected item or None if no selection
        """
        if not self.items or not self.is_open:
            return None
        if 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None

    def get_menu_lines(self, capacity: int) -> List[str]:
        """Get formatted menu lines for rendering.

        Args:
            capacity: Maximum inventory capacity

        Returns:
            List of formatted menu lines
        """
        if not self.is_open:
            return []

        lines = ["=== INVENTORY ==="]
        lines.append(f"Items: {len(self.items)}/{capacity}")
        lines.append("")

        if not self.items:
            lines.append("  (empty)")
            lines.append("")
        else:
            for i, item in enumerate(self.items):
                prefix = ">" if i == self.selected_index else " "
                # Get item name - handle both Item and ComponentEntity
                if hasattr(item, 'name'):
                    item_name = item.name
                else:
                    item_name = str(item)

                letter = chr(ord('a') + i) if i < 26 else '?'
                line = f"{prefix} {letter}) {item_name}"
                lines.append(line)

        lines.append("")
        mode_text = self.mode.upper()
        lines.append(f"Mode: {mode_text}")
        lines.append("[↑/↓] Navigate  [Enter] {mode_text}")
        lines.append("[u] Use  [d] Drop  [x] Examine")
        lines.append("[ESC] Close")
        return lines

    def get_item_description(self, item: InventoryItem) -> List[str]:
        """Get description lines for an item.

        Args:
            item: Item to describe

        Returns:
            List of description lines
        """
        lines = []

        # Item name as title
        if hasattr(item, 'name'):
            lines.append(f"=== {item.name.upper()} ===")
        else:
            lines.append("=== ITEM ===")
        lines.append("")

        # For Item objects, show type and value
        if hasattr(item, 'item_type'):
            lines.append(f"Type: {item.item_type.value}")
            if hasattr(item, 'value') and item.value > 0:
                lines.append(f"Effect Value: {item.value}")

            # Show if targeting is required
            if hasattr(item, 'requires_targeting') and item.requires_targeting():
                lines.append("Requires Target: Yes")
            else:
                lines.append("Requires Target: No")

        # For ComponentEntity with crafting component
        elif hasattr(item, 'get_component'):
            from roguelike.components.crafting import CraftingComponent
            crafting = item.get_component(CraftingComponent)
            if crafting and hasattr(crafting, 'tags'):
                lines.append(f"Tags: {', '.join(sorted(crafting.tags))}")

        return lines
