"""Spell loader for data-driven spell creation."""

import json
from importlib.resources import files
from pathlib import Path

from roguelike.magic.spell import Spell


class SpellLoader:
    """Loads spell definitions from JSON files."""

    def __init__(self, data_path: Path | str | None = None):
        """Initialize spell loader.

        Args:
            data_path: Path to spells.json file. If None, uses packaged resource.
        """
        self.data_path = data_path
        self.spells: dict[str, Spell] = {}
        self._load_spells()

    def _load_spells(self) -> None:
        """Load spell definitions from JSON file or package resource."""
        if self.data_path is not None:
            # Load from custom path
            with open(self.data_path, "r") as f:
                data = json.load(f)
        else:
            # Load from package resource
            resource = files("roguelike.data").joinpath("spells.json")
            data = json.loads(resource.read_text(encoding="utf-8"))

        spell_list = data.get("spells", [])
        for spell_data in spell_list:
            spell = Spell.from_dict(spell_data)
            self.spells[spell.id] = spell

    def get_spell(self, spell_id: str) -> Spell | None:
        """Get a spell by ID.

        Args:
            spell_id: ID of spell to retrieve

        Returns:
            Spell if found, None otherwise
        """
        return self.spells.get(spell_id)

    def get_all_spells(self) -> list[Spell]:
        """Get all loaded spells.

        Returns:
            List of all spells
        """
        return list(self.spells.values())

    def get_available_spell_ids(self) -> list[str]:
        """Get list of available spell IDs.

        Returns:
            List of spell IDs
        """
        return list(self.spells.keys())

    def reload(self) -> None:
        """Reload spells from JSON file."""
        self.spells.clear()
        self._load_spells()
