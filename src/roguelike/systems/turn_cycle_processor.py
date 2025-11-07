"""Turn cycle processor for handling post-action turn processing.

This centralizes the critical component processing order documented in
docs/COMPONENT_COMMUNICATION.md, eliminating duplication across commands.
"""

from typing import List, Optional

from roguelike.components.entity import ComponentEntity
from roguelike.components.helpers import is_alive, is_monster
from roguelike.systems.ai_system import AISystem
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.status_effects import StatusEffectsSystem


class TurnCycleProcessor:
    """Processes the turn cycle after turn-consuming actions.

    This centralizes the critical component processing order:
    1. Player Status Effects (StatusEffectsSystem → HealthComponent)
    2. Enemy AI Turns (AISystem → combat → HealthComponent)
    3. Enemy Status Effects (StatusEffectsSystem → HealthComponent)

    Rationale (from docs/COMPONENT_COMMUNICATION.md):
    - Player sees their action results immediately
    - Status effects apply after action (poison ticks after movement)
    - Enemies respond to player's action
    - Enemy status effects apply last (consistent with player)

    See docs/COMPONENT_COMMUNICATION.md for detailed rationale.
    """

    def __init__(
        self,
        combat_system: CombatSystem,
        ai_system: AISystem,
        status_effects_system: Optional[StatusEffectsSystem],
    ):
        """Initialize turn cycle processor.

        Args:
            combat_system: Combat system for handling death
            ai_system: AI system for processing enemy turns
            status_effects_system: Status effects system for managing effects
        """
        self.combat_system = combat_system
        self.ai_system = ai_system
        self.status_effects_system = status_effects_system

    def process_turn_cycle(
        self,
        player: ComponentEntity,
        entities: List[ComponentEntity],
    ) -> bool:
        """Process the turn cycle.

        This implements the critical processing order for component interactions.
        Each step may modify HealthComponent, so order matters to avoid race conditions.

        Args:
            player: The player entity
            entities: All entities in the game

        Returns:
            True if game is over (player died), False otherwise
        """
        # Step 1: Process status effects on player
        if self.status_effects_system:
            player_died = self.status_effects_system.process_effects(player)
            if player_died:
                # Handle death from status effects (e.g., poison)
                self.combat_system.handle_death(player, killed_by_player=False)
                player.blocks_movement = False
                return True  # Game over

        # Step 2: Process enemy AI turns
        player_died = self.ai_system.process_turns(player, entities)
        if player_died:
            return True  # Game over

        # Step 3: Process status effects on monsters
        if self.status_effects_system:
            for entity in entities:
                if is_monster(entity) and is_alive(entity):
                    died = self.status_effects_system.process_effects(entity)
                    if died:
                        # Handle death from status effects
                        self.combat_system.handle_death(entity, killed_by_player=False)
                        entity.blocks_movement = False

        return False  # Game continues
