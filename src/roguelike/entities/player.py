"""Player character."""

from roguelike.components.equipment import EquipmentComponent
from roguelike.components.mana import ManaComponent
from roguelike.components.status_effects import StatusEffectsComponent
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

        # Add equipment component for managing equipped items
        self.equipment = EquipmentComponent()

        # Add mana component for magic system
        self.mana = ManaComponent(max_mp=20, mp_regen_rate=1)

        # Add status effects component
        self.status_effects = StatusEffectsComponent()

    @property
    def effective_power(self) -> int:
        """Get effective power including equipment bonuses.

        Returns:
            Total power (base + equipment bonuses)
        """
        return self.power + self.equipment.get_total_power_bonus()

    @property
    def effective_defense(self) -> int:
        """Get effective defense including equipment bonuses.

        Returns:
            Total defense (base + equipment bonuses)
        """
        return self.defense + self.equipment.get_total_defense_bonus()

    @property
    def effective_max_hp(self) -> int:
        """Get effective max HP including equipment bonuses.

        Returns:
            Total max HP (base + equipment bonuses)
        """
        return self.max_hp + self.equipment.get_total_max_hp_bonus()
