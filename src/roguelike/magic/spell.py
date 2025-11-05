"""Spell data model and types."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class SpellSchool(Enum):
    """Magic school categorization."""

    EVOCATION = auto()  # Direct damage and energy manipulation
    CONJURATION = auto()  # Summoning and creation
    TRANSMUTATION = auto()  # Transformation and alteration


class TargetType(Enum):
    """Spell targeting types."""

    SELF = auto()  # Caster only
    SINGLE = auto()  # Single target at range
    AREA = auto()  # Area of effect
    BEAM = auto()  # Linear beam


@dataclass
class Spell:
    """Spell definition."""

    id: str  # Unique identifier (e.g., "magic_missile")
    name: str  # Display name
    school: SpellSchool  # Magic school
    mana_cost: int  # Mana required to cast
    power: int  # Base spell power (for damage, healing, etc.)
    target_type: TargetType  # How spell targets
    range: int  # Maximum range in tiles
    area_radius: int = 0  # Radius for area spells
    description: str = ""  # Flavor text

    def __post_init__(self):
        """Convert string school/target to enums if needed."""
        if isinstance(self.school, str):
            self.school = SpellSchool[self.school.upper()]
        if isinstance(self.target_type, str):
            self.target_type = TargetType[self.target_type.upper()]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Spell":
        """Create spell from dictionary.

        Args:
            data: Spell data dictionary

        Returns:
            Spell instance
        """
        return cls(
            id=data["id"],
            name=data["name"],
            school=SpellSchool[data["school"].upper()],
            mana_cost=data["mana_cost"],
            power=data["power"],
            target_type=TargetType[data["target_type"].upper()],
            range=data["range"],
            area_radius=data.get("area_radius", 0),
            description=data.get("description", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert spell to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "name": self.name,
            "school": self.school.name,
            "mana_cost": self.mana_cost,
            "power": self.power,
            "target_type": self.target_type.name,
            "range": self.range,
            "area_radius": self.area_radius,
            "description": self.description,
        }
