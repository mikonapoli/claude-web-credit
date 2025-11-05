"""Movement system handling entity movement and collision."""

from typing import Optional

from roguelike.entities.entity import Entity
from roguelike.utils.position import Position
from roguelike.utils.protocols import Positionable
from roguelike.world.fov import FOVMap
from roguelike.world.game_map import GameMap


class MovementSystem:
    """Handles entity movement and collision detection."""

    def __init__(self, game_map: GameMap):
        """Initialize movement system.

        Args:
            game_map: The game map for terrain checks
        """
        self.game_map = game_map

    def can_move_to(
        self,
        position: Position,
        entities: list[Entity],
        ignore_entity: Optional[Entity] = None,
    ) -> bool:
        """Check if a position is valid for movement.

        Args:
            position: Position to check
            entities: List of all entities
            ignore_entity: Entity to ignore in collision check

        Returns:
            True if position is valid for movement
        """
        # Check terrain
        if not self.game_map.is_walkable(position):
            return False

        # Check for blocking entities
        for entity in entities:
            if entity == ignore_entity:
                continue
            if entity.position == position and entity.blocks_movement:
                return False

        return True

    def get_blocking_entity(
        self,
        position: Position,
        entities: list[Entity],
    ) -> Optional[Entity]:
        """Get entity blocking a position.

        Args:
            position: Position to check
            entities: List of all entities

        Returns:
            Blocking entity or None
        """
        for entity in entities:
            if entity.position == position and entity.blocks_movement:
                return entity
        return None

    def move_entity(
        self,
        entity: Positionable,
        dx: int,
        dy: int,
        entities: list[Entity],
    ) -> bool:
        """Move an entity by offset if valid.

        Args:
            entity: Entity to move
            dx: X offset
            dy: Y offset
            entities: List of all entities for collision

        Returns:
            True if movement was successful
        """
        new_pos = Position(entity.position.x + dx, entity.position.y + dy)

        # Convert Positionable to Entity for collision check
        # This is safe because all Positionables in our game are Entities
        entity_as_entity = entity if isinstance(entity, Entity) else None

        if self.can_move_to(new_pos, entities, ignore_entity=entity_as_entity):
            entity.move(dx, dy)
            return True

        return False

    def move_entity_to(
        self,
        entity: Positionable,
        position: Position,
        entities: list[Entity],
    ) -> bool:
        """Move entity to absolute position if valid.

        Args:
            entity: Entity to move
            position: Target position
            entities: List of all entities for collision

        Returns:
            True if movement was successful
        """
        entity_as_entity = entity if isinstance(entity, Entity) else None

        if self.can_move_to(position, entities, ignore_entity=entity_as_entity):
            entity.move_to(position)
            return True

        return False

    def update_fov(
        self,
        fov_map: FOVMap,
        viewer_position: Position,
        radius: int = 8,
    ) -> None:
        """Update field of view for a viewer.

        Args:
            fov_map: FOV map to update
            viewer_position: Position of the viewer
            radius: FOV radius
        """
        fov_map.compute_fov(viewer_position, radius)
