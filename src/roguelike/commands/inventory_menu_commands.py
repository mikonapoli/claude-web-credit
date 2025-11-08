"""Inventory menu commands for UI interactions."""

from typing import List, Optional

from roguelike.commands.command import Command, CommandResult
from roguelike.components.entity import ComponentEntity
from roguelike.components.inventory import InventoryComponent
from roguelike.entities.item import Item
from roguelike.systems.ai_system import AISystem
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.status_effects import StatusEffectsSystem
from roguelike.systems.targeting import TargetingSystem
from roguelike.ui.inventory_menu import InventoryMenu
from roguelike.ui.message_log import MessageLog
from roguelike.world.fov import FOVMap
from roguelike.world.game_map import GameMap


class OpenInventoryMenuCommand(Command):
    """Command to open the inventory menu."""

    def __init__(
        self,
        player: ComponentEntity,
        inventory_menu: InventoryMenu,
        message_log: MessageLog,
    ):
        """Initialize open inventory menu command.

        Args:
            player: Player entity
            inventory_menu: Inventory menu to open
            message_log: Message log for displaying messages
        """
        self.player = player
        self.inventory_menu = inventory_menu
        self.message_log = message_log

    def execute(self) -> CommandResult:
        """Open the inventory menu."""
        inventory = self.player.get_component(InventoryComponent)

        if not inventory:
            self.message_log.add_message("You don't have an inventory!")
            return CommandResult(success=False, turn_consumed=False)

        items = inventory.get_items()
        self.inventory_menu.open(items)
        return CommandResult(
            success=True,
            turn_consumed=False,
            data={"inventory_menu_opened": True}
        )


class CloseInventoryMenuCommand(Command):
    """Command to close the inventory menu."""

    def __init__(self, inventory_menu: InventoryMenu):
        """Initialize close inventory menu command.

        Args:
            inventory_menu: Inventory menu to close
        """
        self.inventory_menu = inventory_menu

    def execute(self) -> CommandResult:
        """Close the inventory menu."""
        self.inventory_menu.close()
        return CommandResult(
            success=True,
            turn_consumed=False,
            data={"inventory_menu_closed": True}
        )


class NavigateInventoryCommand(Command):
    """Command to navigate the inventory menu."""

    def __init__(self, inventory_menu: InventoryMenu, direction: str):
        """Initialize navigate inventory command.

        Args:
            inventory_menu: Inventory menu to navigate
            direction: Direction to navigate ("up" or "down")
        """
        self.inventory_menu = inventory_menu
        self.direction = direction

    def execute(self) -> CommandResult:
        """Navigate the inventory menu."""
        if self.direction == "up":
            self.inventory_menu.select_previous()
        elif self.direction == "down":
            self.inventory_menu.select_next()

        return CommandResult(success=True, turn_consumed=False)


class SetInventoryModeCommand(Command):
    """Command to set the inventory menu mode."""

    def __init__(self, inventory_menu: InventoryMenu, mode: str):
        """Initialize set inventory mode command.

        Args:
            inventory_menu: Inventory menu
            mode: Mode to set ("use", "drop", or "examine")
        """
        self.inventory_menu = inventory_menu
        self.mode = mode

    def execute(self) -> CommandResult:
        """Set the inventory menu mode."""
        self.inventory_menu.set_mode(self.mode)
        return CommandResult(success=True, turn_consumed=False)


class UseItemFromMenuCommand(Command):
    """Command to use an item from the inventory menu."""

    def __init__(
        self,
        player: ComponentEntity,
        inventory_menu: InventoryMenu,
        entities: List[ComponentEntity],
        ai_system: AISystem,
        combat_system: CombatSystem,
        status_effects_system: Optional[StatusEffectsSystem],
        targeting_system: TargetingSystem,
        fov_map: FOVMap,
        game_map: GameMap,
        message_log: MessageLog,
    ):
        """Initialize use item from menu command.

        Args:
            player: Player entity
            inventory_menu: Inventory menu
            entities: All entities in game
            ai_system: AI system for enemy behavior
            combat_system: Combat system for handling death
            status_effects_system: Status effects system for managing effects
            targeting_system: Targeting system for targeted items
            fov_map: Field of view map
            game_map: Game map
            message_log: Message log for displaying messages
        """
        self.player = player
        self.inventory_menu = inventory_menu
        self.entities = entities
        self.ai_system = ai_system
        self.combat_system = combat_system
        self.status_effects_system = status_effects_system
        self.targeting_system = targeting_system
        self.fov_map = fov_map
        self.game_map = game_map
        self.message_log = message_log

    def execute(self) -> CommandResult:
        """Use the selected item."""
        from roguelike.components.helpers import is_monster, is_alive
        from roguelike.commands.inventory_commands import UseItemCommand

        item = self.inventory_menu.get_selected_item()

        if not item:
            return CommandResult(success=False, turn_consumed=False)

        # Check if this is an Item (not a ComponentEntity crafting material)
        if not isinstance(item, Item):
            self.message_log.add_message("That item cannot be used!")
            return CommandResult(success=False, turn_consumed=False)

        # Check if item requires targeting
        if item.requires_targeting():
            # Get valid targets (living monsters in FOV)
            valid_targets = [
                e
                for e in self.entities
                if is_monster(e) and is_alive(e) and self.fov_map.is_visible(e.position)
            ]

            if not valid_targets:
                self.message_log.add_message("No visible targets!")
                return CommandResult(success=False, turn_consumed=False)

            # Start targeting mode
            started = self.targeting_system.start_targeting(
                origin=self.player.position,
                max_range=10,  # Default range for items
                valid_targets=valid_targets,
                map_width=self.game_map.width,
                map_height=self.game_map.height,
            )

            if started:
                # Close inventory menu and signal targeting mode
                self.inventory_menu.close()
                self.message_log.add_message(
                    f"Select target for {item.name}. [ESC] to cancel."
                )
                return CommandResult(
                    success=True,
                    turn_consumed=False,
                    data={
                        "start_item_targeting": True,
                        "item": item,
                    }
                )
            else:
                self.message_log.add_message("No targets in range!")
                return CommandResult(success=False, turn_consumed=False)
        else:
            # Use item directly (non-targeted)
            use_command = UseItemCommand(self.player, item)
            result = use_command.execute()

            if result.success:
                # Close inventory menu after successful use
                self.inventory_menu.close()
                self.message_log.add_message(f"You used {item.name}.")

                # Process turn cycle (status effects and enemy AI)
                game_over = self._process_turn_cycle(
                    self.player,
                    self.entities,
                    self.ai_system,
                    self.combat_system,
                    self.status_effects_system,
                )

                return CommandResult(
                    success=True,
                    turn_consumed=True,
                    should_quit=game_over,
                    data={"inventory_menu_closed": True}
                )
            else:
                # Item use failed (e.g., already at full HP)
                self.message_log.add_message(f"Cannot use {item.name} right now.")
                return CommandResult(success=False, turn_consumed=False)


class DropItemFromMenuCommand(Command):
    """Command to drop an item from the inventory menu."""

    def __init__(
        self,
        player: ComponentEntity,
        inventory_menu: InventoryMenu,
        entities: List[ComponentEntity],
        ai_system: AISystem,
        combat_system: CombatSystem,
        status_effects_system: Optional[StatusEffectsSystem],
        message_log: MessageLog,
    ):
        """Initialize drop item from menu command.

        Args:
            player: Player entity
            inventory_menu: Inventory menu
            entities: All entities in game
            ai_system: AI system for enemy behavior
            combat_system: Combat system for handling death
            status_effects_system: Status effects system for managing effects
            message_log: Message log for displaying messages
        """
        self.player = player
        self.inventory_menu = inventory_menu
        self.entities = entities
        self.ai_system = ai_system
        self.combat_system = combat_system
        self.status_effects_system = status_effects_system
        self.message_log = message_log

    def execute(self) -> CommandResult:
        """Drop the selected item."""
        from roguelike.commands.inventory_commands import DropItemCommand

        item = self.inventory_menu.get_selected_item()

        if not item:
            return CommandResult(success=False, turn_consumed=False)

        # Check if this is an Item (not a ComponentEntity crafting material)
        if not isinstance(item, Item):
            self.message_log.add_message("That item cannot be dropped!")
            return CommandResult(success=False, turn_consumed=False)

        # Drop the item
        drop_command = DropItemCommand(self.player, item, self.entities)
        result = drop_command.execute()

        if result.success:
            # Close inventory menu after successful drop
            self.inventory_menu.close()
            self.message_log.add_message(f"You dropped {item.name}.")

            # Process turn cycle (status effects and enemy AI)
            game_over = self._process_turn_cycle(
                self.player,
                self.entities,
                self.ai_system,
                self.combat_system,
                self.status_effects_system,
            )

            return CommandResult(
                success=True,
                turn_consumed=True,
                should_quit=game_over,
                data={"inventory_menu_closed": True}
            )
        else:
            self.message_log.add_message(f"Cannot drop {item.name}.")
            return CommandResult(success=False, turn_consumed=False)


class ExamineItemCommand(Command):
    """Command to examine an item from the inventory menu."""

    def __init__(
        self,
        inventory_menu: InventoryMenu,
        message_log: MessageLog,
    ):
        """Initialize examine item command.

        Args:
            inventory_menu: Inventory menu
            message_log: Message log for displaying messages
        """
        self.inventory_menu = inventory_menu
        self.message_log = message_log

    def execute(self) -> CommandResult:
        """Examine the selected item."""
        item = self.inventory_menu.get_selected_item()

        if not item:
            return CommandResult(success=False, turn_consumed=False)

        # Get item description
        description_lines = self.inventory_menu.get_item_description(item)

        # Signal to show examination UI
        return CommandResult(
            success=True,
            turn_consumed=False,
            data={
                "examine_item": True,
                "item": item,
                "description_lines": description_lines,
            }
        )
