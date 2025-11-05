"""Level and experience component for entities."""

from roguelike.components.component import Component


class LevelComponent(Component):
    """Component for entity leveling and experience."""

    def __init__(self, level: int = 1, xp: int = 0, xp_value: int = 0):
        """Initialize level component.

        Args:
            level: Current level
            xp: Current experience points
            xp_value: XP awarded when this entity is killed
        """
        super().__init__()
        self.level = level
        self.xp = xp
        self.xp_value = xp_value
