"""Combat system handling all combat interactions."""

from typing import Optional

from roguelike.engine.events import CombatEvent, DeathEvent, EventBus, LevelUpEvent, XPGainEvent
from roguelike.systems.combat import attack
from roguelike.systems.experience import apply_level_up, check_level_up
from roguelike.utils.protocols import Combatant, Levelable, XPSource


class CombatSystem:
    """Handles combat resolution and related game events."""

    def __init__(self, event_bus: EventBus):
        """Initialize combat system.

        Args:
            event_bus: Event bus for publishing combat events
        """
        self.event_bus = event_bus

    def resolve_attack(
        self,
        attacker: Combatant,
        defender: Combatant,
    ) -> bool:
        """Resolve an attack between two combatants.

        Args:
            attacker: The attacking combatant
            defender: The defending combatant

        Returns:
            True if defender died
        """
        result = attack(attacker, defender)

        # Emit combat event
        self.event_bus.emit(
            CombatEvent(
                attacker_name=result.attacker_name,
                defender_name=result.defender_name,
                damage=result.damage,
                defender_died=result.defender_died,
            )
        )

        return result.defender_died

    def handle_death(
        self,
        victim: XPSource,
        killed_by_player: bool,
    ) -> None:
        """Handle entity death.

        Args:
            victim: Entity that died
            killed_by_player: Whether killed by player
        """
        # Get victim name safely
        victim_name = getattr(victim, "name", "Unknown")

        # Emit death event
        self.event_bus.emit(
            DeathEvent(
                entity_name=victim_name,
                xp_value=victim.xp_value,
                killed_by_player=killed_by_player,
            )
        )

    def award_xp(
        self,
        recipient: Levelable,
        xp_amount: int,
    ) -> Optional[int]:
        """Award XP to an entity and check for level up.

        Applies Lucky Coin bonus if recipient has "lucky" status effect.

        Args:
            recipient: Entity receiving XP
            xp_amount: Amount of XP to award

        Returns:
            New level if level up occurred, None otherwise
        """
        # Check for Lucky Coin bonus (50% XP boost)
        final_xp = xp_amount
        if hasattr(recipient, "_status_effects"):
            effects = recipient._status_effects
            if effects.has_effect("lucky"):
                lucky_power = effects.get_effect("lucky").power
                # Power represents percentage bonus (e.g., 50 = 50% bonus)
                final_xp = xp_amount + int(xp_amount * lucky_power / 100)

        # Award XP
        recipient.xp += final_xp

        # Get recipient name safely
        recipient_name = getattr(recipient, "name", "Unknown")

        # Emit XP gain event (with the final amount after bonuses)
        self.event_bus.emit(
            XPGainEvent(
                entity_name=recipient_name,
                xp_gained=final_xp,
            )
        )

        # Check for level up
        if check_level_up(recipient.xp, recipient.level):
            level_result = apply_level_up(
                recipient,
                {"hp": 20, "power": 1, "defense": 1},
            )

            # Emit level up event
            self.event_bus.emit(
                LevelUpEvent(
                    entity_name=recipient_name,
                    new_level=level_result.new_level,
                    stat_increases={
                        "hp": level_result.hp_increase,
                        "power": level_result.power_increase,
                        "defense": level_result.defense_increase,
                    },
                )
            )

            return level_result.new_level

        return None
