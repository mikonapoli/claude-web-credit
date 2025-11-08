"""Spell menu UI for displaying and selecting spells."""

from typing import List, Optional

from roguelike.magic.spell import Spell


class SpellMenu:
    """Handles spell menu display and selection."""

    def __init__(self):
        """Initialize spell menu."""
        self.is_open = False
        self.spells: List[Spell] = []
        self.selected_index = 0

    def open(self, spells: List[Spell]) -> None:
        """Open the spell menu with available spells.

        Args:
            spells: List of spells to display
        """
        self.is_open = True
        self.spells = spells
        self.selected_index = 0

    def close(self) -> None:
        """Close the spell menu."""
        self.is_open = False
        self.spells = []
        self.selected_index = 0

    def select_next(self) -> None:
        """Move selection down."""
        if self.spells:
            self.selected_index = (self.selected_index + 1) % len(self.spells)

    def select_previous(self) -> None:
        """Move selection up."""
        if self.spells:
            self.selected_index = (self.selected_index - 1) % len(self.spells)

    def get_selected_spell(self) -> Optional[Spell]:
        """Get the currently selected spell.

        Returns:
            Selected spell or None if no selection
        """
        if not self.spells or not self.is_open:
            return None
        return self.spells[self.selected_index]

    def get_menu_lines(self, player_mp: int) -> List[str]:
        """Get formatted menu lines for rendering.

        Args:
            player_mp: Player's current mana

        Returns:
            List of formatted menu lines
        """
        if not self.is_open or not self.spells:
            return []

        lines = ["=== SPELLS ==="]
        lines.append(f"Current MP: {player_mp}")
        lines.append("")

        for i, spell in enumerate(self.spells):
            prefix = ">" if i == self.selected_index else " "
            can_cast = player_mp >= spell.mana_cost
            color_indicator = "" if can_cast else " [!]"
            line = f"{prefix} {spell.name} ({spell.mana_cost} MP){color_indicator}"
            lines.append(line)

        lines.append("")
        lines.append("[Enter] Cast  [ESC] Cancel")
        return lines
