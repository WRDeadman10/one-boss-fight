# Queue U: Antigravity Lane A Audit Report (U-A01 through U-A04)

**Date:** 2026-11-05  
**Author:** Antigravity (Quality & Ledger Lane)  
**Task Scope:** U-A01 (Witness Ledger Update), U-A02 (Production Changes Review), U-A03 (D5 Legacy Defaults Review), U-A04 (Comparator D6/O4 False-PASS Risk Analysis)  
**Reference Directives:** [C-893], [C-894], [C-895], [C-896], [P47], [S35]  

---

## 1. U-A01: Canonical Ledger Witness Status Update (`witness_status_v3.json`)

### 1.1 Census and Version Transition
- **Prior Version:** 3.36 (Census: 75 WITNESSED / 7 PARTIAL / 0 NOT YET; Canonical Total: 82)
- **New Version:** 3.37 (Census: 80 WITNESSED / 2 PARTIAL / 0 NOT YET; Canonical Total: 82)
- **Remaining PARTIAL Requirements:**
  - `BOSS-QA-001` (Runtime overlay: visual HUD presentation active in PIE, continuous headless diagnostics headless)
  - `BOSS-QA-005` (Performance bounds: p99 <= 16.67 ms / 60 FPS target; currently failing ~42 ms GPU bound)

### 1.2 Five Graduated Combat Requirements
In accordance with `Documentation/Boss/P47_ANTIGRAVITY_WITNESSED_ROWS_HANDOVER.md` and Lead build verdicts, five previously PARTIAL requirements have been graduated to **WITNESSED**:

| Requirement ID | Title | Previous Status | New Status | Evidence Citing & Observable Proof |
|---|---|---|---|---|
| **`BOSS-AWR-004`** | Signed angle and hysteresis | PARTIAL | **WITNESSED** | BUILD-146 / BUILD-170: Live cone-edge retention in matched control/hysteresis pair. Cites `Docs/BossCombatReview/Execution/Claude/B_YAW_CONE/pie_hysteresis/editor_raw.log:1578` (`[FrameworkProof] cone_hysteresis degrees=6 seq=1`) and line 1811 (`cone_hysteresis degrees=6 seq=2`). |
| **`BOSS-MOV-001`** | Range-band policy | PARTIAL | **WITNESSED** | BUILD-199: Live four-map range-family selection across Melee (102.87 cm), Close (254.76 cm), Medium (380 cm), and Gap-Closer (701.92 cm). Cites `Docs/BossCombatReview/Execution/Claude/B_FAG5_MOV001/Melee100/editor_raw.log:1577` (`walk start=... rangeCm=102.87 bandMin=90 bandMax=110`) and line 1586 (`decision attack=1 chosen=Move_Sevarog_Melee_FAG5`). |
| **`BOSS-HIT-008`** | Central defense order | PARTIAL | **WITNESSED** | BUILD-203: Guarded contact applies chip damage and rejects full health damage. Cites `Docs/BossCombatReview/Execution/Claude/B_FAG4_HIT008/guarded/editor_raw.log:2054` (`guard_chip incoming=20 applied=5`) and line 2055 (`guard_state instance=2 ... guard=Guarded outcome=Accepted hpApplied=5`). Parry order verified in `B_PARRY`. |
| **`BOSS-COM-004`** | Explicit hit-confirm policy | PARTIAL | **WITNESSED** | BUILD-204 / BUILD-208: Distinct branching witnessed for Hit -> B, Whiff -> C, Guarded -> D, and Parried -> E/Recover. Cites `Docs/BossCombatReview/Execution/Claude/B_FAG23_COM004/guarded/editor_raw.log:3111` (`outcome=Guarded ... result=Continue next=D`) and `B_LIVE_20261104b/com004_parried_phase080/editor_raw.log:2393` (`outcome=Parried ... result=Finished next=None`). |
| **`BOSS-SEL-008`** | No-candidate fallback | PARTIAL | **WITNESSED** | BUILD-208: Continuous neutral strafe reset loop on NoCandidate, strafe-stuck wall reflection, and eligible resume. Cites `Docs/BossCombatReview/Execution/Claude/B_LIVE_20261104b/sel008_blocker/editor_raw.log:1816` (`strafe_stuck flipped=1 movedRatio=0.237298`) and line 2033 (`strafe_end seconds=2.30206 reason=CandidateEligible card=Move_Sevarog_SwingSlow_F7`). |

### 1.3 Route Parity and Integration Witness Section
To keep the 82-point canonical combat requirements strictly separated from route-comparison and architectural gates (per S35 handover), a dedicated `route_parity_and_integration_witnesses` top-level structure was established in `witness_status_v3.json`:
1. **`A5-PARITY`**: 31 of 31 registered driver pairs complete with per-pair parity validated across deterministic messages, timing, and declared stochastic boundaries (`Docs/BossCombatReview/Execution/Claude/B_C835_PARITY/`, BUILD-221).
2. **`D1-ATTACH`**: Selected-route component attach parity verified on boss components (scythe, mantle, crown, gauntlets) matching legacy socket bindings (`Docs/BossCombatReview/Execution/Claude/B_C835_PARITY/`, BUILD-220, `DECISIONS.md` C-840).
3. **`D5-LEGACY-DEFAULTS`**: 424-leaf census verified: 214 MATCH / 0 MISMATCH / 210 player NOT-COMPARABLE (`Docs/BossCombatReview/Execution/Claude/C852_D5_DEFAULTS/`, BUILD-222, `Documentation/Boss/D5_G044_LEGACY_DEFAULT_AUDIT.md`).
4. **`T1-TICK-ORDER`**: Same-frame prerequisite dependency test passed, eliminating frame-skew between `URPGAttackTracker` and boss activation; two-pair A4 S9 0.05s verified (`Docs/BossCombatReview/Execution/Claude/B_C863_TICKORDER/`, BUILD-221).
5. **`G2-SELECTION-REFUSAL`**: Live verification of missing-definition and invalid-manifest refusal, zero legacy bundle leak, and explicit-clear restoration of `LegacyNoSelection` (`Docs/BossCombatReview/Execution/Claude/C872_G2_REFUSAL_v2/`, BUILD-222).

---

## 2. U-A02: Independent Review of Production Changes Since Commit `6c7d3fc`

We reviewed the production code changes incorporated in restore point commit `09f33bd`:

### 2.1 D1 Attach Bundle (`Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp`)
- **Change:** Selected-route component attach logic was refactored to align with legacy socket attachment rules (`ScytheSocket`, `MantleSocket`, `CrownSocket`, `GauntletSocket`).
- **Review Finding:** **APPROVED.** Attaches use exact `FAttachmentTransformRules::SnapToTargetIncludingScale`. No orphan scene components are spawned. Lifecycle cleanup safely detaches components on end play / destroy.

### 2.2 T1 Tick Prerequisites (`Source/OneBossFight/Player/RPGAttackTracker.cpp`, `RPGBossActivation.cpp`)
- **Change:** Explicit tick dependency ordering established via `AddPrerequisiteComponent(AttackTracker)` and `PrimaryComponentTick.bCanEverTick = true`.
- **Review Finding:** **APPROVED.** Eliminates 1-frame skew between attack tracking updates and boss state machine evaluation. Unit test suite in `RPGBossTrackerTickOrderTests.cpp` proves same-frame execution determinism without circular dependency risk.

### 2.3 G1 Benchmark Selector (`Source/OneBossFight/Player/RPGBossActivation.cpp`, `RPGBossEncounter.cpp`)
- **Change:** Support for command-line driven encounter definition activation (`-RPGBenchmark`, `-H019EncounterDefinition=<Name>`).
- **Review Finding:** **APPROVED.** The selector parses command-line tokens safely via `FParse::Value`. When absent, it falls back cleanly to default encounter assets (`LegacyNoSelection`), strictly preventing unintended activation during standard PIE or Shipping play.

### 2.4 CueMode Shipping Guard (`Source/OneBossFight/Player/RPGBossOverlayRules.h`, `RPGBossActivation.cpp`)
- **Change:** Console variable `rpg.CueMode` and debug visual overlays wrapped inside `#if !UE_BUILD_SHIPPING`.
- **Review Finding:** **APPROVED.** Validated against the regular test suite's Shipping guard audit (`Scripts/Tools/test_check_shipping_guards.py`). Zero non-shipping CVar references leak into Shipping build configurations.

### 2.5 P17 Strafe Fields (`Source/OneBossFight/Player/RPGBossFrameworkProfile.h`)
- **Change:** Neutral strafe hold bounds moved from hardcoded literals (`0.8f`, `1.6f`) to `URPGBossFrameworkProfile` fields with identical default values.
- **Review Finding:** **APPROVED.** Preserves exact legacy behavioral parity while allowing data-driven override on the selected route. Regression tests confirm default initialization matches prior constant expressions.

---

## 3. U-A03: Independent Review of D5 Legacy Defaults Table (`legacy_defaults_g044.json`)

- **Audit Target:** `Scripts/Tools/legacy_defaults_g044.json` (249 comparable rules).
- **Verification Method:** Programmatic AST and line-by-line verification against all referenced C++ headers and source files in `Source/OneBossFight/`.
- **Results:**
  - Total Rules Evaluated: **249**
  - Source File Existence: **249 / 249 (100%)**
  - Source Excerpt Verbatim Match: **249 / 249 (100%)**
  - Native Default Mismatches: **0**
- **Verdict:** **AGREE.** The table faithfully represents native C++ UPROPERTY defaults with zero divergence.

---

## 4. U-A04: False-PASS Risk Analysis for Comparator Rules (D6b, D6c, D6d, O4)

### 4.1 Vulnerability Mechanism: Bracketed Token Stripping (`D6c`)
In `Scripts/Tools/compare_encounter_parity.py`:
```python
_BRACKETED_DETAIL = re.compile(r"\[[^\]]*\]")
```
- **The Issue:** `_message_parts()` strips bracketed substrings before numeric tokenization. If a diagnostic log formats key gameplay parameters inside square brackets (e.g. `health=[2000]` vs `health=[1500]`), the bracketed text and its numbers are completely erased before `_message_mismatch()` computes numeric deltas.
- **Consequence:** `_observable_value_matches()` evaluates status only (`PASS == PASS`) and treats the stripped message difference as an advisory warning (`WARN`) rather than a hard failure. This creates a severe **false-PASS risk** where major numeric divergence (such as the 2000 vs 1500 health mismatch) could bypass parity validation undetected if logged in bracketed format.

### 4.2 Relative Tolerance Slack (`MESSAGE_RELATIVE_TOLERANCE = 0.10`)
- Unbracketed numbers in messages allow up to a 10% relative delta (`abs(left - right) <= 0.10 * max(...)`).
- While suitable for floating-point timing jitter across differing frame rates (e.g. 0.033s vs 0.035s), applying 10% tolerance universally to discrete integer metrics (e.g. hit counts, poise thresholds, health values) risks silently absorbing gameplay bugs.

### 4.3 Recommendations for Hardening the Parity Gate
1. **Restrict Bracket Stripping to Registered Volatile Fields:** Do not strip arbitrary bracketed text; limit `_BRACKETED_DETAIL` regex only to designated sample arrays (e.g., `samples=[...]`).
2. **Strict Typology for State Metrics:** Health, damage, hit counts, and phase identifiers must be emitted as distinct, strongly typed receipt fields rather than formatted inside free-text message strings.
3. **Zero-Tolerance Discrete Comparator:** Maintain a strict zero-tolerance numeric rule for all non-timing integer metrics.
