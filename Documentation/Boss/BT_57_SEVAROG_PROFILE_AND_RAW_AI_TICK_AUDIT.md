# BT-57: Sevarog Profile Wiring, Production vs Fixture Split, and Raw AI Tick Evidence Audit (Revision 2)

Date: 2026-11-16
Task: BT-57 (Antigravity, Read-Only Audit)
Reference Run: `Saved/SevarogArenaRoute/Run_20261116_152934_ba15687c`
Reference Receipt: `Saved/SevarogArenaRoute/Run_20261116_152934_ba15687c/acceptance.json`
Task Directives: [X-2531], [X-2532] Codex lead instructions; `Documentation/Boss/BT_56_SMOKE_FAILURE_AND_FOLLOWUP.md`; `Documentation/Boss/BT_13_RAW_BT_TICK_EVIDENCE.md`

---

## 1. Executive Summary & Smoke Evidence Audit

In the latest C-1155 Smoke run (`Run_20261116_152934_ba15687c`), the C-1619 Sevarog arena route achieved several runtime milestones:
1. **Starter Loadout Verified**: `-rpg.Build=Starter` set at engine startup; observed `started, rpg.Build is 'Starter'`.
2. **Sentinel Health Handshake Verified**: Bare-map sentinel initialized to `800/800` via profile target health (`RPGPlayerMovesSubsystem.cpp:691`).
3. **Actor Census & Binding Clean**: Exactly 1 framework boss active, 0 pack bosses, 0 competing bosses, and 0 pack boss HUD widgets.
4. **Pack Boss Suppression**: Placed pack actor `BP_ExampleGreatSwordBoss_C_3` was intercepted before BeginPlay (`began_play=0`, `montage_active=0`).
5. **Combat Engaged**: Production card decisions occurred (`Move_Sevarog_Swing3_Slow`), and the boss damaged the player.

However, acceptance failed (`accepted=false`, `result="FAILED"`, `runtime_acceptance_status="BLOCKED"`) due to two distinct gates:
1. **Boss Max Health Mismatch**:
   - `sevarog_health_1500` observed `sevarog_max_health = 250.0` (criterion requires `1500.0`).
   - The runtime character logged `[FrameworkProof] boss_health max=250 playerHitDamage=100 label=F5_fixture`.
2. **Raw AI Attack-Task Tick Telemetry Uninstrumented**:
   - `raw_behavior_tree_tick_count` remained `BLOCKED_NOT_INSTRUMENTED`.
   - Telemetry lacked direct observation from the actual BehaviorTree attack-task execution path.

This revision audits both findings against project source, data assets, and owner decisions, establishes the baseline for player vs boss health, and provides a fail-closed recommendation for AI tick telemetry.

---

## 2. Framework Profile & Asset Wiring Trace

### 2.1 The Selection Chain
- **Arena Map Default Route**:
  In `L_SevarogArena`, the route switch directs encounter selection to `/Game/OneBossFight/Data/Sevarog/DA_Sevarog_Framework_Encounter.DA_Sevarog_Framework_Encounter` (`DefaultGame.ini`, `RPGPlayerMovesSubsystem.h:56`).
- **Encounter Definition Asset**:
  `DA_Sevarog_Framework_Encounter` is an instance of `URPGBossEncounterDefinition` authored by `Scripts/Editor/author_framework_encounter_definition.py`.
  - Line 20: `BOSS_PATH = "/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_Draft"`
  - Line 21: `PLAYER_PATH = "/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Player_Hero_Draft_V3"`
  - Line 22: `PROFILE_PATH = "/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_FrameworkProfile_Draft"`
  - Lines 152, 189: `asset.set_editor_property("framework_boss_profile", profile)`

### 2.2 Profile Asset Authoring
- `DA_Boss_Sevarog_FrameworkProfile_Draft` is an instance of `URPGBossFrameworkProfile` authored by `Scripts/Editor/author_sevarog_draft_cards.py`.
- Lines 54–67:
  ```python
  FRAMEWORK_PROFILE_FIELDS = {
      "fixture_label": "F5 fixture",
      ...
      "target_health": 800.0, "damage_enabled": True,
      ...
      "boss_max_health": 250.0, "player_hit_damage": 100.0,
      ...
  }
  ```
- This profile was authored explicitly as the **F5 proof fixture**, where `boss_max_health = 250.0` is a minimal testing constant designed to let automated unit tests kill the boss in 3 hits (at 100 damage/hit).

### 2.3 Runtime Ingestion
- In `RPGFrameworkBossCharacter.cpp:185-189`:
  ```cpp
  if (Dependencies->Profile->BossMaxHealth > 0.f)
  {
      bHittable = true;
      MaxHealth = Health = Dependencies->Profile->BossMaxHealth;
      UE_LOG(LogTemp, Display, TEXT("[FrameworkProof] boss_health max=%g playerHitDamage=%g label=%s"),
          MaxHealth, double(Dependencies->Profile->PlayerHitDamage),
          *Dependencies->Profile->FixtureLabel.Replace(TEXT(" "), TEXT("_")));
  }
  ```
- `Dependencies->Profile` points to `DA_Boss_Sevarog_FrameworkProfile_Draft`.
- Crucially, `RPGFrameworkBossCharacter` reads `BossMaxHealth` exclusively from `URPGBossFrameworkProfile`. It does **not** read `URPGBossDefinition::Stats.MaxHealth`.

---

## 3. Truth Baseline: Boss vs Player Health

### 3.1 Boss Health: Canonical Owner-Approved O1 Baseline
The canonical owner approval is recorded in `Documentation/DECISIONS.md` (2026-11-13 O1 / X-1991 / X-2428) and codified in `Scripts/Editor/sevarog_o1_inputs.json`:
- `Stats.MaxHealth = 1500.0`
- `Stats.MaxPosture = 100.0`
- `Stats.PostureRegenDelay = 6.0`
- `Stats.PostureRegenRate = 13.0`
- `Phases[Phase_1].EntryHealthFraction = 0.6`
- `Phases[Phase_1].SpeedMultiplier = 1.0`
- `Phases[Phase_1].RateMultiplier = 1.0`
- `Phases[Phase_1].AttackMultiplier = 1.0`

In the data model:
- `DA_Boss_Sevarog_Draft` (`URPGBossDefinition`) already holds these O1 values in its `Stats` and `Phases` structures (verified by the 115-field parity manifest).
- However, `DA_Boss_Sevarog_FrameworkProfile_Draft` was never updated with these O1 values; it was left as the 250 HP F5 proof fixture.
- Consequently, the PIE driver correctly fails the `sevarog_health_1500` criterion because the loaded profile is explicitly the 250 HP F5 fixture.

### 3.2 Player Health (`TargetHealth`): Fixture vs Production Baseline
Per Codex's directive in [X-2532], the origin of `TargetHealth = 800.0` was deeply traced:
1. **Header Definition (`RPGBossFrameworkProfile.h:74-75`)**:
   `TargetHealth` is documented explicitly as:
   `"Pack player health the proof fixture writes explicitly (a bare proof map has none: measured 0 / 1000000). Fixture value, not tuning."`
2. **Historical Decisions (`DECISIONS.md: KI-150 / C-438`)**:
   `800.0` was introduced by Claude as a test fixture value for the F5 proof fixture to prevent uninitialized pack health clamping.
3. **Pack Authored Default**:
   In the vendor pack (`BP_CombatPlayerCharacter` / `ExampleGreatSwordPlayerCombatStyle`), default player health is **100.0** (`KNOWN_ISSUES.md: KI-150`).
4. **Draft Asset (`DA_Player_Hero_Draft_V3.uasset`)**:
   Contains `Stats.MaxHealth = 800.0`, but this asset resides in `Data/TypedABIFixtures/AuthoringPreview/BossDrafts/` as an unapproved authoring draft, not an Owner-approved O1 decision.
5. **Owner Scope**:
   The Owner O1 decision (2026-11-13) approved only Sevarog boss parameters; it **did not approve** any player health value.
6. **Classification**:
   Production player health is **UNRESOLVED / Owner-gated**. `800.0` is strictly an F5 fixture / draft placeholder value. It must not be labeled as an Owner-approved production tuning value.

---

## 4. Recommended Production-vs-Fixture Split

### 4.1 Why In-Place Mutation of F5 Fixture is Unsafe
Modifying `DA_Boss_Sevarog_FrameworkProfile_Draft` in place to 1500 HP risks breaking existing isolated automation tests in the 573-test DD27j suite that depend on the F5 fixture having 250 HP and label `"F5 fixture"`.

### 4.2 Recommended Architecture
Establish a clean two-asset topology:

1. **Retain F5 Proof Fixture Asset**:
   - Path: `/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_FrameworkProfile_Draft` (or alias/keep as the fixture profile).
   - Fields: `fixture_label = "F5 fixture"`, `boss_max_health = 250.0`, `target_health = 800.0`, `player_hit_damage = 100.0`.
   - Purpose: Reserved for unit tests, isolated combo tests, and fixture regression suites.

2. **Author Dedicated Production Framework Profile Asset**:
   - Path: `/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_FrameworkProfile_Production`.
   - Bound to Owner-Approved O1 Values:
     - `fixture_label = "Production"` (or `"Sevarog_O1_Production"`)
     - `boss_max_health = 1500.0` (from `sevarog_o1_inputs.json:Stats.MaxHealth`)
     - `posture_max = 100.0` (from `sevarog_o1_inputs.json:Stats.MaxPosture`)
     - `posture_regen_delay_seconds = 6.0` (from `sevarog_o1_inputs.json:Stats.PostureRegenDelay`)
     - `posture_regen_per_second = 13.0` (from `sevarog_o1_inputs.json:Stats.PostureRegenRate`)
     - `phase_two_fraction = 0.6` (from `sevarog_o1_inputs.json:Phases[Phase_1].EntryHealthFraction`)
     - `phase_two_id = "Phase_2"`
     - `damage_enabled = true`
     - `target_health = 800.0` marked explicitly as **UNRESOLVED / fixture placeholder** pending future owner player tuning.
     - Retains identical skeletal mesh, anim class, cards, and combo graph assets as authored in `author_sevarog_draft_cards.py`.

3. **Update Encounter Selection**:
   - In `author_framework_encounter_definition.py`, point `PROFILE_PATH` to the production framework profile asset.
   - Re-run locked encounter authoring under C-1155 (in BT-59) to write `DA_Boss_Sevarog_FrameworkProfile_Production` and update `DA_Sevarog_Framework_Encounter`.

---

## 5. Raw AI Attack-Task Tick Telemetry Audit

### 5.1 Discipline & Context (`BT_13_RAW_BT_TICK_EVIDENCE.md`)
As documented in `Documentation/Boss/BT_13_RAW_BT_TICK_EVIDENCE.md`, the lead review established strict evidentiary rules:
- Suppression before BeginPlay (`began_play=0`), `montage_active=0`, and `StopMovement`/`StopLogic` are useful lifecycle safeguards, but **none of them are raw attack-task execution counters**.
- A `UBrainComponent::StopLogic` call cannot count task ticks that already occurred.
- Sampling status flags (`IsRunning()`, `GetActiveNode()`) at actor suppression is an after-the-fact sampling proxy, not a direct observation of historical task execution.
- Hardcoded counters, simulated metrics, or proxy approximations are prohibited.

### 5.2 Pack Boss AI Architecture
Inspection of the exported vendor assets reveals:
- Pack boss actor: `BP_ExampleGreatSwordBoss_C` (inherits from `BP_BaseCombatCharacter_C`).
- Behavior tree: `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/BT_ExampleBoss.uasset`.
- Attack tasks: Multiple instances of `/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/AI/BehaviorTreeNodes/T_TryActivateAbilitiesByTags.uasset` (inherits from `UBTTask_BlueprintBase`).
- Root rule: Vendor pack assets under `/Game/AdvancedARPGCombat/` must **not** be modified directly.

### 5.3 Technical Analysis of Instrumentation Seams
To establish a *true* counter for BehaviorTree attack-task ticks, the execution path of the task node itself must be observed:
1. **Vendor Asset Modification (Prohibited)**:
   Modifying `T_TryActivateAbilitiesByTags.uasset` to add a counter or project delegate would require editing third-party vendor assets, violating project safety rules.
2. **Engine Modification (Prohibited)**:
   Modifying `UBTTask_BlueprintBase::ReceiveTickAI` or `UBTTaskNode` in engine source is impossible without custom engine rebuilds.
3. **Project Proxy Task (Requires Asset Re-wiring)**:
   Replacing `T_TryActivateAbilitiesByTags` in `BT_ExampleBoss` with a project-owned instrumented C++ task (`URPGInstrumentedBTTask`) would require editing the vendor behavior tree asset `BT_ExampleBoss.uasset`, again violating vendor asset immutability.
4. **Suppression-Time Sampling (Rejected per [X-2532])**:
   Querying `UBehaviorTreeComponent::IsRunning()` at suppression time is a post-spawn state check, not a historical tick counter.

### 5.4 Recommendation: Keep Criterion Blocked
In accordance with `BT_13_RAW_BT_TICK_EVIDENCE.md` and [X-2532]:
- **Do NOT introduce a sampling proxy or simulated counter.**
- **Leave `raw_behavior_tree_tick_count` as `BLOCKED_NOT_INSTRUMENTED`.**
- In the PIE acceptance receipt, preserve `blockers: ["RAW_BEHAVIOR_TREE_TICK_COUNTER_NOT_INSTRUMENTED"]` and status `SMOKE_PASS_LIFECYCLE_UNTESTED` (or `BLOCKED`).
- The lifecycle evidence (`suppressed_pack_actor_observed=true`, `no_pack_montage_at_suppression=true`, `binding_framework_one_pack_zero=true`, `no_pack_bosshud_widget=true`) remains 100% truthful and sufficient for Smoke route verification, while raw task tick instrumentation remains properly tracked as an open engineering limitation.

---

## 6. Implementation Scope for BT-59

Following Codex lead review in BT-58, BT-59 implementation should be strictly scoped to:
1. **Production Profile Data Authoring**:
   - In `author_sevarog_draft_cards.py`, add generation of `DA_Boss_Sevarog_FrameworkProfile_Production` with `BossMaxHealth = 1500.0`, `PostureMax = 100.0`, `PostureRegenDelaySeconds = 6.0`, `PostureRegenPerSecond = 13.0`, `PhaseTwoFraction = 0.6`, `fixture_label = "Production"`, and `TargetHealth = 800.0` (noted as unapproved fixture/draft placeholder).
   - Retain `DA_Boss_Sevarog_FrameworkProfile_Draft` unchanged as the F5 proof fixture.
   - Update `author_framework_encounter_definition.py` to point `PROFILE_PATH` to `DA_Boss_Sevarog_FrameworkProfile_Production`.
   - Execute locked C-1155 authoring to write the production profile asset and update the encounter definition.
2. **Acceptance Driver & Contracts**:
   - In `pie_sevarog_arena_route_acceptance.py`:
     - Retain `sevarog_health_1500` criterion (will pass once 1500 HP production profile is loaded).
     - Retain `raw_behavior_tree_tick_count` as `BLOCKED_NOT_INSTRUMENTED` without fake proxies.
   - Contract test updates to verify production profile reference and ensure F5 fixture remains intact.

---

## 7. Operating Discipline

- **Status**: Read-only audit revision completed.
- **Rules Followed**:
  - Zero edits to C++, Python, or configuration files outside this documentation report.
  - Zero Unreal Editor launches, builds, tests, PIE runs, or asset modifications.
  - Zero git commits or pushes.
- **Handoff**: Handoff to Codex (lead) for BT-58 lead review.
