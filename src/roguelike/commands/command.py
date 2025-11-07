"""Base command interface for actions."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from roguelike.components.entity import ComponentEntity
    from roguelike.systems.ai_system import AISystem
    from roguelike.systems.combat_system import CombatSystem
    from roguelike.systems.status_effects import StatusEffectsSystem


@dataclass
class CommandResult:
    """Result of executing a command."""

    success: bool
    turn_consumed: bool
    should_quit: bool = False
    data: Any = None


class Command(ABC):
    """Base class for all commands."""

    @abstractmethod
    def execute(self) -> CommandResult:
        """Execute the command.

        Returns:
            Result of command execution
        """
        pass

    def can_undo(self) -> bool:
        """Check if this command can be undone.

        Returns:
            True if command supports undo
        """
        return False

    def undo(self) -> None:
        """Undo the command.

        Should only be called if can_undo() returns True.
        """
        raise NotImplementedError("Command does not support undo")

    def _process_turn_cycle(
        self,
        player: "ComponentEntity",
        entities: List["ComponentEntity"],
        ai_system: "AISystem",
        combat_system: "CombatSystem",
        status_effects_system: Optional["StatusEffectsSystem"],
        process_player_effects: bool = True,
    ) -> bool:
        """Process the turn cycle (status effects and AI).

        This method implements the standard turn processing order:
        1. Player status effects (if enabled)
        2. Enemy AI turns
        3. Monster status effects

        Args:
            player: Player entity
            entities: All entities in game
            ai_system: AI system for enemy behavior
            combat_system: Combat system for handling death
            status_effects_system: Status effects system for managing effects
            process_player_effects: Whether to process status effects on player

        Returns:
            True if game is over (player died), False otherwise
        """
        from roguelike.components.helpers import is_alive, is_monster

        # Process status effects on player (if enabled)
        if process_player_effects and status_effects_system:
            player_died_from_effects = status_effects_system.process_effects(player)

            if player_died_from_effects:
                # Handle death from status effects
                combat_system.handle_death(player, killed_by_player=False)
                player.blocks_movement = False
                return True  # Game over

        # Process enemy turns
        player_died = ai_system.process_turns(player, entities)
        if player_died:
            return True  # Game over

        # Process status effects on monsters
        if status_effects_system:
            for entity in entities:
                if is_monster(entity) and is_alive(entity):
                    died_from_effects = status_effects_system.process_effects(entity)
                    if died_from_effects:
                        # Handle death from status effects
                        combat_system.handle_death(entity, killed_by_player=False)
                        entity.blocks_movement = False

        return False
