"""Spell casting commands."""

from typing import List, Optional

from roguelike.commands.command import Command, CommandResult
from roguelike.components.entity import ComponentEntity
from roguelike.components.mana import ManaComponent
from roguelike.components.spells import SpellComponent
from roguelike.magic.spell import Spell
from roguelike.systems.ai_system import AISystem
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.magic_system import MagicSystem
from roguelike.systems.status_effects import StatusEffectsSystem
from roguelike.ui.message_log import MessageLog


class CastSpellCommand(Command):
    """Command to cast a spell."""

    def __init__(
        self,
        caster: ComponentEntity,
        target: ComponentEntity,
        spell: Spell,
        entities: List[ComponentEntity],
        magic_system: MagicSystem,
        combat_system: CombatSystem,
        ai_system: AISystem,
        status_effects_system: Optional[StatusEffectsSystem],
        message_log: MessageLog,
    ):
        """Initialize cast spell command.

        Args:
            caster: Entity casting the spell
            target: Target of the spell
            spell: Spell to cast
            entities: All entities in game
            magic_system: Magic system for spell casting
            combat_system: Combat system for handling death
            ai_system: AI system for enemy behavior
            status_effects_system: Status effects system for managing effects
            message_log: Message log for displaying messages
        """
        self.caster = caster
        self.target = target
        self.spell = spell
        self.entities = entities
        self.magic_system = magic_system
        self.combat_system = combat_system
        self.ai_system = ai_system
        self.status_effects_system = status_effects_system
        self.message_log = message_log

    def execute(self) -> CommandResult:
        """Execute spell casting and process turn cycle."""
        # Get mana and spell components
        mana_component = self.caster.get_component(ManaComponent)
        spell_component = self.caster.get_component(SpellComponent)

        # Cast the spell
        result = self.magic_system.cast_spell(
            caster=self.caster,
            target=self.target,
            spell=self.spell,
            mana_component=mana_component,
            spell_component=spell_component,
        )

        if not result.success:
            # Spell failed - show error but don't consume turn
            self.message_log.add_message(result.message)
            return CommandResult(success=False, turn_consumed=False)

        # Handle target death from spell damage
        if result.target_died:
            self.combat_system.handle_death(self.target, killed_by_player=True)
            self.target.blocks_movement = False

        # Process turn cycle (status effects and enemy AI)
        game_over = self._process_turn_cycle(
            self.caster,
            self.entities,
            self.ai_system,
            self.combat_system,
            self.status_effects_system,
        )

        return CommandResult(
            success=True, turn_consumed=True, should_quit=game_over
        )
