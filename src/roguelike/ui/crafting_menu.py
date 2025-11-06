"""Crafting menu UI for recipe discovery and crafting."""

from typing import List, Optional, Set

import tcod

from roguelike.components.crafting import CraftingComponent
from roguelike.components.entity import ComponentEntity
from roguelike.components.inventory import InventoryComponent
from roguelike.components.recipe_discovery import RecipeDiscoveryComponent
from roguelike.systems.crafting import CraftingSystem, Recipe


class CraftingMenu:
    """Interactive crafting menu for selecting ingredients and viewing recipes."""

    def __init__(
        self,
        crafter: ComponentEntity,
        crafting_system: CraftingSystem,
        console_width: int,
        console_height: int,
    ):
        """Initialize crafting menu.

        Args:
            crafter: Entity doing the crafting
            crafting_system: Crafting system to use
            console_width: Width of the console
            console_height: Height of the console
        """
        self.crafter = crafter
        self.crafting_system = crafting_system
        self.console_width = console_width
        self.console_height = console_height
        self.selected_ingredients: List[ComponentEntity] = []
        self.menu_scroll = 0
        self.active_section = "inventory"  # "inventory" or "recipes"

    def get_craftable_items(self) -> List[ComponentEntity]:
        """Get all items in inventory that can be used for crafting.

        Returns:
            List of craftable items
        """
        inventory = self.crafter.get_component(InventoryComponent)
        if not inventory:
            return []

        craftable = []
        for item in inventory.get_items():
            if item.get_component(CraftingComponent):
                craftable.append(item)

        return craftable

    def toggle_ingredient_selection(self, item: ComponentEntity) -> None:
        """Toggle an item's selection as an ingredient.

        Args:
            item: Item to toggle
        """
        if item in self.selected_ingredients:
            self.selected_ingredients.remove(item)
        else:
            # Limit to reasonable number of ingredients
            if len(self.selected_ingredients) < 5:
                self.selected_ingredients.append(item)

    def clear_selection(self) -> None:
        """Clear all selected ingredients."""
        self.selected_ingredients = []

    def get_matching_recipe(self) -> Optional[Recipe]:
        """Get recipe that matches currently selected ingredients.

        Returns:
            Matching recipe or None
        """
        if not self.selected_ingredients:
            return None

        return self.crafting_system.find_matching_recipe(self.selected_ingredients)

    def get_discovered_recipes(self) -> Set[str]:
        """Get set of discovered recipe IDs.

        Returns:
            Set of recipe IDs
        """
        discovery_comp = self.crafter.get_component(RecipeDiscoveryComponent)
        if discovery_comp:
            return discovery_comp.get_discovered_recipes()
        return set()

    def render(self, console: tcod.console.Console) -> None:
        """Render the crafting menu.

        Args:
            console: Console to render to
        """
        # Clear the menu area
        menu_width = min(60, self.console_width - 4)
        menu_height = min(40, self.console_height - 4)
        menu_x = (self.console_width - menu_width) // 2
        menu_y = (self.console_height - menu_height) // 2

        # Draw menu background
        for y in range(menu_y, menu_y + menu_height):
            for x in range(menu_x, menu_x + menu_width):
                console.print(x, y, " ", bg=(0, 0, 50))

        # Draw border
        for x in range(menu_x, menu_x + menu_width):
            console.print(x, menu_y, "─", fg=(255, 255, 255))
            console.print(x, menu_y + menu_height - 1, "─", fg=(255, 255, 255))
        for y in range(menu_y, menu_y + menu_height):
            console.print(menu_x, y, "│", fg=(255, 255, 255))
            console.print(menu_x + menu_width - 1, y, "│", fg=(255, 255, 255))

        # Draw corners
        console.print(menu_x, menu_y, "┌", fg=(255, 255, 255))
        console.print(menu_x + menu_width - 1, menu_y, "┐", fg=(255, 255, 255))
        console.print(menu_x, menu_y + menu_height - 1, "└", fg=(255, 255, 255))
        console.print(
            menu_x + menu_width - 1, menu_y + menu_height - 1, "┘", fg=(255, 255, 255)
        )

        # Title
        title = "Crafting Menu (R to close, 1-9 to select, Enter to craft)"
        console.print(
            menu_x + (menu_width - len(title)) // 2,
            menu_y + 1,
            title,
            fg=(255, 255, 0),
        )

        # Inventory section
        current_y = menu_y + 3
        console.print(menu_x + 2, current_y, "Ingredients:", fg=(200, 200, 255))
        current_y += 1

        craftable_items = self.get_craftable_items()
        for idx, item in enumerate(craftable_items[:9]):  # Limit to 9 items
            selected_marker = "[X]" if item in self.selected_ingredients else "[ ]"
            crafting_comp = item.get_component(CraftingComponent)
            tags_str = ", ".join(sorted(crafting_comp.tags)) if crafting_comp else ""

            item_text = f"{idx + 1}. {selected_marker} {item.name}"
            console.print(menu_x + 4, current_y, item_text, fg=(255, 255, 255))
            current_y += 1

            # Show tags
            if tags_str:
                console.print(
                    menu_x + 8,
                    current_y,
                    f"Tags: {tags_str}",
                    fg=(150, 150, 150),
                )
                current_y += 1

        current_y += 1

        # Selected ingredients summary
        console.print(menu_x + 2, current_y, "Selected:", fg=(200, 200, 255))
        current_y += 1

        if self.selected_ingredients:
            selected_names = ", ".join(item.name for item in self.selected_ingredients)
            console.print(menu_x + 4, current_y, selected_names, fg=(255, 255, 255))
            current_y += 1

            # Check if there's a matching recipe
            matching_recipe = self.get_matching_recipe()
            if matching_recipe:
                console.print(
                    menu_x + 4,
                    current_y,
                    f"→ Creates: {matching_recipe.name}",
                    fg=(0, 255, 0),
                )
                current_y += 1
                console.print(
                    menu_x + 4,
                    current_y,
                    f"   {matching_recipe.description}",
                    fg=(150, 200, 150),
                )
            else:
                console.print(
                    menu_x + 4,
                    current_y,
                    "No matching recipe!",
                    fg=(255, 100, 100),
                )
        else:
            console.print(
                menu_x + 4, current_y, "None - select items above", fg=(128, 128, 128)
            )

        current_y += 2

        # Recipe discovery section
        console.print(menu_x + 2, current_y, "Discovered Recipes:", fg=(200, 200, 255))
        current_y += 1

        discovered = self.get_discovered_recipes()
        all_recipes = self.crafting_system.get_all_recipes()

        if discovered:
            for recipe in all_recipes:
                if recipe.id in discovered:
                    console.print(
                        menu_x + 4,
                        current_y,
                        f"• {recipe.name}",
                        fg=(0, 255, 0),
                    )
                    current_y += 1
                    if current_y >= menu_y + menu_height - 2:
                        break
        else:
            console.print(
                menu_x + 4,
                current_y,
                "No recipes discovered yet!",
                fg=(128, 128, 128),
            )
            current_y += 1

        # Show total
        total_recipes = len(all_recipes)
        discovered_count = len(discovered)
        console.print(
            menu_x + 4,
            current_y,
            f"({discovered_count}/{total_recipes} recipes discovered)",
            fg=(200, 200, 200),
        )

    def handle_key(self, key: int) -> Optional[str]:
        """Handle key input in the crafting menu.

        Args:
            key: Key code

        Returns:
            Action string or None ("craft", "close")
        """
        # Number keys for selection
        if tcod.event.KeySym.N1 <= key <= tcod.event.KeySym.N9:
            index = key - tcod.event.KeySym.N1
            craftable_items = self.get_craftable_items()
            if index < len(craftable_items):
                self.toggle_ingredient_selection(craftable_items[index])
            return None

        # Enter to craft
        if key == tcod.event.KeySym.RETURN:
            return "craft"

        # R or Escape to close
        if key in (tcod.event.KeySym.R, tcod.event.KeySym.ESCAPE):
            return "close"

        return None
