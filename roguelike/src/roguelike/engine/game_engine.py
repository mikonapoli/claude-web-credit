"""Main game engine."""

from typing import List

import tcod.event

from roguelike.entities.entity import Entity
from roguelike.entities.player import Player
from roguelike.ui.input_handler import Action, InputHandler
from roguelike.ui.renderer import Renderer
from roguelike.world.game_map import GameMap


class GameEngine:
    """Main game engine that manages the game loop."""

    def __init__(
        self,
        game_map: GameMap,
        player: Player,
        entities: List[Entity] | None = None,
    ):
        """Initialize the game engine.

        Args:
            game_map: The game map
            player: The player entity
            entities: List of other entities
        """
        self.game_map = game_map
        self.player = player
        self.entities = entities or []
        self.running = False

    def handle_action(self, action: Action) -> bool:
        """Handle a player action.

        Args:
            action: Action to handle

        Returns:
            True if the action consumed a turn
        """
        if action == Action.QUIT:
            self.running = False
            return False

        if action == Action.WAIT:
            return True

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
            return self.try_move_player(dx, dy)

        return False

    def try_move_player(self, dx: int, dy: int) -> bool:
        """Try to move the player.

        Args:
            dx: X offset
            dy: Y offset

        Returns:
            True if movement was successful (consumes turn)
        """
        from roguelike.utils.position import Position

        new_pos = Position(
            self.player.position.x + dx,
            self.player.position.y + dy
        )

        # Check if destination is walkable
        if not self.game_map.is_walkable(new_pos):
            return False

        # Check if any entity blocks movement at destination
        for entity in self.entities:
            if entity.position == new_pos and entity.blocks_movement:
                return False

        # Move is valid
        self.player.move(dx, dy)
        return True

    def run(self, renderer: Renderer) -> None:
        """Run the main game loop.

        Args:
            renderer: The renderer to use
        """
        self.running = True
        input_handler = InputHandler()

        while self.running:
            # Render
            renderer.clear()
            renderer.render_map(self.game_map)
            renderer.render_entities(self.entities)
            renderer.render_entity(self.player)
            renderer.present()

            # Handle input
            for event in tcod.event.wait():
                input_handler.dispatch(event)

            action = input_handler.get_action()
            if action:
                turn_taken = self.handle_action(action)
                # In the future, if turn_taken, we'd process enemy turns here

        renderer.close()
