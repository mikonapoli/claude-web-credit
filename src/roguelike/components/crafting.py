"""Crafting component for items with crafting tags."""

from typing import Set

from roguelike.components.component import Component


class CraftingComponent(Component):
    """Component that defines an item's crafting properties.

    Items with this component can be used in crafting recipes.
    Tags represent abstract qualities (e.g., "herbal", "magical", "metallic").
    """

    def __init__(
        self,
        tags: Set[str],
        consumable: bool = True,
        craftable: bool = False,
    ):
        """Initialize crafting component.

        Args:
            tags: Set of crafting tags (e.g., {"herbal", "magical"})
            consumable: Whether item is consumed when used in crafting
            craftable: Whether this item can be crafted (vs. found only)
        """
        super().__init__()
        self.tags = tags
        self.consumable = consumable
        self.craftable = craftable

    def has_tag(self, tag: str) -> bool:
        """Check if item has a specific tag.

        Args:
            tag: Tag to check for

        Returns:
            True if item has the tag
        """
        return tag in self.tags

    def has_all_tags(self, tags: Set[str]) -> bool:
        """Check if item has all specified tags.

        Args:
            tags: Set of tags to check for

        Returns:
            True if item has all tags
        """
        return tags.issubset(self.tags)

    def has_any_tag(self, tags: Set[str]) -> bool:
        """Check if item has any of the specified tags.

        Args:
            tags: Set of tags to check for

        Returns:
            True if item has at least one tag
        """
        return bool(self.tags.intersection(tags))

    def __repr__(self) -> str:
        """Return string representation."""
        return f"CraftingComponent(tags={self.tags}, consumable={self.consumable}, craftable={self.craftable})"
