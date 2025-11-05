"""Entity loader for data-driven entity creation."""

import json
from pathlib import Path
from typing import Any, Dict

from roguelike.components.combat import CombatComponent
from roguelike.components.crafting import CraftingComponent
from roguelike.components.entity import ComponentEntity
from roguelike.components.equipment import EquipmentSlot, EquipmentStats
from roguelike.components.health import HealthComponent
from roguelike.components.level import LevelComponent
from roguelike.components.recipe_discovery import RecipeDiscoveryComponent
from roguelike.utils.position import Position


class EntityLoader:
    """Loads entity definitions from JSON files."""

    def __init__(self, data_path: Path | str | None = None):
        """Initialize entity loader.

        Args:
            data_path: Path to entities.json file. If None, uses default.
        """
        if data_path is None:
            # Default to entities.json in same directory as this file
            data_path = Path(__file__).parent / "entities.json"
        else:
            data_path = Path(data_path)

        self.data_path = data_path
        self.templates: Dict[str, Dict[str, Any]] = {}
        self._load_templates()

    def _load_templates(self) -> None:
        """Load entity templates from JSON file."""
        with open(self.data_path, "r") as f:
            self.templates = json.load(f)

    def create_entity(
        self, entity_type: str, position: Position
    ) -> ComponentEntity:
        """Create an entity from a template.

        Args:
            entity_type: Type of entity to create (e.g., "player", "orc")
            position: Position to place entity

        Returns:
            ComponentEntity created from template

        Raises:
            KeyError: If entity_type not found in templates
        """
        if entity_type not in self.templates:
            raise KeyError(f"Entity type '{entity_type}' not found in templates")

        template = self.templates[entity_type]

        # Create base entity
        entity = ComponentEntity(
            position=position,
            char=template["char"],
            name=template["name"],
            blocks_movement=template.get("blocks_movement", False),
        )

        # Add components based on template
        components = template.get("components", {})

        if "health" in components:
            health_data = components["health"]
            entity.add_component(
                HealthComponent(max_hp=health_data["max_hp"])
            )

        if "combat" in components:
            combat_data = components["combat"]
            entity.add_component(
                CombatComponent(
                    power=combat_data["power"], defense=combat_data["defense"]
                )
            )

        if "level" in components:
            level_data = components["level"]
            entity.add_component(
                LevelComponent(
                    level=level_data.get("level", 1),
                    xp=level_data.get("xp", 0),
                    xp_value=level_data.get("xp_value", 0),
                )
            )

        if "crafting" in components:
            crafting_data = components["crafting"]
            entity.add_component(
                CraftingComponent(
                    tags=set(crafting_data["tags"]),
                    consumable=crafting_data.get("consumable", True),
                    craftable=crafting_data.get("craftable", False),
                )
            )

        if "recipe_discovery" in components:
            entity.add_component(RecipeDiscoveryComponent())

        if "equipment" in components:
            equipment_data = components["equipment"]
            # Convert slot string to enum
            slot_str = equipment_data["slot"]
            slot = EquipmentSlot(slot_str)
            entity.add_component(
                EquipmentStats(
                    slot=slot,
                    power_bonus=equipment_data.get("power_bonus", 0),
                    defense_bonus=equipment_data.get("defense_bonus", 0),
                    max_hp_bonus=equipment_data.get("max_hp_bonus", 0),
                )
            )

        return entity

    def get_available_types(self) -> list[str]:
        """Get list of available entity types.

        Returns:
            List of entity type names
        """
        return list(self.templates.keys())

    def reload(self) -> None:
        """Reload templates from JSON file."""
        self._load_templates()
