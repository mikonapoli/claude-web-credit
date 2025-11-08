"""Spell casting commands."""

from typing import List, Optional

from roguelike.commands.command import Command, CommandResult
from roguelike.components.entity import ComponentEntity
from roguelike.components.mana import ManaComponent
from roguelike.components.spells import SpellComponent
from roguelike.magic.spell import Spell, TargetType
from roguelike.systems.ai_system import AISystem
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.magic_system import MagicSystem
from roguelike.systems.status_effects import StatusEffectsSystem
from roguelike.systems.targeting import TargetingSystem
from roguelike.ui.message_log import MessageLog
from roguelike.ui.spell_menu import SpellMenu
from roguelike.world.fov import FOVMap
from roguelike.world.game_map import GameMap


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
            self.combat_system.award_xp(self.caster, self.target.xp_value)
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


class OpenSpellMenuCommand(Command):
    """Command to open the spell menu."""

    def __init__(
        self,
        player: ComponentEntity,
        spell_menu: SpellMenu,
        message_log: MessageLog,
    ):
        """Initialize open spell menu command.

        Args:
            player: Player entity
            spell_menu: Spell menu to open
            message_log: Message log for displaying messages
        """
        self.player = player
        self.spell_menu = spell_menu
        self.message_log = message_log

    def execute(self) -> CommandResult:
        """Open the spell menu."""
        spell_component = self.player.get_component(SpellComponent)

        if not spell_component:
            self.message_log.add_message("You don't know any spells!")
            return CommandResult(success=False, turn_consumed=False)

        spells = spell_component.spells
        if not spells:
            self.message_log.add_message("You don't know any spells!")
            return CommandResult(success=False, turn_consumed=False)

        self.spell_menu.open(spells)
        return CommandResult(
            success=True,
            turn_consumed=False,
            data={"spell_menu_opened": True}
        )


class CloseSpellMenuCommand(Command):
    """Command to close the spell menu."""

    def __init__(self, spell_menu: SpellMenu):
        """Initialize close spell menu command.

        Args:
            spell_menu: Spell menu to close
        """
        self.spell_menu = spell_menu

    def execute(self) -> CommandResult:
        """Close the spell menu."""
        self.spell_menu.close()
        return CommandResult(
            success=True,
            turn_consumed=False,
            data={"spell_menu_closed": True}
        )


class SelectSpellCommand(Command):
    """Command to select a spell from the menu and start targeting."""

    def __init__(
        self,
        player: ComponentEntity,
        spell_menu: SpellMenu,
        targeting_system: TargetingSystem,
        entities: List[ComponentEntity],
        fov_map: FOVMap,
        game_map: GameMap,
        message_log: MessageLog,
    ):
        """Initialize select spell command.

        Args:
            player: Player entity
            spell_menu: Spell menu
            targeting_system: Targeting system for targeted spells
            entities: All entities in game
            fov_map: Field of view map
            game_map: Game map
            message_log: Message log for displaying messages
        """
        self.player = player
        self.spell_menu = spell_menu
        self.targeting_system = targeting_system
        self.entities = entities
        self.fov_map = fov_map
        self.game_map = game_map
        self.message_log = message_log

    def execute(self) -> CommandResult:
        """Select spell and start targeting or cast immediately."""
        from roguelike.components.helpers import is_monster, is_alive

        spell = self.spell_menu.get_selected_spell()

        if not spell:
            return CommandResult(success=False, turn_consumed=False)

        # Close the spell menu
        self.spell_menu.close()

        # Handle self-targeting spells (heal, buffs)
        if spell.target_type == TargetType.SELF:
            # Return data to trigger immediate cast on self
            return CommandResult(
                success=True,
                turn_consumed=False,
                data={
                    "cast_spell_on_self": True,
                    "spell": spell,
                }
            )
        else:
            # Get valid targets (living monsters in FOV)
            valid_targets = [
                e
                for e in self.entities
                if is_monster(e) and is_alive(e) and self.fov_map.is_visible(e.position)
            ]

            if not valid_targets:
                self.message_log.add_message("No visible targets!")
                return CommandResult(success=False, turn_consumed=False)

            # Start targeting mode for targeted spells
            started = self.targeting_system.start_targeting(
                origin=self.player.position,
                max_range=spell.range,
                valid_targets=valid_targets,
                map_width=self.game_map.width,
                map_height=self.game_map.height,
            )

            if started:
                self.message_log.add_message(
                    f"Select target for {spell.name}. [ESC] to cancel."
                )
                return CommandResult(
                    success=True,
                    turn_consumed=False,
                    data={
                        "start_spell_targeting": True,
                        "spell": spell,
                    }
                )
            else:
                self.message_log.add_message("No targets in range!")
                return CommandResult(success=False, turn_consumed=False)
