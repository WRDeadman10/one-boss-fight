# Advanced ARPG Combat System V3: inspection (2026-10-19)

Source: `C:\Users\winss\Documents\Unreal Projects\Unreal Assets\Advanced ARPG Combat System V3 - Unreal Engine\`
(a complete UE 5.5 project, `AdvancedARPGCF.uproject`). Inspected by reading file names, config and the `/Script/...`
modules each asset references. No Blueprint graph was opened, so behaviour below comes from asset names and tags, not from
playing the demo map. Creator and licence are not recorded in the download (see `ASSET_LICENSES.md`).

## What it is

- Blueprint-only project: no `Source/` folder, 2,653 assets, 3.2 GB (about 2.4 GB of that is demo VFX and material layers).
- Plugins used: EnhancedInput, CommonUI, GameplayTags, AIModule. It does **not** use Epic's GameplayAbilities plugin: the
  ability, effect, cue and attribute system is its own Blueprint implementation (`BP_AdvancedAbilitySystemComponent`,
  `BP_GameplayEffect`, `BP_AttributesComponent`).
- Setup that travels with it: four gameplay tag tables registered in `Config/DefaultGameplayTags.ini`, a trace channel
  `Interactable` (GameTraceChannel1), input mapping `IMC_AdvancedControls` (29 actions), and its own game mode, game instance,
  player controller and player character (`BP_AdvancedGameMode`, `BP_AdvancedGameInstance`, `BP_AdvancedPlayerController`,
  `BP_CombatPlayerCharacter`).

## What is in it

| Area | Contents (from asset names and tags) |
|---|---|
| Framework (36 MB) | Ability system (abilities, effects with stacking and duration policies, cues, ability tasks, anim notifies to activate or end abilities), attributes (Health, Stamina, Mana, damage, resist, crit, level curve), data-driven combat styles, weapon traces (sweeping socket traces), input buffer, a Blueprint state machine, targeting and lock-on UI, camera modes, interaction, inventory and equipment |
| Melee | Sword, sword and shield, dual swords, twinblades, claymore, polearm, unarmed with shield. Guard block, parry, dodge, dodge attack, charged and strong attacks, falling attack, backstab, fatality and assassination, "punisher" and "focus" stances, hit stun, knockdown, guard-break, poison |
| Enemy AI | Behaviour trees plus a behaviour state machine (patrol, follow, reposition, retaliate, parried, heal), aggression curve, enemy info data assets. Examples: sword enemy, axe enemy, **two bosses** (great sword boss, sword and shield boss) with close, mid, far, rare, leap, sprint and retaliation abilities |
| Souls-like layer | Souls currency and "souls retrieved" widgets, bonfire (rest and selection menu), vendor (buy and sell), loot chests, pick-ups, potions, accessories, armor pieces, quick slots, save game data |
| UI (CommonUI) | Main HUD, boss HUD, enemy health bars, inventory (grid, details, drop, sell), equipment window with character preview, quick slots, pause, options, settings, controls (keyboard and gamepad), confirmation and message popups, lock-on marker, Cinzel font |
| Magic | Fireball, flameblast, cosmic rift, burden, light dart, replenishment, mana, catalyst weapon, aim offsets. About 1.5 GB of demo VFX (FengMao alone 860 MB) |
| Ranged | Bow, draw and release, reload, rain of arrows, poison arrows, aim offsets |
| Animation | About 235 animations and montages (Paragon-derived locomotion and attacks) on the **UE5 combat mannequin**, with anim layer Blueprints per weapon type |
| Characters | `SKM_CombatMannequin`, `SKM_Quinn` and a few armor pieces only |
| Demo | `CombatSystemTestLevel` (greybox), demo room, material layers |

## What it does not contain

The request listed several features that are not in this pack:

- **Poise.** No poise attribute, no stagger meter (searched names and asset contents). Hit reactions use hit stun, a
  `HitStunImmune` status and guard-break instead. Our poise and stagger rules would have to be rebuilt on its attributes.
- **Crafting**, **dialogue and NPC talk**, **quests**: none (the only "Blacksmith" hit is a string inside the vendor).
- **Greystone, Sevarog or any other character mesh.** The only characters are the mannequin and armor pieces.
- Boss phases: the example bosses have ability sets and a behaviour tree, but no phase or health-threshold logic by name.

## Fit with the project as it stands

| Topic | Our project (M3 to M7) | The pack |
|---|---|---|
| Combat core | C++ components, one damage path, 26 automation tests | Blueprint ability system, no tests |
| Decision on file | Custom C++ combat, no GAS (locked in `DECISIONS.md`) | A Blueprint GAS-style framework |
| Player | Greystone (Paragon skeleton) | UE5 mannequin; all anim layers target it |
| Boss | Sevarog, weighted C++ selector plus a thin StateTree | Behaviour tree plus state machine, mannequin bosses |
| UI | UMG built in C++ (HUD, pause, settings) | CommonUI widgets |
| Performance target | 120 FPS at 1080p on an RTX 2060 Super | Unmeasured; Blueprint ticks, behaviour trees and CommonUI are all extra cost |

## Ways to use it

1. **Pack as the backbone (staged).** Import the framework, melee system, inventory, UI and AI at their original paths, add
   the tag tables, trace channel and input mapping, and make its game mode the default. Then bring Greystone and Sevarog in on
   top (retarget the anim layers, wire Sevarog's montages as abilities) and retire our C++ combat only after parity is shown.
   Gains everything in the tables above. Costs: our combat, boss AI and most M3 to M7 work and tests are replaced, poise has to
   be added, and the performance gate is a risk we cannot judge until it runs.
2. **Hybrid.** Keep our combat and boss. Bring over only what we lack and that does not depend on its ability system:
   inventory and equipment, loot, vendor, bonfire and souls, save game, pause and options menus, item icons. Lowest risk; the
   inventory widgets need their components (`BP_InventoryComponent`, `BP_EquipmentComponent`) and an attributes source, so a thin
   bridge to our attribute component is needed.
3. **Reference only** (what has been done so far): sounds, font and materials were taken.

## Before either path starts

- Run its demo map once in its own project to see the real behaviour (not done: first open compiles a very large shader set).
- Check its licence and creator (unknown).
- Decide whether Greystone and Sevarog stay (needs retargeting) or the mannequin and the pack's example bosses replace them.
