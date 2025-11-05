# Equipment System

The equipment system allows players to equip weapons, armor, and other items to enhance their combat effectiveness. Equipment provides stat bonuses that directly modify the player's power, defense, and maximum HP.

## Overview

- **24 Equipment Items**: Diverse selection of weapons, armor, helmets, boots, gloves, rings, and amulets
- **7 Equipment Slots**: Each slot can hold one item at a time
- **Stat Bonuses**: Items provide power, defense, and max HP bonuses
- **Seamless Management**: Equip from inventory, unequip back to inventory
- **Auto-Swapping**: Equipping a new item in an occupied slot automatically returns the old item to inventory

## Equipment Slots

1. **Weapon** - Primary offensive equipment
2. **Armor** - Body armor for defense
3. **Helmet** - Head protection
4. **Boots** - Footwear
5. **Gloves** - Hand protection
6. **Ring** - Magical ring
7. **Amulet** - Neck jewelry

## Stat Bonuses

Equipment can provide three types of stat bonuses:

- **Power Bonus**: Increases attack damage dealt to enemies
- **Defense Bonus**: Reduces damage taken from enemy attacks
- **Max HP Bonus**: Increases maximum health points

Bonuses are immediately applied when equipping and removed when unequipping. HP percentage is maintained when max HP changes from equipment.

## Complete Equipment List

### Weapons

Weapons increase your attack power, allowing you to deal more damage to enemies.

| Item | Symbol | Power | Defense | Max HP | Notes |
|------|--------|-------|---------|--------|-------|
| Wooden Club | `\` | +2 | 0 | 0 | Basic starting weapon |
| Iron Sword | `/` | +3 | 0 | 0 | Reliable early weapon |
| Steel Sword | `/` | +5 | 0 | 0 | Strong mid-game weapon |
| Enchanted Blade | `/` | +7 | +1 | 0 | Powerful with minor defense |
| Battle Axe | `/` | +8 | -1 | 0 | Highest damage, defense penalty |

### Armor

Armor provides defense, reducing incoming damage from enemies.

| Item | Symbol | Power | Defense | Max HP | Notes |
|------|--------|-------|---------|--------|-------|
| Leather Armor | `[` | 0 | +2 | 0 | Light armor, basic protection |
| Chainmail | `[` | 0 | +4 | 0 | Medium armor, good defense |
| Plate Armor | `[` | 0 | +6 | +5 | Heavy armor with HP bonus |
| Dragon Scale Armor | `[` | +1 | +8 | +10 | Legendary armor, best overall |

### Helmets

Helmets provide defense and often increase maximum HP.

| Item | Symbol | Power | Defense | Max HP | Notes |
|------|--------|-------|---------|--------|-------|
| Leather Helmet | `^` | 0 | +1 | +2 | Basic head protection |
| Steel Helmet | `^` | 0 | +2 | +5 | Strong head protection |
| Crown of Kings | `^` | +2 | +3 | +10 | Legendary helm with power |

### Boots

Boots provide mobility and some protection.

| Item | Symbol | Power | Defense | Max HP | Notes |
|------|--------|-------|---------|--------|-------|
| Leather Boots | `]` | 0 | +1 | 0 | Basic footwear |
| Steel Boots | `]` | +1 | +2 | 0 | Armored boots with power |
| Boots of Speed | `]` | 0 | +1 | +5 | Enchanted boots with HP |

### Gloves

Gloves enhance your attack power and provide some defense.

| Item | Symbol | Power | Defense | Max HP | Notes |
|------|--------|-------|---------|--------|-------|
| Leather Gloves | `)` | +1 | 0 | 0 | Basic hand protection |
| Gauntlets | `)` | +2 | +1 | 0 | Armored gloves |

### Rings

Magical rings provide focused bonuses.

| Item | Symbol | Power | Defense | Max HP | Notes |
|------|--------|-------|---------|--------|-------|
| Ring of Power | `=` | +3 | 0 | 0 | Offensive ring |
| Ring of Protection | `=` | 0 | +3 | 0 | Defensive ring |
| Ring of Vitality | `=` | 0 | 0 | +15 | Health ring |

### Amulets

Powerful neck items with strong focused bonuses.

| Item | Symbol | Power | Defense | Max HP | Notes |
|------|--------|-------|---------|--------|-------|
| Amulet of Strength | `"` | +4 | 0 | 0 | Highest power amulet |
| Amulet of Defense | `"` | 0 | +4 | 0 | Highest defense amulet |
| Amulet of Life | `"` | 0 | 0 | +20 | Highest HP amulet |

## How to Use Equipment

### Equipping Items

1. **Pick up** equipment from the ground using `g`
2. **Open inventory** with `i` to view your items
3. **Equip item** using `e` and select the item
4. If the slot is occupied, the old item automatically returns to inventory

### Unequipping Items

1. **Unequip** using `u` and select the slot
2. The item returns to your inventory (if there's space)
3. Your stats are updated to remove the bonuses

### Replacing Equipment

When you equip a new item in an already-occupied slot:
- The old item is automatically unequipped
- The old item returns to your inventory
- The new item's bonuses replace the old bonuses

## Equipment Strategies

### Early Game (Dungeon Level 1-2)

Focus on finding any equipment to survive:
- **Weapon**: Iron Sword or Wooden Club
- **Armor**: Leather Armor
- **Helmet**: Leather Helmet
- **Boots**: Leather Boots
- **Total Bonuses**: ~+5 power, ~+4 defense, ~+2 HP

### Mid Game (Dungeon Level 3-4)

Upgrade to stronger equipment:
- **Weapon**: Steel Sword
- **Armor**: Chainmail
- **Helmet**: Steel Helmet
- **Boots**: Steel Boots
- **Gloves**: Gauntlets
- **Ring**: Ring of Power or Ring of Protection
- **Total Bonuses**: ~+10 power, ~+10 defense, ~+5 HP

### Late Game (Dungeon Level 5+)

Aim for the best equipment:
- **Weapon**: Enchanted Blade or Battle Axe
- **Armor**: Dragon Scale Armor
- **Helmet**: Crown of Kings
- **Boots**: Boots of Speed
- **Gloves**: Gauntlets
- **Ring**: Ring of Vitality
- **Amulet**: Amulet of Strength or Amulet of Life
- **Total Bonuses**: ~+15 power, ~+15 defense, ~+40 HP

### Build Strategies

**Glass Cannon** (High offense, lower defense):
- Battle Axe (+8/-1)
- Leather Armor (+2)
- Ring of Power (+3)
- Amulet of Strength (+4)
- **Total**: +15 power, +1 defense

**Tank** (High defense, moderate offense):
- Steel Sword (+5)
- Dragon Scale Armor (+1/+8/+10)
- Crown of Kings (+2/+3/+10)
- Ring of Protection (+3)
- Amulet of Defense (+4)
- **Total**: +8 power, +18 defense, +20 HP

**Balanced** (Good mix of all stats):
- Enchanted Blade (+7/+1)
- Plate Armor (+6/+5)
- Steel Helmet (+2/+5)
- Steel Boots (+1/+2)
- Gauntlets (+2/+1)
- Ring of Vitality (+15)
- Amulet of Life (+20)
- **Total**: +10 power, +12 defense, +45 HP

## Technical Architecture

### Components

**EquipmentComponent**
- Manages equipment slots for an entity
- Tracks equipped items by slot
- Calculates total stat bonuses from all equipment

**EquipmentStats**
- Component for equipment items
- Stores slot type and stat bonuses
- Defines which slot an item occupies

### Systems

**EquipmentSystem**
- Handles equip/unequip operations
- Applies/removes stat bonuses to combat and health components
- Emits events for equipment changes
- Maintains HP percentage when max HP changes

### Commands

**EquipItemCommand**
- Removes item from inventory
- Equips item to appropriate slot
- Returns previously equipped item to inventory
- Consumes a turn

**UnequipItemCommand**
- Removes item from equipment slot
- Adds item back to inventory
- Checks for inventory space
- Consumes a turn

### Events

**EquipEvent**
- Emitted when an item is equipped
- Contains entity name, item name, slot, and bonuses
- Used for UI feedback (message log)

**UnequipEvent**
- Emitted when an item is unequipped
- Contains entity name, item name, and slot
- Used for UI feedback (message log)

## Integration with Game Systems

### Combat System

Equipment bonuses are applied directly to the CombatComponent:
- Power bonus increases attack damage
- Defense bonus reduces incoming damage
- Works seamlessly with existing combat calculations

### Health System

Max HP bonuses are applied to the HealthComponent:
- HP percentage is maintained when equipping/unequipping
- Prevents HP loss from equipping items
- Clamps current HP to new max when unequipping

### Inventory System

Equipment integrates with inventory:
- Items must be in inventory to equip
- Unequipped items return to inventory
- Requires inventory space for unequipping
- Automatically manages swapping equipped items

## Testing

The equipment system has **67 passing tests** covering:

- **EquipmentComponent (29 tests)**: Slot management, stat calculations, equip/unequip operations
- **EquipmentSystem (22 tests)**: Stat bonus application, event emission, HP management
- **EquipmentCommands (16 tests)**: Inventory integration, turn consumption, error handling

All tests follow the "one assertion per test" principle for immediate failure diagnosis.

## Future Enhancements

Potential additions to the equipment system:

- **Set Bonuses**: Additional bonuses for wearing matching equipment sets
- **Equipment Durability**: Items degrade with use and require repair
- **Cursed Equipment**: Items that can't be unequipped without special means
- **Enchanting System**: Add magical properties to equipment
- **Equipment Upgrades**: Improve equipment with materials
- **Legendary Items**: Extremely rare items with unique abilities
- **Equipment Requirements**: Level or stat requirements to equip items
- **Two-Handed Weapons**: Weapons that occupy multiple slots

## Data-Driven Design

Equipment is defined in `src/roguelike/data/entities.json`:

```json
{
  "iron_sword": {
    "char": "/",
    "name": "Iron Sword",
    "blocks_movement": false,
    "components": {
      "equipment": {
        "slot": "weapon",
        "power_bonus": 3,
        "defense_bonus": 0,
        "max_hp_bonus": 0
      }
    }
  }
}
```

This makes it easy to:
- Add new equipment items
- Balance existing equipment
- Create equipment variants
- Mod the game with custom equipment

## Credits

The equipment system was designed following roguelike best practices:
- **NetHack**: Classic equipment slot system
- **DCSS**: Streamlined equipment management
- **Brogue**: Clear stat bonuses and immediate feedback
- **Diablo**: Build diversity through equipment choices

The system maintains the game's clean architecture with:
- Component-based design
- Event-driven communication
- Data-driven content
- Comprehensive testing
- Clear separation of concerns
