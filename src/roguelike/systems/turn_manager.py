"""Turn management system."""

from typing import List, Tuple

from roguelike.entities.entity import Entity
from roguelike.entities.monster import Monster
from roguelike.entities.player import Player
from roguelike.systems.ai_system import AISystem
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.movement_system import MovementSystem
from roguelike.ui.input_handler import Action
from roguelike.utils.position import Position
from roguelike.world.fov import FOVMap
from roguelike.world.game_map import GameMap


class TurnManager:
    """Manages turn-based game flow."""

    def __init__(
        self,
        combat_system: CombatSystem,
        movement_system: MovementSystem,
        ai_system: AISystem,
    ):
        """Initialize turn manager.

        Args:
            combat_system: Combat system for resolving attacks
            movement_system: Movement system for entity movement
            ai_system: AI system for enemy behavior
        """
        self.combat_system = combat_system
        self.movement_system = movement_system
        self.ai_system = ai_system

    def handle_player_action(
        self,
        action: Action,
        player: Player,
        entities: List[Entity],
        game_map: GameMap,
        fov_map: FOVMap,
        fov_radius: int,
    ) -> Tuple[bool, bool]:
        """Handle a player action.

        Args:
            action: Action to handle
            player: The player entity
            entities: All entities in the game
            game_map: The game map
            fov_map: Field of view map
            fov_radius: FOV radius

        Returns:
            Tuple of (turn_consumed, should_quit)
        """
        if action == Action.QUIT:
            return False, True

        if action == Action.WAIT:
            return True, False

        # Movement actions
        movement_map = {
            Action.MOVE_UP: (0, -1),
            Action.MOVE_DOWN: (0, 1),
            Action.MOVE_LEFT: (-1, 0),
            Action.MOVE_RIGHT: (1, 0),
            Action.MOVE_UP_LEFT: (-1, -1),
            Action.MOVE_UP_RIGHT: (1, -1),
            Action.MOVE_DOWN_LEFT: (-1, -1),
            Action.MOVE_DOWN_RIGHT: (1, 1),
        }

        if action in movement_map:
            dx, dy = movement_map[action]
            turn_consumed = self._try_move_player(
                player, dx, dy, entities, fov_map, fov_radius
            )
            return turn_consumed, False

        return False, False

    def _try_move_player(
        self,
        player: Player,
        dx: int,
        dy: int,
        entities: List[Entity],
        fov_map: FOVMap,
        fov_radius: int,
    ) -> bool:
        """Try to move the player.

        Args:
            player: The player entity
            dx: X offset
            dy: Y offset
            entities: All entities in the game
            fov_map: Field of view map
            fov_radius: FOV radius

        Returns:
            True if movement was successful (consumes turn)
        """
        new_pos = Position(player.position.x + dx, player.position.y + dy)

        # Check for blocking entity at destination
        blocking_entity = self.movement_system.get_blocking_entity(
            new_pos, entities
        )

        if blocking_entity:
            # If it's a living monster, attack it
            if (
                isinstance(blocking_entity, Monster)
                and blocking_entity.is_alive
            ):
                # Use combat system to resolve attack
                defender_died = self.combat_system.resolve_attack(
                    player, blocking_entity
                )

                if defender_died:
                    # Handle death and award XP
                    self.combat_system.handle_death(
                        blocking_entity, killed_by_player=True
                    )
                    self.combat_system.award_xp(
                        player, blocking_entity.xp_value
                    )
                    # Corpses don't block movement
                    blocking_entity.blocks_movement = False

                return True  # Attack consumes turn
            # Other blocking entity (not attackable)
            return False

        # Try to move player
        if self.movement_system.move_entity(player, dx, dy, entities):
            # Update FOV after successful movement
            self.movement_system.update_fov(fov_map, player.position, fov_radius)
            return True

        return False

    def process_turn(
        self,
        action: Action,
        player: Player,
        entities: List[Entity],
        game_map: GameMap,
        fov_map: FOVMap,
        fov_radius: int,
    ) -> bool:
        """Process a complete turn cycle.

        Args:
            action: Player action
            player: The player entity
            entities: All entities in the game
            game_map: The game map
            fov_map: Field of view map
            fov_radius: FOV radius

        Returns:
            True if game should continue, False if game over
        """
        # Handle player action
        turn_consumed, should_quit = self.handle_player_action(
            action, player, entities, game_map, fov_map, fov_radius
        )

        if should_quit:
            return False

        # If turn was consumed and player is alive, process enemy turns
        if turn_consumed and player.is_alive:
            player_died = self.ai_system.process_turns(player, entities)
            if player_died:
                return False  # Game over

        return True
