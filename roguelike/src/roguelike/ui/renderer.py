"""Rendering system using tcod."""

import tcod

from roguelike.entities.entity import Entity
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

    def render_map(self, game_map: GameMap) -> None:
        """Render the game map.

        Args:
            game_map: Map to render
        """
        for y in range(game_map.height):
            for x in range(game_map.width):
                from roguelike.utils.position import Position
                tile = game_map.get_tile(Position(x, y))
                self.console.print(x, y, tile.char, fg=(255, 255, 255))

    def render_entity(self, entity: Entity) -> None:
        """Render a single entity.

        Args:
            entity: Entity to render
        """
        self.console.print(
            entity.position.x,
            entity.position.y,
            entity.char,
            fg=(255, 255, 255)
        )

    def render_entities(self, entities: list[Entity]) -> None:
        """Render multiple entities.

        Args:
            entities: List of entities to render
        """
        for entity in entities:
            self.render_entity(entity)

    def present(self) -> None:
        """Present the console to the screen."""
        self.context.present(self.console)

    def close(self) -> None:
        """Close the rendering context."""
        self.context.close()
