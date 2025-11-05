"""Combat component for entities."""

from roguelike.components.component import Component


class CombatComponent(Component):
    """Component for entity combat stats."""

    def __init__(self, power: int, defense: int):
        """Initialize combat component.

        Args:
            power: Attack power
            defense: Defense value (damage reduction)
        """
        super().__init__()
        self.power = power
        self.defense = defense
