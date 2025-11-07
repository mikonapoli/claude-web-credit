"""Game action commands that directly manipulate systems."""

from typing import List, Optional

from roguelike.commands.command import Command, CommandResult
from roguelike.components.entity import ComponentEntity
from roguelike.components.helpers import is_alive, is_monster
from roguelike.systems.ai_system import AISystem
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.movement_system import MovementSystem
from roguelike.systems.status_effects import StatusEffectsSystem
from roguelike.systems.targeting import TargetingSystem
from roguelike.ui.message_log import MessageLog
from roguelike.utils.position import Position
from roguelike.world.fov import FOVMap
from roguelike.world.game_map import GameMap


class MoveCommand(Command):
    """Command to move the player and process turn cycle."""

    def __init__(
        self,
        player: ComponentEntity,
        dx: int,
        dy: int,
        entities: List[ComponentEntity],
        game_map: GameMap,
        fov_map: FOVMap,
        fov_radius: int,
        movement_system: MovementSystem,
        combat_system: CombatSystem,
        ai_system: AISystem,
        status_effects_system: Optional[StatusEffectsSystem],
    ):
        """Initialize move command.

        Args:
            player: Player entity
            dx: X direction to move
            dy: Y direction to move
            entities: All entities in game
            game_map: The game map
            fov_map: Field of view map
            fov_radius: FOV radius
            movement_system: Movement system for entity movement
            combat_system: Combat system for resolving attacks
            ai_system: AI system for enemy behavior
            status_effects_system: Status effects system for managing effects
        """
        self.player = player
        self.dx = dx
        self.dy = dy
        self.entities = entities
        self.game_map = game_map
        self.fov_map = fov_map
        self.fov_radius = fov_radius
        self.movement_system = movement_system
        self.combat_system = combat_system
        self.ai_system = ai_system
        self.status_effects_system = status_effects_system
        self.previous_position: Optional[Position] = None

    def execute(self) -> CommandResult:
        """Execute the move command and process turn cycle."""
        # Store previous position for undo
        self.previous_position = self.player.position

        # Calculate new position
        new_pos = Position(self.player.position.x + self.dx, self.player.position.y + self.dy)

        # Check for blocking entity at destination
        blocking_entity = self.movement_system.get_blocking_entity(new_pos, self.entities)

        turn_consumed = False
        if blocking_entity:
            # If it's a living monster, attack it
            if is_monster(blocking_entity) and is_alive(blocking_entity):
                # Use combat system to resolve attack
                defender_died = self.combat_system.resolve_attack(self.player, blocking_entity)

                if defender_died:
                    # Handle death and award XP
                    self.combat_system.handle_death(blocking_entity, killed_by_player=True)
                    self.combat_system.award_xp(self.player, blocking_entity.xp_value)
                    # Corpses don't block movement
                    blocking_entity.blocks_movement = False

                turn_consumed = True
        else:
            # Try to move player
            if self.movement_system.move_entity(self.player, self.dx, self.dy, self.entities):
                # Update FOV after successful movement
                self.movement_system.update_fov(self.fov_map, self.player.position, self.fov_radius)
                turn_consumed = True

        # If turn was consumed, process turn cycle
        if turn_consumed and is_alive(self.player):
            game_over = self._process_turn_cycle()
            if game_over:
                return CommandResult(success=False, turn_consumed=True, should_quit=True)

        return CommandResult(
            success=turn_consumed,
            turn_consumed=turn_consumed,
            should_quit=False,
        )

    def _process_turn_cycle(self) -> bool:
        """Process the turn cycle (status effects and AI).

        Returns:
            True if game is over (player died), False otherwise
        """
        # Process status effects on player
        if self.status_effects_system:
            player_died_from_poison = self.status_effects_system.process_effects(self.player)

            if player_died_from_poison:
                # Handle death from poison
                self.combat_system.handle_death(self.player, killed_by_player=False)
                self.player.blocks_movement = False
                return True  # Game over

        # Process enemy turns
        player_died = self.ai_system.process_turns(self.player, self.entities)
        if player_died:
            return True  # Game over

        # Process status effects on monsters
        if self.status_effects_system:
            for entity in self.entities:
                if is_monster(entity) and is_alive(entity):
                    died_from_poison = self.status_effects_system.process_effects(entity)
                    if died_from_poison:
                        # Handle death from poison
                        self.combat_system.handle_death(entity, killed_by_player=False)
                        entity.blocks_movement = False

        return False

    def can_undo(self) -> bool:
        """Move commands can be undone."""
        return self.previous_position is not None

    def undo(self) -> None:
        """Undo the move."""
        if self.previous_position:
            self.player.move_to(self.previous_position)
            self.movement_system.update_fov(
                self.fov_map, self.player.position, self.fov_radius
            )


class WaitCommand(Command):
    """Command to wait/pass turn and process turn cycle."""

    def __init__(
        self,
        player: ComponentEntity,
        entities: List[ComponentEntity],
        ai_system: AISystem,
        combat_system: CombatSystem,
        status_effects_system: Optional[StatusEffectsSystem],
    ):
        """Initialize wait command.

        Args:
            player: Player entity
            entities: All entities in game
            ai_system: AI system for enemy behavior
            combat_system: Combat system for handling death
            status_effects_system: Status effects system for managing effects
        """
        self.player = player
        self.entities = entities
        self.ai_system = ai_system
        self.combat_system = combat_system
        self.status_effects_system = status_effects_system

    def execute(self) -> CommandResult:
        """Execute the wait command and process turn cycle."""
        # Process turn cycle
        if is_alive(self.player):
            game_over = self._process_turn_cycle()
            if game_over:
                return CommandResult(success=False, turn_consumed=True, should_quit=True)

        return CommandResult(success=True, turn_consumed=True, should_quit=False)

    def _process_turn_cycle(self) -> bool:
        """Process the turn cycle (status effects and AI).

        Returns:
            True if game is over (player died), False otherwise
        """
        # Process status effects on player
        if self.status_effects_system:
            player_died_from_poison = self.status_effects_system.process_effects(self.player)

            if player_died_from_poison:
                # Handle death from poison
                self.combat_system.handle_death(self.player, killed_by_player=False)
                self.player.blocks_movement = False
                return True  # Game over

        # Process enemy turns
        player_died = self.ai_system.process_turns(self.player, self.entities)
        if player_died:
            return True  # Game over

        # Process status effects on monsters
        if self.status_effects_system:
            for entity in self.entities:
                if is_monster(entity) and is_alive(entity):
                    died_from_poison = self.status_effects_system.process_effects(entity)
                    if died_from_poison:
                        # Handle death from poison
                        self.combat_system.handle_death(entity, killed_by_player=False)
                        entity.blocks_movement = False

        return False


class QuitCommand(Command):
    """Command to quit the game."""

    def execute(self) -> CommandResult:
        """Execute the quit command."""
        return CommandResult(success=True, turn_consumed=False, should_quit=True)


class DescendStairsCommand(Command):
    """Command to descend stairs."""

    def __init__(
        self,
        player: ComponentEntity,
        stairs_pos: Optional[Position],
        message_log: MessageLog,
    ):
        """Initialize descend stairs command.

        Args:
            player: Player entity
            stairs_pos: Position of stairs (if any)
            message_log: Message log for displaying messages
        """
        self.player = player
        self.stairs_pos = stairs_pos
        self.message_log = message_log

    def execute(self) -> CommandResult:
        """Execute the descend stairs command."""
        # Check if player is on stairs
        if self.stairs_pos and self.player.position == self.stairs_pos:
            # Signal that stairs were descended (game engine handles transition)
            return CommandResult(
                success=True,
                turn_consumed=False,
                should_quit=False,
                data={"descend_stairs": True},
            )
        else:
            self.message_log.add_message("There are no stairs here!")
            return CommandResult(success=False, turn_consumed=False, should_quit=False)


class ShowInventoryCommand(Command):
    """Command to show inventory."""

    def execute(self) -> CommandResult:
        """Execute the show inventory command."""
        # Signal that inventory should be shown (game engine handles UI)
        return CommandResult(
            success=True,
            turn_consumed=False,
            should_quit=False,
            data={"show_inventory": True},
        )


class TargetingMoveCommand(Command):
    """Command to move targeting cursor."""

    def __init__(
        self,
        targeting_system: TargetingSystem,
        dx: int,
        dy: int,
    ):
        """Initialize targeting move command.

        Args:
            targeting_system: Targeting system
            dx: X direction to move
            dy: Y direction to move
        """
        self.targeting_system = targeting_system
        self.dx = dx
        self.dy = dy

    def execute(self) -> CommandResult:
        """Execute the targeting move command."""
        self.targeting_system.move_cursor(self.dx, self.dy)
        return CommandResult(success=True, turn_consumed=False, should_quit=False)


class TargetingSelectCommand(Command):
    """Command to select current target."""

    def __init__(self, targeting_system: TargetingSystem):
        """Initialize targeting select command.

        Args:
            targeting_system: Targeting system
        """
        self.targeting_system = targeting_system

    def execute(self) -> CommandResult:
        """Execute the targeting select command."""
        # Signal that target was selected (game engine handles item use)
        return CommandResult(
            success=True,
            turn_consumed=False,
            should_quit=False,
            data={"targeting_select": True},
        )


class TargetingCancelCommand(Command):
    """Command to cancel targeting."""

    def __init__(self, targeting_system: TargetingSystem):
        """Initialize targeting cancel command.

        Args:
            targeting_system: Targeting system
        """
        self.targeting_system = targeting_system

    def execute(self) -> CommandResult:
        """Execute the targeting cancel command."""
        self.targeting_system.cancel_targeting()
        return CommandResult(
            success=True,
            turn_consumed=False,
            should_quit=False,
            data={"targeting_cancel": True},
        )


class TargetingCycleCommand(Command):
    """Command to cycle through targets."""

    def __init__(
        self,
        targeting_system: TargetingSystem,
        forward: bool = True,
    ):
        """Initialize targeting cycle command.

        Args:
            targeting_system: Targeting system
            forward: True to cycle forward, False to cycle backward
        """
        self.targeting_system = targeting_system
        self.forward = forward

    def execute(self) -> CommandResult:
        """Execute the targeting cycle command."""
        if self.forward:
            self.targeting_system.cycle_target(1)
        else:
            self.targeting_system.cycle_target(-1)
        return CommandResult(success=True, turn_consumed=False, should_quit=False)


class PickupItemCommand(Command):
    """Command to pick up an item from the ground."""

    def __init__(
        self,
        player: ComponentEntity,
        entities: List[ComponentEntity],
        message_log: MessageLog,
    ):
        """Initialize pickup item command.

        Args:
            player: Player entity
            entities: All entities in game
            message_log: Message log for displaying messages
        """
        self.player = player
        self.entities = entities
        self.message_log = message_log

    def execute(self) -> CommandResult:
        """Execute the pickup command.

        Returns:
            CommandResult indicating success/failure
        """
        # Find items at player's position
        items_at_position = [
            item
            for item in self.entities
            if hasattr(item, "item_type") and item.position == self.player.position
        ]

        if not items_at_position:
            self.message_log.add_message("There is nothing here to pick up.")
            return CommandResult(success=False, turn_consumed=False, should_quit=False)

        # Try to pick up first item
        item = items_at_position[0]

        # Check if inventory is full
        if self.player.inventory.is_full():
            self.message_log.add_message("Your inventory is full!")
            return CommandResult(success=False, turn_consumed=False, should_quit=False)

        # Add item to inventory and remove from world
        if self.player.inventory.add(item):
            self.entities.remove(item)
            self.message_log.add_message(f"You picked up {item.name}.")

            # Pickup consumes a turn - process turn cycle
            if is_alive(self.player):
                game_over = self._process_turn_cycle()
                if game_over:
                    return CommandResult(success=False, turn_consumed=True, should_quit=True)

            return CommandResult(success=True, turn_consumed=True, should_quit=False)

        self.message_log.add_message("Could not pick up item.")
        return CommandResult(success=False, turn_consumed=False, should_quit=False)

    def _process_turn_cycle(self) -> bool:
        """Process the turn cycle (AI turns only, no status effects for pickup).

        Returns:
            True if game is over (player died), False otherwise
        """
        # Note: For pickup, we don't process status effects, only AI turns
        # This is a design choice - picking up items is quick and doesn't give
        # poison/other effects time to tick
        return False
