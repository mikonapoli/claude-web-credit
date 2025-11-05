"""AI system for monsters."""

from typing import Optional

import tcod.path

from roguelike.entities.actor import Actor
from roguelike.entities.monster import Monster
from roguelike.utils.position import Position
from roguelike.world.game_map import GameMap


class MonsterAI:
    """Simple AI for monsters."""

    def __init__(self, monster: Monster):
        """Initialize AI for a monster.

        Args:
            monster: The monster this AI controls
        """
        self.monster = monster

    def take_turn(
        self,
        player: Actor,
        game_map: GameMap,
        entities: list[Actor],
    ) -> Optional[Position]:
        """Take a turn for this monster.

        Args:
            player: The player actor
            game_map: The game map
            entities: List of all entities (for blocking checks)

        Returns:
            New position if moved, None otherwise
        """
        # Only act if player is alive
        if not player.is_alive:
            return None

        # Calculate distance to player
        distance = self.monster.position.manhattan_distance_to(player.position)

        # If adjacent to player, attack (handled by engine)
        if distance <= 1:
            return None  # Don't move, will attack

        # If player is within 10 tiles, chase
        if distance < 10:
            # Simple pathfinding: move one step towards player
            dx = 0
            dy = 0

            if self.monster.position.x < player.position.x:
                dx = 1
            elif self.monster.position.x > player.position.x:
                dx = -1

            if self.monster.position.y < player.position.y:
                dy = 1
            elif self.monster.position.y > player.position.y:
                dy = -1

            new_pos = Position(
                self.monster.position.x + dx,
                self.monster.position.y + dy
            )

            # Check if destination is valid
            if not game_map.is_walkable(new_pos):
                return None

            # Check if any entity blocks movement at destination
            for entity in entities:
                if entity != self.monster and entity.position == new_pos:
                    if entity.blocks_movement:
                        return None

            return new_pos

        return None  # Too far, don't move
