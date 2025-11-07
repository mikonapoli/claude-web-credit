"""AI system for monsters using the State pattern."""

from abc import ABC, abstractmethod
from typing import Optional

import tcod.path

from roguelike.components.entity import ComponentEntity
from roguelike.utils.position import Position
from roguelike.world.game_map import GameMap


class AIState(ABC):
    """Abstract base class for AI states."""

    @abstractmethod
    def update(
        self,
        monster: ComponentEntity,
        player: ComponentEntity,
        game_map: GameMap,
        entities: list[ComponentEntity],
    ) -> Optional[Position]:
        """Execute this state's behavior.

        Args:
            monster: The monster being controlled
            player: The player entity
            game_map: The game map
            entities: List of all entities (for blocking checks)

        Returns:
            New position to move to, or None if no movement
        """
        pass


class IdleState(AIState):
    """State when monster is not doing anything (player too far or dead)."""

    def update(
        self,
        monster: ComponentEntity,
        player: ComponentEntity,
        game_map: GameMap,
        entities: list[ComponentEntity],
    ) -> Optional[Position]:
        """Monster does nothing in idle state.

        Args:
            monster: The monster being controlled
            player: The player entity
            game_map: The game map
            entities: List of all entities (for blocking checks)

        Returns:
            None (no movement)
        """
        return None


class ChaseState(AIState):
    """State when monster is chasing the player."""

    def update(
        self,
        monster: ComponentEntity,
        player: ComponentEntity,
        game_map: GameMap,
        entities: list[ComponentEntity],
    ) -> Optional[Position]:
        """Move one step towards the player.

        Args:
            monster: The monster being controlled
            player: The player entity
            game_map: The game map
            entities: List of all entities (for blocking checks)

        Returns:
            New position to move to, or None if movement blocked
        """
        # Simple pathfinding: move one step towards player
        dx = 0
        dy = 0

        if monster.position.x < player.position.x:
            dx = 1
        elif monster.position.x > player.position.x:
            dx = -1

        if monster.position.y < player.position.y:
            dy = 1
        elif monster.position.y > player.position.y:
            dy = -1

        new_pos = Position(
            monster.position.x + dx,
            monster.position.y + dy
        )

        # Check if destination is valid
        if not game_map.is_walkable(new_pos):
            return None

        # Check if any entity blocks movement at destination
        for entity in entities:
            if entity != monster and entity.position == new_pos:
                if entity.blocks_movement:
                    return None

        return new_pos


class AttackState(AIState):
    """State when monster is adjacent to player and ready to attack."""

    def update(
        self,
        monster: ComponentEntity,
        player: ComponentEntity,
        game_map: GameMap,
        entities: list[ComponentEntity],
    ) -> Optional[Position]:
        """Stay in place (attack is handled by AISystem).

        Args:
            monster: The monster being controlled
            player: The player entity
            game_map: The game map
            entities: List of all entities (for blocking checks)

        Returns:
            None (no movement, attack will be handled by AISystem)
        """
        return None


# Singleton instances of states (Flyweight pattern)
_idle_state = IdleState()
_chase_state = ChaseState()
_attack_state = AttackState()


class MonsterAI:
    """AI controller for monsters using State pattern."""

    def __init__(self, monster: ComponentEntity):
        """Initialize AI for a monster.

        Args:
            monster: The monster this AI controls
        """
        self.monster = monster
        self.state: AIState = _idle_state

    def take_turn(
        self,
        player: ComponentEntity,
        game_map: GameMap,
        entities: list[ComponentEntity],
    ) -> Optional[Position]:
        """Take a turn for this monster.

        Args:
            player: The player entity
            game_map: The game map
            entities: List of all entities (for blocking checks)

        Returns:
            New position if moved, None otherwise
        """
        # Update state based on current conditions
        self._update_state(player)

        # Execute current state's behavior
        return self.state.update(self.monster, player, game_map, entities)

    def _update_state(self, player: ComponentEntity) -> None:
        """Update the current state based on conditions.

        Args:
            player: The player entity
        """
        # If player is dead, go idle
        if not player.is_alive:
            self.state = _idle_state
            return

        # Calculate distance to player
        distance = self.monster.position.manhattan_distance_to(player.position)

        # Transition to appropriate state based on distance
        if distance <= 1:
            self.state = _attack_state
        elif distance < 10:
            self.state = _chase_state
        else:
            self.state = _idle_state
