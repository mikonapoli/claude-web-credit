"""Magic system for spell casting and resolution."""

from typing import TYPE_CHECKING, Optional

from roguelike.components.mana import ManaComponent
from roguelike.components.spells import SpellComponent
from roguelike.engine.events import EventBus, ManaChangedEvent, SpellCastEvent
from roguelike.magic.effects import SpellEffect
from roguelike.magic.spell import Spell
from roguelike.utils.protocols import Combatant

if TYPE_CHECKING:
    from roguelike.magic.effects import EffectResult


class MagicSystem:
    """Handles spell casting and magic resolution."""

    def __init__(self, event_bus: EventBus):
        """Initialize magic system.

        Args:
            event_bus: Event bus for publishing magic events
        """
        self.event_bus = event_bus
        self._spell_effects: dict[str, SpellEffect] = {}

    def register_spell_effect(self, spell_id: str, effect: SpellEffect) -> None:
        """Register a spell effect handler.

        Args:
            spell_id: Spell ID to register effect for
            effect: Effect implementation
        """
        self._spell_effects[spell_id] = effect

    def can_cast_spell(
        self,
        caster: Combatant,
        spell: Spell,
        mana_component: Optional[ManaComponent] = None,
        spell_component: Optional[SpellComponent] = None,
    ) -> tuple[bool, str]:
        """Check if caster can cast a spell.

        Args:
            caster: Entity attempting to cast
            spell: Spell to cast
            mana_component: Caster's mana component (if any)
            spell_component: Caster's spell component (if any)

        Returns:
            Tuple of (can_cast, reason)
        """
        # Check if caster is alive
        if not caster.is_alive:
            return False, f"{caster.name} is dead!"

        # Check if spell is known
        if spell_component and not spell_component.knows_spell(spell.id):
            return False, f"{caster.name} doesn't know {spell.name}!"

        # Check mana cost
        if mana_component:
            if not mana_component.has_mana(spell.mana_cost):
                return (
                    False,
                    f"{caster.name} doesn't have enough mana! "
                    f"({mana_component.mp}/{spell.mana_cost})",
                )

        # Check if spell has registered effect
        if spell.id not in self._spell_effects:
            return False, f"No effect registered for {spell.name}!"

        return True, ""

    def cast_spell(
        self,
        caster: Combatant,
        target: Combatant,
        spell: Spell,
        mana_component: Optional[ManaComponent] = None,
        spell_component: Optional[SpellComponent] = None,
    ) -> "EffectResult":
        """Cast a spell from caster to target.

        Args:
            caster: Entity casting the spell
            target: Target of the spell
            spell: Spell to cast
            mana_component: Caster's mana component (if any)
            spell_component: Caster's spell component (if any)

        Returns:
            Result of spell casting
        """
        from roguelike.magic.effects import EffectResult

        # Check if can cast
        can_cast, reason = self.can_cast_spell(
            caster, spell, mana_component, spell_component
        )
        if not can_cast:
            return EffectResult(success=False, message=reason)

        # Consume mana
        if mana_component:
            old_mp = mana_component.mp
            mana_component.consume_mana(spell.mana_cost)

            # Emit mana changed event
            caster_name = caster.name
            self.event_bus.emit(
                ManaChangedEvent(
                    entity_name=caster_name,
                    old_mp=old_mp,
                    new_mp=mana_component.mp,
                    max_mp=mana_component.max_mp,
                )
            )

        # Apply spell effect
        effect = self._spell_effects[spell.id]
        result = effect.apply(caster, target, spell.power)

        # Emit spell cast event
        self.event_bus.emit(
            SpellCastEvent(
                caster_name=caster.name,
                spell_name=spell.name,
                target_name=target.name,
                mana_cost=spell.mana_cost,
                effect_message=result.message,
            )
        )

        return result

    def regenerate_mana(
        self, entity_name: str, mana_component: ManaComponent
    ) -> int:
        """Regenerate mana for an entity.

        Args:
            entity_name: Name of entity regenerating
            mana_component: Entity's mana component

        Returns:
            Amount of mana regenerated
        """
        old_mp = mana_component.mp
        regenerated = mana_component.regenerate()

        if regenerated > 0:
            self.event_bus.emit(
                ManaChangedEvent(
                    entity_name=entity_name,
                    old_mp=old_mp,
                    new_mp=mana_component.mp,
                    max_mp=mana_component.max_mp,
                )
            )

        return regenerated
