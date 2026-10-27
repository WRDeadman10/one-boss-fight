# P1 Staged Shadow Schema & Semantic Adversarial Challenge

**Document ID:** `P1_SHADOW_SCHEMA_CHALLENGE`  
**Date:** 2026-10-27 (Revised per Codex Lead Reviews `[X-178]`, `[X-181]`)  
**Author:** Antigravity (Visual & Technical Animation Investigator)  
**Work Order:** `Docs/BossCombatReview/Execution/ANTIGRAVITY_WORK_ORDER_07.md` (Task **AG07-2**)  
**Governing Documents & Primary Source Anchors:**  
- Work Order: [`ANTIGRAVITY_WORK_ORDER_07.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/ANTIGRAVITY_WORK_ORDER_07.md)
- Target Staged Driver: [`Docs/BossCombatReview/Execution/Codex/Drafts/Scripts/Editor/pie_timeline_shadow.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Scripts/Editor/pie_timeline_shadow.py) (Current SHA256: `c0af0dc6066b73bbbd248981244fc231d653cfc9fbd58cfde4c054958caad99c`)
- Codex Lead Reviews: `[X-177]`, `[X-178]`, `[X-181]`
- C++ Shadow Record Producer: [`Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.cpp`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.cpp) (SHA256: `f6a0274c3bad8d5221981fa10dc529a284aa3285eb1220ba3e4f991a07363924`)
- C++ Shadow Record Header: [`Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.h`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.h) (SHA256: `95da9c0c6a72a302ed16cc1d9c3b0d5f7fd8e758f573dd65bda0bc4b13ca00ab`)
- Staged Timeline Compiler Header: [`Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGTimelineCompiler.h`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGTimelineCompiler.h) (SHA256: `5bf162ff250469cf6b80f2edaad5cfc39e969ed4eb6e8d6256cf56b640fe119e`)
- Challenge Test Harness: [`Docs/BossCombatReview/Execution/Antigravity/test_shadow_schema_challenges.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/test_shadow_schema_challenges.py)
- Serializer Wire Crosswalk: [`Docs/BossCombatReview/Execution/Antigravity/P1_SHADOW_WIRE_CROSSWALK.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/P1_SHADOW_WIRE_CROSSWALK.md)

---

## 1. Executive Summary

This report fulfills Task **AG07-2** of Codex Technical Lead's Work Order 07 (`[X-174]`, revised per `[X-178]`, `[X-181]`).

It performs an independent, adversarial challenge of the staged shadow record validator `validate_records` in [`pie_timeline_shadow.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Scripts/Editor/pie_timeline_shadow.py). While Codex's hardening in `shadow_record_validator_checks.py` (31/31 checks) successfully enforced canonical decimal-string representation for uint64 ordinals and closed type-coercion defects, **the current validator function is strictly a wire transport schema validator, not a trace-level continuity validator or a gameplay parity verdict**.

Using AST-only function extraction and safe in-memory fake buffers (zero Unreal import, zero runtime execution), this audit demonstrates:
1. **Valid Diagnostic Behaviors Clarified:**
   - **Zero crossings on `MATCH` rows is legitimate:** When a montage sample is mid-window, no boundary transition occurs during that tick; `compiled_crossings == []` is valid engine behavior.
   - **Reset generation advancement is legitimate:** In `RPGShadowCompare.cpp:124`, `OnSnapshot` updates `Participant` on key changes across duel resets, retaining the record buffer. Monotonic generation advancement within the same world session is normal multi-duel telemetry.
   - **Discrete Markers & Closures:** `EEdge::Marker` (`edge = 2`) and `EEdge::Closed` (`edge = 3`, where `id` is legitimately `None`) are valid structural crossing events emitted by the cursor.
   - **Required Null-Valued Wire Keys:** `authoritative_action` and `engine_instance` are always emitted on the wire as explicit JSON `null` when unset.
   - **Acceptance of `REGRESSION_CANDIDATE` rows is legitimate wire transport:** Diagnostic buffers must record regressions; the flaw exists only if a test caller equates `validate_records == True` with parity verification.
2. **Material Schema & Trace Gaps Identified:**
   - **Disjoint World/Encounter Drift:** Buffer accepts records switching between unrelated world sessions and encounters without trace demarcation.
   - **Backwards Game Time:** Buffer accepts non-monotonic `game_time` within a single continuous session.
   - **Reset World Clock Inversion:** Buffer accepts backwards `game_time` across encounter resets (`generation: 1 @ 100.0s -> generation: 2 @ 2.5s`). Encounter resets advance generation but do NOT reset `UWorld::GetTimeSeconds`; generation advancement cannot excuse a backwards world clock within the same world session segment.
   - **Unvalidated Nested Garbage:** Validator permits arbitrary corrupted objects inside `compiled_crossings` and `window_projections` arrays.
   - **Missing Required `legacy_snapshot` Fields:** Real C++ producer unconditionally emits 6 fields (`tracked`, `move`, `phase`, `instance`, `illegal_starts`, `double_launches`), but validator accepts `{}` (empty dict) or missing keys.

---

## 2. Adversarial Challenge Results Table

Executed against AST-extracted `validate_records` using [`test_shadow_schema_challenges.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/test_shadow_schema_challenges.py):

| Probe ID | Challenge Probe Title | Test Payload Injected | Expected Evidence Contract | Validator Result | Flaw / Behavior Classification |
|---|---|---|---|---|---|
| **PROBE-00** | Baseline Valid Row | Standard synthetic row conforming to 31 Codex checks. | Satisfies wire transport schema shape. | **`True` (Accepted)** | Valid Baseline |
| **PROBE-01** | Valid MATCH with Zero Crossings | `comparison_status = 'MATCH'`, `compiled_crossings = []`. | Active mid-window sample has 0 edge transitions; legitimate engine state. | **`True` (Accepted)** | **Valid Engine Behavior:** Empty crossings valid on MATCH |
| **PROBE-02** | Reset Generation Advancement | Row 0: `gen=1`. Row 1: `gen=2` in same world session / encounter. | Monotonic generation advance on encounter reset (`OnSnapshot:124`). | **`True` (Accepted)** | **Valid Engine Behavior:** Same-world reset generation advance |
| **PROBE-03** | Cross-Row World/Encounter Drift | Row 0: `world-1`, `enc-1`. Row 1: `world-2`, `enc-999`. | Traces must belong to invariant world session and encounter instance. | **`True` (Accepted)** | **Material Trace Gap:** Identity Leak |
| **PROBE-04** | Backwards Game Time Sequence | Row 0: `game_time = 100.0s`. Row 1: `game_time = 2.5s` (Ordinal 1 $\rightarrow$ 2). | Time must be monotonically non-decreasing within continuous session. | **`True` (Accepted)** | **Material Trace Gap:** Temporal Inversion |
| **PROBE-05** | Unverified Traversal Jump | Playhead jumps from $0.1\text{ s}$ to $150.0\text{ s}$ in $16\text{ ms}$ of simulation time. | Playhead traversal requires section/instance cursor metadata. | **`True` (Accepted)** | **Inconclusive Traversal Gap:** Traversal Discontinuity |
| **PROBE-06** | Diagnostic Acceptance of Regressions | Buffer containing `REGRESSION_CANDIDATE` rows. | Wire transport valid; flaw only if caller equates with parity success. | **`True` (Accepted)** | **Defensible Diagnostic Shape:** Transport vs Parity |
| **PROBE-07** | Unvalidated Nested Crossing Elements | `compiled_crossings = ['string', 123, None, {'bad': True}]`. | Nested crossing elements must validate `id`, `semantic`, `position`, `edge`. | **`True` (Accepted)** | **Material Schema Gap:** Nested Crossing Corruption |
| **PROBE-08** | Empty Legacy Snapshot Missing Fields | `legacy_snapshot = {}` (empty dictionary). | Real C++ producer always emits 6 required legacy fields (`RPGShadowCompare.cpp:164-168`). | **`True` (Accepted)** | **Material Schema Gap:** Missing Required Snapshot Fields |
| **PROBE-09** | Positive Fixture for EEdge::Marker | `edge = 2` (`EEdge::Marker`), `position = 0.35s`. | Valid discrete sync marker event from cursor. | **`True` (Accepted)** | **Valid Engine Behavior:** Discrete Marker Crossing |
| **PROBE-10** | Positive Fixture for EEdge::Closed | `edge = 3` (`EEdge::Closed`), `id = 'None'`. | Valid window closure event with closure-reason semantic. | **`True` (Accepted)** | **Valid Engine Behavior:** Window Closure Event |
| **PROBE-11** | Explicit Null-Valued Required Wire Keys | `authoritative_action = None`, `engine_instance = None`. | Emitted unconditionally as explicit JSON null when unset. | **`True` (Accepted)** | **Valid Engine Behavior:** Nullable Wire Keys |
| **PROBE-12** | Reset World Clock Inversion | Row 0: `gen=1, time=100.0s`. Row 1: `gen=2, time=2.5s`. | Reset advances generation but UWorld clock is continuous; time cannot regress. | **`True` (Accepted)** | **Material Trace Gap:** Reset Clock Inversion |
| **PROBE-13** | Malformed Window Projections Elements | `window_projections = [{'unrecognized_garbage': 123}]`. | Array elements must validate `window_id`, `ClampedFrom`, `effective_end`. | **`True` (Accepted)** | **Material Schema Gap:** Unvalidated Projection Objects |

---

## 3. Analysis of Legitimate vs Corrupted Diagnostic States

### 3.1 Legitimate Engine Behavior (Probes 01, 02, 09, 10, 11)
- **Zero Crossings on `MATCH` (Probe 01):**
  In [`RPGShadowCompare.cpp:170-176`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.cpp#L170-L176), `Advance.Crossings` records *boundary transitions* (entering, exiting, or hitting a marker). During continuous active playback, `EngineActive == true` and `LegacyActive == true` produce `comparison_status == "MATCH"`, but 0 boundaries are crossed on that tick. Demanding non-empty crossings on every MATCH row is an error; **`compiled_crossings == []` is completely valid**.
- **Same-World Reset Generation Advancement (Probe 02):**
  In [`RPGShadowCompare.cpp:124`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.cpp#L124), when an encounter reset occurs, `Participant` is updated to the new generation and continues logging into the retained buffer. **Monotonic generation advancement within the same world session is valid**.
- **Marker and Closure Edges (Probes 09 & 10):**
  `EEdge` has 4 valid states: `Begin = 0`, `End = 1`, `Marker = 2`, `Closed = 3`. A closure event legitimately carries `id = None` and represents cursor shutdown.
- **Required Nullable Wire Keys (Probe 11):**
  `authoritative_action` and `engine_instance` are unconditionally present on the wire (`Lines 147-148, 162-163`), serialized as `null` when unset.

### 3.2 Material Trace Gaps (Probes 03, 04, 12)
- **Disjoint World/Encounter Drift (Probe 03):**
  The validator loop inspects string presence per-row without verifying that `world_session` and `encounter_instance` remain invariant. A single trace can silently interleave events from unrelated worlds or streaming levels.
- **Backwards Game Time (Probe 04):**
  The validator enforces `observation_ordinal` ordering, but ignores `game_time`. A buffer can accept backwards time jumps ($100.0\text{ s} \rightarrow 2.5\text{ s}$) within the same session.
- **Reset World Clock Inversion (Probe 12):**
  Encounter reset resets encounter state and advances `generation`, but **does NOT reset `UWorld::GetTimeSeconds`**. A later generation cannot excuse backwards world time ($100.0\text{ s} \rightarrow 2.5\text{ s}$) within the same world session segment.

### 3.3 Material Schema Gaps (Probes 07, 08, 13)
- **Unvalidated Crossing Elements (Probe 07):**
  `isinstance(row.get("compiled_crossings"), list)` accepts arrays containing arbitrary corrupted data (`[None, 123, "bad"]`) without validating struct fields (`id`, `semantic`, `position`, `edge`, `loop_ordinal`).
- **Empty `legacy_snapshot` (Probe 08):**
  `isinstance(row.get("legacy_snapshot"), dict)` accepts an empty dictionary `{}`, even though the C++ producer in `RPGShadowCompare.cpp:164-168` always serializes `tracked`, `move`, `phase`, `instance`, `illegal_starts`, and `double_launches`.
- **Malformed `window_projections` (Probe 13):**
  `isinstance(row.get("window_projections"), list)` accepts dictionaries with unrecognized keys, omitting required `window_id`, `ClampedFrom`, and `effective_end`.

---

## 4. Minimal Proposed Contract Corrections

To harden the validator without introducing unapproved pass/fail gates:

### 4.1 Trace Invariant Validation (Demarcate Sessions)
Within `validate_records`:
```python
first_row = rows[0]
target_world = first_row["world_session"]
target_encounter = first_row["encounter_instance"]
previous_generation = first_row["generation"]
previous_time = first_row["game_time"]

for row in rows:
    # 1. Enforce invariant world session and encounter instance
    if row["world_session"] != target_world or row["encounter_instance"] != target_encounter:
        return False
    # 2. Enforce monotonic generation advancement (resets allowed)
    if row["generation"] < previous_generation:
        return False
    # 3. Enforce monotonic game time across the entire world session (reset does NOT reset world clock!)
    if row["game_time"] < previous_time:
        return False
    previous_generation = row["generation"]
    previous_time = row["game_time"]
```

### 4.2 Structural Validation of Nested Fields
```python
# Validate required legacy_snapshot fields from RPGShadowCompare.cpp:164-168
legacy = row.get("legacy_snapshot")
if not isinstance(legacy, dict):
    return False
for req_key, req_type in [("tracked", bool), ("move", str), ("phase", str),
                           ("instance", int), ("illegal_starts", int), ("double_launches", int)]:
    val = legacy.get(req_key)
    if val is None or type(val) is not req_type:
        return False

# Validate compiled_crossings elements when present
crossings = row.get("compiled_crossings")
if not isinstance(crossings, list):
    return False
for c in crossings:
    if not isinstance(c, dict):
        return False
    if not isinstance(c.get("id"), str) or not isinstance(c.get("semantic"), str):
        return False
    if type(c.get("position")) not in (int, float) or type(c.get("edge")) is not int:
        return False
    if c.get("edge") not in (0, 1, 2, 3):  # Begin, End, Marker, Closed
        return False

# Validate window_projections elements when present
projections = row.get("window_projections")
if not isinstance(projections, list):
    return False
for p in projections:
    if not isinstance(p, dict):
        return False
    if not isinstance(p.get("window_id"), str):
        return False
    if type(p.get("ClampedFrom")) not in (int, float) or type(p.get("effective_end")) not in (int, float):
        return False
```

### 4.3 Removal of Arbitrary Metric Gates
Per Codex Lead review `[X-178]`, all previously suggested arbitrary metric gates (such as `< 5%` inconclusive cutoff or unspecified `minimumN` thresholds) are **explicitly removed**. Wire validation records raw counts and status distributions; high-level parity evaluation remains unclosed and subject to future Lead/Owner approval.

---

## 5. Offline Verification & Artifact Hashes

- **Harness:** [`Docs/BossCombatReview/Execution/Antigravity/test_shadow_schema_challenges.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/test_shadow_schema_challenges.py)
- **Command:** `python Docs/BossCombatReview/Execution/Antigravity/test_shadow_schema_challenges.py`
- **Output:** 14 total challenge probes executed; **14/14 accepted by staged validator**, confirming valid engine behaviors (zero crossings, reset generation, markers, closures, null keys) and material schema/trace gaps.
- **Target Staged Driver Hash:** `c0af0dc6066b73bbbd248981244fc231d653cfc9fbd58cfde4c054958caad99c`
- **C++ Producer Hash:** `f6a0274c3bad8d5221981fa10dc529a284aa3285eb1220ba3e4f991a07363924`
- **C++ Producer Header Hash:** `95da9c0c6a72a302ed16cc1d9c3b0d5f7fd8e758f573dd65bda0bc4b13ca00ab`
- **Staged Compiler Header Hash:** `5bf162ff250469cf6b80f2edaad5cfc39e969ed4eb6e8d6256cf56b640fe119e`
- **Current Dependency Pins:**
  - `test_shadow_schema_challenges.py`: `6a9cac2f6a42dbf3f022b973b5d8096544887dc603df449083b2d577af36eb0c`
  - `P1_SHADOW_WIRE_CROSSWALK.md`: `3355ed25c14f731a4b3247eda1f8f678991c3383085936b7d31fd356d1eeeb74`
