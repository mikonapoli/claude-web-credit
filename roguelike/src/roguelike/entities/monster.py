"""Monster entities."""

from roguelike.entities.actor import Actor
from roguelike.utils.position import Position


class Monster(Actor):
    """A hostile monster."""

    def __init__(
        self,
        position: Position,
        char: str,
        name: str,
        max_hp: int,
        defense: int,
        power: int,
        xp_value: int,
    ):
        """Initialize a monster.

        Args:
            position: Starting position
            char: Display character
            name: Monster name
            max_hp: Maximum hit points
            defense: Defense value
            power: Attack power
            xp_value: XP awarded when killed
        """
        super().__init__(
            position=position,
            char=char,
            name=name,
            max_hp=max_hp,
            defense=defense,
            power=power,
            xp_value=xp_value,
        )


# Predefined monster types
def create_orc(position: Position) -> Monster:
    """Create an orc.

    Args:
        position: Monster position

    Returns:
        Orc monster
    """
    return Monster(
        position=position,
        char="o",
        name="Orc",
        max_hp=10,
        defense=0,
        power=3,
        xp_value=35,
    )


def create_troll(position: Position) -> Monster:
    """Create a troll.

    Args:
        position: Monster position

    Returns:
        Troll monster
    """
    return Monster(
        position=position,
        char="T",
        name="Troll",
        max_hp=16,
        defense=1,
        power=4,
        xp_value=100,
    )
