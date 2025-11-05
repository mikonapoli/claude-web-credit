"""Rendering system using tcod."""

from typing import Optional

import tcod

from roguelike.entities.entity import Entity
from roguelike.ui.message_log import MessageLog
from roguelike.utils.position import Position
from roguelike.world.fov import FOVMap
from roguelike.world.game_map import GameMap


class Renderer:
    """Handles all rendering operations."""

    def __init__(self, width: int, height: int, title: str = "Roguelike"):
        """Initialize the renderer.

        Args:
            width: Console width in characters
            height: Console height in characters
            title: Window title
        """
        self.width = width
        self.height = height
        self.title = title

        # Create the console
        tileset = tcod.tileset.load_tilesheet(
            tcod.tileset.FONT_DEJAVU_SANS_MONO,
            32, 8,  # Font dimensions
            tcod.tileset.CHARMAP_TCOD
        )
        self.console = tcod.console.Console(width, height)
        self.context = tcod.context.new(
            console=self.console,
            columns=width,
            rows=height,
            tileset=tileset,
            title=title,
            vsync=True,
        )

    def clear(self) -> None:
        """Clear the console."""
        self.console.clear()

    def render_map(
        self,
        game_map: GameMap,
        fov_map: Optional[FOVMap] = None,
        max_height: Optional[int] = None
    ) -> None:
        """Render the game map.

        Args:
            game_map: Map to render
            fov_map: Optional FOV map for visibility
            max_height: Maximum height to render (for viewport clipping)
        """
        render_height = min(max_height, game_map.height) if max_height else game_map.height

        for y in range(render_height):
            for x in range(game_map.width):
                pos = Position(x, y)
                tile = game_map.get_tile(pos)

                # Determine color based on visibility
                if fov_map:
                    if fov_map.is_visible(pos):
                        # Visible tiles are bright
                        fg = (255, 255, 255)
                    elif fov_map.is_explored(pos):
                        # Explored but not visible tiles are dim
                        fg = (128, 128, 128)
                    else:
                        # Unexplored tiles are not rendered
                        continue
                else:
                    # No FOV, render everything bright
                    fg = (255, 255, 255)

                self.console.print(x, y, tile.char, fg=fg)

    def render_entity(self, entity: Entity, fov_map: Optional[FOVMap] = None) -> None:
        """Render a single entity.

        Args:
            entity: Entity to render
            fov_map: Optional FOV map for visibility
        """
        # Only render if visible (or if no FOV map)
        if fov_map and not fov_map.is_visible(entity.position):
            return

        self.console.print(
            entity.position.x,
            entity.position.y,
            entity.char,
            fg=(255, 255, 255)
        )

    def render_entities(self, entities: list[Entity], fov_map: Optional[FOVMap] = None) -> None:
        """Render multiple entities.

        Args:
            entities: List of entities to render
            fov_map: Optional FOV map for visibility
        """
        for entity in entities:
            self.render_entity(entity, fov_map)

    def render_message_log(
        self,
        message_log: MessageLog,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> None:
        """Render the message log in a specified area.

        Args:
            message_log: The message log to render
            x: X position of message area
            y: Y position of message area (top-left)
            width: Width of message area
            height: Height of message area (number of lines)
        """
        # Get the most recent messages that fit in the area
        messages = message_log.get_messages(count=height)

        # Reverse so oldest is at top, newest at bottom
        messages = list(reversed(messages))

        # Render each message
        for i, message in enumerate(messages):
            # Truncate message if too long
            if len(message) > width:
                message = message[:width-3] + "..."

            self.console.print(x, y + i, message, fg=(255, 255, 255))

    def present(self) -> None:
        """Present the console to the screen."""
        self.context.present(self.console)

    def close(self) -> None:
        """Close the rendering context."""
        self.context.close()
