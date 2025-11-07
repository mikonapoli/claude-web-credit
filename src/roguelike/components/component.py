"""Base component class for entity composition."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from roguelike.components.entity import ComponentEntity


class Component:
    """Base class for all components.

    Component Pattern:
    ------------------
    Components are data containers attached to entities. They use the
    SHARED STATE communication pattern:
    - Components store state
    - Systems orchestrate behavior by reading/writing component state
    - Components DO NOT directly reference other components

    Each component should:
    - Encapsulate a single concern (health, combat, inventory, etc.)
    - Expose clean interfaces for systems to use
    - Maintain their own invariants

    See docs/COMPONENT_COMMUNICATION.md for detailed guidelines.
    """

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
