"""AI coordination system."""

from typing import Dict, List

from roguelike.entities.entity import Entity
from roguelike.entities.monster import Monster
from roguelike.entities.player import Player
from roguelike.systems.ai import MonsterAI
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.movement_system import MovementSystem
from roguelike.world.game_map import GameMap


class AISystem:
    """Coordinates AI behavior for all monsters."""

    def __init__(
        self,
        combat_system: CombatSystem,
        movement_system: MovementSystem,
        game_map: GameMap,
    ):
        """Initialize the AI system.

        Args:
            combat_system: Combat system for resolving attacks
            movement_system: Movement system for moving entities
            game_map: The game map
        """
        self.combat_system = combat_system
        self.movement_system = movement_system
        self.game_map = game_map
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

            # Get all living entities for blocking checks
            living_entities = [
                e for e in entities if isinstance(e, Monster) and e.is_alive
            ]
            living_entities.append(player)

            # Check if monster is adjacent to player (attack range)
            if entity.position.manhattan_distance_to(player.position) <= 1:
                # Use combat system for consistency and event emission
                defender_died = self.combat_system.resolve_attack(
                    entity, player
                )
                if defender_died:
                    # Handle player death
                    self.combat_system.handle_death(
                        player, killed_by_player=False
                    )
                    player_died = True
            else:
                # Let AI decide on movement
                new_pos = ai.take_turn(player, self.game_map, living_entities)
                if new_pos:
                    # Move to new position
                    entity.move_to(new_pos)

        return player_died
