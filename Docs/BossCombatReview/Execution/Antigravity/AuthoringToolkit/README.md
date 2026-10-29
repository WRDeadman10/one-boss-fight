# OneBossFight Authoring Toolkit (AG-CONTENT19 REV27)

**Author:** Antigravity (Party Code A) - Senior C++ Implementer & Unreal Engine Specialist  
**Work Order:** [C-343] / AG-CONTENT19 (Order A-226: Witness Grounding & Repeatable --only Asset Selector)  
**Review Status:** Delivery A-226 submitted for Lead Reviewer Claude (C) and Implementer Codex (X). Work Orders [C-294] through [C-343].  
**Preserved Archives:** original_A178/ through original_A226/ preserved byte-for-byte.  
**Execution Boundary:** **STRICTLY OFFLINE IMPLEMENTATION**. Zero Unreal Engine processes launched; zero assets created, mutated, or deleted; zero pack edits; zero git commits or pushes.

---

## Offline Float64 Qualification & IEEE 754 float32 Storage Parity

> [!IMPORTANT]
> **Offline float64 checks do NOT certify native float32 conversion or input-mode parity.**  
> All offline tests and validators execute in CPython where floating-point literals and operations default to 64-bit IEEE 754 double precision (`float64`). In contrast, Unreal Engine native C++ `UProperty` / `FProperty` fields on `UStruct` and `UObject` (e.g. `MaxHealth`, `EntryHealthFraction`, `RiposteAlignSeconds`, `InitialThreshold`, `HpFraction`, `Damage`, `Reach`, `InnerRadius`, `BladeHeight`, `SweepFromDegrees`, `SweepToDegrees`) store 32-bit single-precision floats (`float32`).  
> The authoring toolkit uses Python's standard `struct.pack('f')` / `struct.unpack('f')` (`to_float32`) to simulate native float32 truncation and verify that valid float32 values survive round-trip without precision drift or unexpected readback failure (e.g., `0.35` -> `0.3499999940395355`, `0.03` -> `0.029999999329447746`).  
> Requested scalar values that are finite in float64 but overflow the IEEE 754 32-bit float range (`> 3.402823466e+38`) are strictly refused with `ValueError` / diagnostic refusal. However, offline unit test execution does not execute live UE5.5 C++ serialization, runtime memory layout, or input-mode controller parity.

---

## 1. Architecture Overview & Components

The **OneBossFight Authoring Toolkit** provides a pure, defensive, staged Python infrastructure for inspecting, validating, authoring, and exporting gameplay Data Assets for Unreal Engine 5.5.

The toolkit connects four cohesive deliverables:

```
AuthoringToolkit/
├── authoring_core.py                 <-- Pure Python shared validation core (standard library only)
├── draft_boss_profiles.py            <-- Staged DRAFT creator for boss & player participant URPGBossDefinition assets
├── inspect_authored_assets.py        <-- Read-only complete typed asset inspector & JSON exporter (zero mutations)
├── test_authoring_core.py            <-- Standard library unittest test suite (128 adversarial & regression tests)
├── test_run_output.txt               <-- Raw test suite execution output (128/128 PASS, exit code 0)
├── examples/
│   └── boss_draft_profiles.json      <-- Explicit two-boss + one-player draft profile specifications (exact native schema)
├── original_A178/                    <-- Byte-exact preserved A-178 historical delivery
├── original_A179/                    <-- Byte-exact preserved A-179 historical delivery
├── original_A180/                    <-- Byte-exact preserved A-180 historical delivery
├── original_A181/                    <-- Byte-exact preserved A-181 historical delivery
├── original_A182/                    <-- Byte-exact preserved A-182 historical delivery
├── original_A183/                    <-- Byte-exact preserved A-183 historical delivery
├── original_A184/                    <-- Byte-exact preserved A-184 historical delivery
├── README.md                         <-- This integrated architecture and usage specification
└── evidence_sha256.txt               <-- Cryptographic SHA-256 evidence receipt

BuildAuthoringHelper/
├── author_custom_build.py            <-- Staged custom build & cloned catalog authoring helper (imports authoring_core)
├── original_A176/                    <-- Byte-exact preserved A-176 historical delivery
├── original_A177/                    <-- Byte-exact preserved A-177 historical delivery
├── original_A178/                    <-- Byte-exact preserved A-178 historical delivery
├── original_A179/                    <-- Byte-exact preserved A-179 historical delivery
├── original_A180/                    <-- Byte-exact preserved A-180 historical delivery
├── original_A181/                    <-- Byte-exact preserved A-181 historical delivery
├── original_A182/                    <-- Byte-exact preserved A-182 historical delivery
├── original_A183/                    <-- Byte-exact preserved A-183 historical delivery
├── original_A184/                    <-- Byte-exact preserved A-184 historical delivery
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
8. **Native Arithmetic Floors & Capability Domains (`authoring_core.py`):**
   * Aligned directly with native backend constraints in `Source/OneBossFight/Boss/RPGBossPhaseAdapters.cpp` and `RPGBossStatsAdapters.cpp`:
     * `NATIVE_HEALTH_OVERRIDE_FLOOR = 1.0` (`RPGBossStatsAdapters.cpp:95`): MaxHealth must be strictly `> 1.0` for native override activation.
     * `NATIVE_DAMAGE_SCALE_FLOOR = 1.0` (`RPGBossPhaseAdapters.cpp:149`): AttackMultiplier must be strictly `>= 1.0` so damage scaling can be reversed by native baseline reset.
     * `MaxPosture > 0.0` (`RPGBossStatsAdapters.cpp:79`): zero or negative posture is rejected by native backend.
     * `0.0 < EntryHealthFraction <= 1.0` (`RPGBossPhaseAdapters.cpp:122`): health fraction of 0.0 is strictly illegal; native phase transitions require strictly positive entry fraction.
     * `SpeedMultiplier > 0.0` and `RateMultiplier > 0.0` with finite float inverses (`RPGBossPhaseAdapters.cpp:131, 138, 143`).
9. **Native JSON to Generated Python Property Mapping (`PyGenUtil::PythonizePropertyName` Parity):**
   * Translates native C++ PascalCase / CamelCase property names into generated UE5.5 Python snake_case identifiers.
   * Strips boolean `b` prefix (e.g. `bResetOnPlayerRespawn` -> `reset_on_player_respawn`, `bHoldPostureAtZero` -> `hold_posture_at_zero`, `bFireballEnabled` -> `fireball_enabled`, `bEnabled` -> `enabled`).
   * Explicitly populates typed struct constructor dictionaries (`map_native_dict_to_python_keys`) so that `PyWrapperStruct.cpp:CastPyObject` finds generated `InitParam.ParamName` keys and avoids silent default-loss.
   * Covers all 79 fields across 12 native structs with 100% test coverage against pinned reference files.
   * **Provenance Limit (Digit Handling in PyGenUtil):** The generated Python property names for CloseClipSwap (close_ability_class_name, ttack_montages_name, 1_montage, 3a_montage, 3b_montage) follow the engine digit rule as analyzed in A-181. The first real proof of the digit names is the Codex-operated engine readback, not this offline test.
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
12. **Soft Object Path Lexical Pre-Check & Engine Macros Parity:**
    * Exact character sets copied from Unreal Engine 5.5 source headers:
      - `Core/Public/UObject/NameTypes.h:168`:
        `INVALID_OBJECTNAME_CHARACTERS = "\"' ,/.:|&!~\n\r\t@#(){}[]=;^%$`"`
      - `Core/Public/UObject/NameTypes.h:174`:
        `INVALID_LONGPACKAGE_CHARACTERS = "\\:*?\"<>|' ,.&!~\n\r\t@#"`
    * `validate_soft_path_structure` checks:
      1. Path must begin with leading slash (`/`).
      2. No whitespace or control characters (`< 32`).
      3. No sub-object delimiter (`:`).
      4. Must contain package folder (last slash > 0).
      5. Must terminate in `<package>.<asset>` format.
      6. Package string must contain zero characters from `INVALID_LONGPACKAGE_CHARACTERS`.
      7. Package segments cannot be empty, `.`, or `..`.
      8. Asset object name must contain zero characters from `INVALID_OBJECTNAME_CHARACTERS`.
    * **Lexical Pre-check Qualification:** This check is a lexical pre-check that mirrors, not replaces, the engine validators (`FPackageName::IsValidTextForLongPackageName` and `FName::IsValidXName`). Agreement beyond these two macros (such as operating system file path length limits or platform reserved names) is not claimed.
13. **DD20 `FRPGLowSweepConfig` Reflected Domain & Validation Invariants (`RPGBossLowSweepAdapters.cpp` Parity):**
    * **Status Qualification:** Reflected implementation in toolkit is staged pending DD20 live verification run by Codex.
    * **MoveId Qualification:** `MoveId` text validation is **SYNTACTIC IDENTITY ONLY** (verifies non-empty FName and absence of whitespace/control characters). It does NOT prove tracker resolution, timing, or that an ability ever fires.
    * Reflected fields (8 authored properties):
      - `bEnabled` (bool, default `True`): accepts both boolean states; disabled records still validate completely.
      - `MoveId` (FName, default `"A4"`): required, non-empty, not `"None"`, no whitespace or control characters (`InvalidDependency.Missing` / `InvalidDependency.Malformed`).
      - `Damage` (float, default `20.0`): finite, `>= 0.0` (`InvalidLowSweep.Negative: LowSweep.Damage`). Zero damage is legal.
      - `Reach` (float, default `380.0`): finite, `> 0.0` (`InvalidLowSweep.NotPositive: LowSweep.Reach`). Fractional sub-1 reach (e.g. 0.5) is accepted (no editor min-1 floor).
      - `InnerRadius` (float, default `60.0`): finite, `>= 0.0` (`InvalidLowSweep.Negative: LowSweep.InnerRadius`). Zero inner radius is legal.
      - `InnerRadius < Reach`: strictly enforced (`InvalidLowSweep.InnerNotBelowReach: LowSweep.InnerRadius`).
      - `BladeHeight` (float, default `40.0`): finite, `> 0.0` (`InvalidLowSweep.NotPositive: LowSweep.BladeHeight`). Fractional sub-1 height (e.g. 0.4) is accepted.
      - `SweepFromDegrees` & `SweepToDegrees` (floats, defaults `90.0`, `-90.0`): finite, in `[-360.0, 360.0]` (`InvalidLowSweep.AngleOutOfRange`).
      - Equal angles (`SweepFromDegrees == SweepToDegrees`) are legal and form a stationary band.
      - Reversed angles (`SweepFromDegrees < SweepToDegrees` or `SweepFromDegrees > SweepToDegrees`) are legal.
      - Exact `+-360.0` endpoints are legal.
    * Validation ordering strictly preserves native error precedence:
      1. Non-finite scalars fail first across ALL SIX floats in declaration order (`InvalidLowSweep.NotFinite: LowSweep.<Field>`). A late non-finite float beats an earlier domain failure.
      2. Domain rules in declaration order (`Damage`, `Reach`, `InnerRadius`, `InnerRadius < Reach`, `BladeHeight`, `SweepFromDegrees`, `SweepToDegrees`).
      3. `MoveId` syntactic check (`InvalidDependency.Missing` / `InvalidDependency.Malformed`).
    * Full PyGenUtil property name mapping (`bEnabled` -> `enabled`, `MoveId` -> `move_id`, etc.).
    * Float32 readback normalization applied during draft profile apply and readback verification.

---

## 3. Staged Authoring Workflow & Anti-Overwrite Policy

All authoring tools implement a defensive three-phase lifecycle:

1. **Dry-Run Mode (Default):**
   * Validates input parameters, checks namespace collisions, inspects source packages, verifies destination paths, and outputs a formatted Proposed Plan.
   * Zero writes, zero saves, zero engine mutations.
2. **In-Memory Apply Mode (`--apply`):**
   * Creates Data Assets in memory only using explicit `set_editor_property` and soft object paths.
   * Populates and verifies read-back for **all 17 typed struct and manifest properties** (including `bleed` and `low_sweep`).
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
  * `Bleed`: `InitialThreshold`, `ThresholdIncrease`, `ThresholdMax`, `HpFraction`, `EffectHeight`, `ProcEffect`, `ProcSound` (strictly validated per `RPGBossBleedAdapters.cpp:ValidateBleed`).
  * `LowSweep`: `bEnabled`, `MoveId`, `Damage`, `Reach`, `InnerRadius`, `BladeHeight`, `SweepFromDegrees`, `SweepToDegrees` (strictly validated per `RPGBossLowSweepAdapters.cpp:ValidateLowSweep`).
  * `Fields`: Empty `[]` for draft status (no fabricated 51-row provenance manifest).
* **Pinned Existing Assets on Disk:**
  * Skeleton: `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin.SK_CombatMannequin`
  * Animations: `/Game/OneBossFight/Boss01/Animations/AN_Boss01_A1_QuickSlash.AN_Boss01_A1_QuickSlash` and `AN_Boss01_A3a_Combo1.AN_Boss01_A3a_Combo1`
* **Complete Readback Verification:**
  * `execute_draft_apply` sets and reads back all 17 properties via `set_editor_property` and `get_editor_property`, asserting exact equality before returning success.

---

## 5. Complete Typed Asset Inspector (`inspect_authored_assets.py`)

* **Strictly Read-Only:** Zero setters, zero asset creation/duplication, zero deletions, zero saves.
* **Non-PIE and Editor Guard:** Verifies Editor environment and non-PIE mode.
* **Non-Intrusive Invariant:** Snapshots package dirty states before and after inspection to guarantee zero dirtiness is introduced.
* **Complete Typed Snapshots:** Exports full reflected properties for all asset classes:
  * Catalog: schema_version, weapons, builds.
  * Build definitions: build_id, console_name, aliases, display_name, ui_order, legacy_slot, weapon_id.
  * Weapon definitions: weapon_id, style_name, item_path, bRequireExactRows.
  * Boss definitions: schema, definition_id, presentation_id, skeleton, animations, stats, encounter_policy, stagger_policy, phase_flow, fireball, phase_dependencies, stagger_profile, dormant_wake, phases, bleed, low_sweep, fields.
* **Fail-Closed Diagnostics:** Returns non-zero CLI exit code (`1`) if any asset does not exist, fails to load, has unrecognized class, or if package states drift.

---

## 6. Offline Unit Test Suite Results (`test_run_output.txt`)

Executed with Python standard library `unittest`:
```bash
python Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/test_authoring_core.py -v
```

* **Results:** **100/100 tests PASS** (0 failures, 0 errors, exit code `0`).
* **Coverage:**
  * Native-to-Python property name mapping (`pythonize_property_name`): PascalCase to snake_case, boolean prefix stripping (`bResetOnPlayerRespawn` -> `reset_on_player_respawn`, `bEnabled` -> `enabled`). Verified for all 79 native fields across 12 structs (`test_all_79_native_fields_parity`).
  * Complete DD19 Bleed Policy & Domain verification (`TestBleedPolicyDomain`): baseline validity, non-finite scalar rejection, initial threshold floor, threshold increase non-negativity, threshold max bounds, hp fraction range, signed effect height, required soft object path enforcement, soft path structural syntax, float32 overflow refusal, float32 readback normalization, and full Python property name mapping.
  * Exhaustive Character-by-Character Soft Path Tests:
    - `test_soft_path_all_invalid_longpackage_characters`: asserts rejection for every one of the 20 characters in `INVALID_LONGPACKAGE_CHARACTERS` (`\ : * ? " < > | '   , . & ! ~ \n \r \t @ #`).
    - `test_soft_path_all_invalid_objectname_characters`: asserts rejection for every one of the 28 characters in `INVALID_OBJECTNAME_CHARACTERS` (`" '   , / . : | & ! ~ \n \r \t @ # ( ) { } [ ] = ; ^ % $ ` `).
    - `test_soft_path_accept_cases`: asserts acceptance of standard `/Game` path and synthetic non-`/Game` mounts (`/Engine`, `/MyPlugin`, `/SyntheticMount`).
  * Complete DD20 Low Sweep Policy & Domain verification (`TestLowSweepPolicyDomain` - 15 tests):
    - Baseline validity.
    - Non-finite scalar float rejection across all 6 floats in declaration order (NaN, +Inf, -Inf, bool).
    - Precedence verification: late non-finite angle beating earlier domain error.
    - Damage domain (`< 0` rejected, `== 0` accepted).
    - Reach domain (`<= 0` rejected, sub-1 accepted).
    - InnerRadius domain (`< 0` rejected, `== 0` accepted).
    - InnerRadius vs Reach ordering (`>= Reach` rejected).
    - BladeHeight domain (`<= 0` rejected, sub-1 accepted).
    - Angle domains (`[-360, 360]`).
    - Equal angles (stationary band) and reversed angles acceptance.
    - Exact `+-360` bounds acceptance.
    - Disabled record (`bEnabled = False`) acceptance and continued field validation.
    - MoveId syntactic validation (None, empty, `"None"` missing rejection; whitespace/control character malformation rejection).
    - Float32 overflow refusal.
    - Float32 readback normalization.
    - Engine Python property name mapping across all 8 fields.
  * Explicit struct dictionary constructor mapping (`map_native_dict_to_python_keys`) and canonical primitive readback (`extract_canonical_primitives`).
  * Recording fake writer enforcing UE5.5 `PyWrapperStruct` attribute lookup and catching default-loss / unmapped CamelCase dict regressions across all 17 verified properties.
  * Complete scalar-domain validation: `StaggerPolicy`, `EncounterPolicy`, `PhaseFlow`, `Fireball`, `Stats`, and `Phases`.
  * Strict fail-closed editor guard (`verify_editor_environment`): 8 permutations.
  * Strict Unreal API presence check in `execute_draft_apply`.
  * Exact native normalization parity (`""off""` -> `'"off"'`, `TrimQuotesInline`).
  * FName case-insensitivity without whitespace stripping.
  * Path traversal, sub-object colon, and unauthorized root rejections.
  * Finite integer and float boundary checks (anti-NaN, anti-Infinity, anti-bool).
  * Build namespace collision and reserved keyword rejections.
  * Pinned 3-build legacy contract validation (Starter/SwordCombatStyle, Dex/DualSwordCombatStyle).
  * Deep source inventory snapshot comparison, mutation isolation, and package set drift detection.
  * Cloned catalog readback ordering and parity verification.
  * Draft boss profile validation against native schema (rejection of NaN multipliers, invented fields, invalid bools, and phase domain checks).
  * Partial operation report records.

---

---

## 6. Single-Purpose Review Aid: `diff_against_cpp.py`

Per Tech Lead Claude directive `[C-271]`, the toolkit incorporates a single-purpose, deterministic offline review aid:
`diff_against_cpp.py`.

### Purpose & Architecture
Given a path to an `RPGBoss*Adapters.cpp` (or running over all accepted adapters by default), the tool:
1. **Extracts C++ Checks in Source Order:** Parses `Validate*` in the C++ adapter and resolves `Field*` constants (e.g. `FieldDamage` -> `LowSweep.Damage`) using header and cpp definitions. It unrolls scalar loops (`FScalar Scalars[]`) checking `NotFinite` across all scalars in source order, followed by all domain `Refuse(...)` calls, `OutError = FString::Printf(...)` diagnostics, and `CheckRequiredReference(...)` soft-path checks.
2. **Extracts Python Checks in Source Order:** Parses the corresponding domain validator in `authoring_core.py` (e.g., `validate_bleed_domain`, `validate_low_sweep_domain`, `validate_shockwave_domain`, `validate_heal_punish_domain`, and `validate_look_domain`).
3. **Parity Comparison:** Mechanically compares the ordered sequences of `(Token, Field)` pairs, printing `OK` or flagging the first difference with exact source line token details.

### C-272 Review Aid Refinements (A-191)
- **Read-Only by Default:** Running `diff_against_cpp.py` with no flags executes purely in-memory and prints to standard output without touching or overwriting `diff_report.txt`. Writing to disk requires explicit `--report` or `--output <path>`.
- **Reproducible Repo-Relative Reporting:** All source file paths in the report are normalized as repo-relative forward-slash posix paths (`Source/OneBossFight/...`), resolving repo root deterministically from the script location. The resulting report is 100% byte-identical across runs, checkouts, and current working directories.
- **Fail-Closed Header Error Handling:** When an adapter `.cpp` is evaluated, the matching `.h` is strictly required next to it. If missing, the tool raises `HeaderNotFoundError` and exits with code `2` with the named diagnostic `"<Header>.h not found next to the .cpp"`, rather than generating a false difference.

### Verified Parity Results (`diff_report.txt`)
- **Bleed** (`RPGBossBleedAdapters.cpp` vs `validate_bleed_domain`): **13/13 checks OK** in exact source order.
- **LowSweep** (`RPGBossLowSweepAdapters.cpp` vs `validate_low_sweep_domain`): **15/15 checks OK** in exact source order.
- **Shockwave** (`RPGBossShockwaveAdapters.cpp` vs `validate_shockwave_domain`): **20/20 checks OK** in exact source order.
- **HealPunish** (`RPGBossHealPunishAdapters.cpp` vs `validate_heal_punish_domain`): **33/33 checks OK** in exact source order.
- **Total Parity Checks:** **81 checks verified** across all 4 accepted adapters with zero discrepancies.

---


## 7. Parity Field Manifest Generator: emit_fields_manifest.py (A-202 / C-294)

Per Tech Lead Claude directive [C-294], the toolkit incorporates a deterministic, repo-relative generator:
emit_fields_manifest.py.

### Purpose & Architecture
Produces compliant FRPGParityField rows for all 15 known clusters (106 paths) whose values are truthfully known under Lead conventions (C-294), outputting JSON formatted for draft profiles:
1. **Live Source Hashing:** Hashes defining C++ headers and source files in the working tree to populate SourceSHA256 (64-character hexadecimal).
2. **Deterministic Parity Conventions:**
   - FieldPath: 106 known paths matching DD26 preflight literals.
   - Value: Truthful string representation of native C++ constructor defaults or Lead contract values (informational audit only; unread by runtime C++).
   - Type: Declared C++ UPROPERTY type name.
   - Units: Physical unit or 'dimensionless'.
   - SourcePath: Repo-relative posix path of defining file.
   - SourceSite: Defining C++ symbol or declaration line.
   - Origin: Allowed taxonomy (NativeDefault, SubsystemOverride, LeadContract, AuthoredAsset).
   - Precedence: Fixed literal 'typed-record'.
   - Destination: Native target component member (Class::Member).
   - FirstRead: Standardized lifecycle token 'PrepareBatch.Configure'.
   - Witness: Measured automation test suite (AutomationTest:OneBossFight.Binding.<Suite>.Assign).
3. **Phase Gaps Identification:** Explicitly documents 4 phase paths (Phases[<PhaseId>].EntryHealthFraction, SpeedMultiplier, RateMultiplier, AttackMultiplier) marked as 'Needs Phase Spec' and excludes them from emission.

### Operational Boundaries & Safeguards
- **Provenance Stamp, Not a Runtime Check:** The manifest columns are informational audit records for tooling, compiler identity, and preflight completeness checks. Adapters and component configure callbacks read from typed structs, never from manifest value strings.
- **Stale Hash Risk:** SourceSHA256 reflects the live working-tree hash computed at toolkit execution time. Any subsequent source file modification will invalidate the recorded hash until the manifest is re-emitted.
- **Uncovered Clusters:** The 4 phase-dependent paths remain unpopulated pending explicit phase/profile specifications.
- **Zero Activation:** Manifest generation produces static profile JSON only; it does not wire unwired plans, activate subsystems, or alter runtime gameplay execution.

---
## 8. Read-Only Unreal API Reflection Probe: probe_unreal_api.py (A-206 / A-207 / A-209 / C-301 / C-302 / C-305)

Per Tech Lead Claude directives [C-301], [C-302], and [C-305], authored following the Codex DD27 editor guard failure ([DRAFT_APPLY] FATAL: Missing required Unreal API: unreal.SystemLibrary.is_editor) and the DD27b probe run, the toolkit incorporates a standalone, strictly read-only Unreal API reflection probe: probe_unreal_api.py.

### Purpose & Architecture
Instead of guessing which engine Python APIs, exported types, and pythonized struct properties exist in Unreal Engine 5.5.4, probe_unreal_api.py conducts a two-stage evidence-based diagnostic evaluation:

#### Stage 1: Static AST Analysis & Class-Level Reflection (Default Mode)
1. **Static AST Analysis (Works 100% Offline without unreal):**
   - Parses draft_boss_profiles.py, uthoring_core.py, and inspect_authored_assets.py using Python's standard st module.
   - Extracts all attribute chains rooted at unreal (e.g. unreal.EditorAssetLibrary.does_asset_exist, unreal.SystemLibrary.is_editor, unreal.AssetToolsHelpers.get_asset_tools, unreal.load_class, etc.) with exact ile:line citations.
   - Extracts candidate reflective types dynamically from C++ source headers (Source/OneBossFight/Player/RPGEncounterBinding.h and native component headers) and strips C++ prefix letters (F for structs, U/A for classes, E for enums) to derive true Python wrapper names (e.g. FRPGBleedConfig -> RPGBleedConfig, FRPGDeathConfig -> RPGDeathConfig, ERPGBossDeathMode -> RPGBossDeathMode).
   - Extracts expected pythonized property mappings across all 17 structs defined in STRUCT_SPECS in uthoring_core.py (e.g. 1_montage, stagger_seconds, death_mode, guard_pack_death).
2. **Runtime Reflection Probe (Active only when import unreal succeeds):**
   - **Static Chain Resolution:** Tests existence (hasattr), callability (callable), and runtime type for every extracted attribute chain without invoking mutations or loading packages.
   - **Dual C++ / Python Name Verification:** Tests BOTH the native C++ name (cpp=<Name>) and the prefix-stripped Python name (py=<Name>) for every candidate type: [PROBE] type cpp=<cpp_name> py=<py_name> exists_cpp=<b> exists_py=<b>.
   - **Library Public Member Discovery:** Dumps the full sorted list of public members (dir() without underscores) for key editor libraries (SystemLibrary, EditorAssetLibrary, AssetToolsHelpers, UnrealEditorSubsystem, and the AssetTools instance) to discover truthful replacement APIs for editor checks from engine evidence.
   - **Filtered Symbol Inventory:** Scans dir(unreal) for all exported symbols matching keywords: Editor, Subsystem, AssetTools, DataAsset, Factory, Load, Save, RPG.
   - **Struct Property Matching:** For all 17 authored structs, compares class property names from dir() against uthoring_core.py pythonized names, reporting explicit MATCH or MISMATCH.
   - **Enum Member Matching:** Compares RPGBossDeathMode enumerator names against toolkit values (PackMontage, OwnClip), reporting explicit MATCH or MISMATCH.

#### Stage 2: In-Memory Instance & CDO Probe (--instances Mode, C-305 / A-209)
Active only when --instances is explicitly passed; default is off so the Stage 1 report remains 100% byte-identical.
1. **Transient Struct Instantiation (unreal.<py_struct>()):**
   - Constructs ONE in-memory instance per authored struct (17 structs) using default constructors.
   - **Harmlessness Guarantee:** Instantiates a plain Python/UStruct wrapper in memory; does not create a UObject, does not touch package manager, does not register with any subsystem, and performs zero disk writes.
2. **Instance Property Queries (inst.get_editor_property(prop) & hasattr):**
   - Tests whether pythonized snake_case property names are accessible via get_editor_property.
   - On the first failure for any struct, automatically tests the native C++ PascalCase spelling (INSTANCE_ALT_CPP) to determine whether the engine wrapper expects snake_case or PascalCase keys.
   - Explicitly prints scalar values for float-typed properties (alue=<val>).
   - Explicitly prints type names for complex members (arrays, soft paths, enums, structs): SpawnSockets, Pieces, DeathMode, Fields.
3. **Class Default Object (CDO) Inspection (unreal.RPGBossDefinition.get_default_object()):**
   - Retrieves the class default object singleton without mutating it.
   - Tests get_editor_property across all top-level definition properties set by the authoring toolkit (schema, definition_id, presentation_id, skeleton, nimations, phases, ields, and the 15 typed component sub-structs).
4. **Module-Level Editor Mode Query (unreal.is_editor):**
   - Checks presence and type of unreal.is_editor. If callable, executes it once and prints the boolean return value.

### Full List of Calls Performed in Stage 2 (--instances)
1. unreal.RPGBossStatsConfig() (transient in-memory struct)
2. unreal.RPGEncounterPolicyConfig() (transient in-memory struct)
3. unreal.RPGStaggerPolicyConfig() (transient in-memory struct)
4. unreal.RPGPhaseFlowConfig() (transient in-memory struct)
5. unreal.RPGFireballConfig() (transient in-memory struct)
6. unreal.RPGPhaseDependencyConfig() (transient in-memory struct)
7. unreal.RPGStaggerProfileConfig() (transient in-memory struct)
8. unreal.RPGDormantWakeConfig() (transient in-memory struct)
9. unreal.RPGBleedConfig() (transient in-memory struct)
10. unreal.RPGLowSweepConfig() (transient in-memory struct)
11. unreal.RPGShockwaveConfig() (transient in-memory struct)
12. unreal.RPGHealPunishConfig() (transient in-memory struct)
13. unreal.RPGLookConfig() (transient in-memory struct)
14. unreal.RPGCloseClipSwapConfig() (transient in-memory struct)
15. unreal.RPGDeathConfig() (transient in-memory struct)
16. unreal.RPGPhaseConfig() (transient in-memory struct)
17. unreal.RPGParityField() (transient in-memory struct)
18. inst.get_editor_property(prop_name) (read-only property lookup on in-memory instance)
19. hasattr(inst, prop_name) (read-only attribute lookup on in-memory instance)
20. unreal.RPGBossDefinition.get_default_object() (read-only CDO retrieval)
21. cdo.get_editor_property(top_prop) (read-only property lookup on CDO)
22. unreal.is_editor() (read-only editor state query function call)

### Execution Safety Guarantees
- **STRICTLY READ-ONLY:** Zero asset creation, zero asset loading, zero save operations, zero editor property writes (set_editor_property), zero package registry scans.
- Zero disk writes unless explicit --output <path> is provided.
- Always exits with code 0 ([PROBE] SUMMARY missing=<n> present=<n>) as a diagnostic inquiry tool.
- **An offline run proves nothing about the engine:** all runtime presence checks, type reflection, library members, and instance property matches require live execution inside Unreal Engine Python.

---

## 9. Engine Reflection Truths

### Ground Truth from DD27e Soft-Path Probe Run (Order A-214 / Lead C-318)
The Codex DD27e probe run captured definitive runtime evidence from live Unreal Engine 5.5.4 editor reflection (`softref_lines_verbatim.txt`):
1. **Rejection of `str` and `SoftObjectPath` (`softref_lines_verbatim.txt` lines 3, 4, 8, 9, 13, 14):**
   - Line 3: `[PROBE] SOFTREF RPGBleedConfig.proc_effect form=str result=error:TypeError: RPGBleedConfig: Failed to convert type 'str' to property 'ProcEffect' (SoftObjectProperty) ... Cannot nativize 'str' as 'ProcEffect' ... Cannot nativize 'str' as 'Object' (allowed Class type: 'NiagaraSystem')`
   - Line 4: `[PROBE] SOFTREF RPGBleedConfig.proc_effect form=SoftObjectPath_ctor result=error:TypeError: RPGBleedConfig: Failed to convert type 'SoftObjectPath' ... Cannot nativize 'SoftObjectPath' as 'Object' (allowed Class type: 'NiagaraSystem')`
   - Line 1: `unreal.SoftObjectPath` members: `['assign', 'cast', 'copy', 'export_text', 'get_editor_property', 'import_text', 'set_editor_properties', 'set_editor_property', 'static_struct', 'to_tuple']`. It exposes no path constructor, no `set_path`, and no `asset_path_name`.
2. **Acceptance of Loaded UObject (`softref_lines_verbatim.txt` lines 5, 7, 10, 12):**
   - Line 7: `[PROBE] SOFTREF RPGBleedConfig.proc_effect form=load_asset result=ok readback_type=NiagaraSystem readback_repr=<Object '/Game/BloodPack/Hit/Niagara/NS_BulletHit_Med.NS_BulletHit_Med' ... Class 'NiagaraSystem'>`
   - Line 12: `[PROBE] SOFTREF RPGLookConfig.body form=load_asset result=ok readback_type=SkeletalMesh readback_repr=<Object '/Game/OneBossFight/Boss01/Body/SK_Boss01_Body.SK_Boss01_Body' ... Class 'SkeletalMesh'>`
   - Line 5 & 10: `form=none result=ok readback_type=NoneType readback_repr=None`
3. **Array Properties (`softref_lines_verbatim.txt` lines 13, 14, 15, 16, 17):**
   - Line 13 & 14: `pieces form=list_str / list_SoftObjectPath result=error:TypeError: ... Cannot nativize 'str' / 'SoftObjectPath' as 'TransientPythonProperty'`
   - Line 15: `pieces form=list_none result=ok`
   - Line 16: `pieces form=empty_list result=ok`
   - Line 17: `pieces form=list_load_asset result=ok readback_type=Array`
4. **Open Question Residual Limit:**
   - The probe evidence establishes that valid existing assets load cleanly into memory and nativize into `TSoftObjectPtr` properties as loaded `UObject` instances.
   - The probe evidence does NOT answer whether a failed load or a path to a not-yet-existing asset can be authored by any other API (e.g. C++ serialization or asset registry hooks).
   - In accordance with Order A-214, the helper strictly enforces that any missing or unloadable asset is a recorded failure (`convert` step) in diagnostic mode, and an immediate fail-fast error in `--save` mode.

### Script-Derived Asset Existence Audit (Orders A-214 & A-216 / Lead C-324)
Per Tech Lead Claude directive `[C-324]` and Codex's DD29 evidence (`C320_profile_path_count_comparison.json`), the asset paths were extracted directly by script from `examples/boss_draft_profiles.json` and audited against the working tree on disk (`Content/**/*.uasset`):
- **Total Distinct `/Game` Asset Paths in JSON:** 27
- **Total Property References in JSON:** 80
- **Assets Present on Disk:** 27 / 27 (100% Present)
- **Missing Assets:** 0 (Zero missing assets)
- **Metadata Directory String:** 1 (`/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/`, excluded as non-asset container path)

Every referenced skeletal mesh, static mesh, montage, animation sequence, Niagara system, sound cue, and gameplay effect blueprint exists on disk under `Content/`. Therefore, live `unreal.EditorAssetLibrary.load_asset(path)` calls will succeed for all drafted profiles.

#### Verified 27-Asset Presence Matrix:
| # | Asset Package Path | On Disk | Refs | Profile JSON Location Pointers |
| :- | :--- | :-: | :-: | :--- |
| 1 | `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin.SK_CombatMannequin` | **True** | 3 | `profiles[0..2].skeleton` |
| 2 | `/Game/AdvancedARPGCombat/MagicCombatSystem/Blueprints/AI/ExampleMagicEnemy/GA_Fireball_Enemy.GA_Fireball_Enemy_C` | **True** | 3 | `profiles[0..2].fireball.FireballAbility` |
| 3 | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/Ability_R_Intro_Anim_Montage.Ability_R_Intro_Anim_Montage` | **True** | 3 | `profiles[0..2].phase_dependencies.TransitionMontage` |
| 4 | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/KnockdownStart_Anim_Montage.KnockdownStart_Anim_Montage` | **True** | 3 | `profiles[0..2].stagger_profile.FallMontage` |
| 5 | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/Knockdown_Getup_Anim_Montage.Knockdown_Getup_Anim_Montage` | **True** | 3 | `profiles[0..2].stagger_profile.GetUpMontage` |
| 6 | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C` | **True** | 6 | `profiles[0..2].phase_dependencies/stagger_profile.ImmunityEffect` |
| 7 | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue.A_Guardian_ImpactL_Cue` | **True** | 3 | `profiles[0..2].bleed.ProcSound` |
| 8 | `/Game/BloodPack/Hit/Niagara/NS_BulletHit_Med.NS_BulletHit_Med` | **True** | 3 | `profiles[0..2].bleed.ProcEffect` |
| 9 | `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A1.AM_Boss01_A1` | **True** | 3 | `profiles[0..2].close_clip_swap.A1Montage` |
| 10 | `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3a.AM_Boss01_A3a` | **True** | 3 | `profiles[0..2].close_clip_swap.A3aMontage` |
| 11 | `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3b.AM_Boss01_A3b` | **True** | 3 | `profiles[0..2].close_clip_swap.A3bMontage` |
| 12 | `/Game/OneBossFight/Boss01/Animations/AM_Boss01_DeathLegend.AM_Boss01_DeathLegend` | **True** | 3 | `profiles[0..2].death.DeathMontage` |
| 13 | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_A1_QuickSlash.AN_Boss01_A1_QuickSlash` | **True** | 1 | `profiles[0].animations[0]` |
| 14 | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_A3a_Combo1.AN_Boss01_A3a_Combo1` | **True** | 1 | `profiles[1].animations[0]` |
| 15 | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_DeathLegend.AN_Boss01_DeathLegend` | **True** | 3 | `profiles[0..2].death.DeathClip` |
| 16 | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_DormantIdle.AN_Boss01_DormantIdle` | **True** | 3 | `profiles[0..2].dormant_wake.DormantClip` |
| 17 | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_PhaseRoar.AN_Boss01_PhaseRoar` | **True** | 3 | `profiles[0..2].phase_dependencies.RoarClip` |
| 18 | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_StaggerDown.AN_Boss01_StaggerDown` | **True** | 3 | `profiles[0..2].stagger_profile.DownClip` |
| 19 | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_StaggerFall.AN_Boss01_StaggerFall` | **True** | 3 | `profiles[0..2].stagger_profile.FallClip` |
| 20 | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Wake.AN_Boss01_Wake` | **True** | 3 | `profiles[0..2].dormant_wake.WakeClip` |
| 21 | `/Game/OneBossFight/Boss01/Animations/AN_Riposte_Boss_Reaction.AN_Riposte_Boss_Reaction` | **True** | 3 | `profiles[0..2].stagger_profile.RiposteBossClip` |
| 22 | `/Game/OneBossFight/Boss01/Animations/AN_Riposte_Player_Front.AN_Riposte_Player_Front` | **True** | 3 | `profiles[0..2].stagger_profile.RipostePlayerClip` |
| 23 | `/Game/OneBossFight/Boss01/Body/SK_Boss01_Body.SK_Boss01_Body` | **True** | 3 | `profiles[0..2].look.Body` |
| 24 | `/Game/OneBossFight/Boss01/Body/SK_Boss01_BrazierGauntlet.SK_Boss01_BrazierGauntlet` | **True** | 3 | `profiles[0..2].look.Pieces[2]` |
| 25 | `/Game/OneBossFight/Boss01/Body/SK_Boss01_Crown.SK_Boss01_Crown` | **True** | 3 | `profiles[0..2].look.Pieces[0]` |
| 26 | `/Game/OneBossFight/Boss01/Body/SK_Boss01_Mantle.SK_Boss01_Mantle` | **True** | 3 | `profiles[0..2].look.Pieces[1]` |
| 27 | `/Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword.SM_Boss01_Greatsword` | **True** | 3 | `profiles[0..2].look.Sword` |


### Ground Truth from DD27d In-Memory Apply Run & Order A-213 Diagnostics
The Codex DD27d in-memory apply run (C-312 / X-323 / C-314) executed `draft_boss_profiles.py --input-json examples/boss_draft_profiles.json --apply` inside Unreal Editor without saving:
1. **Successful In-Memory Contracts:**
   - Default struct constructors (`cls()`) and `inst.set_editor_property(py_name, val)` succeeded for all non-soft properties.
   - `unreal.Name(val)` for `FName` succeeded.
   - Floats, ints, bools, and FName arrays (`SpawnSockets`) succeeded.
   - Top-level struct assignment to `new_asset` (`set_editor_property`) succeeded for all structs without soft paths: `stats`, `encounter_policy`, `stagger_policy`, `phase_flow`, `low_sweep`, `shockwave`, `heal_punish`.
   - Nested arrays of structs (`phases` and `fields`) succeeded completely, proving the 110 parity field rows can be constructed and assigned.
2. **Defect Identified (Soft Object Paths):**
   - Exactly 29 failures occurred across the three drafts, all raising `TypeError`.
   - Failing properties were exclusively those carrying `TSoftObjectPtr`: top-level `skeleton` and `animations`, and structs `fireball`, `phase_dependencies`, `stagger_profile`, `dormant_wake`, `bleed`, `look`, `close_clip_swap`, `death`.
3. **Helper Diagnostic Enhancements (Order A-213):**
   - **Untruncated Failure Output:** Following the summary table, `DiagnosticFailureCollector` prints one untruncated line per failure: `[DRAFT_APPLY][FAILURE] <asset> <section> <property> expected=<full> actual_type=<..> actual_repr=<full> exception=<class>: <full message>`.
   - **Clear Step Attribution:** Labels failures with exact failing step (`construct`, `convert`, `set_editor_property`, `readback`) on the specific property name, eliminating generic `(constructor)` labels.
   - **Per-Asset Status Rewording:** Only drafts with zero failures print `Initialized & verified all N typed properties`. Failing drafts print `Draft asset '<name>': N properties set, M failed`.
   - **Numeric Fields Readback Witness:** Outputs direct numeric witness `[DRAFT_APPLY] fields rows read back: <n> of <n expected>` confirming the 110 parity rows.
, Grounded Evidence & Residual Verification Limits (Order A-212 / C-309 / DD27c)

### Engine Reflection Evidence Ground Truth (DD27c Stage 2 Probe)
The Codex DD27c reflection probe run captured verified runtime truths from the live Unreal Engine 5.5.4 editor environment (`probe_lines.txt`, SHA256 `4ad279a4d302e5b44edfc12d7c6f937100b4f5f3019335fb94cceb99e6da7137`):
1. **Module-Level Editor Guard:** `unreal.is_editor` exists as a callable builtin function at the root of `unreal` and returned `True` (`[PROBE] unreal.is_editor exists=True callable=True type=builtin_function_or_method`, `[PROBE] unreal.is_editor() result=True`). The fail-closed editor guard in `draft_boss_profiles.py` and `inspect_authored_assets.py` uses this verified function, retiring the missing `unreal.SystemLibrary.is_editor` (KI-135).
2. **UStruct Class vs Instance Property Reflection:**
   - In Unreal Engine 5.5.4 Python, `dir()` on a `UStruct` class exposes only builtin wrapper methods (`assign`, `copy`, `get_editor_property`, `set_editor_property`, etc.).
   - Struct properties are accessible ONLY on struct instances via `inst.get_editor_property(py_name)`.
   - `hasattr(inst, py_name)` is `False` for ALL 123 properties across all 17 structs. There is NO attribute access on struct instances.
3. **Default Struct Constructors:** All 17 authored structs instantiate transient in-memory objects via default constructors (`unreal.RPGBossStatsConfig()`, `unreal.RPGBleedConfig()`, `unreal.RPGDeathConfig()`, etc.).
4. **DataAsset Type Enforcement:** Passing a Python `dict` for a struct property (e.g. `new_asset.set_editor_property("stats", dict)`) is rejected by Unreal Engine's type converter. The helper constructs real struct instances via `create_struct_instance` and sets them via `set_editor_property`.
5. **CDO Reflection:** `unreal.RPGBossDefinition.get_default_object()` reflects all 22 top-level properties: `schema` (int), `definition_id` (Name), `presentation_id` (Name), `skeleton` (NoneType), `animations` (Array), `phases` (Array), `fields` (Array), and the 15 typed struct members.
6. **Death Mode Enumerator:** `unreal.RPGBossDeathMode` reflects members `PACK_MONTAGE` and `OWN_CLIP`.

### Residual Verification Limits (What the Probe Did NOT Prove)
1. **Soft-path form on write:** Probe proved `unreal.SoftObjectPath exists=True callable=True type=type`, but did not execute `set_editor_property` with soft paths. The helper implements `to_soft_ref` which tries `unreal.SoftObjectPath(path)` with string fallback.
2. **Enum assignment on write:** Probe proved enum members exist, but did not execute `set_editor_property("death_mode", enumerator)`.
3. **Nested struct assignment to DataAsset:** Probe proved struct instances can be constructed and read, but did not execute `new_asset.set_editor_property("stats", inst)`.
4. **Array of struct assignment:** Probe proved `phases` and `fields` are reflected as `type=Array`, but did not execute `new_asset.set_editor_property("phases", [inst, ...])`.
5. **Unverified API chain:** `unreal.Vector2D` was not probed in DD27c. It is strictly guarded with `hasattr(unreal, "Vector2D")` and falls back to `[float, float]` in `convert_property_for_engine`.

---

### Troubleshooting: Soft-Object (`TSoftObjectPtr`) vs. Soft-Class (`TSoftClassPtr`) Model (KI-139 / DD27f / C-325)
During the Codex DD27f in-memory draft run (`draft_boss_profiles.py --apply`), 19 of 22 typed properties initialized cleanly across all drafts, but exactly 3 properties failed across each draft (9 failures total):
1. `fireball.FireballAbility` rejected `unreal.Name` with `TypeError: Failed to convert type 'Name' to property 'FireballAbility' (SoftClassProperty)`.
   - **Root Cause:** In historical `authoring_core.py`, `"FireballAbility"` was categorized under `FNAME_PROPERTIES`, causing Python to pass an `FName` to a `SoftClassProperty`.
2. `phase_dependencies.ImmunityEffect` and `stagger_profile.ImmunityEffect` failed in `to_soft_ref`:
   - **Root Cause:** `to_soft_ref` calls `unreal.EditorAssetLibrary.does_asset_exist(path)`. The path in the profile includes the generated class suffix (`...GE_HitStunImmune.GE_HitStunImmune_C`). In Unreal Engine, `does_asset_exist` queries the package asset on disk (`GE_HitStunImmune.uasset`), which returns `False` for paths ending in `_C` even though the asset file exists on disk.

#### Key Architectural Distinction in Unreal Engine 5.5.4 Python:
- **`TSoftObjectPtr<T>` (Soft Object Pointer):**
  - Points to a specific asset instance (e.g., `USkeletalMesh`, `UAnimMontage`, `UNiagaraSystem`, `USoundBase`).
  - Strict Python Reflection Rule: Rejects `str` and `unreal.SoftObjectPath` with `TypeError`.
  - Required Form on Write: Must be assigned the loaded `UObject` instance returned by `unreal.EditorAssetLibrary.load_asset(path)` (or `None`).
  - Readback: `inst.get_editor_property(name)` returns the loaded `UObject`, canonicalized via `obj.get_path_name()`.
- **`TSoftClassPtr<T>` (Soft Class Pointer):**
  - Points to a `UClass` or `UBlueprintGeneratedClass` (e.g., `GA_Fireball_Enemy_C`, `GE_HitStunImmune_C`).
  - Strict Python Reflection Rule: Rejects `str`, `unreal.Name`, and `unreal.SoftObjectPath` with `TypeError`.
  - Package vs Class Suffix: The `.uasset` on disk is `Content/.../BlueprintName.uasset`. The class object is `BlueprintName_C`. `does_asset_exist` checks the package path without `_C`.
  - Candidate Forms on Write: Probed via `probe_unreal_api.py --classrefs` (DD27g) across `unreal.load_class(None, "<path>_C")`, `EditorAssetLibrary.load_blueprint_class("<path>")`, and `EditorAssetLibrary.load_asset("<path>").generated_class()`.

#### DD27g Live Engine Ground Truth (Orders A-217 / A-218 / Lead C-327 / C-328):
The Codex DD27g reflection probe run (`classref_lines_verbatim.txt`) measured candidate class acquisition forms across all 3 soft-class sites (`RPGFireballConfig.fireball_ability`, `RPGPhaseDependencyConfig.immunity_effect`, `RPGStaggerProfileConfig.immunity_effect`):
1. **Forms that WORK with successful `set_editor_property` and readback:**
   - `unreal.load_class(None, "<path>_C")` -> loads `BlueprintGeneratedClass`, `result=ok` readback at all 3 sites.
   - `unreal.EditorAssetLibrary.load_blueprint_class("<path WITHOUT _C>")` -> `result=ok` readback at all 3 sites.
   - `unreal.EditorAssetLibrary.load_asset("<path without _C>").generated_class()` -> `result=ok` readback at all 3 sites.
   - `unreal.load_object(None, "<path>_C")` -> `result=ok` readback at all 3 sites.
   - `None` -> successfully clears/initializes soft class property to null.
2. **Forms that FAIL with TypeError:**
   - `str` (both with `_C` and without `_C`) -> `TypeError: Failed to convert type 'str' to property '...' (SoftClassProperty)`.
   - `unreal.SoftClassPath` (both forms) -> `TypeError: Cannot nativize 'SoftClassPath' as 'Class'`.
   - `unreal.Name` -> `TypeError: Failed to convert type 'Name' to property '...' (SoftClassProperty)`.
3. **The Silent-None Pitfall in Unreal Engine Python:**
   - `unreal.load_class(None, "<path without _C>")` returns `None` **WITHOUT raising an exception** (silent failure).
   - `unreal.EditorAssetLibrary.load_blueprint_class("<path WITH _C>")` logs asset registry errors and returns `None` **WITHOUT raising an exception**.
   - If an authoring helper silently accepts `None` as a valid return, it would author an empty/null reference into the data asset, causing silent data loss.
   - **Protection:** `to_class_ref()` strictly enforces that a `None` result from `load_class` for any non-empty path raises `RuntimeError("class did not load: '<path>'")`.
4. **Why `unreal.load_class(None, path_C)` Was Chosen for Production:**
   - The path stored in `boss_draft_profiles.json` and native C++ struct declarations (`RPGEncounterBinding.h:92, 128`) is already the canonical generated-class string ending in `_C` (e.g. `.../GA_Fireball_Enemy.GA_Fireball_Enemy_C`).
   - It executes in exactly ONE engine call without requiring path string slicing or asset-vs-class path rewriting.
   - It directly returns the `UBlueprintGeneratedClass` instance required by `TSoftClassPtr<UObject>`.


### Ground Truth from DD27i Save Run (Owner Approved, [C-338] / [X-339] / [C-339])

Following Owner approval in chat ("Save the 3 draft boss assets? -Save it", recorded in `[C-338]`), Codex executed `draft_boss_profiles.py --apply --save` under exclusive engine lock (`[X-339]`, accepted in `[C-339]`).
Exactly three draft `.uasset` files were saved and verified on disk under `Content/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/`:
- `DA_Boss_AbyssalRevenant_Draft.uasset` (SHA256: `90ee817f380aac486cecfa86d474078af98005190da1d8f370a62762af975ac5`, 6,101 bytes)
- `DA_Boss_EmberWarden_Draft.uasset` (SHA256: `ba05a8aa93fec66526c59bf12f51bb824103f67860bdee16efcdd5217d6a3e2b`, 79,966 bytes)
- `DA_Player_Hero_Draft.uasset` (SHA256: `8d18711526b7a746e1bb95546db984708984fccbc6cda3546eea39cd72edc822`, 4,552 bytes)

> [!WARNING]
> **Verification Boundary & Limits:**
> 3 drafts saved (sha256 as above), reload/compile unverified.
> This run proves serialization to disk only. Fresh serialized reload from disk, `CompileParticipant`, twelve-plan preflight compilation, Details panel rendering, and live gameplay execution remain unverified until subsequent pipeline stages (`DD27j` and `DD30`).

### Player Hero Target-Only Manifest Implementation (Order A-225 / Lead [C-342])

Following Tech Lead Claude directive [C-342] to resolve the DD27j participant compiler failure without modifying C++ validators, the toolkit implements **Option A** (a minimal truthful manifest for the Player Hero target definition):

1. **Non-Circular Provenance File (`examples/hero_target_source.json`):**
   - The 4 authored scalar values (`MaxHealth: 800.0`, `MaxPosture: 60.0`, `PostureRegenDelay: 1.5`, `PostureRegenRate: 25.0`) are isolated in a dedicated frozen JSON source file (`Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/examples/hero_target_source.json`).
   - Frozen SHA-256: `25e50a332009da8ddec783ce7e6f2c992f94a50d8f8c6a14427fcfa47240cc41` (329 bytes).
   - This eliminates circular hashing where adding manifest rows to `boss_draft_profiles.json` would alter the hash cited in its own rows.

2. **Truthful Free-Text Rows (Zero False Hydration Claims):**
   - **Destination:** `"FRPGParticipantConfig.Stats (compile copy only)"` (accurately reflects that `CompileParticipant` copies the struct to `Value->Stats`, while the player character has no live `URPGBossPosture` component).
   - **FirstRead:** `"none after compile: TargetOnly has no consumer plan (X-341, Preflight.cpp:449-455)"` (honestly acknowledges that `PrepareBatch.Configure` is never invoked for `TargetOnly`).
   - **Witness:** `"AutomationTest:OneBossFight.Binding.StatsAdapters.Assign (proves FRPGPostureConfig parsing only)"`.

3. **New Asset Profile (`DA_Player_Hero_Draft_V2`):**
   - Staged as a distinct 4th profile in `boss_draft_profiles.json`.
   - The saved 3 assets from DD27i (`DA_Player_Hero_Draft`, `DA_Boss_EmberWarden_Draft`, `DA_Boss_AbyssalRevenant_Draft`) remain 100% untouched on disk.

4. **Manifest Emitter Extension (`emit_fields_manifest.py --hero-target`):**
   - Deterministically generates the 4 truthful rows directly from `hero_target_source.json`.
   - Verified by unit tests in `test_emit_fields_manifest.py` (10/10 PASS).

---

### Repeatable Asset Selector (`--only`) & Grounded Witness (Order A-226 / Lead [C-343])

Per Tech Lead Claude directive [C-343], two blocking fixes were delivered before engine execution:

1. **Strictly Grounded Witness (Fix 1):**
   - The 4 manifest rows on `DA_Player_Hero_Draft_V2` cite exclusively the verified passing test:
     `"AutomationTest:OneBossFight.Binding.StatsAdapters.Assign (proves FRPGPostureConfig parsing only)"`.
   - The unpassed `AuthoredDraft` compile test was removed; a saved asset carries only witnesses that have actually passed in the working tree.

2. **Repeatable `--only <asset_name>` Flag (Fix 2):**
   - `draft_boss_profiles.py` now supports repeatable `--only <asset_name>` to target specific draft assets (e.g. `--only DA_Player_Hero_Draft_V2` for DD27l/DD27m).
   - Validated by unit tests (`TestDraftBossProfilesOnlySelector`):
     * `--only DA_Player_Hero_Draft_V2`: processes exactly one asset.
     * Unknown asset name: fails with descriptive error exit code 1.
     * Default behavior (no flag): validates all 4 draft profiles.
     * `--only` with an already-saved asset: still strictly refuses overwrite/delete.

3. **Offline Test Qualification:**
   - 229 unit tests pass in 1.016s (0 failures, 0 errors, exit 0).

---

## 10. Delivered Artifacts
| Path | Description |
| :--- | :--- |
| Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/authoring_core.py | Pure Python shared validation core with struct instantiation & conversion helpers |
| Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/draft_boss_profiles.py | Staged DRAFT creator with Diagnostic In-Memory Mode & real struct instantiation |
| Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/inspect_authored_assets.py | Read-only complete typed asset inspector with module-level editor guard |
| Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/diff_against_cpp.py | Single-purpose review aid comparing adapter checks against authoring core |
| Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/emit_fields_manifest.py | Parity Field Manifest generator producing FRPGParityField rows |
| Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/probe_unreal_api.py | Read-only Unreal Engine API reflection probe (Stage 1 Class + Stage 2 Instance) |
| Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/test_authoring_core.py | Comprehensive standard-library unittest suite including Fake Unreal qualification (192 tests) |
| Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/test_emit_fields_manifest.py | Unit tests for manifest generator (8 tests) |
| Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/test_probe_unreal_api.py | Unit tests for Unreal API reflection probe Stage 1 & Stage 2 (12 tests) |
| Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/test_run_output.txt | Raw test suite execution output (229/229 PASS, exit 0) |
| Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/examples/boss_draft_profiles.json | Sample draft boss and player profile definitions |
| Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/original_A205/ | Byte-exact preserved A-205 historical deliverables |
| Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/original_A206/ | Byte-exact preserved A-206 historical deliverables |
| Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/original_A207/ | Byte-exact preserved A-207 historical deliverables |
| Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/original_A211/ | Byte-exact preserved A-211 historical deliverables |
| Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/original_A212/ | Byte-exact preserved A-212 historical deliverables |
| Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/original_A213/ | Byte-exact preserved A-213 historical deliverables |
| Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/README.md | Integrated architecture, safeguards, and verification guide |
| Docs/BossCombatReview/Execution/Antigravity/AuthoringToolkit/evidence_sha256.txt | Cryptographic SHA-256 evidence receipt |
| Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/author_custom_build.py | Updated build authoring helper integrating authoring_core |
| Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/original_A205/ | Preserved byte-exact A-205 deliverables |
| Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/original_A206/ | Preserved byte-exact A-206 deliverables |
| Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/original_A207/ | Preserved byte-exact A-207 deliverables |
| Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/original_A211/ | Preserved byte-exact A-211 deliverables |
| Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/original_A212/ | Preserved byte-exact A-212 deliverables |
| Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/original_A213/ | Preserved byte-exact A-213 deliverables |
| Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/README.md | Build helper usage and verification guide |
| Docs/BossCombatReview/Execution/Antigravity/BuildAuthoringHelper/evidence_sha256.txt | Build helper evidence receipt |