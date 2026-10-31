# Designer Guide: Creating a New Boss with `new_boss.py` (Track C1 / C4)

**Document:** `Documentation/Boss/C1_NEW_BOSS_HOWTO.md`  
**Audience:** Technical Designers, Combat Designers, AI Animators  
**Tools:** `Docs/BossCombatReview/Execution/Claude/C1/new_boss.py`  
**Prerequisites:** Windowed Unreal Editor (5.5.4), PowerShell 5.1+, Python 3.11+  
**Status:** Canonical Authoring Reference  

---

## 1. Prerequisites (Mesh & Animation Blueprint)

Before running the utility, your character assets must satisfy three non-negotiable structural requirements:

### 1.1 Weapon Sockets
The Skeletal Mesh must contain two distinct authored sockets defining the weapon blade segment for sub-tick capsule sweeps:
- **`SocketA` (Base)**: Typically `weapon_r` (socket at hand/hilt).
- **`SocketB` (Tip)**: Typically `root_weapon_end_r` (socket at weapon tip) or custom named bone.
- *Failure Mode*: If sockets are missing or identical ($A == B$), the card validator fails closed with `MoveCard.Socket` ([RPGBossMoveCard.cpp:81](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossMoveCard.cpp#L81)) or `Framework.Boss.WeaponBone`.

### 1.2 AnimBP `FullBody` Slot
The boss Animation Blueprint must implement a pose slot named `"FullBody"`:
- In your AnimGraph, place an **`AnimNode_Slot`** node in the main pose path before the Output Pose.
- Set its **Slot Name** property to `FullBody`.
- *Verification*: The engine introspects this via `RPGFramework::HasSlotNode` ([RPGBossFrameworkProfile.cpp:133-146](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp#L133-L146)). If missing, profile resolution fails with `Framework.Profile.AnimSkeleton` or `Framework.Profile.SequenceTelemetryOnly`.

### 1.3 In-Place Animations Only
- All attack and locomotion sequences must be authored **in-place** (zero root motion).
- Ensure **EnableRootMotion** is unchecked in sequence asset properties.
- *Failure Mode*: If an animation sequence has root motion, the validator fails with `MoveCard.UnsupportedRootMotion` ([RPGBossMoveCard.cpp:45](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossMoveCard.cpp#L45)).

---

## 2. Configuration File Reference (`config.json`)

`new_boss.py` reads a single JSON file. Below is the complete 40-key schema covering baseline locomotion, combat bands, optional two-phase transitions, posture stance break, bleed hemorrhage, and move cards:

```json
{
  "boss_name": "SevarogV1",
  "destination_package_dir": "/Game/OneBossFight/FrameworkProof",
  "fixture_label": "F5 fixture",
  "damage_enabled": true,
  "mesh_path": "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog.Sevarog",
  "anim_class_path": "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sevarog_AnimBlueprint.Sevarog_AnimBlueprint_C",
  "target_pawn_class_path": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C",
  "band_min_cm": 110.0,
  "band_max_cm": 135.0,
  "walk_speed_cm_per_second": 180.0,
  "acceptance_cm": 5.0,
  "walk_timeout_seconds": 10.0,
  "blend_in_seconds": 0.1,
  "blend_out_seconds": 0.03,
  "capsule_radius_cm": 60.0,
  "capsule_half_height_cm": 165.0,
  "target_health": 800.0,
  "hit_step_cm": 15.0,
  "hit_max_substeps": 8,
  "repeat_penalty": 0.2,
  "repeat_memory": 2,
  "attack_count": 2,
  "boss_max_health": 250.0,
  "player_hit_damage": 100.0,
  "phase_two_fraction": 0.5,
  "phase_two_id": "Phase_Two",
  "posture_max": 100.0,
  "player_posture_hit_amount": 25.0,
  "stagger_seconds": 3.0,
  "posture_regen_delay_seconds": 5.0,
  "posture_regen_per_second": 10.0,
  "bleed_buildup_per_hit": 25.0,
  "bleed_initial_threshold": 100.0,
  "bleed_threshold_increase": 50.0,
  "bleed_threshold_max": 300.0,
  "bleed_hp_fraction": 0.15,
  "alignment_authored": true,
  "mesh_relative_transform": {
    "location": [0.0, 0.0, -165.0],
    "rotation": [0.0, 0.0, -90.0],
    "scale": [1.0, 1.0, 1.0]
  },
  "cards": [
    {
      "move_id": "Move_Sevarog_AntiGreed_C1",
      "cooldown_seconds": 2.5,
      "weight": 1.0,
      "spec_json": "C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/C1/example_new_card_antigreed_c1.json",
      "bake": true
    },
    {
      "move_id": "Move_Sevarog_SwingSlow_F7_R2",
      "cooldown_seconds": 3.0,
      "weight": 1.0
    }
  ],
  "proof_level": {
    "boss_spawn_location": [500.0, 0.0, 170.0],
    "player_start_location": [0.0, 0.0, 100.0]
  }
}
```

### 2.1 Complete Field-by-Field Reference

The configuration contains 30 standard keys (or 40 keys when optional Posture and Bleed blocks are populated):

| Key | Status | Type | Description & Constraints | Validation Failure Token |
| :--- | :--- | :--- | :--- | :--- |
| `boss_name` | Mandatory | String | Unique boss label used for naming assets (`DA_<boss>_Profile`, `L_<boss>FrameworkProof`). | — |
| `destination_package_dir` | Mandatory | Path | Target package path (e.g. `/Game/OneBossFight/FrameworkProof`). | `Framework.BossConfig.DestinationExists` |
| `fixture_label` | Mandatory | String | Must be `"F5 fixture"` (or `"F4 fixture"` / `"F3 fixture"`). | `Framework.Profile.Identity` |
| `damage_enabled` | Mandatory | Bool | Must be `true` for F4/F5; `false` for F3. | `Framework.Profile.Identity` |
| `mesh_path` | Mandatory | Asset Path | Soft path to `USkeletalMesh`. | `Framework.Profile.Identity` |
| `anim_class_path` | Mandatory | Class Path | Soft path to `UAnimBlueprintGeneratedClass` (`_C`). | `Framework.Profile.Identity` |
| `target_pawn_class_path` | Mandatory | Class Path | Soft path to player pawn class (`BP_CombatPlayerCharacter_C`). | `Framework.Profile.Identity` |
| `band_min_cm`, `band_max_cm` | Mandatory | Float | Near and far combat band edges. Order: $\text{BandMin} < \text{BandMax}$. | `Framework.Profile.Geometry`, `Framework.Profile.CardBandOrBlendTail` |
| `acceptance_cm` | Mandatory | Float | Arrival tolerance. Must satisfy $\text{AcceptanceCm} < 0.5 \times (\text{BandMax} - \text{BandMin})$. | `Framework.Profile.Geometry` |
| `walk_speed_cm_per_second` | Mandatory | Float | Locomotion approach speed (finite $> 0$). | `Framework.Profile.Domain` |
| `walk_timeout_seconds` | Mandatory | Float | Approach safety timeout in seconds (finite $> 0$). | `Framework.Profile.Domain` |
| `blend_in_seconds` | Mandatory | Float | Crossfade into card. Must be $< \text{Card.ActiveStartSeconds}$. | `Framework.Profile.SequenceTelemetryOnly` |
| `blend_out_seconds` | Mandatory | Float | Crossfade to idle. Must satisfy $\text{RecoveryEnd} + \text{BlendOut} \le \text{ClipLength}$. | `Framework.Profile.CardBandOrBlendTail` |
| `capsule_radius_cm`, `capsule_half_height_cm` | Mandatory | Float | Collision bounds. Invariant: $\text{Radius} \le \text{HalfHeight}$. | `Framework.Profile.Geometry` |
| `target_health` | Mandatory | Float | Target dummy HP. Must exceed $\max(\text{HPDamage}) \times \text{AttackCount}$. | `Framework.Profile.DamageBudget` |
| `hit_step_cm`, `hit_max_substeps` | Mandatory | Float, Int | Sweep sub-stepping: step $> 0$, substeps $\in [1, 64]$. | `Framework.Profile.Domain` |
| `repeat_penalty`, `repeat_memory`, `attack_count` | Mandatory | Float, Int, Int | Selector rules: penalty $\in (0, 1]$, memory $\in [1, 8]$, count $\in [1, 8]$. | `Framework.Profile.Domain` |
| `alignment_authored`, `mesh_relative_transform` | Mandatory | Bool, Object | Offset placing mesh base at capsule bottom ($Z = -\text{HalfHeight}$, $\text{Yaw} = -90^\circ$). Authored must be `true`. | `Framework.Profile.Alignment` |
| `cards` | Mandatory | Array | Candidate moves array. Supports reused cards and newly authored cards. | `Framework.Profile.PhaseCooldownStarvation`, `MoveCard.Socket` |
| `proof_level` | Mandatory | Object | Spawn coordinates `{boss_spawn_location: [X,Y,Z], player_start_location: [X,Y,Z]}`. | — |
| `boss_max_health`, `player_hit_damage` | **Optional Block** | Float, Float | Boss HP and player damage per hit. Both $0.0$ (unhittable) OR both $> 0.0$ ($\text{hit\_damage} \le \text{max\_health}$). | `Framework.Profile.Domain` |
| `phase_two_fraction`, `phase_two_id` | **Optional Block** | Float, String | Phase 2 transition trigger. Strictly $0.0 < \text{fraction} < 1.0$ and non-empty ID $\ne \text{None}$. | `Framework.Profile.Phase`, `Framework.Profile.PhaseCards` |
| `posture_*` (5 fields) | **Optional Block** | Floats | Posture pool: `posture_max`, `player_posture_hit_amount`, `stagger_seconds`, `posture_regen_delay_seconds`, `posture_regen_per_second`. **All-or-nothing**: all $0.0$ (off) OR all positive with $\text{hit} \le \text{max}$ and $\text{stagger} \in [0.5, 60.0]$. | `Framework.Profile.Posture` |
| `bleed_*` (5 fields) | **Optional Block** | Floats | Bleed pool: `bleed_buildup_per_hit`, `bleed_initial_threshold`, `bleed_threshold_increase`, `bleed_threshold_max`, `bleed_hp_fraction`. **All-or-nothing**: all $0.0$ (off) OR all positive with $\text{initial} \ge 1.0$, $\text{max} \ge \text{initial}$, and $\text{fraction} \in (0.0, 1.0]$. | `Framework.Profile.Bleed` |

### 2.2 Reusing Cards vs. Authoring & Baking New Cards
In the `cards` array:
- **Reusing an existing card**: Provide only `move_id`, `cooldown_seconds`, and `weight`. `new_boss.py` loads the card from `<destination_package_dir>/Cards/<move_id>` on disk.
- **Authoring and baking a new card**: Provide `move_id`, `cooldown_seconds`, `weight`, and **both** `spec_json` (absolute path with forward slashes to the card spec JSON) and **`bake: true`** (mandatory to trigger 120 Hz component-space blade trajectory sampling).

---

## 3. Tool Command Lines

`new_boss.py` runs inside the Unreal Editor process. Because the editor's working directory is engine binaries (`UE_5.5\Engine\Binaries\Win64`), **all file paths inside `-Script` must be absolute paths with forward slashes**.  
-OutDir must be absolute, the editor does not run from the repo root. Furthermore, `run_editor_script.ps1` requires mandatory `-OutDir` and `-Task` parameters.

### 3.1 Dry-Run Validation (Zero Writes)
Runs offline preflight checks (schema, timing, geometry, range band, phase starvation) without modifying assets:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Docs\BossCombatReview\Execution\Claude\run_editor_script.ps1 `
  -Script "C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/C1/new_boss.py C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/C1/example_v1_boss.json --dry-run" `
  -OutDir "C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\C1\runs_v1\dry" `
  -Task "C1_v1_DryRun" `
  -NullRhi 0
```

> The example config describes assets that ALREADY exist in this repository, so running 3.1 or 3.2 on it as is is refused (`Framework.BossConfig.DestinationExists` or `new card already exists`): copy it to your own file first and change `boss_name`, the new card's `move_id` and the same `MoveId` and `WindowId` inside its `spec_json` file. (Checked by running 3.1 verbatim: `[NEWBOSS_FATAL] new card already exists, refusing`.)

### 3.2 Full Authoring, 120 Hz Baking, and Map Generation
Executes the unified single-session pipeline:
1. Samples 120 Hz component-space blade paths via `bake_blade_path.py`.
2. Authors and saves `URPGBossMoveCard` assets via `author_move_cards.py`.
3. Verifies post-bake pose drift $\le 2.0\text{ cm}$ via `verify_baked_cards.py`.
4. Creates `DA_<Boss>_Profile` with read-back verification.
5. Spawns proof level `L_<Boss>FrameworkProof` with floor, player start, and fixture actor.
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Docs\BossCombatReview\Execution\Claude\run_editor_script.ps1 `
  -Script "C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/C1/new_boss.py C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/C1/example_v1_boss.json" `
  -OutDir "C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\C1\runs_v1\create" `
  -Task "C1_v1_Create" `
  -NullRhi 0
```

---

## 4. PIE Proof & Verification

Once generated, test the boss inside the unattended PIE driver via `run_pie.ps1`.

### 4.1 Running the PIE Proof (Working Form)
Mandatory parameters: `-Map`, `-OutDir`, `-Task`:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Docs\BossCombatReview\Execution\Claude\F4\run_pie.ps1 `
  -Map "/Game/OneBossFight/FrameworkProof/L_SevarogC1v1FrameworkProof" `
  -OutDir "C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\C1\runs_v1\pie_run1" `
  -Task "PIE_SevarogC1v1_Proof" `
  -RealBuild Dex `
  -RealSwing "0.0:Light,1.0:Light"
```

### 4.2 Available Driver Flags
- `-Inject "0.5,0.9"`: Comma-separated list of seconds after the first `playback_start` (boss attack begin). Each injected hit subtracts `PlayerHitDamage` from boss HP.
- `-InjectPie "4.5,6.0"`: Comma-separated seconds after PIE start (waits for boss pawn spawn; can strike boss during approach walk).
- `-InjectRow "0.0:ClaymoreCombatStyle:Strong"`: Injects hits carrying `DA_WeaponAttacks` row data (`"sec:WeaponStyle:Kind[:p1|p2]"`).
- `-RealBuild <Starter|Strength|Dex>`: Equips player loadout build (Claymore, Dual Swords, Starter Sword) via console `rpg.Build`.
- `-RealSwing "0.0:Light,1.0:Light"`: Injects real player pack attacks with action holding (`"t[:Light|Strong|Charged],..."`).
- `-Live <seconds>`: Triggers `restart_encounter_for_test(2)` on a LIVE boss at `<seconds>` after `playback_start` (to test that mid-combat reset is properly refused).
- `-Restart`: Calls `restart_encounter_for_test(2)` to verify combat reset.
- `-DiagLong`: Diagnostic telemetry logged every second up to 20 seconds.

### 4.3 The 10-Second Pack-Style Warmup (KI-150)
> [!IMPORTANT]
> The Advanced ARPG Combat pack requires **~10 seconds** at startup to initialize gameplay ability tags, equipment montages, and combat styles.
> The automated driver waits for player `EnterCombat` and `Idle` before firing attacks. Never schedule real attacks at $t < 10.0\text{ s}$ from map load.

---

## 5. How to Read the Proof Logs

Inspect `editor_raw.log` inside the run output directory to verify combat milestones:

| Log Signature | Meaning | Expected Outcome |
| :--- | :--- | :--- |
| `[F5C_ATTACK] {"move": "Move_..."}` | Boss selector chose and initiated an attack card. | Verified move selected from candidate pool. |
| `[F4C_SWEEP] ... Hit=1 ... Point=(X,Y,Z)` | Sub-tick blade trace registered player capsule overlap. | Hit landed cleanly during active window. |
| `LogRPGSwing: REAL swing ... IA_NormalAttack` | Real player weapon attack injected and executed. | Player attack montage playing. |
| `attack_row weapon=... posture=X bleed=Y found=1` | Hit intake mapped player strike onto combat table. | Proper posture/bleed values extracted. |
| `boss_hit ... damage=100.0 ... posture=X` | Player strike registered on boss health/posture pool. | Boss HP and posture decreased. |
| `stance_break state=Neutral` | Boss posture depleted to 0; attack aborted. | Boss entering staggered state for `StaggerSeconds`. |
| `bleed_proc ... chunk=X` | Hemorrhage threshold reached; burst damage applied. | Boss loses percentage of maximum health. |
| `[F3D_RESULT] CompletedWithDamage` | Proof test completed with zero asserts or unhandled fatal errors. | **Run Passed**. |

### 5.1 Automated Log Graders
Run the automated regex grader on the raw log:
```powershell
python Docs\BossCombatReview\Execution\Antigravity\Reviews\grade_f10_log.py Docs\BossCombatReview\Execution\Claude\C1\runs_v1\pie_run1\editor_raw.log
```
Returns exit code 0 and `PASS: all combat milestones confirmed`.

---

## 6. Troubleshooting Table

| Error Token / Diagnostic | Root Cause | Designer Action / Fix |
| :--- | :--- | :--- |
| `Framework.BossConfig.DestinationExists` | `DA_<boss>_Profile` or `L_<boss>FrameworkProof` already exists on disk. | Choose a new `boss_name` in config. If re-running the same name, delete **only your own new, unreferenced proof assets** (CLAUDE.md: "Never delete and recreate assets that other assets reference"). |
| `Framework.Profile.Identity` | `fixture_label` ("F5 fixture") does not match `damage_enabled`, or cards array is empty. | Set `damage_enabled: true` for F5; ensure `cards` array has $\ge 1$ entry. |
| `Framework.Profile.Geometry` | `band_min_cm >= band_max_cm` or `acceptance_cm >= 0.5 * (band_max - band_min)`. | Ensure `band_min < band_max` and arrival acceptance fits within half the band thickness. |
| `Framework.Profile.Alignment` | `alignment_authored` is `false`, or transform contains NaNs/zero scale. | Set `alignment_authored: true` and specify valid `[X, Y, Z]` location/scale. |
| `Framework.Profile.Phase` | `phase_two_fraction` declared without valid `phase_two_id`, or fraction outside $(0, 1)$ exclusive. | Set fraction strictly between $0.0$ and $1.0$ (e.g. $0.5$) and provide non-empty `phase_two_id`. |
| `Framework.Profile.PhaseCards` | Cards in pool do not match Phase 1 or Phase 2 ID, or a phase has 0 cards. | Ensure at least 1 card belongs to Phase 1 and at least 1 card belongs to `phase_two_id`. |
| `Framework.Profile.PhaseCooldownStarvation` | A phase has fewer cards than `attack_count` and all cards have cooldown $> 0$ (KI-149). | Add more cards to the phase pool, decrease `attack_count`, or give at least one card cooldown $0.0\text{ s}$. |
| `Framework.Profile.CardBandOrBlendTail` | `band_min < card.MinRange` or `band_max > card.MaxRange`, or `RecoveryEnd + BlendOut > ClipLength`. | Adjust locomotion band to fit within card reach, or increase animation clip length. |
| `Framework.Profile.DamageBudget` | Worst card damage $\times$ `attack_count` $\ge$ `target_health`. | Increase `target_health` or reduce card damage so the target dummy survives proof attacks. |
| `MoveCard.Socket` | Declared `SocketA` or `SocketB` missing on Skeletal Mesh, or sockets are identical. | Open Skeletal Mesh in editor and add `weapon_r` / `root_weapon_end_r` sockets. |
| `MoveCard.Timeline` | Card timeline order violated: commit $\le$ activeStart $<$ activeEnd $\le$ recoveryEnd $\le$ clipLength. | Fix window timing in card JSON so hit windows strictly lie within active window. |
| `[BAKE_FATAL] Stale baked path detected for MoveId='...' ... drift X cm exceeds tolerance` | Socket positions in live AnimPose drifted $> 2.0\text{ cm}$ from stored `BakedSamples` (animation sequence was modified after bake). | The card already exists, so re-running is refused (`new card already exists`). Increment the card's `move_id` suffix (e.g. `_v2`), OR delete your own new, unreferenced card asset before re-running (CLAUDE.md: "Never delete and recreate assets that other assets reference"). |
| `Framework.Profile.AnimSkeleton` | Animation sequence skeleton does not match AnimBP target skeleton. | Retarget animation to the boss skeleton or fix `Skeleton` soft pointer in card spec. |
