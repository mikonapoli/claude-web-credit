"""Player character."""

from roguelike.components.mana import ManaComponent
from roguelike.components.spells import SpellComponent
from roguelike.entities.actor import Actor
from roguelike.systems.inventory import Inventory
from roguelike.utils.position import Position


class Player(Actor):
    """The player character."""

    def __init__(self, position: Position):
        """Initialize the player.

        Args:
            position: Starting position
        """
        super().__init__(
            position=position,
            char="@",
            name="Player",
            max_hp=30,
            defense=2,
            power=5,
        )
        self.inventory = Inventory(capacity=26)
        self.mana = ManaComponent(max_mp=50, mp_regen_rate=2)
        self.spells = SpellComponent()
