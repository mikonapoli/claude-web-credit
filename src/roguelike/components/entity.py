"""Component-based entity class."""

from typing import Dict, Optional, Type, TypeVar

from roguelike.components.component import Component
from roguelike.utils.position import Position

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

    def __repr__(self) -> str:
        """Return string representation."""
        components = ", ".join([c.__class__.__name__ for c in self._components.values()])
        return f"ComponentEntity(name={self.name!r}, pos={self.position}, components=[{components}])"
