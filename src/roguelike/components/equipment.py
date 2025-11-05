"""Equipment component for managing equipped items."""

from enum import Enum
from typing import Dict, Optional

from roguelike.components.component import Component


class EquipmentSlot(Enum):
    """Equipment slots for items."""

    WEAPON = "weapon"
    ARMOR = "armor"
    HELMET = "helmet"
    BOOTS = "boots"
    GLOVES = "gloves"
    RING = "ring"
    AMULET = "amulet"


class EquipmentStats(Component):
    """Component for equipment items with stat bonuses."""

    def __init__(
        self,
        slot: EquipmentSlot,
        power_bonus: int = 0,
        defense_bonus: int = 0,
        max_hp_bonus: int = 0,
    ):
        """Initialize equipment stats.

        Args:
            slot: Equipment slot this item occupies
            power_bonus: Attack power bonus
            defense_bonus: Defense bonus
            max_hp_bonus: Maximum HP bonus
        """
        super().__init__()
        self.slot = slot
        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.max_hp_bonus = max_hp_bonus


class EquipmentComponent(Component):
    """Component for managing equipped items on an entity."""

    def __init__(self):
        """Initialize equipment component with empty slots."""
        super().__init__()
        self._equipped: Dict[EquipmentSlot, "ComponentEntity"] = {}

    def equip(self, item: "ComponentEntity") -> Optional["ComponentEntity"]:
        """Equip an item.

        Args:
            item: Item entity to equip

        Returns:
            Previously equipped item in that slot, or None
        """
        from roguelike.components.entity import ComponentEntity

        # Get equipment stats to determine slot
        equipment_stats = item.get_component(EquipmentStats)
        if not equipment_stats:
            raise ValueError(f"Item {item.name} has no EquipmentStats component")

        slot = equipment_stats.slot
        previous_item = self._equipped.get(slot)

        # Equip the new item
        self._equipped[slot] = item

        return previous_item

    def unequip(self, slot: EquipmentSlot) -> Optional["ComponentEntity"]:
        """Unequip item from a slot.

        Args:
            slot: Equipment slot to unequip

        Returns:
            Unequipped item, or None if slot was empty
        """
        return self._equipped.pop(slot, None)

    def get_equipped(self, slot: EquipmentSlot) -> Optional["ComponentEntity"]:
        """Get equipped item in a slot.

        Args:
            slot: Equipment slot to check

        Returns:
            Equipped item or None
        """
        return self._equipped.get(slot)

    def get_all_equipped(self) -> Dict[EquipmentSlot, "ComponentEntity"]:
        """Get all equipped items.

        Returns:
            Dictionary of slot to equipped item
        """
        return self._equipped.copy()

    def is_slot_empty(self, slot: EquipmentSlot) -> bool:
        """Check if a slot is empty.

        Args:
            slot: Equipment slot to check

        Returns:
            True if slot is empty
        """
        return slot not in self._equipped

    def get_total_power_bonus(self) -> int:
        """Calculate total power bonus from all equipment.

        Returns:
            Sum of power bonuses
        """
        total = 0
        for item in self._equipped.values():
            equipment_stats = item.get_component(EquipmentStats)
            if equipment_stats:
                total += equipment_stats.power_bonus
        return total

    def get_total_defense_bonus(self) -> int:
        """Calculate total defense bonus from all equipment.

        Returns:
            Sum of defense bonuses
        """
        total = 0
        for item in self._equipped.values():
            equipment_stats = item.get_component(EquipmentStats)
            if equipment_stats:
                total += equipment_stats.defense_bonus
        return total

    def get_total_max_hp_bonus(self) -> int:
        """Calculate total max HP bonus from all equipment.

        Returns:
            Sum of max HP bonuses
        """
        total = 0
        for item in self._equipped.values():
            equipment_stats = item.get_component(EquipmentStats)
            if equipment_stats:
                total += equipment_stats.max_hp_bonus
        return total
