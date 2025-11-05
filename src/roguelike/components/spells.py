"""Spell component for entities that can cast magic."""

from typing import Optional

from roguelike.components.component import Component
from roguelike.magic.spell import Spell


class SpellComponent(Component):
    """Component for managing an entity's known spells."""

    def __init__(self):
        """Initialize spell component."""
        super().__init__()
        self._spells: dict[str, Spell] = {}

    @property
    def spells(self) -> list[Spell]:
        """Get list of all known spells.

        Returns:
            List of known spells
        """
        return list(self._spells.values())

    def learn_spell(self, spell: Spell) -> bool:
        """Learn a new spell.

        Args:
            spell: Spell to learn

        Returns:
            True if spell was learned, False if already known
        """
        if spell.id in self._spells:
            return False
        self._spells[spell.id] = spell
        return True

    def forget_spell(self, spell_id: str) -> bool:
        """Forget a spell.

        Args:
            spell_id: ID of spell to forget

        Returns:
            True if spell was forgotten, False if not known
        """
        if spell_id not in self._spells:
            return False
        del self._spells[spell_id]
        return True

    def knows_spell(self, spell_id: str) -> bool:
        """Check if entity knows a spell.

        Args:
            spell_id: Spell ID to check

        Returns:
            True if spell is known
        """
        return spell_id in self._spells

    def get_spell(self, spell_id: str) -> Optional[Spell]:
        """Get a known spell by ID.

        Args:
            spell_id: Spell ID to retrieve

        Returns:
            Spell if known, None otherwise
        """
        return self._spells.get(spell_id)

    @property
    def spell_count(self) -> int:
        """Get number of known spells.

        Returns:
            Number of spells known
        """
        return len(self._spells)

    def get_spells_by_school(self, school) -> list[Spell]:
        """Get all spells of a specific school.

        Args:
            school: SpellSchool to filter by

        Returns:
            List of spells from that school
        """
        return [spell for spell in self._spells.values() if spell.school == school]
