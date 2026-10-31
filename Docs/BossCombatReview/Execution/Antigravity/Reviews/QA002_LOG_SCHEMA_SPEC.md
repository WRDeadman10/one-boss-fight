# QA-002 Structured Event Log Schema Specification & Repository Audit (v2.0)

**Document Version:** 2.0.0  
**Author:** Antigravity  
**Task Reference:** `[C-552]`, `[C-553]` (QA-002 Log Schema Validator, Semantic Monotonicity, and Mutation Audit)  
**Requirement Reference:** `requirements.json` -> `BOSS-QA-002` (*Structured event log*)  
**Status:** DELIVERED (Formal Schema, 50 Tokens, Semantic Ordering, 50/50 Mutation Tests, Pure LF)  

---

## 1. Executive Summary & Verification Census

Per Tech Lead Claude's instructions in `[C-552]` and `[C-553]`, this document defines the formal production schema and semantic stability audit for all `[FrameworkProof]` structured telemetry emitted by the One Boss Fight Sevarog Combat Framework (spanning F3d telemetry proof through F11 stagger/phases and Track B COMBO3).

A dedicated offline Python validator (`validate_framework_proof_logs.py`) and automated test suite (`test_validate_framework_proof_logs.py`) were developed to ingest, parse, validate syntax, and verify semantic monotonicity across all tracked logs in the repository.

### Ingestion Census Across Tracked Repository Logs:
- **Total Tracked Log Files Scanned:** 633 files across `Docs/BossCombatReview/Execution/`
- **Total `[FrameworkProof]` Lines Analyzed:** 62,725 lines
- **Distinct Telemetry Tokens Identified:** 50 canonical tokens
- **Syntax Conformance:** The formal schema describes the committed logs across all 62,725 lines (zero syntax mismatches).
- **Semantic Findings:** Exactly 17 semantic findings identified across 633 logs (detailed in Section 4).
- **Ledger Status:** `BOSS-QA-002` remains **PARTIAL** per Tech Lead ruling in `[C-553]`.

---

## 2. Requirement Coverage Matrix (Categories vs Telemetry Tokens)

The canonical requirement `BOSS-QA-002` states:
*"Decisions, commits, windows, contacts, defenses, branches, interrupts and transitions use stable IDs/times."*

The table below maps each of the 8 canonical requirements to the framework telemetry token that carries it, its primary identifier key, and its time key. Defenses and interrupts are explicitly identified as **NOT LOGGED**:

| Requirement Category | Logged Status | Token | ID Key | Time Key | Behavioral & Architectural Notes |
|:---|:---:|:---|:---|:---|:---|
| **Decisions** | **LOGGED** | `decision` | `attack` (ordinal int) | UE Timestamp / `range` snapshot | Emitted at neutral gate when move is selected. Ordinal attack index tracks execution budget. |
| **Commits** | **LOGGED** | `heading_commit` / `playback_start` | `instance` (int) | UE Timestamp | `heading_commit` latches rotation; `playback_start` commits montage playback. |
| **Windows** | **LOGGED** | `event` | `window` (name), `group` (name) | `localSeconds` (float) / UE Timestamp | Emitted at `kind=Open`, `kind=Close`, `kind=Recovery`, and `kind=Finished`. |
| **Contacts** | **LOGGED** | `hit` | `instance`, `window`, `key` | UE Timestamp | Records `ERPGDamageOutcome::Accepted` vs `RejectedDuplicate` with damage and health deltas. |
| **Defenses** | **NOT LOGGED** | *(None)* | *(None)* | *(None)* | **NOT LOGGED.** Player block, shield absorption, and weapon parry systems are not implemented in the framework (`COM-004` verifies live telemetry produces only Hit and Whiff outcomes). |
| **Branches** | **LOGGED** | `combo_gate` | `gate` (monotonic uint64) | UE Timestamp / gate snapshot | Evaluated at card completion with fresh target range and signed yaw snapshot. |
| **Interrupts** | **NOT LOGGED** | *(None)* | *(None)* | *(None)* | **NOT LOGGED.** Generic external combat interruption is not built. (Boss stance break aborts log `event kind=Aborted` and `cleanup reason=StanceBreak`, but external interruption is unrepresented). |
| **Transitions** | **LOGGED** | `phase_transition` / `stance_break` | `attack` / `generation` | UE Timestamp | `phase_transition` logs threshold crossing; `stance_break` logs stagger state duration. |

---

## 3. Complete 50-Token Formal Schema Matrix

Each `[FrameworkProof]` log line follows the canonical Unreal Engine log format:
`[<Timestamp>][<FrameIndex>]<LogCategory>: <Verbosity>: [FrameworkProof] <Token> <Payload>`

The 50 recognized tokens, grouped by functional lifecycle domain with exact occurrence counts across the repository, are detailed below:

| Token | Category | Occurrence Count | Payload Schema & Field Types | Version Notes |
|:---|:---|:---:|:---|:---|
| `playback` | Attack Playback | 49,332 | `instance=<int> position=<float> nodeWeight=<float> montageWeight=<float> base=<Vector> tip=<Vector>` | High-frequency continuous tick telemetry. Vector format: `X=%g Y=%g Z=%g`. |
| `sweep` | Hit Detection | 3,633 | `instance=<int> window=<str> from=<float> to=<float> tipDistanceCm=<float> substeps=<int> clamped=<int> [baked=<int>]` | F4-F6 chord sweep; F7+ adds optional `baked=1` for 120 Hz apex path. |
| `event` | Hit Windows | 1,967 | `encounter=<int> generation=<int> instance=<int> kind=<Open\|Close\|Recovery\|Finished> window=<str> group=<str> localSeconds=<float> label=<str>` | State transitions for attack active windows. |
| `hit` | Hit Detection | 1,109 | `instance=<int> window=<str> key=<str> outcome=<OutcomeEnum> hpApplied=<float> healthBefore=<float> healthAfter=<float>` | Records Accepted vs RejectedDuplicate hit outcomes. |
| `refusal` | Move Selector | 895 | `attack=<int> card=<str> reason=<RefusalToken>` | Hard-filter disqualifications prior to scoring. |
| `candidate` | Move Selector | 888 | `attack=<int> card=<str> score=<float>` | Qualified candidates evaluated with normalized utility scores. |
| `cleanup` | Move Execution | 551 | `reason=<str> modelIdle=<int> ownedMontageStopped=<int>` | Playback cleanup; `reason` may include multi-word text. |
| `playback_start` | Attack Playback | 492 | `encounter=<int> generation=<int> instance=<int> montage=<str> slot=<str> rate=<float> label=<str>` | Emitted upon montage instance commitment. |
| `decision` | Move Selector | 422 | `attack=<int> chosen=<str> score=<float> range=<float> [phase=<str>]` | Decision gate selection; F11+ adds `phase=Phase_N`. |
| `boss_hit` | Player Intake | 289 | `damage=<float> healthBefore=<float> healthAfter=<float>` | Character health damage applied via hit intake. |
| `nav` | Navigation | 267 | `request=<int> projected=<Vector> fullPath=<int> result=<int>` | Projected target location and path validity. |
| `walk` | Locomotion | 260 | `start=<Vector> end=<Vector> distanceCm=<float> rangeCm=<float> bandMin=<float> bandMax=<float> capsule=<Vector> mesh=<Vector>` | Locomotion approach to card range band. |
| `RESULT` | Fixture Run | 248 | `outcome=<str> [acceptedHits=<int>] [attacks=<int>]` | F3d: `CompletedTelemetryOnly`; F4: `acceptedHits=1`; F5+: `attacks=M`. |
| `boss_health_read` | Fixture Health | 240 | `reader=<str> ok=<int> value=<float> max=<float>` | Attribute reader verification. |
| `target_health_init` | Fixture Target | 227 | `value=<float> readback=<float> label=<str>` | Target dummy initialization HP. |
| `slot_graph` | Animation Graph | 222 | `name=<str> nodeClass=<str> verified=<int> label=<str>` | AnimBP slot graph integrity check. |
| `dependencies` | Asset Wiring | 222 | `mesh=<str> skeleton=<str> animClass=<str> sequence=<str> slot=<str> resolved=<int> label=<str>` | Profile asset resolution validation. |
| `nav_ready` | Navigation | 213 | `waitedSeconds=<float>` | Navigation system readiness time. |
| `invariant` | Test Verification | 203 | `targetHPBefore=<float> targetHPAfter=<float> (expectedHP=<float> acceptedHits=<int> appliedDamage=<float> \| damageAPIInvocationsByThisExecutor=<int>)` | F3d telemetry verification vs F4+ damage verification. |
| `boss_health` | Fixture Health | 133 | `max=<float> playerHitDamage=<float> label=<str>` | Boss HP pool configuration. |
| `pack_style_known` | Player Intake | 107 | `waitedSeconds=<float>` | Player pack combat style detection wait. |
| `posture_drain` | Posture System | 95 | `amount=<float> postureBefore=<float> postureAfter=<float> max=<float>` | Discrete posture drain per hit. |
| `montage_natural_end`| Attack Playback | 89 | `instance=<int> lastPosition=<float> naturalEnd=<float>` | Natural blend-out completion detection. |
| `phase_transition` | Life Phases | 76 | `attack=<int> from=<str> to=<str> health=<float> max=<float> fraction=<float>` | Threshold crossing triggering phase transition. |
| `heading_commit` | Motion Control | 66 | `instance=<int> yaw=<float> turnedDegrees=<float> maxRateDegPerSec=<float> capDegPerSec=<float> [decisionRangeCm=<float> liveRangeCm=<float>]` | Rotation rate cap; BUILD-104 adds range telemetry. |
| `heading_locked` | Motion Control | 62 | `instance=<int> yawAtCommit=<float> maxDriftAfterCommitDegrees=<float>` | Verifies 0 drift during commit lock. |
| `bleed_buildup` | Ailments | 58 | `amount=<float> buildup=<float> threshold=<float> result=<str>` | Bleed accumulation step. |
| `attack_row` | Weapon Intake | 49 | `weapon=<str> kind=<str> found=<int> posture=<float> bleed=<float> healthMult=<float> [via=<str>]` | F10 baseline; BUILD-85 adds `via=pending`. |
| `boss_dead` | Life Phases | 45 | `generation=<int> executorAborted=<int>` | Death state transition and executor abort. |
| `encounter_reset` | Encounter Lifecycle | 40 | `(generation=<int> oldState=<str> executorRearmed=<int> bossHealth=<float> targetHealth=<float> \| refused generation=<int> reason=<str>)` | Clean encounter reset vs restart refusal. |
| `ERROR` | Diagnostics | 34 | `token=<str> [details...]` | Framework error and invariant failure lines. |
| `combo_gate` | Conditional Combos | 31 | `gate=<int> node=<str> outcome=<str> range=<float> yaw=<float> result=<str> next=<str> reason=<str>` | Combo branch decision at gate snapshot. |
| `stance_break` | Stagger System | 26 | `state=<str> duration=<float> generation=<int> phase=<str>` | Stance break stagger state entry. |
| `stagger_recovery` | Stagger System | 24 | `postureRefilled=<float> generation=<int>` | Stagger completion and posture refill. |
| `overlay` | Debug Display | 22 | `Card=<str> State=<str> Phase=<str> Range=<str> Cone=<str> Window=<str> Posture=<str> Health=<str> Stagger=<str> PhaseHold=<str>` | Continuous runtime overlay telemetry. |
| `combo_start` | Conditional Combos | 16 | `root=<str> move=<str> maxDepth=<int>` | Combo chain initiation. |
| `combo_step` | Conditional Combos | 15 | `node=<str> move=<str> depth=<int>` | Combo progression to next child node. |
| `stagger_anim` | Stagger System | 8 | `state=<Start\|Loop\|End\|Finished> [sequence=<str> slot=<str> length=<float> loops=<int> postureRefilled=<float>]` | Triplet montage progression. |
| `pending_hit_queued`| Weapon Intake | 8 | `weapon=<str> kind=<str> blades=<int>` | Pending hit queue intake. |
| `bleed_proc` | Ailments | 7 | `procs=<int> damage=<float> healthBefore=<float> healthAfter=<float> nextThreshold=<float>` | Burst damage and threshold scaling on proc. |
| `combo_end` | Conditional Combos | 6 | `reason=<str>` | Clean combo conclusion (e.g. `AttackBudget`). |
| `reposition` | Locomotion | 5 | `attempt=<int> max=<int> range=<float> reason=<str>` | Opt-in walk repositioning attempt. |
| `walk_resumed` | Locomotion | 5 | `generation=<int>` | Navigation walk resumption. |
| `combo_gate_duplicate`| Conditional Combos| 4 | `gate=<int> result=<str> reason=<str> stateUnchanged=<int>` | Rejection of duplicate gate evaluation. |
| `phase_anim` | Life Phases | 4 | `(state=Triggered sequence=<str> slot=<str> length=<float> from=<str> to=<str> \| state=Finished phase=<str>)` | Dedicated phase transition animation montage. |
| `reposition_turn` | Locomotion | 3 | `start yawToTarget=<float> range=<float> ratePerSecond=<float>` | In-band turn-in-place repositioning. |
| `target_health_mismatch`| Fixture Target | 3 | `valid=<int> actual=<float> expected=<float> generation=<int>` | Target HP corruption detection. |
| `posture_regen_start`| Posture System | 2 | `posture=<float> sinceLastDrainSeconds=<float> delaySeconds=<float> perSecond=<float>` | Posture regeneration initiation. |
| `posture_regen_full`| Posture System | 1 | `posture=<float> max=<float>` | Full posture pool restoration. |
| `nav_not_ready` | Navigation | 1 | `navSystem=<int> buildInProgress=<int> targetLocation=<Vector>` | Navigation mesh wait diagnostics. |

---

## 4. Semantic Monotonicity & Ordering Analysis

Per `[C-553]`, four formal semantic monotonicity checks were executed across all 633 log files:
1. **Timestamp Monotonicity:** UE timestamps (when present) must be non-decreasing ($t_{i} \ge t_{i-1}$).
   - **Result:** **0 violations.** Timestamps never go backwards in any committed log.
2. **Gate ID Uniqueness:** `gate=` in `combo_gate` must be unique within an encounter run.
   - **Result:** **0 violations.** Monotonic gate progression holds in all runs.
3. **Instance ID Reuse:** `instance=` in `playback_start` must not be reused within the same generation.
   - **Result:** **0 violations.** Instance indices increment monotonically per generation.
4. **Attack ID Monotonicity:** `attack=` in `decision` must be strictly increasing ($attack_N > attack_{N-1}$) within one encounter run.
   - **Result:** Exactly **17 occurrences of `DUPLICATE_ATTACK_ID`** identified across 633 logs.

### Root Cause of the 17 Duplicate Attack ID Findings:
All 17 occurrences occurred in the F8 mid-attack stance break proof suite and its subsequent regression runs:
- In F8 (`L_SevarogFrameworkProofF8`), the test harness injects a posture-draining player hit at $t_0 + 0.94\text{s}$ during attack 1.
- Attack 1 is aborted mid-swing (`event kind=Aborted`, `cleanup reason=StanceBreak`, `stance_break state=MidAttack`).
- The framework character controller tracks `AttacksDone`, which only increments upon *natural completion* of an attack.
- Consequently, after recovery from stagger and transition to Phase 2, `AttacksDone` is still 0, so the next decision evaluates as `decision attack=1` a second time.

### Exhaustive List of the 17 Semantic Findings:
1. `Docs/BossCombatReview/Execution/Claude/B_COMBO2/reg_f8/editor_raw.log:1714` -> `DUPLICATE_ATTACK_ID: attack=1 already seen in run`
2. `Docs/BossCombatReview/Execution/Claude/B_DEF002/reg_f8/editor_raw.log:1706` -> `DUPLICATE_ATTACK_ID: attack=1 already seen in run`
3. `Docs/BossCombatReview/Execution/Claude/B_QA001/pie2/editor_raw.log:1728` -> `DUPLICATE_ATTACK_ID: attack=1 already seen in run`
4. `Docs/BossCombatReview/Execution/Claude/B_QA001/pie_f8_overlay/editor_raw.log:1729` -> `DUPLICATE_ATTACK_ID: attack=1 already seen in run`
5. `Docs/BossCombatReview/Execution/Claude/F10/clay/editor_raw.log:1747` -> `DUPLICATE_ATTACK_ID: attack=1 already seen in run`
6. `Docs/BossCombatReview/Execution/Claude/F10/reg_L_SevarogFrameworkProofF8/editor_raw.log:1723` -> `DUPLICATE_ATTACK_ID: attack=1 already seen in run`
7. `Docs/BossCombatReview/Execution/Claude/F11/pie_midattack/editor_raw.log:1724` -> `DUPLICATE_ATTACK_ID: attack=1 already seen in run`
8. `Docs/BossCombatReview/Execution/Claude/F11/reg_f8/editor_raw.log:1725` -> `DUPLICATE_ATTACK_ID: attack=1 already seen in run`
9. `Docs/BossCombatReview/Execution/Claude/F8/ki150b/mid/editor_raw.log:1710` -> `DUPLICATE_ATTACK_ID: attack=1 already seen in run`
10. `Docs/BossCombatReview/Execution/Claude/F8/midattack_after_walkfix/editor_raw.log:1625` -> `DUPLICATE_ATTACK_ID: attack=1 already seen in run`
11. `Docs/BossCombatReview/Execution/Claude/F8/pie_run1/editor_raw.log:1629` -> `DUPLICATE_ATTACK_ID: attack=1 already seen in run`
12. `Docs/BossCombatReview/Execution/Claude/F8/pie_run2/editor_raw.log:1624` -> `DUPLICATE_ATTACK_ID: attack=1 already seen in run`
13. `Docs/BossCombatReview/Execution/Claude/F8/pie_run3/editor_raw.log:1621` -> `DUPLICATE_ATTACK_ID: attack=1 already seen in run`
14. `Docs/BossCombatReview/Execution/Claude/F9/reg_L_SevarogFrameworkProofF8/editor_raw.log:1722` -> `DUPLICATE_ATTACK_ID: attack=1 already seen in run`
15. `Docs/BossCombatReview/Execution/Claude/KI151/clay/editor_raw.log:1770` -> `DUPLICATE_ATTACK_ID: attack=1 already seen in run`
16. `Docs/BossCombatReview/Execution/Claude/KI151/reg_L_SevarogFrameworkProofF8/editor_raw.log:1717` -> `DUPLICATE_ATTACK_ID: attack=1 already seen in run`
17. `Docs/BossCombatReview/Execution/Claude/KI151/reg_f10_clay_immediate/editor_raw.log:1744` -> `DUPLICATE_ATTACK_ID: attack=1 already seen in run`

---

## 5. 50-Token Mutation Verification Suite

To prove that the schema validator strictly rejects corrupted, malformed, or misspelled fields across every single recognized token, the test suite `test_validate_framework_proof_logs.py` implements an automated 50-token mutation test (`test_50_token_mutation_suite`):
- For each of the 50 tokens, a verified real line is extracted from the committed logs.
- The primary key is mutated (e.g. `attack=` -> `attackz=`, `instance=` -> `instancez=`, `reason=` -> `reasonz=`).
- The mutated line is passed to `validator.validate_line()`.
- **Result:** **50 of 50 tokens correctly fail validation when mutated.**

---

## 6. Architectural Decision: `BOSS-QA-002` Retained as PARTIAL

In strict adherence to Tech Lead Claude's evaluation in `[C-553]`, `BOSS-QA-002` remains **PARTIAL** in the Track B Ledger:
1. **Missing Categories:** Defenses (player block, guard, parry) and generic interrupts have no runtime telemetry in the framework.
2. **Semantic Stability Limits:** While timestamps, gate IDs, and instances are strictly monotonic, attack IDs re-evaluate following mid-attack stagger aborts (17 occurrences).
3. **Evidence Boundary:** A Python format validation script, while essential for telemetry hygiene and CI regression testing, does not constitute a C++ framework test assertion or an exact live PIE value line.
4. **Current Status:** Census remains **34 WITNESSED / 24 PARTIAL / 24 NOT YET**.
