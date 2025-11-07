"""Component-based entity class."""

from typing import TYPE_CHECKING, Dict, Optional, Type, TypeVar

from roguelike.components.component import Component
from roguelike.utils.position import Position

if TYPE_CHECKING:
    from roguelike.components.combat import CombatComponent
    from roguelike.components.health import HealthComponent
    from roguelike.components.level import LevelComponent

T = TypeVar("T", bound=Component)


class ComponentEntity:
    """Entity built from composable components."""

    def __init__(
        self,
        position: Position,
        char: str,
        name: str,
        blocks_movement: bool = False,
    ):
        """Initialize component-based entity.

        Args:
            position: Current position in the game world
            char: ASCII character to display
            name: Entity name
            blocks_movement: Whether this entity blocks movement
        """
        self.position = position
        self.char = char
        self.name = name
        self.blocks_movement = blocks_movement
        self._components: Dict[Type[Component], Component] = {}

    def add_component(self, component: Component) -> None:
        """Add a component to this entity.

        Args:
            component: Component to add
        """
        component.attach(self)
        self._components[type(component)] = component

    def get_component(self, component_type: Type[T]) -> Optional[T]:
        """Get a component by type.

        Args:
            component_type: Type of component to retrieve

        Returns:
            Component instance or None if not found
        """
        return self._components.get(component_type)  # type: ignore

    def has_component(self, component_type: Type[Component]) -> bool:
        """Check if entity has a specific component type.

        Args:
            component_type: Type of component to check

        Returns:
            True if entity has the component
        """
        return component_type in self._components

    def remove_component(self, component_type: Type[Component]) -> None:
        """Remove a component from this entity.

        Args:
            component_type: Type of component to remove
        """
        if component_type in self._components:
            del self._components[component_type]

    def move(self, dx: int, dy: int) -> None:
        """Move entity by a relative offset.

        Args:
            dx: X offset
            dy: Y offset
        """
        self.position = Position(self.position.x + dx, self.position.y + dy)

    def move_to(self, position: Position) -> None:
        """Move entity to an absolute position.

        Args:
            position: New position
        """
        self.position = position

    # Properties for protocol compatibility
    # These delegate to components when available

    @property
    def hp(self) -> int:
        """Current hit points (delegates to HealthComponent)."""
        from roguelike.components.health import HealthComponent

        health = self.get_component(HealthComponent)
        if health is None:
            raise AttributeError(f"Entity {self.name} has no HealthComponent")
        return health.hp

    @hp.setter
    def hp(self, value: int) -> None:
        """Set hit points (delegates to HealthComponent)."""
        from roguelike.components.health import HealthComponent

        health = self.get_component(HealthComponent)
        if health is None:
            raise AttributeError(f"Entity {self.name} has no HealthComponent")
        health.hp = value

    @property
    def max_hp(self) -> int:
        """Maximum hit points (delegates to HealthComponent)."""
        from roguelike.components.health import HealthComponent

        health = self.get_component(HealthComponent)
        if health is None:
            raise AttributeError(f"Entity {self.name} has no HealthComponent")
        return health.max_hp

    @max_hp.setter
    def max_hp(self, value: int) -> None:
        """Set maximum hit points (delegates to HealthComponent)."""
        from roguelike.components.health import HealthComponent

        health = self.get_component(HealthComponent)
        if health is None:
            raise AttributeError(f"Entity {self.name} has no HealthComponent")
        health.max_hp = value

    @property
    def is_alive(self) -> bool:
        """Check if entity is alive (delegates to HealthComponent)."""
        from roguelike.components.health import HealthComponent

        health = self.get_component(HealthComponent)
        return health.is_alive if health else True

    @property
    def power(self) -> int:
        """Attack power (delegates to CombatComponent)."""
        from roguelike.components.combat import CombatComponent

        combat = self.get_component(CombatComponent)
        if combat is None:
            raise AttributeError(f"Entity {self.name} has no CombatComponent")
        return combat.power

    @power.setter
    def power(self, value: int) -> None:
        """Set attack power (delegates to CombatComponent)."""
        from roguelike.components.combat import CombatComponent

        combat = self.get_component(CombatComponent)
        if combat is None:
            raise AttributeError(f"Entity {self.name} has no CombatComponent")
        combat.power = value

    @property
    def defense(self) -> int:
        """Defense value (delegates to CombatComponent)."""
        from roguelike.components.combat import CombatComponent

        combat = self.get_component(CombatComponent)
        if combat is None:
            raise AttributeError(f"Entity {self.name} has no CombatComponent")
        return combat.defense

    @defense.setter
    def defense(self, value: int) -> None:
        """Set defense value (delegates to CombatComponent)."""
        from roguelike.components.combat import CombatComponent

        combat = self.get_component(CombatComponent)
        if combat is None:
            raise AttributeError(f"Entity {self.name} has no CombatComponent")
        combat.defense = value

    @property
    def level(self) -> int:
        """Entity level (delegates to LevelComponent)."""
        from roguelike.components.level import LevelComponent

        level_comp = self.get_component(LevelComponent)
        if level_comp is None:
            raise AttributeError(f"Entity {self.name} has no LevelComponent")
        return level_comp.level

    @level.setter
    def level(self, value: int) -> None:
        """Set entity level (delegates to LevelComponent)."""
        from roguelike.components.level import LevelComponent

        level_comp = self.get_component(LevelComponent)
        if level_comp is None:
            raise AttributeError(f"Entity {self.name} has no LevelComponent")
        level_comp.level = value

    @property
    def xp(self) -> int:
        """Experience points (delegates to LevelComponent)."""
        from roguelike.components.level import LevelComponent

        level_comp = self.get_component(LevelComponent)
        if level_comp is None:
            raise AttributeError(f"Entity {self.name} has no LevelComponent")
        return level_comp.xp

    @xp.setter
    def xp(self, value: int) -> None:
        """Set experience points (delegates to LevelComponent)."""
        from roguelike.components.level import LevelComponent

        level_comp = self.get_component(LevelComponent)
        if level_comp is None:
            raise AttributeError(f"Entity {self.name} has no LevelComponent")
        level_comp.xp = value

    @property
    def xp_value(self) -> int:
        """XP awarded when killed (delegates to LevelComponent)."""
        from roguelike.components.level import LevelComponent

        level_comp = self.get_component(LevelComponent)
        if level_comp is None:
            raise AttributeError(f"Entity {self.name} has no LevelComponent")
        return level_comp.xp_value

    @xp_value.setter
    def xp_value(self, value: int) -> None:
        """Set XP awarded when killed (delegates to LevelComponent)."""
        from roguelike.components.level import LevelComponent

        level_comp = self.get_component(LevelComponent)
        if level_comp is None:
            raise AttributeError(f"Entity {self.name} has no LevelComponent")
        level_comp.xp_value = value

    def take_damage(self, amount: int) -> int:
        """Take damage (delegates to HealthComponent).

        Args:
            amount: Damage amount

        Returns:
            Actual damage taken
        """
        from roguelike.components.health import HealthComponent

        health = self.get_component(HealthComponent)
        if health is None:
            raise AttributeError(f"Entity {self.name} has no HealthComponent")
        return health.take_damage(amount)

    def heal(self, amount: int) -> int:
        """Heal damage (delegates to HealthComponent).

        Args:
            amount: Heal amount

        Returns:
            Actual amount healed
        """
        from roguelike.components.health import HealthComponent

        health = self.get_component(HealthComponent)
        if health is None:
            raise AttributeError(f"Entity {self.name} has no HealthComponent")
        return health.heal(amount)

    @property
    def inventory(self):
        """Get inventory (delegates to InventoryComponent)."""
        from roguelike.components.inventory import InventoryComponent

        inv_comp = self.get_component(InventoryComponent)
        if inv_comp is None:
            raise AttributeError(f"Entity {self.name} has no InventoryComponent")
        return inv_comp._inventory

    def __repr__(self) -> str:
        """Return string representation."""
        components = ", ".join([c.__class__.__name__ for c in self._components.values()])
        return f"ComponentEntity(name={self.name!r}, pos={self.position}, components=[{components}])"
