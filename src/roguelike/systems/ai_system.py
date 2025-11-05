"""AI coordination system."""

import random
from typing import Dict, List, Optional

from roguelike.entities.entity import Entity
from roguelike.entities.monster import Monster
from roguelike.entities.player import Player
from roguelike.systems.ai import MonsterAI
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.movement_system import MovementSystem
from roguelike.systems.status_effects import StatusEffectsSystem
from roguelike.utils.position import Position
from roguelike.world.game_map import GameMap


class AISystem:
    """Coordinates AI behavior for all monsters."""

    def __init__(
        self,
        combat_system: CombatSystem,
        movement_system: MovementSystem,
        game_map: GameMap,
        status_effects_system: Optional[StatusEffectsSystem] = None,
    ):
        """Initialize the AI system.

        Args:
            combat_system: Combat system for resolving attacks
            movement_system: Movement system for moving entities
            game_map: The game map
            status_effects_system: Status effects system for checking effects
        """
        self.combat_system = combat_system
        self.movement_system = movement_system
        self.game_map = game_map
        self.status_effects_system = status_effects_system
        self.monster_ais: Dict[Monster, MonsterAI] = {}

    def register_monster(self, monster: Monster) -> None:
        """Register a monster with the AI system.

        Args:
            monster: Monster to register
        """
        if monster not in self.monster_ais:
            self.monster_ais[monster] = MonsterAI(monster)

    def unregister_monster(self, monster: Monster) -> None:
        """Unregister a monster from the AI system.

        Args:
            monster: Monster to unregister
        """
        if monster in self.monster_ais:
            del self.monster_ais[monster]

    def process_turns(
        self,
        player: Player,
        entities: List[Entity],
    ) -> bool:
        """Process all AI-controlled entity turns.

        Args:
            player: The player entity
            entities: All entities in the game

        Returns:
            True if player died during AI turns
        """
        player_died = False

        for entity in entities:
            # Skip non-monsters and dead monsters
            if not isinstance(entity, Monster) or not entity.is_alive:
                continue

            # Get AI for this monster
            ai = self.monster_ais.get(entity)
            if not ai:
                continue

            # Check if monster is confused
            is_confused = (
                self.status_effects_system
                and self.status_effects_system.has_effect(entity, "confusion")
            )

            # Check if player is invisible
            player_invisible = (
                self.status_effects_system
                and self.status_effects_system.has_effect(player, "invisibility")
            )

            # Get all living entities for blocking checks
            living_entities = [
                e for e in entities if isinstance(e, Monster) and e.is_alive
            ]
            living_entities.append(player)

            # If confused, move randomly
            if is_confused:
                self._handle_confused_turn(entity, living_entities)
                continue

            # Check if monster is adjacent to player (attack range)
            if entity.position.manhattan_distance_to(player.position) <= 1:
                # Don't attack if player is invisible
                if player_invisible:
                    # Monster can't see player, just wander
                    new_pos = ai.take_turn(player, self.game_map, living_entities)
                    if new_pos:
                        entity.move_to(new_pos)
                else:
                    # Use combat system for consistency and event emission
                    defender_died = self.combat_system.resolve_attack(
                        entity, player
                    )
                    if defender_died:
                        # Handle player death
                        self.combat_system.handle_death(
                            player, killed_by_player=False
                        )
                        # Corpses don't block movement
                        player.blocks_movement = False
                        player_died = True
            else:
                # Don't pursue if player is invisible
                if player_invisible:
                    # Just wander randomly
                    self._handle_confused_turn(entity, living_entities)
                else:
                    # Let AI decide on movement
                    new_pos = ai.take_turn(player, self.game_map, living_entities)
                    if new_pos:
                        # Move to new position
                        entity.move_to(new_pos)

        return player_died

    def _handle_confused_turn(
        self, entity: Monster, living_entities: List[Entity]
    ) -> None:
        """Handle a confused monster's turn with random movement.

        Args:
            entity: The confused monster
            living_entities: All living entities
        """
        # Try random directions
        directions = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0),           (1, 0),
            (-1, 1),  (0, 1),  (1, 1),
        ]
        random.shuffle(directions)

        for dx, dy in directions:
            new_pos = Position(
                entity.position.x + dx,
                entity.position.y + dy
            )

            # Check if move is valid
            if not self.game_map.in_bounds(new_pos.x, new_pos.y):
                continue

            if self.game_map.tiles[new_pos.x, new_pos.y].blocks_movement:
                continue

            # Check for blocking entities
            blocking_entity = self.movement_system.get_blocking_entity(
                new_pos, living_entities
            )
            if blocking_entity:
                continue

            # Move to this position
            entity.move_to(new_pos)
            break  # Successfully moved
