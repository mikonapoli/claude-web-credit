"""Equipment-related commands."""

from roguelike.commands.command import Command, CommandResult
from roguelike.components.entity import ComponentEntity
from roguelike.components.equipment import EquipmentComponent, EquipmentSlot, EquipmentStats
from roguelike.components.inventory import InventoryComponent
from roguelike.systems.equipment_system import EquipmentSystem


class EquipItemCommand(Command):
    """Command to equip an item from inventory."""

    def __init__(
        self,
        entity: ComponentEntity,
        item: ComponentEntity,
        equipment_system: EquipmentSystem,
    ):
        """Initialize equip command.

        Args:
            entity: Entity equipping the item
            item: Item to equip
            equipment_system: Equipment system to handle equipping
        """
        self.entity = entity
        self.item = item
        self.equipment_system = equipment_system

    def execute(self) -> CommandResult:
        """Execute the equip command.

        Returns:
            CommandResult indicating success/failure
        """
        # Check if entity has equipment component
        equipment_comp = self.entity.get_component(EquipmentComponent)
        if equipment_comp is None:
            return CommandResult(success=False, turn_consumed=False)

        # Check if item has equipment stats
        equipment_stats = self.item.get_component(EquipmentStats)
        if equipment_stats is None:
            return CommandResult(success=False, turn_consumed=False)

        # Check if entity has inventory component
        inventory = self.entity.get_component(InventoryComponent)
        if inventory is None:
            return CommandResult(success=False, turn_consumed=False)

        # Check if item is in inventory
        if self.item not in inventory.get_items():
            return CommandResult(success=False, turn_consumed=False)

        # Remove item from inventory
        inventory.remove_item(self.item)

        # Equip the item (this handles replacing previous equipment)
        previous_item = self.equipment_system.equip_item(self.entity, self.item)

        # If there was a previously equipped item, put it back in inventory
        if previous_item:
            # If inventory is full, drop the previous item
            if inventory.is_full():
                # This shouldn't happen since we just removed an item,
                # but handle it just in case
                return CommandResult(success=False, turn_consumed=False)
            inventory.add_item(previous_item)

        return CommandResult(success=True, turn_consumed=True)


class UnequipItemCommand(Command):
    """Command to unequip an item to inventory."""

    def __init__(
        self,
        entity: ComponentEntity,
        slot: EquipmentSlot,
        equipment_system: EquipmentSystem,
    ):
        """Initialize unequip command.

        Args:
            entity: Entity unequipping the item
            slot: Equipment slot to unequip from
            equipment_system: Equipment system to handle unequipping
        """
        self.entity = entity
        self.slot = slot
        self.equipment_system = equipment_system

    def execute(self) -> CommandResult:
        """Execute the unequip command.

        Returns:
            CommandResult indicating success/failure
        """
        # Check if entity has equipment component
        equipment_comp = self.entity.get_component(EquipmentComponent)
        if equipment_comp is None:
            return CommandResult(success=False, turn_consumed=False)

        # Check if there's an item in that slot
        if equipment_comp.is_slot_empty(self.slot):
            return CommandResult(success=False, turn_consumed=False)

        # Check if entity has inventory component
        inventory = self.entity.get_component(InventoryComponent)
        if inventory is None:
            return CommandResult(success=False, turn_consumed=False)

        # Check if inventory has space
        if inventory.is_full():
            return CommandResult(success=False, turn_consumed=False)

        # Unequip the item
        item = self.equipment_system.unequip_item(self.entity, self.slot)

        if item is None:
            return CommandResult(success=False, turn_consumed=False)

        # Add unequipped item to inventory
        if not inventory.add_item(item):
            # If we can't add to inventory, re-equip the item
            self.equipment_system.equip_item(self.entity, item)
            return CommandResult(success=False, turn_consumed=False)

        return CommandResult(success=True, turn_consumed=True)
