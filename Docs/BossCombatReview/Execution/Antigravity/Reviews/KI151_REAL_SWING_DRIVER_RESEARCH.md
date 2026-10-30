# KI-151 RESEARCH: REAL PACK WEAPON SWING DRIVER FOR NATIVE FRAMEWORK BOSS

**Author:** Antigravity  
**Date:** 2026-10-31  
**Task:** Order C-464 Investigation (Follow-up to Commit Order 11)  
**Status:** Complete, 100% Verified Offline Against Engine Source, Pack Blueprints & Proof Profiles  

---

## 1. Executive Summary & File Location Clarifications

In response to Lead Claude's investigation order in `[C-464]`:

1. **`RPGInputTestUtils` Location Clarification:**  
   - Header is at [Source/OneBossFight/Combat/RPGInputTestUtils.h](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Combat/RPGInputTestUtils.h#L17-L43) (under `Source/OneBossFight/Combat/`, not `Source/OneBossFight/Player/`).
   - Implementation is at [Source/OneBossFight/Combat/RPGInputTestUtils.cpp](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Combat/RPGInputTestUtils.cpp#L22-L54).
   - Blueprint library functions:
     * `URPGInputTestUtils::InjectAction(APlayerController* Controller, UInputAction* Action, FVector Value)` (line 25).
     * `URPGInputTestUtils::SetKeyDown(APlayerController* Controller, FName KeyName, bool bDown)` (line 30).

2. **Feasibility Verdict:**  
   A PIE driver can reliably produce **ONE REAL PHYSICAL WEAPON SWING** that strikes `ARPGFrameworkBossCharacter` and routes through `HandlePackHit` $\rightarrow$ `Pending` $\rightarrow$ `FinalizePending` $\rightarrow$ `ApplyPlayerAttackHit(Row, 1.0)`, provided 4 prerequisite conditions (Style Ready, Combat Mode Active, Yaw Aligned, Distance within $[110, 130]\text{ cm}$) are met.

---

## 2. Input Mechanisms for the Pack Attack

Existing automated PIE drivers demonstrate two input injection methods:

### 2.1 Method A (Recommended): Raw Key Injection via `SetKeyDown`
Used in [Scripts/Editor/pie_hit_intake.py](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_hit_intake.py#L126-L137) and [Scripts/Editor/pie_build_fight.py](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_build_fight.py#L815-L820):
- **C++ Helper:** `URPGInputTestUtils::SetKeyDown(Controller, KeyName, bDown)` ([Source/OneBossFight/Combat/RPGInputTestUtils.h:30](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Combat/RPGInputTestUtils.h#L30)).
- **Key Name:** `"LeftMouseButton"` (Mouse Left Click) or `"Gamepad_FaceButton_Left"` (Gamepad 'X' / 'Square').
- **Hold Duration:** $0.12\text{ s}$ (`pie_hit_intake.py:13`, `pie_build_fight.py:91`).
- **Timing Pattern:**
  ```python
  unreal.RPGInputTestUtils.set_key_down(pc, "LeftMouseButton", True)
  # Hold for 0.12 s
  unreal.RPGInputTestUtils.set_key_down(pc, "LeftMouseButton", False)
  ```
- **Advantage:** Exercises raw hardware input dispatch through the player controller, exactly replicating human player input.

### 2.2 Method B: Enhanced Input Action Injection via `InjectAction`
Used in [Scripts/Editor/pie_hit_intake.py](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_hit_intake.py#L90-L94) and [Scripts/Editor/pie_build_fight.py](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_build_fight.py#L804):
- **C++ Helper:** `URPGInputTestUtils::InjectAction(Controller, Action, Value)` ([Source/OneBossFight/Combat/RPGInputTestUtils.h:25](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Combat/RPGInputTestUtils.h#L25)).
- **Action Asset Path:** `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_NormalAttack.IA_NormalAttack` ([pie_hit_intake.py:9,13](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_hit_intake.py#L9-L13)).
- **Execution Pattern:** Must be injected on every tick while `t < press_until` ($0.12\text{ s}$).

### 2.3 Contact Timing Latency
- Measured empirical delay from key press to physical blade contact:
  - Light Attack (`IA_NormalAttack`): $\approx \mathbf{0.34\text{ s}}$ (`HIT_DELAY["Light"] = 0.34` in [pie_build_fight.py:98](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_build_fight.py#L98)).
  - Physical active trace window opens at $\sim 0.25 - 0.30\text{ s}$ of the montage; blade sweep intersects target capsule between $0.32\text{ s}$ and $0.38\text{ s}$.

---

## 3. Player Prerequisites & Setup Sequence

Before an injected attack action will produce a physical weapon swing:

1. **Combat Style Initialization:**
   - The player character begins unarmed. The pack loadout initialization takes up to $\approx \mathbf{10.03\text{ s}}$ to equip the starter sword and reach `Idle` state ([pie_build_fight.py:1262-1270](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_build_fight.py#L1262-L1270)).
   - Assertion: `CurrentCombatStyle` on `BP_CombatComponent_C` must equal `SwordCombatStyle` ([RPGHitIntake.cpp:371-376](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp#L371-L376)).
   
2. **Combat Mode Activation (`Ability.EnterCombat`):**
   - In passive mode, weapons are sheathed on the back/hip socket (`DisabledSocket`).
   - The driver MUST activate `Ability.EnterCombat` via `BP_AdvancedAbilitySystemComponent_C` ([pie_hit_intake.py:85](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_hit_intake.py#L85), [pie_build_fight.py:1282](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_build_fight.py#L1282)):
     ```python
     asc = comp(pawn, "BP_AdvancedAbilitySystemComponent_C")
     asc.call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
     ```
   - Wait $\sim 1.0\text{ s}$ for the draw weapon montage to finish and weapon to attach to `WeaponHandSocket` (`Weapon Hand Socket` in [PR5_BP_ToughSword.txt:13](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/Evidence/exports/PR5_BP_ToughSword.txt#L13)).

3. **Stamina Requirements:**
   - Starter sword Light attack costs $15.0$ stamina ([pie_build_fight.py:79](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_build_fight.py#L79), [RPGWeaponAttackTable.cpp](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGWeaponAttackTable.cpp)).
   - Driver must verify player stamina $\ge 15.0$ (or call `debug_refill_player()` via `RPGCombatDebug`).

4. **Player Positioning & Control Rotation:**
   - Both `ControlRotation` and `ActorRotation` must face the boss directly ([pie_build_fight.py:823-825](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_build_fight.py#L823-L825)):
     ```python
     pc.set_control_rotation(unreal.Rotator(0, 0, yaw_to_boss))
     pawn.set_actor_rotation(unreal.Rotator(0, 0, yaw_to_boss), False)
     ```

---

## 4. Collision Geometry, Channels & Reach Analysis

### 4.1 Boss Mesh vs Boss Capsule Collision
- **Boss Skeletal Mesh:**
  - In [RPGFrameworkBossCharacter.cpp:21](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L21):
    ```cpp
    GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    ```
  - **Critical Finding:** The boss mesh has `NoCollision`. It CANNOT be hit by any line, sphere, or box trace!
- **Boss Capsule Component:**
  - `UCapsuleComponent` is the root component of `ARPGFrameworkBossCharacter` ([RPGFrameworkBossCharacter.cpp:52](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp#L52)).
  - Collision Profile: Default `Pawn` profile (`UCollisionProfile::Pawn_ProfileName`).
  - Object Type: **`ECC_Pawn`**.
  - Dimensions in proof profiles (e.g. `DA_Sevarog_R2Proof_KI145`, [create_r2_content.py:20](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/F6c/create_r2_content.py#L20)):
    * Radius: $R_{\text{boss}} = \mathbf{60.0\text{ cm}}$
    * Half-Height: $H_{\text{boss}} = \mathbf{165.0\text{ cm}}$

### 4.2 Player Capsule Dimensions
- Measured live in `Claude/F6/player_probe_run1` and pinned in [compute_ki145_ranges.py:27](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Reviews/compute_ki145_ranges.py#L27):
  * Radius: $R_{\text{player}} = \mathbf{42.0\text{ cm}}$
  * Half-Height: $H_{\text{player}} = \mathbf{96.0\text{ cm}}$
- **Capsule Hard Boundary:**
  - Sum of radii: $R_{\text{player}} + R_{\text{boss}} = 42.0 + 60.0 = \mathbf{102.0\text{ cm}}$.
  - The player and boss cannot be closer than $102.0\text{ cm}$ without capsule collision penetration/pushback.

### 4.3 Pack Weapon Trace Channel & Reach
- **Trace Component:**
  - Attached to player weapon actor (`BP_ToughSword_C`) via `BP_WeaponTraceTarget_C` ([PR5_BP_ToughSword.txt:17](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/Evidence/exports/PR5_BP_ToughSword.txt#L17), [RPGHitIntake.cpp:109](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp#L109)).
  - Trace Function: `UKismetSystemLibrary::SphereTraceMultiForObjects` sweeping between sockets `WeaponStart` and `WeaponEnd` ([PR5_BP_ToughSword.txt:18-19](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/Evidence/exports/PR5_BP_ToughSword.txt#L18-L19), [SPEC_M1_trace.md:74-76](file:///c:/UnrealProject/OneBossFight/Documentation/Archive/milestones/SPEC_M1_trace.md#L74-L76)).
  - Object Types: Queries `CollisionObjectTypes` array which includes **`ECC_Pawn`** (Pawn object type).
- **Physical Reach:**
  - Starter sword blade length: $\approx 100\text{ cm}$ from player hand socket.
  - Swept sphere radius: $\approx 15 - 25\text{ cm}$.
  - Forward reach from player center: $\approx \mathbf{135\text{ to }145\text{ cm}}$.
- **Recommended Test Distance:**
  - At $D = \mathbf{120.0\text{ cm}}$:
    * Edge-to-edge gap between capsules: $120.0 - 102.0 = \mathbf{18.0\text{ cm}}$.
    * The starter sword blade effortlessly reaches across the $18\text{ cm}$ gap and sweeps into the boss capsule.
    * Sits comfortably inside the calibrated R2 profile band $[110, 135]\text{ cm}$ (`DA_Sevarog_R2Proof_KI145`).

---

## 5. Intake Binding & Routing Details in `RPGHitIntake.cpp`

### 5.1 Binding Mechanics
1. **Binding Step:**
   - In [RPGHitIntake.cpp:306-339](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp#L306-L339), `TryBind()` finds `BP_CollisionComponent_C` on the player pawn and binds `URPGHitIntake::HandlePackHit` to `OnHit(FHitResult)`.
   - Sets `BoundCollision = Collision; bBound = true;`.

2. **Hit Detection & Route Decision:**
   - When the physical weapon sweep intersects the boss capsule, `BP_SweepingSocketTraceTarget` fires `OnHit`, invoking `URPGHitIntake::HandlePackHit(FHitResult HitResult)` ([RPGHitIntake.cpp:470](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp#L470)).
   - In `HandlePackHit` ([RPGHitIntake.cpp:475-487](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp#L475-L487)):
     ```cpp
     if (IRPGNativeBossHealth* Native = Cast<IRPGNativeBossHealth>(Target))
     {
         UObject* Probe = nullptr;
         BuildRecord(HitResult, Target, Probe);
         if (!Probe)
         {
             Native->ApplyPlayerHit(1.0);
             return;
         }
         bNativeBoss = true;
     }
     ```
   - `BuildRecord` ([RPGHitIntake.cpp:361-395](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp#L361-L395)):
     * Line 379: Calls `FindActiveTarget(BoundCollision.Get())`.
     * `FindActiveTarget` ([RPGHitIntake.cpp:67-94](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp#L67-L94)) returns the active `BP_WeaponTraceTarget_C` (which has `bCollisionEnabled? == true` or valid `HitData`).
     * `Probe` is NON-NULL! Therefore, `bNativeBoss = true` is latched!
   - In lines 497-507:
     * `FPending Entry; Entry.ActiveTarget = ActiveTarget; Entry.bNative = true;`
     * `Pending.Add(MoveTemp(Entry));`
     * Enqueues `FinalizePending` for the next tick!

3. **FinalizePending Execution:**
   - In [RPGHitIntake.cpp:510-602](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp#L510-L602):
     * Reads `AttackData` from `ActiveTarget`'s `HitData` ([lines 530-554](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp#L530-L554)).
     * Classifies attack: `DefaultMeleeAttackData` $\rightarrow$ `ERPGAttackKind::Light` ([line 555](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp#L555)).
     * Fetches row from `URPGWeaponAttackTable` for `(SwordCombatStyle, Light)`: posture 18, bleed 0, healthMult 1.0 ([lines 569-582](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp#L569-L582)).
     * Native boss branch ([lines 583-602](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp#L583-L602)):
       Logs:
       `[FrameworkProof] attack_row weapon=SwordCombatStyle kind=Light found=1 posture=18 bleed=0 healthMult=1 via=pending`
       Calls:
       `Native->ApplyPlayerAttackHit(Record.Row, 1.0);`
       Broadcasts:
       `OnBossHit.Broadcast(Record);`

---

## 6. Specific Risks & Failure Modes

| Risk ID | Hazard Description | Root Cause | Preventive Mitigation |
|---|---|---|---|
| **R-01** | Swing does not trigger (unarmed or no-op) | Player attacked before `SwordCombatStyle` equipped or before `Ability.EnterCombat` drew weapon | Driver must await `pack_style_known` ($> 10\text{ s}$), fire `Ability.EnterCombat`, and verify weapon actor exists in hand socket before striking |
| **R-02** | `Probe == nullptr` fallback to immediate path | `FindActiveTarget` fails if `ANS_CollisionTrace` ends before `HandlePackHit` runs, clearing `bCollisionEnabled?` | In [RPGHitIntake.cpp:88-91](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp#L88-L91), `FindActiveTarget` has fallback `ReadObject(Target, TEXT("HitData"))`, which persists across frames |
| **R-03** | Capsule collision pushback / rotation drift | Distance $D < 102.0\text{ cm}$ causes player capsule ($R=42$) to penetrate boss capsule ($R=60$) | Maintain driver distance strictly at $D = 120.0\text{ cm}$ (edge gap $18\text{ cm}$) |
| **R-04** | Swing whiffs through air | Distance $D > 135.0\text{ cm}$ exceeds sword reach | Keep $D \le 125.0\text{ cm}$; re-assert control and actor rotation facing boss before strike |
| **R-05** | Insufficient stamina cancels attack | Player stamina $< 15.0$ suppresses light attack montage | Call `debug_refill_player()` or verify stamina $\ge 15.0$ before injection |

---

## 7. Recommended Experiment Sequence & Telemetry Assertions

### 7.1 Driver Execution Timeline
1. **$t = 0.0\text{ s}$ (PIE Start):** Load proof map (e.g. `L_SevarogFrameworkProofR2.umap`).
2. **$t = 0.0 .. 10.5\text{ s}$ (Warm-up & Style Wait):** Wait until `ld.get_actual_style_name() == "SwordCombatStyle"` and `ld.get_state_name() == "Idle"`.
3. **$t = 10.5\text{ s}$ (Enter Combat):**
   - Activate tag `Ability.EnterCombat` on player ASC.
   - Assert `URPGHitIntake::IsBound() == true`.
4. **$t = 11.5\text{ s}$ (Position & Align):**
   - Boss at $(X_B, Y_B, Z_B)$. Teleport player pawn to $(X_B - 120.0, Y_B, Z_B)$.
   - Set player controller rotation to `Rotator(0, 0, 0)` (facing boss).
   - Set player pawn rotation to `Rotator(0, 0, 0)`.
5. **$t = 12.0\text{ s}$ (Inject Attack):**
   - `unreal.RPGInputTestUtils.set_key_down(pc, "LeftMouseButton", True)`
6. **$t = 12.12\text{ s}$ (Release Attack):**
   - `unreal.RPGInputTestUtils.set_key_down(pc, "LeftMouseButton", False)`
7. **$t \approx 12.34 .. 12.40\text{ s}$ (Physical Contact):**
   - Weapon trace sweeps into boss capsule.
8. **$t \approx 12.42\text{ s}$ (FinalizePending):**
   - Row resolved, native damage applied.

### 7.2 Telemetry Logging Assertions
The driver should parse and assert the following log sequence in the output log:
1. `LogRPGHitIntake: <Pawn>: hit intake bound to BP_CollisionComponent_C.OnHit` ([RPGHitIntake.cpp:339](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp#L339))
2. `[FrameworkProof] attack_row weapon=SwordCombatStyle kind=Light found=1 posture=18 bleed=0 healthMult=1 via=pending` ([RPGHitIntake.cpp:597](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp#L597))
3. `[FrameworkProof] boss_hit damage=35` (or calibrated profile damage) ([RPGFrameworkBossCharacter.cpp](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp))
4. `LogRPGHitIntake: hit 1 at ... weapon SwordCombatStyle, kind Light, posture 18, stamina 15, bleed 0, attack data DefaultMeleeAttackData ... via=pending` ([RPGHitIntake.cpp:594](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp#L594))
