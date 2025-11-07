"""Equipment system for managing equipment and stat bonuses."""

from typing import Optional

from roguelike.components.combat import CombatComponent
from roguelike.components.entity import ComponentEntity
from roguelike.components.equipment import EquipmentComponent, EquipmentSlot, EquipmentStats
from roguelike.components.health import HealthComponent
from roguelike.engine.events import EquipEvent, EventBus, UnequipEvent


class EquipmentSystem:
    """Manages equipment and applies stat bonuses.

    Component Communication:
    ------------------------
    This system uses the SHARED STATE pattern and modifies multiple components:
    - Reads: EquipmentComponent, EquipmentStats
    - Modifies: CombatComponent (power/defense), HealthComponent (max_hp)

    Processing Order Dependencies:
    ------------------------------
    Equipment bonuses are applied IMMEDIATELY when equipping/unequipping.
    These bonuses persist in the component stats (not recalculated each frame).

    IMPORTANT: When modifying max_hp:
    - Maintains HP percentage to avoid unfair HP loss/gain
    - Ensures living entities keep at least 1 HP

    See docs/COMPONENT_COMMUNICATION.md for more details.
    """

    def __init__(self, event_bus: EventBus):
        """Initialize equipment system.

        Args:
            event_bus: Event bus for publishing equipment events
        """
        self.event_bus = event_bus

    def equip_item(
        self,
        entity: ComponentEntity,
        item: ComponentEntity,
    ) -> Optional[ComponentEntity]:
        """Equip an item on an entity.

        This will:
        1. Remove item from previous slot if it exists
        2. Place item in new slot
        3. Apply stat bonuses to entity
        4. Emit equip event

        Args:
            entity: Entity equipping the item
            item: Item to equip

        Returns:
            Previously equipped item in that slot, or None

        Raises:
            ValueError: If entity has no EquipmentComponent
            ValueError: If item has no EquipmentStats
        """
        # Get components
        equipment_comp = entity.get_component(EquipmentComponent)
        if not equipment_comp:
            raise ValueError(f"Entity {entity.name} has no EquipmentComponent")

        equipment_stats = item.get_component(EquipmentStats)
        if not equipment_stats:
            raise ValueError(f"Item {item.name} has no EquipmentStats component")

        # If there's a previously equipped item, unapply its bonuses
        previous_item = equipment_comp.get_equipped(equipment_stats.slot)
        if previous_item:
            self._unapply_bonuses(entity, previous_item)
            # Emit unequip event for the swapped item
            self.event_bus.emit(
                UnequipEvent(
                    entity_name=entity.name,
                    item_name=previous_item.name,
                    slot=equipment_stats.slot.value,
                )
            )

        # Equip the new item
        previous_item = equipment_comp.equip(item)

        # Apply stat bonuses
        self._apply_bonuses(entity, item)

        # Emit equip event
        self.event_bus.emit(
            EquipEvent(
                entity_name=entity.name,
                item_name=item.name,
                slot=equipment_stats.slot.value,
                power_bonus=equipment_stats.power_bonus,
                defense_bonus=equipment_stats.defense_bonus,
                max_hp_bonus=equipment_stats.max_hp_bonus,
            )
        )

        return previous_item

    def unequip_item(
        self,
        entity: ComponentEntity,
        slot: EquipmentSlot,
    ) -> Optional[ComponentEntity]:
        """Unequip an item from a slot.

        This will:
        1. Remove item from slot
        2. Unapply stat bonuses
        3. Emit unequip event

        Args:
            entity: Entity unequipping the item
            slot: Slot to unequip from

        Returns:
            Unequipped item, or None if slot was empty

        Raises:
            ValueError: If entity has no EquipmentComponent
        """
        # Get components
        equipment_comp = entity.get_component(EquipmentComponent)
        if not equipment_comp:
            raise ValueError(f"Entity {entity.name} has no EquipmentComponent")

        # Get the item before unequipping
        item = equipment_comp.get_equipped(slot)
        if not item:
            return None

        # Unequip the item
        item = equipment_comp.unequip(slot)

        # Unapply stat bonuses
        self._unapply_bonuses(entity, item)

        # Emit unequip event
        self.event_bus.emit(
            UnequipEvent(
                entity_name=entity.name,
                item_name=item.name,
                slot=slot.value,
            )
        )

        return item

    def _apply_bonuses(self, entity: ComponentEntity, item: ComponentEntity) -> None:
        """Apply stat bonuses from an item to an entity.

        Args:
            entity: Entity receiving bonuses
            item: Item providing bonuses
        """
        equipment_stats = item.get_component(EquipmentStats)
        if not equipment_stats:
            return

        # Apply power bonus
        if equipment_stats.power_bonus != 0:
            combat_comp = entity.get_component(CombatComponent)
            if combat_comp:
                combat_comp.power += equipment_stats.power_bonus

        # Apply defense bonus
        if equipment_stats.defense_bonus != 0:
            combat_comp = entity.get_component(CombatComponent)
            if combat_comp:
                combat_comp.defense += equipment_stats.defense_bonus

        # Apply max HP bonus
        if equipment_stats.max_hp_bonus != 0:
            health_comp = entity.get_component(HealthComponent)
            if health_comp:
                # Calculate HP percentage before change
                hp_percent = health_comp.hp / health_comp.max_hp if health_comp.max_hp > 0 else 1.0

                # Increase max HP
                health_comp.max_hp += equipment_stats.max_hp_bonus

                # Restore same HP percentage (so player doesn't lose HP when equipping)
                new_hp = round(health_comp.max_hp * hp_percent)
                # If entity was alive (hp_percent > 0), ensure they have at least 1 HP
                if new_hp == 0 and hp_percent > 0:
                    new_hp = 1
                health_comp.hp = new_hp

    def _unapply_bonuses(self, entity: ComponentEntity, item: ComponentEntity) -> None:
        """Remove stat bonuses from an item from an entity.

        Args:
            entity: Entity losing bonuses
            item: Item that was providing bonuses
        """
        equipment_stats = item.get_component(EquipmentStats)
        if not equipment_stats:
            return

        # Remove power bonus
        if equipment_stats.power_bonus != 0:
            combat_comp = entity.get_component(CombatComponent)
            if combat_comp:
                combat_comp.power -= equipment_stats.power_bonus

        # Remove defense bonus
        if equipment_stats.defense_bonus != 0:
            combat_comp = entity.get_component(CombatComponent)
            if combat_comp:
                combat_comp.defense -= equipment_stats.defense_bonus

        # Remove max HP bonus
        if equipment_stats.max_hp_bonus != 0:
            health_comp = entity.get_component(HealthComponent)
            if health_comp:
                # Calculate HP percentage before change
                hp_percent = health_comp.hp / health_comp.max_hp if health_comp.max_hp > 0 else 1.0

                # Decrease max HP
                health_comp.max_hp -= equipment_stats.max_hp_bonus

                # Restore same HP percentage (mirrors the equip path)
                new_hp = round(health_comp.max_hp * hp_percent)
                # If entity was alive (hp_percent > 0), ensure they have at least 1 HP
                if new_hp == 0 and hp_percent > 0:
                    new_hp = 1
                health_comp.hp = new_hp

    def get_effective_power(self, entity: ComponentEntity) -> int:
        """Get entity's effective power including equipment bonuses.

        Note: Equipment bonuses are already applied to the CombatComponent,
        so this just returns the current power value.

        Args:
            entity: Entity to calculate power for

        Returns:
            Current power (already includes equipment bonuses)
        """
        combat_comp = entity.get_component(CombatComponent)
        if combat_comp:
            return combat_comp.power
        return 0

    def get_effective_defense(self, entity: ComponentEntity) -> int:
        """Get entity's effective defense including equipment bonuses.

        Note: Equipment bonuses are already applied to the CombatComponent,
        so this just returns the current defense value.

        Args:
            entity: Entity to calculate defense for

        Returns:
            Current defense (already includes equipment bonuses)
        """
        combat_comp = entity.get_component(CombatComponent)
        if combat_comp:
            return combat_comp.defense
        return 0
