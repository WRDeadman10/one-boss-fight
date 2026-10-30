# KI-151 RESEARCH: LOADOUT SWITCH & ATTACK ACTIONS SPECIFICATION FOR REAL SWINGS

**Author:** Antigravity  
**Date:** 2026-10-31  
**Task:** Lead Order C-465 (Follow-up to Commit Order 12 & -RealSwing Extension)  
**Status:** Complete, 100% Verified Offline Against Engine Source, Pack Blueprints & Driver Scripts  

---

## 1. Executive Summary

To extend the `-RealSwing` PIE driver from the Starter Sword light attack to arbitrary weapons (`Starter`, `Strength`, `Dex`) and attack actions (`Light`, `Strong`, `Charged`, `JumpLight`, `JumpHeavy`):

1. **Loadout Switching:**
   - Execute console command `rpg.Build "<Build>"` (or call `URPGBuildLoadout::SetBuild(Name)`).
   - Poll until `ld.get_actual_style_name() == STYLE[build]` and `ld.get_state_name() == "Idle"` (timeout $\le 20.0\text{ s}$).
   - Verify `ld.has_weapon_ability_for_test(ABILITY[build]) == True`.
   - Activate tag `Ability.EnterCombat` via `BP_AdvancedAbilitySystemComponent_C` to unsheathe the weapon to `WeaponHandSocket` (wait $1.0\text{ s}$).

2. **Attack Injection:**
   - Ground attacks: Inject action (or set key down) for `press_seconds` ($0.12\text{ s}$ tap, or $1.6\text{ s}$ for charged).
   - Airborne attacks (`JumpLight`, `JumpHeavy`): Press jump key `Gamepad_FaceButton_Bottom` (or `SpaceBar`) for $0.12\text{ s}$, wait $0.30\text{ s}$ for lift-off, then inject attack action.

3. **Attack Capabilities (`CAPS`):**
   - Starter Sword (`SwordCombatStyle`): All 5 attacks supported.
   - Claymore (`ClaymoreCombatStyle`): All 5 attacks supported.
   - Dual Swords (`DualSwordCombatStyle`): Light, Strong, JumpLight, JumpHeavy supported; **Charged is FALSE** (no charged montage exists in pack; attempting charged attack performs default light or no-op).

---

## 2. Loadout Switch Flow & Wait Criteria

### 2.1 Triggering the Loadout Switch
In [Scripts/Editor/pie_builds.py:2-9,115-125](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_builds.py#L2-L9) and [Scripts/Editor/pie_build_fight.py:1260-1275](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_build_fight.py#L1260-L1275):
- **Console Variable:** `rpg.Build` is process-wide and persists across PIE restarts.
- **Python Execution:**
  ```python
  # Via Console Command:
  unreal.SystemLibrary.execute_console_command(world, 'rpg.Build "%s"' % build_name)
  # Or via C++ Component Method directly on pawn:
  ld = pawn.get_component_by_class(unreal.RPGBuildLoadout)
  ld.set_build(build_name)
  ```

### 2.2 Loadout Specification Constants
From [Scripts/Editor/pie_builds.py:23-26](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_builds.py#L23-L26) and [Scripts/Editor/pie_build_fight.py:72-75](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_build_fight.py#L72-L75):

| Build Name | Combat Style Asset (`STYLE`) | Weapon Ability (`ABILITY`) | Weapon Actor Class (`ACTOR`) | HUD Line (`LINE`) |
|---|---|---|---|---|
| **Starter** | `SwordCombatStyle` | `GA_Sword_Melee_C` | `BP_ToughSword_C` | `Build: Starter (Sword)` |
| **Strength** | `ClaymoreCombatStyle` | `GA_Claymore_Melee_C` | `BP_KwangSword_C` | `Build: Strength (Claymore)` |
| **Dex** | `DualSwordCombatStyle` | `GA_DuaSword_Melee_C` *(note pack typo)* | `BP_DualSteelSwords_C` | `Build: Dex (Dual Swords)` |

### 2.3 Required Wait Loop & Readiness Assertions
From [Scripts/Editor/pie_build_fight.py:1263-1270](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_build_fight.py#L1263-L1270) and [Source/OneBossFight/Player/RPGBuildLoadout.h:71-76](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBuildLoadout.h#L71-L76):
```python
# Wait up to 20.0 seconds for loadout to apply and settle to Idle
t0 = time.time()
while time.time() - t0 < 20.0:
    if ld.get_actual_style_name() == STYLE[build_name] and ld.get_state_name() == "Idle":
        break
    yield dt

assert ld.get_actual_style_name() == STYLE[build_name], "Combat style mismatch"
assert ld.get_state_name() == "Idle", "Loadout did not settle to Idle"
assert ld.has_weapon_ability_for_test(ABILITY[build_name]), "Weapon ability missing on ASC"
assert ld.get_chosen_build_name() == build_name, "Chosen build name mismatch"
```

### 2.4 Drawing Weapon (`Ability.EnterCombat`)
- Once the loadout is `Idle`, the weapon is initially sheathed (`DisabledSocket`).
- The driver MUST activate `Ability.EnterCombat` via `BP_AdvancedAbilitySystemComponent_C` ([pie_hit_intake.py:85](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_hit_intake.py#L85), [pie_build_fight.py:1282](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_build_fight.py#L1282)):
  ```python
  asc = comp(pawn, "BP_AdvancedAbilitySystemComponent_C")
  asc.call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
  ```
- Wait $\approx \mathbf{1.0\text{ s}}$ for the equip/draw montage to complete before injecting attacks.

---

## 3. Attack Actions, Inputs, Timings & Delays

### 3.1 Input Actions & Hold Durations
From [Scripts/Editor/pie_builds.py:40-47](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_builds.py#L40-L47) and [Scripts/Editor/pie_build_fight.py:89-96](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_build_fight.py#L89-L96):

| Attack Kind | Input Action Asset (`IA`) | Key / Button | Hold Duration | Jump First? |
|---|---|---|---|---|
| **Light** | `IA_NormalAttack.uasset` | `LeftMouseButton` / `Gamepad_FaceButton_Left` | $0.12\text{ s}$ | False |
| **Strong** | `IA_StrongAttack.uasset` | `RightMouseButton` / `Gamepad_FaceButton_Top` | $0.12\text{ s}$ | False |
| **Charged** | `IA_ChargedAttack.uasset` | `RightMouseButton` (Held) | $1.60\text{ s}$ | False |
| **JumpLight** | `IA_NormalAttack.uasset` | `LeftMouseButton` in air | $0.12\text{ s}$ | True (after $0.30\text{ s}$ jump) |
| **JumpHeavy** | `IA_StrongAttack.uasset` | `RightMouseButton` in air | $0.12\text{ s}$ | True (after $0.30\text{ s}$ jump) |

### 3.2 Jump Injection Protocol
For `JumpLight` and `JumpHeavy` ([Scripts/Editor/pie_hit_intake.py:126-140](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_hit_intake.py#L126-L140)):
1. $t = 0.0\text{ s}$: `unreal.RPGInputTestUtils.set_key_down(pc, "Gamepad_FaceButton_Bottom", True)`
2. $t = 0.12\text{ s}$: `unreal.RPGInputTestUtils.set_key_down(pc, "Gamepad_FaceButton_Bottom", False)`
3. $t = 0.30\text{ s}$ (character airborne, $Z$ velocity positive):
   `unreal.RPGInputTestUtils.inject_action(pc, action, Vector(1, 0, 0))` for $0.12\text{ s}$.

### 3.3 Contact Latency Table (`HIT_DELAY`)
From [Scripts/Editor/pie_build_fight.py:98](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_build_fight.py#L98):
- **Light:** $0.34\text{ s}$ from key press to first physical hit.
- **Strong:** $0.69\text{ s}$ from key press to first physical hit.
- **Charged:** $1.90\text{ s}$ from key press to first physical hit.
- **JumpLight:** $0.55\text{ s}$ from jump key press ($0.25\text{ s}$ after attack key press).
- **JumpHeavy:** $0.85\text{ s}$ from jump key press ($0.55\text{ s}$ after attack key press).

---

## 4. Master Specification Matrix (Build $\times$ Action)

The authoritative values below are extracted directly from [Source/OneBossFight/Player/RPGWeaponAttackTable.cpp:44-106](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGWeaponAttackTable.cpp#L44-L106) (`DA_WeaponAttacks`) and [Scripts/Editor/pie_builds.py:28-48](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_builds.py#L28-L48):

| Build | Weapon Style | Attack Kind | Supported (`CAPS`) | Input Action | Hold Time | Posture Damage | Bleed Buildup | Health Multiplier | Expected Damage ($100 \times \text{Mult}$) | Stamina Cost | Hyperarmor Window |
|---|---|---|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **Starter** | `SwordCombatStyle` | **Light** | YES | `IA_NormalAttack` | $0.12\text{ s}$ | **18.0** | **0.0** | **0.39** | **39.0** | 15.0 | None |
| **Starter** | `SwordCombatStyle` | **Strong** | YES | `IA_StrongAttack` | $0.12\text{ s}$ | **30.0** | **0.0** | **0.39** | **39.0** | 15.0 | None |
| **Starter** | `SwordCombatStyle` | **Charged** | YES | `IA_ChargedAttack` | $1.60\text{ s}$ | **38.0** | **0.0** | **0.39** | **39.0** | 15.0 | None |
| **Starter** | `SwordCombatStyle` | **JumpLight** | YES | `IA_NormalAttack` | $0.12\text{ s}$ (jump) | **18.0** | **0.0** | **0.39** | **39.0** | 15.0 | None |
| **Starter** | `SwordCombatStyle` | **JumpHeavy** | YES | `IA_StrongAttack` | $0.12\text{ s}$ (jump) | **38.0** | **0.0** | **0.39** | **39.0** | 15.0 | None |
| **Strength** | `ClaymoreCombatStyle` | **Light** | YES | `IA_NormalAttack` | $0.12\text{ s}$ | **18.0** | **0.0** | **1.00** | **100.0** | 15.0 | None |
| **Strength** | `ClaymoreCombatStyle` | **Strong** | YES | `IA_StrongAttack` | $0.12\text{ s}$ | **30.0** | **0.0** | **1.00** | **100.0** | 35.0 | $0.352 - 0.618\text{ s}$ (`Ability_E`) |
| **Strength** | `ClaymoreCombatStyle` | **Charged** | YES | `IA_ChargedAttack` | $1.60\text{ s}$ | **38.0** | **0.0** | **1.00** | **100.0** | 35.0 | $0.423 - 1.005\text{ s}$ (`ChargedAttack`) |
| **Strength** | `ClaymoreCombatStyle` | **JumpLight** | YES | `IA_NormalAttack` | $0.12\text{ s}$ (jump) | **18.0** | **0.0** | **1.00** | **100.0** | 15.0 | None |
| **Strength** | `ClaymoreCombatStyle` | **JumpHeavy** | YES | `IA_StrongAttack` | $0.12\text{ s}$ (jump) | **38.0** | **0.0** | **1.00** | **100.0** | 35.0 | $0.352 - 0.618\text{ s}$ (`Ability_E`) |
| **Dex** | `DualSwordCombatStyle` | **Light** | YES | `IA_NormalAttack` | $0.12\text{ s}$ | **6.0** | **20.0** | **1.00** | **100.0** | 10.0 | None *(blades merged in Pending)* |
| **Dex** | `DualSwordCombatStyle` | **Strong** | YES | `IA_StrongAttack` | $0.12\text{ s}$ | **10.0** | **20.0** | **1.00** | **100.0** | 10.0 | None |
| **Dex** | `DualSwordCombatStyle` | **Charged** | **NO** | `IA_ChargedAttack` | $1.60\text{ s}$ | *(14.0)* | *(20.0)* | *(1.00)* | *(100.0)* | *(10.0)* | **UNSUPPORTED** (`CAPS=False`) |
| **Dex** | `DualSwordCombatStyle` | **JumpLight** | YES | `IA_NormalAttack` | $0.12\text{ s}$ (jump) | **6.0** | **20.0** | **1.00** | **100.0** | 10.0 | None |
| **Dex** | `DualSwordCombatStyle` | **JumpHeavy** | YES | `IA_StrongAttack` | $0.12\text{ s}$ (jump) | **14.0** | **20.0** | **1.00** | **100.0** | 10.0 | None |

> [!NOTE]
> 1. **Starter Health Multiplier:** Defined as `0.39f` in `RPGWeaponAttackTable.cpp:66-73` (KI-097 calibration). Against base hit profile ($100.0$ damage), Starter hits deal $39.0$ damage. Both Strength and Dex default to `HealthDamageMultiplier = 1.0f` ($100.0$ damage).
> 2. **Dex Dual Blade Merging:** Dex light swings strike with 2 blades in the same frame. `FinalizePending` merges the duplicate montage hit ([RPGHitIntake.cpp:521-526](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp#L521-L526)), applying Posture ($6.0$) and Bleed ($20.0$) exactly once per swing.
> 3. **Dex Charged Attack:** Marked `False` in `CAPS["Dex"]["Charged"]` ([pie_builds.py:38](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_builds.py#L38)). The pack character has no charged montage for dual swords.
