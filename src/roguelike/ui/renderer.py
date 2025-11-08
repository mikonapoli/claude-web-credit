"""Rendering system using tcod."""

from typing import Optional

import tcod

from roguelike.components.entity import ComponentEntity
from roguelike.components.equipment import EquipmentComponent
from roguelike.components.helpers import get_equipment_bonuses
from roguelike.components.mana import ManaComponent
from roguelike.components.status_effects import StatusEffectsComponent
from roguelike.entities.entity import Entity
from roguelike.ui.message_log import MessageLog
from roguelike.ui.health_bar_renderer import HealthBarRenderer
from roguelike.ui.spell_menu import SpellMenu
from roguelike.ui.inventory_menu import InventoryMenu
from roguelike.ui.stats_bar_renderer import StatsBarRenderer
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

        # Create stats bar renderer for player stats panel
        self.stats_bar_renderer = StatsBarRenderer(bar_width=15)

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
        player: ComponentEntity,
        x: int,
        y: int,
    ) -> None:
        """Render comprehensive player stats panel.

        Displays:
        - Level and XP
        - HP bar with numeric values
        - Mana bar (if player has ManaComponent)
        - Base and effective Power/Defense stats
        - Equipment bonuses

        Args:
            player: Player entity
            x: X position for stats display (left edge)
            y: Y position for stats display (top edge)
        """
        current_y = y

        # Title
        self.console.print(x, current_y, "=== PLAYER ===", fg=(255, 255, 100))
        current_y += 1

        # Level and XP
        level_text = f"Level: {player.level}"
        xp_text = f"XP: {player.xp}"
        self.console.print(x, current_y, level_text, fg=(200, 200, 200))
        current_y += 1
        self.console.print(x, current_y, xp_text, fg=(200, 200, 200))
        current_y += 1

        # Blank line
        current_y += 1

        # Health bar
        self.stats_bar_renderer.render_health_bar(
            self.console, x, current_y, player.hp, player.max_hp
        )
        current_y += 1

        # Mana bar (if player has mana)
        mana = player.get_component(ManaComponent)
        if mana:
            self.stats_bar_renderer.render_mana_bar(
                self.console, x, current_y, mana.mp, mana.max_mp
            )
            current_y += 1

        # Blank line
        current_y += 1

        # Combat stats with equipment bonuses
        # Note: player.power and player.defense already include equipment bonuses
        # (applied by EquipmentSystem), so we subtract to get the true base values
        power_bonus, defense_bonus, hp_bonus = get_equipment_bonuses(player)

        current_power = player.power  # Already includes bonuses
        current_defense = player.defense  # Already includes bonuses
        base_power = current_power - power_bonus
        base_defense = current_defense - defense_bonus

        # Show base stats with bonuses
        if power_bonus > 0:
            power_text = f"Power: {base_power} (+{power_bonus}) = {current_power}"
            self.console.print(x, current_y, power_text, fg=(255, 150, 150))
        else:
            power_text = f"Power: {current_power}"
            self.console.print(x, current_y, power_text, fg=(200, 200, 200))
        current_y += 1

        if defense_bonus > 0:
            defense_text = f"Defense: {base_defense} (+{defense_bonus}) = {current_defense}"
            self.console.print(x, current_y, defense_text, fg=(150, 150, 255))
        else:
            defense_text = f"Defense: {current_defense}"
            self.console.print(x, current_y, defense_text, fg=(200, 200, 200))
        current_y += 1

        if hp_bonus > 0:
            hp_bonus_text = f"Max HP Bonus: +{hp_bonus}"
            self.console.print(x, current_y, hp_bonus_text, fg=(150, 255, 150))
            current_y += 1

    def render_status_effects(
        self,
        entity: ComponentEntity,
        x: int,
        y: int,
        max_width: int = 30,
    ) -> int:
        """Render active status effects for an entity.

        Args:
            entity: Entity to display status effects for
            x: X position for display
            y: Y position for display (top)
            max_width: Maximum width for status effect display

        Returns:
            Number of lines rendered
        """
        status_effects = entity.get_component(StatusEffectsComponent)
        if not status_effects:
            return 0

        effects = status_effects.get_all_effects()
        if not effects:
            return 0

        current_y = y
        self.console.print(x, current_y, "Status Effects:", fg=(200, 200, 100))
        current_y += 1

        # Define colors for different effect types
        effect_colors = {
            "poison": (100, 255, 100),  # Green
            "confusion": (255, 100, 255),  # Magenta
            "invisibility": (150, 150, 255),  # Light blue
        }

        for effect in effects:
            # Get appropriate color or default
            color = effect_colors.get(effect.effect_type, (200, 200, 200))

            # Format effect display
            effect_text = f"  {effect.effect_type.capitalize()}"
            if effect.power > 0:
                effect_text += f" ({effect.power})"
            effect_text += f" [{effect.duration}]"

            # Truncate if too long
            if len(effect_text) > max_width:
                effect_text = effect_text[:max_width - 3] + "..."

            self.console.print(x, current_y, effect_text, fg=color)
            current_y += 1

        return current_y - y

    def render_equipment(
        self,
        entity: ComponentEntity,
        x: int,
        y: int,
        max_width: int = 30,
    ) -> int:
        """Render equipped items for an entity.

        Args:
            entity: Entity to display equipment for
            x: X position for display
            y: Y position for display (top)
            max_width: Maximum width for equipment display

        Returns:
            Number of lines rendered
        """
        equipment = entity.get_component(EquipmentComponent)
        if not equipment:
            return 0

        equipped_items = equipment.get_all_equipped()
        if not equipped_items:
            return 0

        current_y = y
        self.console.print(x, current_y, "Equipment:", fg=(200, 200, 100))
        current_y += 1

        # Display each equipped item by slot
        for slot, item in equipped_items.items():
            slot_name = slot.value.capitalize()
            item_name = item.name

            # Truncate item name if necessary
            display_text = f"  {slot_name}: {item_name}"
            if len(display_text) > max_width:
                display_text = display_text[:max_width - 3] + "..."

            self.console.print(x, current_y, display_text, fg=(180, 180, 255))
            current_y += 1

        return current_y - y

    def render_spell_menu(
        self,
        spell_menu: SpellMenu,
        player: ComponentEntity,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> None:
        """Render the spell menu overlay.

        Args:
            spell_menu: Spell menu to render
            player: Player entity (for current MP)
            x: X position for menu
            y: Y position for menu
            width: Width of menu area
            height: Height of menu area
        """
        if not spell_menu.is_open:
            return

        # Get player's current mana
        mana = player.get_component(ManaComponent)
        current_mp = mana.mp if mana else 0

        # Get menu lines
        lines = spell_menu.get_menu_lines(current_mp)

        # Render background box
        for dy in range(min(len(lines) + 2, height)):
            for dx in range(width):
                self.console.print(x + dx, y + dy, " ", bg=(0, 0, 64))

        # Render menu lines
        for i, line in enumerate(lines[:height - 2]):
            # Highlight selected spell line
            if i >= 3 and ">" in line:  # Lines after header
                fg_color = (255, 255, 100)  # Yellow for selected
            else:
                fg_color = (255, 255, 255)

            self.console.print(x + 1, y + i + 1, line[:width - 2], fg=fg_color)

    def render_inventory_menu(
        self,
        inventory_menu: InventoryMenu,
        player: ComponentEntity,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> None:
        """Render the inventory menu overlay.

        Args:
            inventory_menu: Inventory menu to render
            player: Player entity (for inventory capacity)
            x: X position for menu
            y: Y position for menu
            width: Width of menu area
            height: Height of menu area
        """
        if not inventory_menu.is_open:
            return

        # Get inventory capacity
        from roguelike.components.inventory import InventoryComponent
        inventory = player.get_component(InventoryComponent)
        capacity = inventory.capacity if inventory else 0

        # Get menu lines
        lines = inventory_menu.get_menu_lines(capacity)

        # Render background box
        for dy in range(min(len(lines) + 2, height)):
            for dx in range(width):
                self.console.print(x + dx, y + dy, " ", bg=(0, 64, 0))

        # Render menu lines
        for i, line in enumerate(lines[:height - 2]):
            # Highlight selected item line
            if ">" in line:  # Selected line
                fg_color = (255, 255, 100)  # Yellow for selected
            else:
                fg_color = (255, 255, 255)

            self.console.print(x + 1, y + i + 1, line[:width - 2], fg=fg_color)

    def render_item_examination(
        self,
        description_lines: list[str],
    ) -> None:
        """Render item examination UI showing item details.

        Args:
            description_lines: Lines of item description to display
        """
        # Clear screen for examination display
        self.console.clear()

        # Calculate layout
        start_y = 2
        current_y = start_y

        # Render title from first line
        if description_lines:
            title = description_lines[0]
            title_x = (self.width - len(title)) // 2
            self.console.print(title_x, 0, title, fg=(255, 255, 100))
            current_y = start_y

            # Render rest of description
            for line in description_lines[1:]:
                if current_y >= self.height - 2:
                    break
                self.console.print(2, current_y, line, fg=(200, 200, 200))
                current_y += 1

        # Render instructions at bottom
        instructions = "Press ESC to close"
        inst_x = (self.width - len(instructions)) // 2
        self.console.print(inst_x, self.height - 1, instructions, fg=(150, 150, 150))

    def render_recipe_book(
        self,
        recipes_data: list[dict],
        title: str = "Recipe Book",
    ) -> None:
        """Render the recipe book UI showing discovered/undiscovered recipes.

        Args:
            recipes_data: List of dicts with 'recipe' and 'discovered' keys
            title: Title for the recipe book display
        """
        # Clear screen for recipe book display
        self.console.clear()

        # Calculate layout
        start_y = 2
        current_y = start_y

        # Render title
        title_x = (self.width - len(title)) // 2
        self.console.print(title_x, 0, title, fg=(255, 255, 100))

        # Render instructions
        instructions = "Press ESC to close | Discovered recipes show ingredients"
        inst_x = (self.width - len(instructions)) // 2
        self.console.print(inst_x, 1, instructions, fg=(150, 150, 150))

        # Render recipes
        for data in recipes_data:
            recipe = data["recipe"]
            discovered = data["discovered"]

            if current_y >= self.height - 2:
                # Near bottom of screen, show "more recipes..." message
                self.console.print(2, current_y, "... more recipes ...", fg=(128, 128, 128))
                break

            # Recipe name with discovery indicator
            if discovered:
                name_color = (100, 255, 100)  # Green for discovered
                prefix = "[+] "
            else:
                name_color = (128, 128, 128)  # Gray for undiscovered
                prefix = "[ ] "

            recipe_name = f"{prefix}{recipe.name}"
            self.console.print(2, current_y, recipe_name, fg=name_color)
            current_y += 1

            # Show description and ingredients only if discovered
            if discovered:
                # Description
                desc_text = f"    {recipe.description}"
                if len(desc_text) > self.width - 4:
                    desc_text = desc_text[:self.width - 7] + "..."
                self.console.print(2, current_y, desc_text, fg=(200, 200, 200))
                current_y += 1

                # Ingredients (show required tags)
                ingredients_text = "    Ingredients: "
                tag_parts = []
                for tag_set in recipe.required_tags:
                    tag_str = " or ".join(sorted(tag_set))
                    tag_parts.append(f"[{tag_str}]")
                ingredients_text += ", ".join(tag_parts)

                # Handle long ingredient lists
                if len(ingredients_text) > self.width - 4:
                    ingredients_text = ingredients_text[:self.width - 7] + "..."

                self.console.print(2, current_y, ingredients_text, fg=(150, 200, 255))
                current_y += 1

            # Blank line between recipes
            current_y += 1

        # Show discovery count at bottom
        discovered_count = sum(1 for d in recipes_data if d["discovered"])
        total_count = len(recipes_data)
        count_text = f"Discovered: {discovered_count}/{total_count}"
        count_x = (self.width - len(count_text)) // 2
        self.console.print(count_x, self.height - 1, count_text, fg=(255, 255, 100))

    def present(self) -> None:
        """Present the console to the screen."""
        self.context.present(self.console)

    def close(self) -> None:
        """Close the rendering context."""
        self.context.close()
