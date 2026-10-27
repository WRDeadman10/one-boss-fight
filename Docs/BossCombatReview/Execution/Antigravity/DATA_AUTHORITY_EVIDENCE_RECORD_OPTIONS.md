# AG19: Data Authority and Evidence-Record Options (Design Only) — Rev 04

**Document Version:** 4.0.0 (Post-X-228 Consistency Corrections)  
**Date:** 2026-10-27  
**Author:** Antigravity (Pair Programmer)  
**Governing Directives:** `Docs/BossCombatReview/Execution/Codex/AG18_A148_ACCEPTANCE.md` (`[X-224]`), `Docs/BossCombatReview/Execution/Codex/AG19_A149_REVIEW.md` (`[X-226]`), `Docs/BossCombatReview/Execution/Codex/AG19_A150_REVIEW.md` (`[X-227]`), & `Docs/BossCombatReview/Execution/Codex/AG19_A151_REVIEW.md` (`[X-228]`)  
**Status:** DESIGN ONLY — Pure Offline Architectural & Verification Model (Zero edits to `Source/`, `Config/`, `Scripts/`, or Unreal assets; no UObject instantiation; Claude resting; Owner commits only)

---

## 1. Executive Summary & Context

Work Order AG18 established that parity manifest entries (`FRPGParityField`) represent author-stated intent rather than runtime proof, and that typed component assignment onto native components does not verify that underlying combat pack gameplay attributes have been modified or verified.

Review `AG19_A151_REVIEW.md` (`[X-228]`) identified a narrow consistency discrepancy between Conceptual Rule 1 and Case 1: Rule 1 previously forced `overallAssessment` into a narrow binary (`UNVERIFIED_INCOMPLETE` or `DOCUMENTARY_DISCREPANCY`) whenever telemetry was unobserved, which contradicted Case 1's use of `APPLICATION_GUARD_SKIPPED`.

This Rev 04 report delivers the focused resolution:
1. **Refined Precedence & Prohibition of Premature Full Parity (Rule 1):** Clarifies that missing telemetry strictly prohibits `FULL_PARITY` and mandates that `evidenceCoverage` records incomplete capture, without artificially restricting the headline `overallAssessment`. A known application guard skip or documentary discrepancy can validly serve as the headline assessment while the incomplete telemetry status is fully preserved.
2. **Explicit Interpretation of Staged Observations:** Clarifies that Case 1 represents a **hypothetical future observation scenario** (demonstrating how planned assignment and analyzed branch bypass are recorded together), not an actual executed run or proof of runtime branch execution.
3. **Case-to-Rule Consistency Checklist:** Added an explicit verification checklist confirming that all illustrative cases and the rejected false-closure case strictly adhere to the defined conceptual rules.
4. **Preserved Governance Boundaries:** All analysis remains strictly offline design; no code/config/script edits, no engine runs, Claude resting, and owner commits only.

---

## 2. The Four Statements of Combat State

To prevent conflating author intent with runtime fact, combat parameters must be expressible across four independent statements. Each statement has distinct authority, target identity, representation, lifecycle stage, and evidentiary backing:

```
[Statement 1: Declared Metadata]
  - Authority: Manifest Author / Asset Data
  - Lifecycle: Static Authoring Time
         │
         ▼
[Statement 2: Extracted Effective Baseline] ─── Independent Comparison (Offline Reconciliation)
  - Authority: Pre-Migration Effective Config
  - Lifecycle: Snapshot Baseline
         │
         ▼
[Statement 3: Typed Component Assignment]
  - Authority: Native Adapter Plan / Subsystem
  - Lifecycle: Post-Configure / Registration
         │
         ▼
[Statement 4: Observed Runtime Readback]
  - Authority: Pack Component / Extended Attributes
  - Lifecycle: Active Combat Encounter Execution
```

### Detailed Statement Matrix for First-Cluster Fields

| Dimension | Statement 1: Declared Metadata | Statement 2: Extracted Effective Baseline | Statement 3: Typed Component Assignment | Statement 4: Observed Runtime Readback |
| :--- | :--- | :--- | :--- | :--- |
| **Authority** | Human Author or Pipeline Tool authoring `FRPGParityField` entries (in `URPGBossDefinition::Fields`) | Pre-migration effective configuration: C++ definitions, constructor overrides, authored DataAssets, cvars, and serialized level actor state | Native Adapter Components (`URPGBossEncounter`, `URPGBossPosture`, `RPGBossPhases`) via typed structs (`FRPGBossStatsConfig`, `FRPGPhaseConfig`) | Live Combat Pack Engine Actor (`Attribute.Health`, active montage playback states, component timers) |
| **Target Identity** | String key path: e.g. `Boss.MaxHealth`, `Boss.PostureRegenDelay`, `Boss.Phase1.AttackRateScale` | Specific code symbol or asset property: `BossMaxHealth` in `RPGBossEncounter.h:35`, `RegenDelaySeconds` in `RPGBossPosture.h:23` | Typed struct member and target component instance: `Stats.MaxHealth`, `Posture->RegenDelaySeconds`, `Phases->AttackRateScale` | Live reflected pack attribute or active engine instance state (e.g. `RPGPack::ReadAttribute("Attribute.Health", true, Max)`) |
| **Type & Units** | String metadata representation: Value (e.g. `"2000.0"`), Units (e.g. `"HP"`, `"Seconds"`, `"Multiplier"`) | Typed C++ literal or serialized property: `float` (absolute scalar, seconds, unitless scale factor) | Typed struct member: `float MaxHealth`, `float PostureRegenDelay`, `float AttackRateScale` | Engine runtime float / double: pack attribute float, timer float, active montage play rate |
| **Lifecycle & Freshness** | Authored offline; static until re-authored or regenerated | Pre-migration baseline snapshot; static for a verified project revision | Instantiation & Configuration: applied during encounter binding hydration or registration | Encounter Active: dynamic across encounter reset, phase transition, damage resolution |
| **Evidence / Proof** | Synthesizer/Author JSON/Asset hash; `FRPGParityField` record in DataAsset | Independent AST scraper / Asset export report with scoped source hashes | Native registration log / unit test assertion verifying typed struct transfer | Operator-captured telemetry artifact / diagnostic log witness from test run |

*Identifier & Scope Grounding:*
- The actual field array in `Source/OneBossFight/Player/RPGEncounterBinding.h:58` is `URPGBossDefinition::Fields` (annotated: `/** Must cover private/constructor/instance fields too before migration is accepted. */`). Any aggregate wrapper (such as `FRPGParityManifest`) is an illustrative proposed concept, not an existing engine USTRUCT.
- **Structural Availability vs Domain Capability:** Component presence and hydration interfaces (`IsRegistered`, `IsHydrated`) establish structural availability only. An actor having an attached component, mesh, or property does not prove native capability for a selected domain, readiness, or combat parity.

---

## 3. Comparative Analysis: Design Alternatives

We evaluate two architectural patterns for reconciling combat parameters between legacy ARPG pack configurations and native encounter bindings.

### Option A: Non-Authoritative Attestation Manifest + Offline Reconciliation Packet

In this model, parity manifest records (`FRPGParityField`) are treated strictly as **attestation documents**—declarations of what the author or extraction pipeline expects parameters to be. They exert no runtime authority. An independent offline tool reads the manifest, ingests pre-migration effective baselines, consumes operator-captured runtime readback telemetry artifacts, and produces an offline **Reconciliation Evidence Packet**.

* **Architecture:**
  ```
  [Author Manifest (Attestation)] ──────────┐
                                             ├──> [Offline Reconciliation Tool] ──> [Evidence Packet]
  [Pre-Migration Effective Baseline] ────────┤
                                             │
  [Operator-Captured Readback Artifacts] ───┘
  ```

* **Drift Vulnerability:** Moderate. Because manifests are maintained separately from C++ configurations, developers may update C++ properties without updating manifest entries (or vice versa), producing cosmetic drift or false alarms until manually reconciled.
* **Single Source of Truth (SSOT):** The C++ code, DataAssets, and level configurations remain the runtime source of truth. The manifest is explicitly documented as secondary non-authoritative metadata.
* **Oracle Independence:** High. The offline reconciliation tool relies on independent source inspection and artifact verification decoupled from runtime binding code. However, calling a separate parser "independent" does not guarantee oracle independence if it merely re-reads the same defaults while omitting serialized overrides or pack lifecycle layers.
* **Authoring Overhead:** High if manual; requires dual-entry maintenance across C++ structs and parity records.
* **Runtime Execution & Safety:** Zero new runtime gameplay overhead. Manifest strings are never parsed during live combat. Existing runtime adapters continue using their verified native and reflected pack paths.

### Option B: Authoring-Time Generated Manifest from Typed Records + Independent Baseline

In this model, parity manifest records are synthesized deterministically by an authoring-time script or pre-commit step from typed C++ definitions (`FRPGBossStatsConfig`, `FRPGPhaseConfig`, component headers). An independent verification tool compares this generated manifest against the pre-migration baseline and operator-captured telemetry.

* **Architecture:**
  ```
  [Typed C++ Structs / Defaults] ──> [Deterministic Generator] ──> [Generated Parity Manifest]
                                                                            │
  [Pre-Migration Baseline] ─────────────────────────────────────────────────┼──> [Parity Verification Report]
                                                                            │
  [Operator-Captured Readback Artifacts] ───────────────────────────────────┘
  ```

* **Drift Vulnerability:** Lowered for matching fields, but **not eliminated**. Generated manifests can still diverge due to stale generator runs, omitted fields, incorrect semantic mappings, uncommitted/dirty workspace changes, tool bugs, or type aliases. Furthermore, a generated manifest is merely a derived statement of C++ declarations; it does not constitute proof that the value was applied to components or executed by the pack.
* **Single Source of Truth (SSOT):** Centralized in typed C++ structs and asset definitions, with the manifest acting as a derivative projection.
* **Oracle Tautology Risk:** High if unconstrained. If the generator uses the same reflection or parsing schemas as the verification tool, circular confirmation occurs (asserting that a tool agrees with its own schema). **Mitigation:** The generation pipeline must be strictly isolated from the baseline extraction oracle (e.g. generator inspects native C++; oracle inspects pre-migration legacy pack assets and captured telemetry).
* **Authoring Overhead:** Low. Authors maintain typed C++ structs; manifests update via automated tooling.
* **Runtime Execution & Safety:** Zero new runtime gameplay overhead. Game code executes native typed paths. Existing runtime adapters remain unchanged.

---

## 4. Concrete Illustrative Walks across First-Cluster Fields

The following walks demonstrate how discrepancies are classified across the four statements without silent coercion, runtime fallbacks, or unauthorized combat retuning. All numeric values are **illustrative examples**; runtime readbacks remain **unobserved and unknown** until operator telemetry is captured.

### Field 1: Boss Max Health (`MaxHealth`)

* **Illustrative Scenario:**
  - Statement 1 (Manifest Claim): `Value = "2000.0"`, `Units = "HP"`
  - Statement 2 (Extracted Source Baseline): `RPGBossEncounter.h:35` default `BossMaxHealth = 2000.f`
  - Statement 3 (Typed Component Assignment): `FRPGBossStatsConfig::MaxHealth = 2000.f`
  - Statement 4 (Observed Runtime Readback): **UNKNOWN / UNOBSERVED** (No live capture artifact provided)
* **Discrepancy & Precondition Handling:**
  - If Statement 1 claims `"9999.0"` while Statement 2 extracts `2000.0f`, the offline tool records `METADATA_BASELINE_MISMATCH`.
  - **No Coercion:** The system must not overwrite `BossMaxHealth` with `9999.0f` at runtime.
  - **Separation of Assignment and Native Application (`RPGBossEncounter.cpp:90`):**
    ```cpp
    if (!bMaxHealthApplied && BossMaxHealth > 1.f)
    ```
    If an illustrative test configuration assigns `BossMaxHealth = 0.5f`, the typed assignment itself **succeeds** (Statement 3 records `0.5f`). However, during subsequent native encounter application, this guard evaluates to false (`0.5f <= 1.f`), skipping the override branch. 
    - The assignment status is recorded as `CONFIGURED_ASSIGNED`.
    - The native application disposition is recorded as `SKIPPED_OVERRIDE_GUARD`.
    - Pack health readback remains **UNKNOWN / UNOBSERVED** absent runtime capture (no fabricated 500 or 2000 outcome).

### Field 2: Posture Regen Delay (`PostureRegenDelay`)

* **Illustrative Scenario:**
  - Statement 1 (Manifest Claim): `Value = "6.0"`, `Units = "Seconds"`
  - Statement 2 (Extracted Source Baseline): `RPGBossPosture.h:23` default `RegenDelaySeconds = 6.0f`
  - Statement 3 (Typed Component Assignment): `Posture->RegenDelaySeconds = 6.0f`
  - Statement 4 (Observed Runtime Readback): **UNKNOWN / UNOBSERVED**
* **Channel Distinction & Target Identity:**
  - Native `URPGBossPosture` manages regeneration delay independently via tick-based delta timers (`RegenDelaySeconds`).
  - The legacy ARPG combat pack contains separate extended attribute channels (e.g. poise cooldown suppression).
  - Native `RegenDelaySeconds` and pack poise cooldowns are separate channels requiring distinct evidence targets. Readback cannot be assumed to be zero or missing without actual telemetry.

### Field 3: Phase Attack Rate Multiplier (`AttackRateScale`)

* **Illustrative & Grounded Native Source Mechanics:**
  - Source Declaration: `RPGBossPhases.h:58` declares:
    ```cpp
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Phase", meta = (ClampMin = "1.0"))
    float AttackRateScale = 1.2f;
    ```
  - Phase Entry (`RPGBossPhases.cpp:364`):
    ```cpp
    ScaleAttackRates(AttackRateScale);
    ```
  - Direct Scaling Loop (`RPGBossPhases.cpp:441-444`):
    ```cpp
    void* Value = RateField->ContainerPtrToValuePtr<void>(Entries.GetRawPtr(E));
    RateField->SetFloatingPointPropertyValue(Value, RateField->GetFloatingPointPropertyValue(Value) * Factor);
    ```
    *Phase entry directly multiplies each reflected montage `PlayRate` field by `Factor = AttackRateScale = 1.2f`.*
  - Phase Removal (`RPGBossPhases.cpp:388`):
    ```cpp
    ScaleAttackRates(1.f / AttackRateScale);
    ```
    *Inverse scaling (`1.f / 1.2f`) is applied exclusively upon phase removal to restore baseline rates.*
* **Symbolic Formulation:**
  - Let base montage play rate be $r$, and phase factor be $a = 1.2$.
  - Phase Entry applies $r_{scaled} = r \times a$. Phase Removal applies $r_{restored} = r_{scaled} \times (1/a)$.
  - Active montage play rate during combat is subject to animation blueprint state, blend weights, and timing limitations; it cannot be assumed to equal the reflected entry property value without telemetry.

---

## 5. Smallest Unresolved Decisions & Candidate Record Specification

Decisions are partitioned into **ordinary engineering proposals** (managed within technical execution) and **genuine owner scope decisions** (reserved for user approval).

### Ordinary Engineering Proposals (Technical Team Execution)
* Structure and formatting of offline reconciliation output reports (JSON artifacts and markdown summaries under `Docs/BossCombatReview/Execution/Antigravity/`).
* Function signatures for offline AST scrapers and telemetry artifact parsers.
* Design of candidate data structures for comparing captured telemetry.
* *Note on File Placement:* Placement of future tools under `Scripts/` is a proposal only; no write permissions outside AG review directories are requested or exercised during offline work.

### Genuine Owner Scope & Behavioral Decisions (Reserved for Owner)
1. **Build Gate Policy:** Whether offline reconciliation failures should act as a **fatal build/cook error** (halting compilation/packaging) or a **non-fatal audit warning**.
2. **Parity Model Mandate:** Approval of Option A (non-authoritative attestation) versus Option B (authoring-time generated manifest).
3. **Combat Tuning & Phase Mapping:** Any modification to approved baseline values (e.g. `AttackRateScale = 1.2f`) or phase mapping structures (single multiplier vs per-phase array).

*No owner interruption or immediate decision is required during this design phase.*

---

### Candidate Evidence-Record Specification (Orthogonal Non-Validating Sketch)

To resolve the state-model conflict, the record replaces the single scalar enum with **orthogonal dimensions**, preserving both documentary facts and execution status simultaneously without collision:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "CombatParityEvidenceRecord_OrthogonalSketch",
  "type": "object",
  "required": [
    "recordId",
    "targetFieldPath",
    "workspaceContext",
    "statement1_declared",
    "statement2_sourceBaseline",
    "statement3_typedAssignment",
    "nativeApplicationDisposition",
    "statement4_runtimeReadback",
    "reconciliationSummary"
  ],
  "properties": {
    "recordId": { "type": "string" },
    "targetFieldPath": { "type": "string" },
    "workspaceContext": {
      "type": "object",
      "required": ["workingStateRef", "isDirty", "toolVersion"],
      "properties": {
        "workingStateRef": { "type": "string" },
        "isDirty": { "type": "boolean" },
        "toolVersion": { "type": "string" }
      }
    },
    "statement1_declared": {
      "type": "object",
      "required": ["status"],
      "properties": {
        "status": { "type": "string", "enum": ["DECLARED", "OMITTED", "UNKNOWN"] },
        "value": { "type": ["string", "null"] },
        "units": { "type": ["string", "null"] },
        "sourceAsset": { "type": ["string", "null"] },
        "artifactSHA256": { "type": ["string", "null"] }
      }
    },
    "statement2_sourceBaseline": {
      "type": "object",
      "required": ["status"],
      "properties": {
        "status": { "type": "string", "enum": ["EXTRACTED", "UNRESOLVED", "UNKNOWN"] },
        "symbolOrProperty": { "type": ["string", "null"] },
        "numericValue": { "type": ["number", "null"] },
        "sourceFile": { "type": ["string", "null"] },
        "sourceFileSHA256": { "type": ["string", "null"] }
      }
    },
    "statement3_typedAssignment": {
      "type": "object",
      "required": ["status"],
      "properties": {
        "status": { "type": "string", "enum": ["CONFIGURED_ASSIGNED", "CONFIGURATION_FAILED", "UNEXECUTED", "UNKNOWN"] },
        "structName": { "type": ["string", "null"] },
        "propertyName": { "type": ["string", "null"] },
        "assignedValue": { "type": ["number", "null"] }
      }
    },
    "nativeApplicationDisposition": {
      "type": "object",
      "required": ["status"],
      "properties": {
        "status": { "type": "string", "enum": ["APPLIED", "SKIPPED_OVERRIDE_GUARD", "UNEXECUTED", "NOT_APPLICABLE", "UNKNOWN"] },
        "guardCondition": { "type": ["string", "null"] },
        "details": { "type": ["string", "null"] }
      }
    },
    "statement4_runtimeReadback": {
      "type": "object",
      "required": ["status"],
      "properties": {
        "status": { "type": "string", "enum": ["VERIFIED_READBACK", "UNOBSERVED", "UNAVAILABLE", "UNKNOWN"] },
        "targetSystem": { "type": ["string", "null"] },
        "observedValue": { "type": ["number", "null"] },
        "telemetryArtifactRef": { "type": ["string", "null"] }
      }
    },
    "reconciliationSummary": {
      "type": "object",
      "required": ["evidenceCoverage", "metadataComparison", "runtimeDisposition", "overallAssessment"],
      "properties": {
        "evidenceCoverage": {
          "type": "string",
          "enum": ["INCOMPLETE_DOCUMENTARY_ONLY", "STAGED_PRE_EXECUTION", "FULL_EVIDENCE_OBSERVED", "UNKNOWN_INCOMPLETE"]
        },
        "metadataComparison": {
          "type": "string",
          "enum": ["MATCH", "MISMATCH", "INCOMPARABLE", "UNCHECKED"]
        },
        "runtimeDisposition": {
          "type": "string",
          "enum": ["AGREES_WITH_BASELINE", "DIVERGES_FROM_BASELINE", "SKIPPED_PRECONDITION", "UNOBSERVED", "UNKNOWN"]
        },
        "overallAssessment": {
          "type": "string",
          "enum": ["FULL_PARITY", "DOCUMENTARY_DISCREPANCY", "APPLICATION_GUARD_SKIPPED", "RUNTIME_DIVERGENCE", "UNVERIFIED_INCOMPLETE"]
        },
        "discrepancyDetails": { "type": "string" }
      }
    }
  }
}
```

*Testing Clarification:* The schema above is an illustrative design specification. Local Python `jsonschema` was unavailable in the workspace environment, no external dependencies were installed, and no executable schema validation test ran. The conditional consistency rules below represent conceptual checker requirements.

#### Proposed Conceptual Consistency Rules
1. **Rule 1 (Prohibition of Premature Full Parity & Coverage Incompleteness):** If `statement4_runtimeReadback.status` is `"UNOBSERVED"` or `"UNKNOWN"`, `overallAssessment` **must not** evaluate to `"FULL_PARITY"`, and `evidenceCoverage` **must** reflect incomplete capture (`"INCOMPLETE_DOCUMENTARY_ONLY"`, `"STAGED_PRE_EXECUTION"`, or `"UNKNOWN_INCOMPLETE"`). The headline `overallAssessment` reports the most critical known finding (e.g. `"APPLICATION_GUARD_SKIPPED"` if a native override branch was skipped, `"DOCUMENTARY_DISCREPANCY"` if metadata conflicts with baseline, or `"UNVERIFIED_INCOMPLETE"` if no earlier discrepancies exist), without erasing incomplete telemetry status.
2. **Rule 2 (Orthogonal Fact Preservation):** Known application bypasses (`nativeApplicationDisposition: "SKIPPED_OVERRIDE_GUARD"`) and documentary mismatches (`metadataComparison: "MISMATCH"`) are recorded independently in their respective orthogonal fields, ensuring that all findings remain visible regardless of which finding forms the primary headline in `overallAssessment`.
3. **Rule 3 (Full Parity Verification Precondition):** `overallAssessment` may evaluate to `"FULL_PARITY"` **only if** all four statements possess active, non-null data that agree within defined numerical tolerance across identical target identities and units.

---

### Three Illustrative Case Records

#### Case 1: Assigned 0.5, Native Override Guard Skipped, Readback Unknown
*Clarification:* This record represents a **hypothetical future observation scenario** (illustrating how staged plan assignment and analyzed branch bypass are recorded together), not an actual executed run on live actors:

```json
{
  "recordId": "REC-CASE1-HEALTH-GUARD",
  "targetFieldPath": "Boss.MaxHealth",
  "workspaceContext": {
    "workingStateRef": "HYPOTHETICAL_STAGE_CTX",
    "isDirty": true,
    "toolVersion": "OfflineReconciler-0.2-sketch"
  },
  "statement1_declared": {
    "status": "DECLARED",
    "value": "0.5",
    "units": "HP",
    "sourceAsset": "DA_BossDefinition_Illustrative.json",
    "artifactSHA256": "illustrative_hash_01"
  },
  "statement2_sourceBaseline": {
    "status": "EXTRACTED",
    "symbolOrProperty": "BossMaxHealth",
    "numericValue": 2000.0,
    "sourceFile": "Source/OneBossFight/Player/RPGBossEncounter.h",
    "sourceFileSHA256": "4f3ab203562ef2d3a2d18828feaf5f437a5a7eaff1054e9b6ce60e9150cae9d6"
  },
  "statement3_typedAssignment": {
    "status": "CONFIGURED_ASSIGNED",
    "structName": "FRPGBossStatsConfig",
    "propertyName": "MaxHealth",
    "assignedValue": 0.5
  },
  "nativeApplicationDisposition": {
    "status": "SKIPPED_OVERRIDE_GUARD",
    "guardCondition": "BossMaxHealth > 1.f (RPGBossEncounter.cpp:90)",
    "details": "Value 0.5f <= 1.f; native override branch skipped during encounter setup."
  },
  "statement4_runtimeReadback": {
    "status": "UNOBSERVED",
    "targetSystem": null,
    "observedValue": null,
    "telemetryArtifactRef": null
  },
  "reconciliationSummary": {
    "evidenceCoverage": "STAGED_PRE_EXECUTION",
    "metadataComparison": "MISMATCH",
    "runtimeDisposition": "SKIPPED_PRECONDITION",
    "overallAssessment": "APPLICATION_GUARD_SKIPPED",
    "discrepancyDetails": "Assigned 0.5f successfully configured in struct. Native application skipped override guard (0.5 <= 1.f). Runtime pack health readback is unobserved; effective health remains strictly unknown."
  }
}
```

#### Case 2: Declared 9999 vs Baseline 2000, Readback Unknown
Demonstrates how a known documentary mismatch coexists with incomplete runtime telemetry, preserving both facts simultaneously:

```json
{
  "recordId": "REC-CASE2-DOC-MISMATCH",
  "targetFieldPath": "Boss.MaxHealth",
  "workspaceContext": {
    "workingStateRef": "HYPOTHETICAL_STAGE_CTX",
    "isDirty": true,
    "toolVersion": "OfflineReconciler-0.2-sketch"
  },
  "statement1_declared": {
    "status": "DECLARED",
    "value": "9999.0",
    "units": "HP",
    "sourceAsset": "DA_BossDefinition_Illustrative.json",
    "artifactSHA256": "illustrative_hash_02"
  },
  "statement2_sourceBaseline": {
    "status": "EXTRACTED",
    "symbolOrProperty": "BossMaxHealth",
    "numericValue": 2000.0,
    "sourceFile": "Source/OneBossFight/Player/RPGBossEncounter.h",
    "sourceFileSHA256": "4f3ab203562ef2d3a2d18828feaf5f437a5a7eaff1054e9b6ce60e9150cae9d6"
  },
  "statement3_typedAssignment": {
    "status": "CONFIGURED_ASSIGNED",
    "structName": "FRPGBossStatsConfig",
    "propertyName": "MaxHealth",
    "assignedValue": 2000.0
  },
  "nativeApplicationDisposition": {
    "status": "APPLIED",
    "guardCondition": "BossMaxHealth > 1.f",
    "details": "Native override applied value 2000.0f."
  },
  "statement4_runtimeReadback": {
    "status": "UNOBSERVED",
    "targetSystem": null,
    "observedValue": null,
    "telemetryArtifactRef": null
  },
  "reconciliationSummary": {
    "evidenceCoverage": "INCOMPLETE_DOCUMENTARY_ONLY",
    "metadataComparison": "MISMATCH",
    "runtimeDisposition": "UNOBSERVED",
    "overallAssessment": "DOCUMENTARY_DISCREPANCY",
    "discrepancyDetails": "Documentary conflict: Declared 9999.0 HP does not match extracted baseline 2000.0 HP. Runtime telemetry is unobserved; both documentary mismatch and incomplete evidence are preserved."
  }
}
```

#### Case 3: Unavailable Baseline, Unexecuted Assignment, No Telemetry
Demonstrates an honest record where baseline and execution are unknown without fabricated numbers or inferred configuration success:

```json
{
  "recordId": "REC-CASE3-ALL-UNKNOWN",
  "targetFieldPath": "Boss.UnmigratedCustomSpecial",
  "workspaceContext": {
    "workingStateRef": "HYPOTHETICAL_STAGE_CTX",
    "isDirty": true,
    "toolVersion": "OfflineReconciler-0.2-sketch"
  },
  "statement1_declared": {
    "status": "UNKNOWN",
    "value": null,
    "units": null,
    "sourceAsset": null,
    "artifactSHA256": null
  },
  "statement2_sourceBaseline": {
    "status": "UNKNOWN",
    "symbolOrProperty": null,
    "numericValue": null,
    "sourceFile": null,
    "sourceFileSHA256": null
  },
  "statement3_typedAssignment": {
    "status": "UNKNOWN",
    "structName": null,
    "propertyName": null,
    "assignedValue": null
  },
  "nativeApplicationDisposition": {
    "status": "UNKNOWN",
    "guardCondition": null,
    "details": null
  },
  "statement4_runtimeReadback": {
    "status": "UNKNOWN",
    "targetSystem": null,
    "observedValue": null,
    "telemetryArtifactRef": null
  },
  "reconciliationSummary": {
    "evidenceCoverage": "UNKNOWN_INCOMPLETE",
    "metadataComparison": "UNCHECKED",
    "runtimeDisposition": "UNKNOWN",
    "overallAssessment": "UNVERIFIED_INCOMPLETE",
    "discrepancyDetails": "Field baseline, configuration, and telemetry are unobserved and uncaptured. Stored honestly as all-unknown."
  }
}
```

---

### Conceptual False-Closure Case (Illustrative Checker Failure)

The following example illustrates an invalid claim where a generator or author attempts to assert full parity while runtime evidence is unobserved:

```json
{
  "recordId": "REC-REJECTED-FALSE-CLOSURE",
  "targetFieldPath": "Boss.Phase1.AttackRateScale",
  "workspaceContext": {
    "workingStateRef": "HYPOTHETICAL_STAGE_CTX",
    "isDirty": true,
    "toolVersion": "OfflineReconciler-0.2-sketch"
  },
  "statement1_declared": { "status": "DECLARED", "value": "1.2", "units": "Multiplier" },
  "statement2_sourceBaseline": { "status": "EXTRACTED", "symbolOrProperty": "AttackRateScale", "numericValue": 1.2 },
  "statement3_typedAssignment": { "status": "CONFIGURED_ASSIGNED", "assignedValue": 1.2 },
  "nativeApplicationDisposition": { "status": "APPLIED" },
  "statement4_runtimeReadback": { "status": "UNOBSERVED", "observedValue": null },
  "reconciliationSummary": {
    "evidenceCoverage": "STAGED_PRE_EXECUTION",
    "metadataComparison": "MATCH",
    "runtimeDisposition": "UNOBSERVED",
    "overallAssessment": "FULL_PARITY",
    "discrepancyDetails": "INVALID CLAIM"
  }
}
```
*Checker Evaluation:* Consistency Rule 1 triggers immediately: `statement4_runtimeReadback.status` is `"UNOBSERVED"`, which strictly prohibits `overallAssessment: "FULL_PARITY"`. The checker rejects the claim and forces `overallAssessment` to `"UNVERIFIED_INCOMPLETE"`.

---

### Case-to-Rule Consistency Checklist

The following checklist confirms compliance between the illustrative case records and the conceptual consistency rules:

| Case Record | Readback Status | Primary Known Finding | Evaluated `overallAssessment` | Compliance with Rule 1 (`FULL_PARITY` Prohibited) | Compliance with Rule 2 (Orthogonal Facts Preserved) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Case 1** (Health Guard Skip) | `UNOBSERVED` | Native guard bypassed (`0.5 <= 1.f`) | `APPLICATION_GUARD_SKIPPED` | **PASS**: Does not claim `FULL_PARITY`; `evidenceCoverage` is `STAGED_PRE_EXECUTION`. | **PASS**: Assignment (0.5), guard skip, and metadata mismatch are all preserved in orthogonal fields. |
| **Case 2** (Documentary Mismatch) | `UNOBSERVED` | Metadata mismatch (`9999 != 2000`) | `DOCUMENTARY_DISCREPANCY` | **PASS**: Does not claim `FULL_PARITY`; `evidenceCoverage` is `INCOMPLETE_DOCUMENTARY_ONLY`. | **PASS**: Documentary mismatch preserved alongside incomplete telemetry. |
| **Case 3** (All Stages Unknown) | `UNKNOWN` | No data across any stage | `UNVERIFIED_INCOMPLETE` | **PASS**: Does not claim `FULL_PARITY`; `evidenceCoverage` is `UNKNOWN_INCOMPLETE`. | **PASS**: All stages honestly marked `UNKNOWN` without dummy values. |
| **Rejected False-Closure** | `UNOBSERVED` | Author asserted `FULL_PARITY` | Rejection Triggered (`FULL_PARITY` -> `UNVERIFIED_INCOMPLETE`) | **PASS**: Checker correctly identifies missing telemetry and overrides invalid `FULL_PARITY` claim. | **PASS**: Preserves staged configuration while rejecting false closure. |

*All unobserved parameters remain strictly UNVERIFIED, ensuring all 83 active tasks maintain their required verification backlog without premature claims of closure.*

---

## 6. Input Artifact Receipts & Verifications

The analysis in this report was conducted strictly offline against the following pinned codebase artifacts:

| Artifact Path | Size (Bytes) | SHA256 Checksum |
| :--- | :--- | :--- |
| `Source/OneBossFight/Player/RPGEncounterBinding.h` | 7,338 | `4330f8c416cd75284e829856b5d1cba7001c5ee62f40bdc7b1bf98a8dbf94a80` |
| `Source/OneBossFight/Player/RPGEncounterBinding.cpp` | 14,964 | `2fe63bcb78261b9bdd15be33607ea3c696ae33227989facc5b67e15cd91110dc` |
| `Source/OneBossFight/Player/RPGBossPhases.h` | 8,607 | `0887f37564a28564261b81ad21a1baf2a4c6f6adae99a3a49c3c15622225a69a` |
| `Source/OneBossFight/Player/RPGBossPhases.cpp` | 21,965 | `c43615412e1f345d6ed75cc6d6a6b0d9ece6acaaac612e545b42cc24087f7a06` |
| `Source/OneBossFight/Player/RPGBossPosture.h` | 7,551 | `bca70f5816a45733f0ea2d5550651da7192ba179a5e31d736eab90fd46cd3ff8` |
| `Source/OneBossFight/Player/RPGBossEncounter.h` | 5,359 | `4f3ab203562ef2d3a2d18828feaf5f437a5a7eaff1054e9b6ce60e9150cae9d6` |
| `Source/OneBossFight/Player/RPGBossEncounter.cpp` | 12,526 | `dc149393f2fff1788ea22daf42db0b14f85ac36f58ad59c459b44ee94600c96d` |
| `Docs/BossCombatReview/Execution/Codex/Step2Preparation/02_ADAPTER_FIELD_AUDIT.md` | 14,623 | `ec676909bc43c13b19314a18aae834265044361b571f9137b3b1e1c436d1bd20` |
| `Docs/BossCombatReview/Execution/Codex/Step2Preparation/09_FIRST_CLUSTER_TYPED_PARITY_CROSSWALK.md` | 9,936 | `13b747fdcfba9951af5a0062e46499cd037d821aed94ac9e7e60eb1dcc03fd13` |
| `Docs/BossCombatReview/Execution/Codex/Step2Preparation/18_NATIVE_CAPABILITY_PROPOSAL.md` | 8,066 | `5f5b4a029f55a145f76d67796c53928944a975b6714a82a5c2bc5078753a3be1` |
| `Docs/BossCombatReview/Execution/Codex/AG18_A148_ACCEPTANCE.md` | 5,773 | `c042ead91284dcba4fc43fde9f46472ee02cfb4d3c46f7c8e15ebdf05b8a17e4` |
| `Docs/BossCombatReview/Execution/Codex/AG19_A149_REVIEW.md` | 7,531 | `689a4b42ec5c8048cf052cbda8db54abe975b1505538ac5d363dd6bcb3b65ef7` |
| `Docs/BossCombatReview/Execution/Codex/AG19_A150_REVIEW.md` | 4,889 | `63776bd64d635af238430b0b1e5c6909d7c7f9638cc7b0071f0f851161303f95` |
| `Docs/BossCombatReview/Execution/Codex/AG19_A151_REVIEW.md` | 2,660 | `bc3b883393f0616af9dcf2af8b84b5d77d86dc52d0c9ae7e2e8aed6d8be8dece` |
| `Docs/BossCombatReview/Execution/Antigravity/PARITY_MANIFEST_VALIDATION_AUDIT.md` [Rev 03] | 25,606 | `da4dabdbd3184d13b1de4f37223258f99968dbc0e927f6791988187355e523ef` |
