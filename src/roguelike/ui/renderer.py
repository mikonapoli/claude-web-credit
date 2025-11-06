"""Rendering system using tcod."""

from typing import Optional

import tcod

from roguelike.entities.entity import Entity
from roguelike.ui.message_log import MessageLog
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
        # Load a monospace font - use Courier or fallback to any available font
        try:
            tileset = tcod.tileset.load_truetype_font(
                "/System/Library/Fonts/Courier.dfont", 16, 16
            )
        except Exception:
            # Fallback to a simple tileset if Courier isn't available
            try:
                tileset = tcod.tileset.load_truetype_font(
                    "/System/Library/Fonts/Monaco.dfont", 16, 16
                )
            except Exception:
                # Last resort: use default tileset (may fail)
                tileset = None

        self.console = tcod.console.Console(width, height)
        self.context = tcod.context.new(
            console=self.console,
            columns=width,
            rows=height,
            tileset=tileset,
            title=title,
            vsync=True,
        )

        # Create health bar renderer with smaller width for less invasive display
        self.health_bar_renderer = HealthBarRenderer(bar_width=5)

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

    def render_entity(
        self,
        entity: Entity,
        fov_map: Optional[FOVMap] = None,
        max_height: Optional[int] = None
    ) -> None:
        """Render a single entity.

        Args:
            entity: Entity to render
            fov_map: Optional FOV map for visibility
            max_height: Maximum height to render (for viewport clipping)
        """
        # Only render if visible (or if no FOV map)
        if fov_map and not fov_map.is_visible(entity.position):
            return

        # Skip rendering if entity is below viewport
        if max_height and entity.position.y >= max_height:
            return

        self.console.print(
            entity.position.x,
            entity.position.y,
            entity.char,
            fg=(255, 255, 255)
        )

    def render_entities(
        self,
        entities: list[Entity],
        fov_map: Optional[FOVMap] = None,
        max_height: Optional[int] = None
    ) -> None:
        """Render multiple entities.

        Args:
            entities: List of entities to render
            fov_map: Optional FOV map for visibility
            max_height: Maximum height to render (for viewport clipping)
        """
        for entity in entities:
            self.render_entity(entity, fov_map, max_height)

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

    def render_targeting_cursor(self, position: Position, target_name: Optional[str] = None) -> None:
        """Render the targeting cursor at a position.

        Args:
            position: Position to render cursor
            target_name: Optional name of target at cursor position
        """
        # Render cursor as a highlighted X with a distinct color
        self.console.print(
            position.x,
            position.y,
            "X",
            fg=(255, 255, 0),  # Yellow cursor
            bg=(64, 0, 0)  # Dark red background
        )

        # If there's a target, show its name nearby
        if target_name:
            # Show name above the cursor if possible
            name_y = max(0, position.y - 1)
            name_x = max(0, min(position.x, self.width - len(target_name)))
            self.console.print(name_x, name_y, target_name, fg=(255, 255, 0))
    def render_player_stats(
        self,
        player: HealthBarRenderable,
        x: int,
        y: int,
    ) -> None:
        """Render player stats as text (health, level, power, defense, mana, etc.).

        Args:
            player: Player entity with health stats
            x: X position for stats display
            y: Y position for stats display
        """
        current_y = y

        # Render health - use effective_max_hp if available
        max_hp = player.max_hp
        if hasattr(player, "effective_max_hp"):
            max_hp = player.effective_max_hp
        health_text = f"HP: {player.hp}/{max_hp}"

        # Color based on health percentage
        fill_percentage = self.health_bar_renderer.calculate_fill_percentage(
            player.hp, max_hp
        )
        color = self.health_bar_renderer.get_health_color(fill_percentage)
        self.console.print(x, current_y, health_text, fg=color)
        current_y += 1

        # Render mana if player has mana component
        if hasattr(player, "mana"):
            mana = player.mana
            mana_text = f"MP: {mana.mp}/{mana.max_mp}"
            # Mana color: cyan/blue
            mana_percentage = mana.mana_percentage
            if mana_percentage >= 0.6:
                mana_color = (100, 200, 255)  # Bright cyan
            elif mana_percentage >= 0.25:
                mana_color = (50, 150, 200)  # Medium cyan
            else:
                mana_color = (50, 100, 150)  # Dark cyan
            self.console.print(x, current_y, mana_text, fg=mana_color)
            current_y += 1

        # Render level and XP
        if hasattr(player, "level") and hasattr(player, "xp"):
            level_text = f"Level: {player.level}"
            self.console.print(x, current_y, level_text, fg=(255, 215, 0))  # Gold
            current_y += 1

            xp_text = f"XP: {player.xp}"
            self.console.print(x, current_y, xp_text, fg=(200, 180, 0))  # Dark gold
            current_y += 1

        # Render power (base + equipment bonus)
        if hasattr(player, "effective_power"):
            power = player.effective_power
            base_power = player.power
            bonus = power - base_power
            if bonus > 0:
                power_text = f"Power: {base_power}+{bonus}"
            else:
                power_text = f"Power: {power}"
            self.console.print(x, current_y, power_text, fg=(255, 100, 100))  # Red
            current_y += 1
        elif hasattr(player, "power"):
            power_text = f"Power: {player.power}"
            self.console.print(x, current_y, power_text, fg=(255, 100, 100))  # Red
            current_y += 1

        # Render defense (base + equipment bonus)
        if hasattr(player, "effective_defense"):
            defense = player.effective_defense
            base_defense = player.defense
            bonus = defense - base_defense
            if bonus > 0:
                defense_text = f"Defense: {base_defense}+{bonus}"
            else:
                defense_text = f"Defense: {defense}"
            self.console.print(x, current_y, defense_text, fg=(100, 150, 255))  # Blue
            current_y += 1
        elif hasattr(player, "defense"):
            defense_text = f"Defense: {player.defense}"
            self.console.print(x, current_y, defense_text, fg=(100, 150, 255))  # Blue
            current_y += 1

        # Render status effects if player has them
        if hasattr(player, "status_effects"):
            effects = player.status_effects.get_all_effects()
            if effects:
                current_y += 1  # Add spacing
                self.console.print(x, current_y, "Effects:", fg=(200, 100, 255))  # Purple
                current_y += 1
                for effect in effects[:3]:  # Show max 3 effects to save space
                    effect_text = f" {effect.effect_type[:8]}: {effect.duration}t"
                    self.console.print(x, current_y, effect_text, fg=(180, 80, 200))
                    current_y += 1

        # Render equipped items count
        if hasattr(player, "equipment"):
            equipped_items = player.equipment.get_all_equipped()
            if equipped_items:
                current_y += 1  # Add spacing
                equipped_text = f"Equipped: {len(equipped_items)}"
                self.console.print(x, current_y, equipped_text, fg=(150, 150, 150))  # Gray

    def present(self) -> None:
        """Present the console to the screen."""
        self.context.present(self.console)

    def close(self) -> None:
        """Close the rendering context."""
        self.context.close()
