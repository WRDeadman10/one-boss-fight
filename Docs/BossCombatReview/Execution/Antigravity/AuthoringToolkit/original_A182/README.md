# OneBossFight Authoring Toolkit (`AG-CONTENT04`)

**Author:** Antigravity (Party Code `A`) - Senior C++ Implementer & Unreal Engine Specialist  
**Work Order:** `[X-282]`, `[X-283]`, `[X-286]`, `[X-288]`, `[X-291]`, `[X-293]` / `Docs/BossCombatReview/Execution/Codex/AG_CONTENT04_MCP_CONTINUATION.md`  
**Review Status:** Frozen delivery `A-182` submitted for Lead Reviewer Claude (`C`) and Implementer Codex (`X`). Work Orders `[C-256]`, `[X-291]`, `[X-288]`.  
**Execution Boundary:** **STRICTLY OFFLINE IMPLEMENTATION**. Zero Unreal Engine processes launched; zero assets created, mutated, or deleted; zero pack edits; zero git commits or pushes.

---

## Offline Float64 Qualification & IEEE 754 float32 Storage Parity

> [!IMPORTANT]
> **Offline float64 checks do NOT certify native float32 conversion or input-mode parity.**  
> All offline tests and validators execute in CPython where floating-point literals and operations default to 64-bit IEEE 754 double precision (`float64`). In contrast, Unreal Engine native C++ `UProperty` / `FProperty` fields on `UStruct` and `UObject` (e.g. `MaxHealth`, `EntryHealthFraction`, `RiposteAlignSeconds`) store 32-bit single-precision floats (`float32`).  
> The authoring toolkit uses Python's standard `struct.pack('f')` / `struct.unpack('f')` (`to_float32`) to simulate native float32 truncation and verify that valid float32 values survive round-trip without precision drift or unexpected readback failure (e.g., `0.35` -> `0.3499999940395355`, `0.03` -> `0.029999999329447746`).  
> Requested scalar values that are finite in float64 but overflow the IEEE 754 32-bit float range (`> 3.402823466e+38`) are strictly refused with `ValueError`. However, offline unit test execution does not execute live UE5.5 C++ serialization, runtime memory layout, or input-mode controller parity.

---

## 1. Architecture Overview & Components

The **OneBossFight Authoring Toolkit** provides a pure, defensive, staged Python infrastructure for inspecting, validating, authoring, and exporting gameplay Data Assets for Unreal Engine 5.5.

The toolkit connects four cohesive deliverables:

```
AuthoringToolkit/
├── authoring_core.py                 <-- Pure Python shared validation core (standard library only)
├── draft_boss_profiles.py            <-- Staged DRAFT creator for boss & player participant URPGBossDefinition assets
├── inspect_authored_assets.py        <-- Read-only complete typed asset inspector & JSON exporter (zero mutations)
├── test_authoring_core.py            <-- Standard library unittest test suite (59 adversarial & regression tests)
├── test_run_output.txt               <-- Raw test suite execution output (59/59 PASS, exit code 0)
├── examples/
│   └── boss_draft_profiles.json      <-- Explicit two-boss + one-player draft profile specifications (exact native schema)
├── original_A178/                    <-- Byte-exact preserved A-178 historical delivery
├── original_A179/                    <-- Byte-exact preserved A-179 historical delivery
├── original_A180/                    <-- Byte-exact preserved A-180 historical delivery
├── README.md                         <-- This integrated architecture and usage specification
└── evidence_sha256.txt               <-- Cryptographic SHA-256 evidence receipt

BuildAuthoringHelper/
├── author_custom_build.py            <-- Staged custom build & cloned catalog authoring helper (imports authoring_core)
├── original_A176/                    <-- Byte-exact preserved A-176 historical delivery
├── original_A177/                    <-- Byte-exact preserved A-177 historical delivery
├── original_A178/                    <-- Byte-exact preserved A-178 historical delivery
├── original_A179/                    <-- Byte-exact preserved A-179 historical delivery
├── original_A180/                    <-- Byte-exact preserved A-180 historical delivery
├── README.md                         <-- Build helper usage and verification guide
└── evidence_sha256.txt               <-- Build helper evidence receipt
```

---

## 2. Core Validation Invariants & Bounded Fixes (`authoring_core.py`)

1. **Exact Native Normalization (`exact_native_normalize`):**
   * Mirrors Unreal Engine 5.5 `String.cpp.inl:971-974 TrimQuotesInline` and `RPGCombatRegistry::Normalize`:
     ```cpp
     FString Normalize(const FString& Text) {
         return Text.TrimStartAndEnd().TrimQuotes().TrimStartAndEnd().ToLower();
     }
     ```
   * Trims leading/trailing whitespace, trims **at most ONE leading and ONE trailing double quote (`"`)**, trims whitespace again, and converts to lowercase (ASCII parity scope).
   * For repeated quotes such as `""off""`, native leaves `"off"`.
   * **Single quotes (`'`) are preserved characters** in native UE5 strings and are never stripped.
2. **Pinned 3-Build Legacy Compatibility Contract:**
   * Directly matches `Source/OneBossFight/Player/RPGBuildRules.h:50-57` and `RPGCombatCatalog.cpp:158-172`:
     * Slot 0: `BuildId = "Starter"`, `ConsoleName = "Starter"`, `DisplayName = "Starter"`, `UiOrder = 0`, `WeaponId = "Starter"`, `ExpectedStyle = "SwordCombatStyle"`.
     * Slot 1: `BuildId = "Strength"`, `ConsoleName = "Strength"`, `DisplayName = "Strength"`, `UiOrder = 1`, `WeaponId = "Strength"`, `ExpectedStyle = "ClaymoreCombatStyle"`.
     * Slot 2: `BuildId = "Dex"`, `ConsoleName = "Dex"`, `DisplayName = "Dex"`, `UiOrder = 2`, `WeaponId = "Dex"`, `ExpectedStyle = "DualSwordCombatStyle"` (singular "Sword").
3. **Strict FName Semantics (`exact_fname_equal`):**
   * Case-insensitive ASCII comparison.
   * **Whitespace is significant**: in Unreal Engine, `FName(" Strength ") != FName("Strength")`.
4. **Canonical Path & Anti-Traversal Enforcement:**
   * Enforces authorized project roots (`/Game/OneBossFight/Data/Catalog/`, `/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/`).
   * Rejects path traversal (`..`), empty segments (`//`), backslashes (`\`), sub-object colons (`:`), and non-canonical characters.
5. **Finite Numeric Domain Verification:**
   * Validates strict finite integers and floats.
   * Rejects booleans (which are subclasses of `int` in Python), `NaN`, positive infinity, and negative infinity.
6. **Immutable Deep Source Snapshotting (`SourceInventorySnapshot`):**
   * Uses `copy.deepcopy` upon initialization so that any post-snapshot mutation of source build or weapon objects cannot alter the snapshot baseline.
   * Deeply compares weapon arrays, build arrays, ordering, field values, and complete package sets/statuses.
   * Fails closed if any package became dirty or missing.
7. **Cloned Catalog Read-Back Verification:**
   * Verifies that the cloned catalog contains all original builds in the exact same order, plus exactly one new reference pointing to the custom build.

---

8. **Native Arithmetic Floors & Capability Domains (`authoring_core.py`):**
   * Aligned directly with native backend constraints in `Source/OneBossFight/Boss/RPGBossPhaseAdapters.cpp` and `RPGBossStatsAdapters.cpp`:
     * `NATIVE_HEALTH_OVERRIDE_FLOOR = 1.0` (`RPGBossStatsAdapters.cpp:95`): MaxHealth must be strictly `> 1.0` for native override activation.
     * `NATIVE_DAMAGE_SCALE_FLOOR = 1.0` (`RPGBossPhaseAdapters.cpp:149`): AttackMultiplier must be strictly `>= 1.0` so damage scaling can be reversed by native baseline reset.
     * `MaxPosture > 0.0` (`RPGBossStatsAdapters.cpp:79`): zero or negative posture is rejected by native backend.
     * `0.0 < EntryHealthFraction <= 1.0` (`RPGBossPhaseAdapters.cpp:122`): health fraction of 0.0 is strictly illegal; native phase transitions require strictly positive entry fraction.
     * `SpeedMultiplier > 0.0` and `RateMultiplier > 0.0` with finite float inverses (`RPGBossPhaseAdapters.cpp:131, 138, 143`).

---

9. **Native JSON to Generated Python Property Mapping (`PyGenUtil::PythonizePropertyName` Parity):**
   * Translates native C++ PascalCase / CamelCase property names into generated UE5.5 Python snake_case identifiers.
   * Strips boolean `b` prefix (e.g. `bResetOnPlayerRespawn` -> `reset_on_player_respawn`, `bHoldPostureAtZero` -> `hold_posture_at_zero`, `bFireballEnabled` -> `fireball_enabled`).
   * Explicitly populates typed struct constructor dictionaries (`map_native_dict_to_python_keys`) so that `PyWrapperStruct.cpp:CastPyObject` finds generated `InitParam.ParamName` keys and avoids silent default-loss.
10. **Canonical Primitive Readback (`extract_canonical_primitives`):**
    * Inspects actual struct attributes, `FVector2D`, and soft object paths from Unreal Python wrappers, translating them back to canonical primitive JSON dictionaries.
    * Compares every scalar and array directly with the requested non-default values, asserting exact equality.
11. **Complete Native Capability & Scalar Domain Enforcement:**
    * `StaggerPolicy`: non-negative fields (`StaggerSeconds`, `FreezeAtPosition`, `RiposteRange`, `RiposteArmSeconds`, `RipostePlayerStartGap`, `RiposteImpactSeconds`, `RiposteBaseDamage`, `CooldownSeconds >= 0.0`), strictly positive division fields (`RiposteAlignSeconds > 0.0`, `GetUpRate > 0.0` with finite inverses), angular ranges `[0.0, 360.0]`, and `CriticalMultiplier >= 1.0` (`NATIVE_CRITICAL_MULTIPLIER_FLOOR = 1.0`).
    * `EncounterPolicy`: `GateRadius >= 0.0` (cm horizontal; 0 = no gate).
    * `PhaseFlow`: `TransitionSeconds >= 0.0`.
    * `Fireball`: cooldown `[min, max]` with `min >= 0.0` and `max >= min`; ranges `min >= 0.0` and `max >= min`.
    * `Stats`: `MaxHealth > 1.0` (`NATIVE_HEALTH_OVERRIDE_FLOOR`), `MaxPosture > 0.0`, `PostureRegenDelay/Rate >= 0.0`.
    * `Phases`: `0.0 < EntryHealthFraction <= 1.0`, `SpeedMultiplier/RateMultiplier > 0.0` with finite inverse, `AttackMultiplier >= 1.0` (`NATIVE_DAMAGE_SCALE_FLOOR`).
12. **Future Unreviewed Profile Boundary (DD19 Qualification):**
    * In accordance with `[X-293]`, DD19's upcoming reflected `Bleed` profile is recognized as future scope and is deliberately excluded from this frozen toolkit release pending formal native schema acceptance.

---

## 3. Staged Authoring Workflow & Anti-Overwrite Policy

All authoring tools implement a defensive three-phase lifecycle:

1. **Dry-Run Mode (Default):**
   * Validates input parameters, checks namespace collisions, inspects source packages, verifies destination paths, and outputs a formatted Proposed Plan.
   * Zero writes, zero saves, zero engine mutations.
2. **In-Memory Apply Mode (`--apply`):**
   * Creates Data Assets in memory only using explicit `set_editor_property` and soft object paths.
   * Populates and verifies read-back for **all 15 typed struct and manifest properties**.
   * **Does not save to disk by default.**
3. **Explicit Save Opt-in (`--apply --save`):**
   * Saves newly created output packages to disk only when explicitly requested.
   * Verifies source packages remain clean. Any source drift blocks saving.
4. **Anti-Overwrite Protection:**
   * If target output packages already exist on disk or in memory before creation, execution halts with a fatal refusal.
   * **Existing outputs block retry.** Re-running the command after an apply will not silently overwrite, delete, or recreate assets.

---

## 4. Draft Boss & Player Profiles (`draft_boss_profiles.py`)

Authors `URPGBossDefinition` assets from JSON specifications matching `native_profile_schema.json`:

* **Exact Native Reflected Fields:**
  * `Stats`: `MaxHealth`, `MaxPosture`, `PostureRegenDelay`, `PostureRegenRate` (finite non-negative floats).
  * `EncounterPolicy`: `GateRadius` (float), `bResetOnPlayerRespawn` (bool).
  * `StaggerPolicy`: `StaggerSeconds`, `FreezeAtPosition`, `CriticalMultiplier`, `RiposteRange`, `RiposteConeDegrees`, `RiposteFacingDegrees`, `RiposteArmSeconds`, `RipostePlayerStartGap`, `RiposteAlignSeconds`, `RiposteImpactSeconds`, `RiposteBaseDamage`, `CooldownSeconds`, `GetUpRate`, `bHoldPostureAtZero`.
  * `PhaseFlow`: `TransitionSeconds`, `bUseRoarClip`, `bPausePostureInTransition`, `bLockLeapUntilPhaseTwo`, `AttackAbilityPrefix`, `LeapAbilityTag`.
  * `Fireball`: `bFireballEnabled`, `FireballAbility`, `FireballCooldown` (2-float array), `FireballMinRange`, `FireballMaxRange`.
  * `PhaseDependencies`: `RoarClip`, `TransitionMontage`, `ImmunityEffect`.
  * `StaggerProfile`: `bUseClips`, `bUseRiposteClips`, `bCriticalOnEveryHit`, `HitStunAbilityClassName`, `FallMontage`, `GetUpMontage`, `FallClip`, `DownClip`, `RipostePlayerClip`, `RiposteBossClip`, `ImmunityEffect`.
  * `DormantWake`: `DormantClip`, `WakeClip`.
  * `Phases`: `PhaseId`, `EntryHealthFraction` (domain `0.0 < EntryHealthFraction <= 1.0` strictly enforced per `RPGBossPhaseAdapters.cpp:122`), `SpeedMultiplier`, `RateMultiplier`, `AttackMultiplier`.
  * `Fields`: Empty `[]` for draft status (no fabricated 51-row provenance manifest).
* **Pinned Existing Assets on Disk:**
  * Skeleton: `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin.SK_CombatMannequin`
  * Animations: `/Game/OneBossFight/Boss01/Animations/AN_Boss01_A1_QuickSlash.AN_Boss01_A1_QuickSlash` and `AN_Boss01_A3a_Combo1.AN_Boss01_A3a_Combo1`
* **Complete Readback Verification:**
  * `execute_draft_apply` sets and reads back all 15 properties via `set_editor_property` and `get_editor_property`, asserting exact equality before returning success.

---

## 5. Complete Typed Asset Inspector (`inspect_authored_assets.py`)

* **Strictly Read-Only:** Zero setters, zero asset creation/duplication, zero deletions, zero saves.
* **Non-PIE and Editor Guard:** Verifies Editor environment and non-PIE mode.
* **Non-Intrusive Invariant:** Snapshots package dirty states before and after inspection to guarantee zero dirtiness is introduced.
* **Complete Typed Snapshots:** Exports full reflected properties for all asset classes:
  * Catalog: schema_version, weapons, builds.
  * Build definitions: build_id, console_name, aliases, display_name, ui_order, legacy_slot, weapon_id.
  * Weapon definitions: weapon_id, style_name, item_path, bRequireExactRows.
  * Boss definitions: schema, definition_id, presentation_id, skeleton, animations, stats, encounter_policy, stagger_policy, phase_flow, fireball, phase_dependencies, stagger_profile, dormant_wake, phases, fields.
* **Fail-Closed Diagnostics:** Returns non-zero CLI exit code (`1`) if any asset does not exist, fails to load, has unrecognized class, or if package states drift.

---

## 6. Offline Unit Test Suite Results (`test_run_output.txt`)

Executed with Python standard library `unittest`:
```bash
python Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/test_authoring_core.py -v
```

* **Results:** **70/70 tests PASS** (0 failures, 0 errors, exit code `0`).
* **Coverage:**
  * Native-to-Python property name mapping (`pythonize_property_name`): PascalCase to snake_case, boolean prefix stripping (`bResetOnPlayerRespawn` -> `reset_on_player_respawn`).
  * Explicit struct dictionary constructor mapping (`map_native_dict_to_python_keys`) and canonical primitive readback (`extract_canonical_primitives`).
  * Recording fake writer enforcing UE5.5 `PyWrapperStruct` attribute lookup and catching default-loss / unmapped CamelCase dict regressions.
  * Complete scalar-domain validation: `StaggerPolicy` (non-negatives, strictly positive division fields, angular bounds, `CriticalMultiplier >= 1.0`), `EncounterPolicy` (GateRadius >= 0), `PhaseFlow` (TransitionSeconds >= 0), `Fireball` (cooldown min/max, range bounds), `Stats` (MaxHealth > 1.0, MaxPosture > 0.0), and `Phases` (0.0 < fraction <= 1.0, positive multipliers, attack scale floor).
  * Strict fail-closed editor guard (`verify_editor_environment`): 8 permutations covering offline refusal, empty unreal namespace refusal, missing `is_editor`, `is_editor() == False`, missing `get_editor_subsystem`, subsystem returning None, PIE mode refusal, and valid editor acceptance.
  * Strict Unreal API presence check in `execute_draft_apply`: verifies `AssetToolsHelpers`, `EditorAssetLibrary`, `DataAssetFactory`, `load_class`, `Name`, `SoftObjectPath` before any write.
  * Exact native normalization parity (`""off""` -> `'"off"'`, `TrimQuotesInline`).
  * FName case-insensitivity without whitespace stripping.
  * Path traversal, sub-object colon, and unauthorized root rejections.
  * Finite integer and float boundary checks (anti-NaN, anti-Infinity, anti-bool).
  * Build namespace collision and reserved keyword rejections.
  * Pinned 3-build legacy contract validation (Starter/SwordCombatStyle, Dex/DualSwordCombatStyle).
  * Deep source inventory snapshot comparison, mutation isolation, and package set drift detection.
  * Cloned catalog readback ordering and parity verification.
  * Draft boss profile validation against native schema (rejection of NaN multipliers, invented fields, invalid bools, and phase domain checks).
  * Recording fake writer verification proving that `execute_draft_apply` sets and reads back all 15 properties with zero omissions.
  * Partial operation report records.

---

## 7. Delivered Artifacts
| Path | Description |
| :--- | :--- |
| `Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/authoring_core.py` | Pure Python shared validation core (standard library only) |
| `Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/draft_boss_profiles.py` | Staged DRAFT creator for URPGBossDefinition assets |
| `Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/inspect_authored_assets.py` | Read-only complete typed asset inspector & JSON exporter |
| `Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/test_authoring_core.py` | Comprehensive standard-library unittest suite (70 tests) |
| `Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/test_run_output.txt` | Raw test suite execution output (70/70 PASS, exit 0) |
| `Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/examples/boss_draft_profiles.json` | Sample draft boss and player profile definitions |
| `Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/original_A178/` | Byte-exact preserved A-178 historical deliverables |
| `Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/original_A179/` | Byte-exact preserved A-179 historical deliverables |
| `Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/README.md` | Integrated architecture, safeguards, and verification guide |
| `Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/evidence_sha256.txt` | Cryptographic SHA-256 evidence receipt |
| `Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/author_custom_build.py` | Updated build authoring helper integrating authoring_core |
| `Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/original_A176/` | Preserved byte-exact A-176 deliverables |
| `Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/original_A177/` | Preserved byte-exact A-177 deliverables |
| `Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/original_A178/` | Preserved byte-exact A-178 deliverables |
