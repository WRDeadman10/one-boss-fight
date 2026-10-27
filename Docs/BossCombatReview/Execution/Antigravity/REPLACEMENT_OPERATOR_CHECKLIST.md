# Replacement-Operator Checklist: Unmet Evidence Needs in Scope

**Document ID:** `REPLACEMENT_OPERATOR_CHECKLIST`  
**Date:** 2026-10-27 (Revised per Codex Lead Review `[X-178]`)  
**Author:** Antigravity (Visual & Technical Animation Investigator)  
**Governing Work Order:** `Docs/BossCombatReview/Execution/ANTIGRAVITY_WORK_ORDER_07.md` (Codex Lead `[X-174]`, `[X-178]`)  
**Scope Boundary:** Documents strictly unmet evidence needs already within scope. Does not schedule autonomous engine runs, request unapproved tests, or ping resting Claude. All 83 active reference requirements (`06_REFERENCE_REQUIREMENTS.md`) and prior failure/unknown classifications are preserved.

---

## 1. Visual Presentation & Animation Evidence (P1 Scope)

- [ ] **CAP-01 Hand-Release Visual Departure Timing (Move A5):**
  - *Current Status:* **PARKED AS UNVERIFIED** per Owner directive (`DECISIONS.md`).
  - *Unmet Need:* If unparked by Owner, requires high-speed viewport frame capture to measure visual departure frame against configured tracker window ($0.450\text{ s} - 0.500\text{ s}$) and runtime spawn ($0.470\text{ s}$).
- [ ] **CAP-02 Low Sweep Geometry Observation (Move A4):**
  - *Current Status:* Documented in `E-008` (Revision 2). $312\text{ cm}$ is the largest sampled **bounds-axis endpoint estimate**, not a verified physical blade tip or global reach bound; $68\text{ cm}$ is a sample-relative difference between the $380\text{ cm}$ geometric query reach and the bounds estimate, not a proven physical collision overreach.
  - *Unmet Need:* Requires visual confirmation whether the sample-relative difference produces observable visual hit discrepancy during active combat sweeps against player dodge frames.
- [ ] **A6 Ground Shockwave Production Cue (Shipping Build):**
  - *Current Status:* Architectural design completed (`P1_SHIPPING_WAVE_CUE_DESIGN.md`). Candidate demonstration assets identified (`SM_Shockwave_Disc.uasset`, `M_Shockwave_Soft.uasset`, `BP_Niagara_ImpactEffect.uasset`).
  - *Unmet Need:* Operator readback of candidate asset material domains, vertex layout, and shader scalar parameters (currently all UNKNOWN). Empirical measurement of visual outer edge against collision band ($Radius \pm 90\text{ cm}$) in PIE. Verification of cue visibility in packaged Shipping build. No visual implementation exists to test yet.

---

## 2. Encounter Binding & Diagnostics Evidence (Step 2 Scope)

- [ ] **Dedicated Two-Encounter Map Fixture (Prerequisite):**
  - *Current Status:* Staged driver `pie_encounter_binding.py` requires an explicitly reviewed two-encounter map; currently an unapproved prerequisite status.
  - *Unmet Need:* Placement and review of a fixture map containing exactly two distinct `ARPGEncounterBinding` actors with valid `(Boss, Player)` slots to allow non-vacuous driver execution.
- [ ] **CVar State Isolation Hardening:**
  - *Current Status:* Audited in `P1_BINDING_DIAGNOSTIC_AUDIT.md`. Driver currently saves/restores only `rpg.CatalogSource` and `rpg.CatalogTestInvalid`.
  - *Unmet Need:* Update `ORIGINAL` dictionary in `pie_encounter_binding.py` to capture and restore all 4 catalog CVars (`rpg.CatalogSource`, `rpg.CatalogTestFourth`, `rpg.CatalogPath`, `rpg.CatalogTestInvalid`), preventing cross-test contamination from uncleaned external sessions or crashes.
- [ ] **Live Pack Boss Hydration & Attribute Readback:**
  - *Current Status:* Current unit tests (`RPGEncounterBindingTests.cpp`) use real spawned `AActor` hosts with synthetic configuration and only verify `BossMaxHealth` and `GateRadius0`.
  - *Unmet Need:* Empirical readback verifying that live `URPGBossEncounter`, `URPGBossPosture`, and `URPGBossPhases` components receive typed values on actual boss character instances during BeginPlay.

---

## 3. Timeline Shadow Parity Evidence (Step 3 Scope)

- [ ] **Shadow Trace Semantic Parity Assertion:**
  - *Current Status:* Audited in `P1_SHADOW_SCHEMA_CHALLENGE.md` and `P1_SHADOW_WIRE_CROSSWALK.md`. `validate_records` validates transport shape, but accepts cross-row world/encounter drift, backwards time across reset, and unvalidated nested containers.
  - *Unmet Need:* Implement semantic validation requiring continuous session/encounter identity, monotonic game time across encounter resets, producer-required nested field/type validation (`legacy_snapshot`, `window_projections`, `compiled_crossings`), and explicit tracking of candidate divergences (`REGRESSION_CANDIDATE`). Acknowledge that mid-window `MATCH` ticks naturally carry zero crossings without invalidating trace validity, and that `MATCH` verifies sampled active timing only, not hit/geometry/cause parity. Parity acceptance policy remains unclosed.
- [ ] **Natural Attack Timeline Shadow Run:**
  - *Current Status:* Inert offline checks verified (`shadow_record_validator_checks.py: 31/31`).
  - *Unmet Need:* Controlled PIE execution capturing live duel shadow records to prove candidate adapter parity against legacy pack animation execution without simulation drift.

---

## 4. Operational Guardrails for Replacement Operator

1. **Do not launch Unreal Editor or PIE autonomously:** Wait for explicit Owner or Lead scheduling.
2. **Do not commit unreviewed code batches:** Authorize commits only for reviewed, passing changes.
3. **Keep Claude resting:** Claude account transition remains held until operator resume.
4. **Preserve prior unknowns:** Do not relabel unverified states as passing without reproducible empirical logs.
