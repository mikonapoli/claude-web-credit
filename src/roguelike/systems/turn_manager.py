"""Turn management system."""

from typing import List, Optional

from roguelike.components.entity import ComponentEntity
from roguelike.components.helpers import is_alive, is_monster
from roguelike.systems.ai_system import AISystem
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.movement_system import MovementSystem
from roguelike.systems.status_effects import StatusEffectsSystem
from roguelike.utils.position import Position
from roguelike.world.fov import FOVMap
from roguelike.world.game_map import GameMap


class TurnManager:
    """Manages turn-based game flow.

    NOTE: This class is now primarily used for legacy tests. New code should
    use Command objects directly which handle their own turn cycle processing.

    CRITICAL: Component Processing Order
    =====================================
    The order in which components are processed each turn is CRITICAL to avoid
    race conditions and ensure predictable behavior. This order must be maintained:

    1. Player Action (combat may modify HealthComponent)
    2. Player Status Effects (StatusEffectsSystem → HealthComponent)
       - If player dies from status effects → game over
    3. Enemy AI Turns (combat may modify HealthComponent)
       - If player dies from enemy attack → game over
    4. Enemy Status Effects (StatusEffectsSystem → HealthComponent)
       - Enemies may die from status effects

    Rationale:
    - Player sees their action results immediately
    - Status effects apply after action (poison ticks after movement)
    - Enemies respond to player's action
    - Enemy status effects apply last (consistent with player)

    See docs/COMPONENT_COMMUNICATION.md for more details.
    """

    def __init__(
        self,
        combat_system: CombatSystem,
        movement_system: MovementSystem,
        ai_system: AISystem,
        status_effects_system: Optional[StatusEffectsSystem] = None,
    ):
        """Initialize turn manager.

        Args:
            combat_system: Combat system for resolving attacks
            movement_system: Movement system for entity movement
            ai_system: AI system for enemy behavior
            status_effects_system: Status effects system for managing effects
        """
        self.combat_system = combat_system
        self.movement_system = movement_system
        self.ai_system = ai_system
        self.status_effects_system = status_effects_system
