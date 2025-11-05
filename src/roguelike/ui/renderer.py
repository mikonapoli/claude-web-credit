"""Rendering system using tcod."""

from typing import Optional

import tcod

from roguelike.entities.entity import Entity
from roguelike.ui.health_bar_renderer import HealthBarRenderer
from roguelike.utils.position import Position
from roguelike.utils.protocols import HealthBarRenderable
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

        # Create health bar renderer
        self.health_bar_renderer = HealthBarRenderer(bar_width=10)

    def clear(self) -> None:
        """Clear the console."""
        self.console.clear()

    def render_map(self, game_map: GameMap, fov_map: Optional[FOVMap] = None) -> None:
        """Render the game map.

        Args:
            game_map: Map to render
            fov_map: Optional FOV map for visibility
        """
        for y in range(game_map.height):
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

    def render_health_bar(
        self,
        entity: HealthBarRenderable,
        fov_map: Optional[FOVMap] = None,
        y_offset: int = -1,
    ) -> None:
        """Render a health bar above an entity.

        Args:
            entity: Entity with health to render
            fov_map: Optional FOV map for visibility
            y_offset: Vertical offset from entity position (negative = above)
        """
        # Only render if entity is visible and alive
        if fov_map and not fov_map.is_visible(entity.position):
            return
        if not entity.is_alive:
            return

        # Calculate health bar position (centered above entity)
        bar_y = entity.position.y + y_offset
        bar_x = entity.position.x - self.health_bar_renderer.bar_width // 2

        # Clamp to screen bounds
        bar_x = max(0, min(bar_x, self.width - self.health_bar_renderer.bar_width))
        bar_y = max(0, min(bar_y, self.height - 1))

        # Render the health bar
        self.health_bar_renderer.render(
            self.console,
            x=bar_x,
            y=bar_y,
            hp=entity.hp,
            max_hp=entity.max_hp,
        )

    def render_health_bars(
        self,
        entities: list[HealthBarRenderable],
        fov_map: Optional[FOVMap] = None,
        y_offset: int = -1,
    ) -> None:
        """Render health bars for multiple entities.

        Args:
            entities: List of entities to render health bars for
            fov_map: Optional FOV map for visibility
            y_offset: Vertical offset from entity position (negative = above)
        """
        for entity in entities:
            self.render_health_bar(entity, fov_map, y_offset)

    def present(self) -> None:
        """Present the console to the screen."""
        self.context.present(self.console)

    def close(self) -> None:
        """Close the rendering context."""
        self.context.close()
