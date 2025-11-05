"""Base component class for entity composition."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from roguelike.components.entity import ComponentEntity


class Component:
    """Base class for all components."""

    def __init__(self, entity: Optional["ComponentEntity"] = None):
        """Initialize component.

        Args:
            entity: The entity this component belongs to
        """
        self.entity = entity

    def attach(self, entity: "ComponentEntity") -> None:
        """Attach this component to an entity.

        Args:
            entity: The entity to attach to
        """
        self.entity = entity
