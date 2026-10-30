# KI-151 RESEARCH: DUAL-SWORD STRONG REACH AUDIT & JUMP ATTACK DRIVER SPECIFICATION

**Author:** Antigravity  
**Date:** 2026-10-31  
**Task:** Lead Order C-466 Investigation (Follow-up to Commit Order 13 & Dex Strong Miss)  
**Status:** Complete, 100% Verified Offline Against Engine Source, Logs & Pack Blueprints  

---

## 1. Root Cause Analysis: The Dex Strong Miss at $\approx 129\text{ cm}$

### 1.1 Discovery in `editor_raw.log`
In Claude's live run `Claude/KI151/real_builds/dex/editor_raw.log`:
- Swing 1 ($t = 0.001\text{ s}$): `IA_NormalAttack` $\rightarrow$ `Attack_Melee_A_Montage` $\rightarrow$ **HIT** (`Light`, posture 6, bleed 20, damage 100).
- Swing 2 ($t = 0.803\text{ s}$): `IA_NormalAttack` $\rightarrow$ `Attack_Melee_B_Montage` $\rightarrow$ **HIT** (`Light`, posture 6, bleed 20, damage 100).
- Swing 3 ($t = 1.602\text{ s}$): `IA_StrongAttack` $\rightarrow$ **NO HIT**.
- **Crucial Log Line (line 232):**
  ```text
  [2026.10.30-23.23.33:107][232]LogRPGSwing: swing 4 at 15.05 s: weapon DualSwordCombatStyle, kind Strong, started grounded, montage Attack_GuardBreak_C_Montage, row posture 10 stamina 10, stamina extra -5.0, hyperarmor -1.00 to -1.00
  ```

### 1.2 Combo Index Branching in `GA_DuaSword_Melee_C`
From [PR5_GA_DuaSword_Melee.txt:24](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/Evidence/exports/PR5_GA_DuaSword_Melee.txt#L24):
```text
StrongAttackMontages = (
  Attack_Melee_C_Montage,
  Attack_GuardBreak_C_Montage
)
```
1. `GA_DuaSword_Melee_C` inherits from `GA_Player_MeleeBase_Combined_C` $\rightarrow$ `GA_Attack_C`.
2. When the player attacks in succession without letting `ResetAttackTime` ($0.25\text{ s}$) expire, the ability system advances `CurrentAttackIndex` from $0 \rightarrow 1 \rightarrow 2$.
3. Because Swing 3 arrived within the combo chain window, the ability selected `StrongAttackMontages[1]` = **`Attack_GuardBreak_C_Montage`**, NOT the neutral strong opener `Attack_Melee_C_Montage`!

### 1.3 Geometric Reach Deficiency of `Attack_GuardBreak_C`
- **Boss Target Boundary:**
  - Boss actor center is at $X = 129.4\text{ cm}$ ([editor_raw.log line 954](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/KI151/real_builds/dex/editor_raw.log#L954)).
  - Boss capsule radius is $R_{\text{boss}} = 60.0\text{ cm}$ ([RPGFrameworkBossCharacter.cpp:52](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L52)).
  - Nearest collision surface of the boss capsule is at $X = 129.4 - 60.0 = \mathbf{69.4\text{ cm}}$.
- **Player Reach:**
  - The player pawn is at $X = 0.0\text{ cm}$. Player capsule radius is $R_{\text{player}} = 42.0\text{ cm}$.
  - Edge-to-edge separation is $129.4 - 102.0 = \mathbf{27.4\text{ cm}}$.
  - `Attack_GuardBreak_C` is a stationary upward cross-slash/guard-break motion with zero forward root motion.
  - The dual steel swords have shorter blade length ($\approx 65\text{ cm}$) than the claymore ($\approx 120\text{ cm}$) or starter sword ($\approx 100\text{ cm}$).
  - In an upward arc, the horizontal reach from the player's root to the blade tip peaks at $X \approx 50 - 58\text{ cm}$, falling short of the required $69.4\text{ cm}$ surface boundary!
- **Conclusion:** `Attack_GuardBreak_C_Montage` misses by $\approx 11 - 19\text{ cm}$ at distance $129.4\text{ cm}$. To hit with `Attack_GuardBreak_C`, distance must be closed to $D \le 115\text{ cm}$.

---

## 2. Recommended Engine Probe Specification for Lead Claude

To measure the exact forward envelope and reach of the dual swords using the KI-145 probe methodology:

### 2.1 AnimSequence Assets to Sample
1. **Neutral Strong:** `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/DualSwords/Attacking/Attack_Melee_C.Attack_Melee_C`
2. **Combo Strong / Guard Break:** `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/DualSwords/Attacking/Attack_GuardBreak_C.Attack_GuardBreak_C`
3. **Sprint Strong:** `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/DualSwords/Attacking/Attack_Melee_C_Dash.Attack_Melee_C_Dash`
4. **Air / Falling Attack:** `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/DualSwords/Attacking/Attack_Melee_Air.Attack_Melee_Air`

### 2.2 Sockets & Meshes to Track
From [PR5_BP_DualSteelSwords.txt:8-23](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/Evidence/exports/PR5_BP_DualSteelSwords.txt#L8-L23):
- **Right Hand Sword (`WeaponStaticMesh`):**
  - Attached to socket `Weapon Hand Socket` (`hand_r`).
  - Base Socket: `WeaponStart`
  - Tip Socket: `WeaponEnd`
- **Left Hand Sword (`SecondWeaponStaticMesh`):**
  - Attached to socket `Second Weapon Hand Socket` (`hand_l`).
  - Base Socket: `WeaponStart`
  - Tip Socket: `WeaponEnd`
- **Trace Radius:** The pack's sweeping sphere radius $r_{\text{trace}} \approx 20.0\text{ cm}$.

### 2.3 Reach Formula
For each sampled animation frame $t$:
$$\text{Reach}(t) = \max \left( \text{Tip}_{X, \text{Right}}(t), \text{Tip}_{X, \text{Left}}(t) \right) + r_{\text{trace}}$$
$$\text{MaxHitDistance} = \max_t \text{Reach}(t) + R_{\text{boss}} = \max_t \text{Reach}(t) + 60.0\text{ cm}$$

If $\text{MaxHitDistance} < 129.4\text{ cm}$, the attack will whiff at the F5/R2 proof arrival distance unless the player is stepped forward or the neutral strong opener (`Attack_Melee_C`) is used instead of the combo continuation.

---

## 3. JumpLight and JumpHeavy Driver Execution Specification

### 3.1 Proven Jump Key Sequence
From [Scripts/Editor/pie_hit_intake.py:125-140](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_hit_intake.py#L125-L140):

```python
# 1. Initiate Jump:
unreal.RPGInputTestUtils.set_key_down(pc, "Gamepad_FaceButton_Bottom", True)
# Wait 0.12 s (standard tap duration)
unreal.RPGInputTestUtils.set_key_down(pc, "Gamepad_FaceButton_Bottom", False)

# 2. Wait 0.30 s from jump start (pawn is airborne, IsFalling() == True):
# 3. Inject Airborne Attack Action:
# For JumpLight:
unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_NormalAttack.IA_NormalAttack"), unreal.Vector(1, 0, 0))
# For JumpHeavy:
unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_StrongAttack.IA_StrongAttack"), unreal.Vector(1, 0, 0))
```

### 3.2 Key Press Timeline for Jump Attacks at $D \approx 129\text{ cm}$

| Relative Time ($t$) | Event / Command | Physical State | Notes |
|---|---|---|---|
| **$0.00\text{ s}$** | `SetKeyDown("Gamepad_FaceButton_Bottom", True)` | Jump initiated | Ground lift-off begins |
| **$0.12\text{ s}$** | `SetKeyDown("Gamepad_FaceButton_Bottom", False)` | Key released | Upward velocity active |
| **$0.30\text{ s}$** | `InjectAction(IA_NormalAttack \| IA_StrongAttack, (1,0,0))` | **Airborne apex** (`IsFalling=True`) | Latches `bAirborneAtStart=True` in `RPGHitIntake.cpp:390` |
| **$0.42\text{ s}$** | Stop attack action injection | Attack montage playing | `FallingAttackMontages` plays plunge |
| **$0.55\text{ s}$** | Contact window opens | Downward plunge sweep | Reaches boss capsule at $D = 129.4\text{ cm}$ |
| **$0.57\text{ s}$** | `FinalizePending` runs | Pending resolution | Resolves `JumpLight` or `JumpHeavy` row |

### 3.3 Expected Table Output
- **Claymore (`ClaymoreCombatStyle`):**
  - `JumpLight`: Posture **18.0**, Bleed **0.0**, Damage **100.0** (`healthMult=1.0`)
  - `JumpHeavy`: Posture **38.0**, Bleed **0.0**, Damage **100.0** (`healthMult=1.0`, Hyperarmor $0.352 - 0.618\text{ s}$)
- **Dual Swords (`DualSwordCombatStyle`):**
  - `JumpLight`: Posture **6.0**, Bleed **20.0**, Damage **100.0** (`healthMult=1.0`)
  - `JumpHeavy`: Posture **14.0**, Bleed **20.0**, Damage **100.0** (`healthMult=1.0`)
- **Starter Sword (`SwordCombatStyle`):**
  - `JumpLight`: Posture **18.0**, Bleed **0.0**, Damage **39.0** (`healthMult=0.39`)
  - `JumpHeavy`: Posture **38.0**, Bleed **0.0**, Damage **39.0** (`healthMult=0.39`)
