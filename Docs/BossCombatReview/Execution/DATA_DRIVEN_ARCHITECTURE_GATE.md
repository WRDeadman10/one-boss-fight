# Data-driven architecture gate (for the owner's approval)

Author: Claude (technical lead). 2026-10-25. Status: OWNER DECISIONS RECEIVED 2026-10-25 (see section 0). Code, asset and config changes only inside the approved decisions; no pack file changes; no commits. Inputs: owner directive (`OWNER_DIRECTIVE_2026-10-25.md`), Codex D01 to D04 (`Codex/`), Antigravity contract and sheets (`Antigravity/`), my evidence E-001 to E-008 (`Claude/Evidence/`), mailbox C-88 to C-94.

## 0. Owner decisions (2026-10-25, in chat, answering the questions of this document)

- **G-1 APPROVED:** the architecture and order of sections 3 and 4 (data foundation DD-1 first with identical behaviour, then P1 to P7 as data-driven features, then the second-boss canary at P8).
- **G-3 APPROVED:** the scratch-folder asset test (a project-owned `BP_EnemyInfo` and a minimal project BehaviorTree selected through the placed boss's `EnemyInfoRef`). Scope: new assets in a scratch folder only, no pack asset edit, no overwrite of any existing asset.
- **G-4 NOT APPROVED:** no `Montage_Stop` call-stack instrumentation. **G-5 NOT APPROVED:** no test hook to start the pack moves on demand. The A2 canceller and CAP-03 stay open until evidence can be gathered without them.
- **G-2 DECIDED: no N/A.** All 83 requirements must end IMPLEMENTED with evidence. Consequence, stated plainly: the conditional rows become real work, in particular BOSS-QA-008 (server authority: replicated attack identity, start time, section, target and phase and a two-client test at 80/150 ms latency), BOSS-HIT-012 (a boss grab), BOSS-ANM-003 (variable bounded hold), BOSS-AWR-008 (capped adaptive memory), BOSS-SEL-004 (comparable utility scoring on top of or instead of the ordered pack selector), and ANM-006/DEF-005. Claude will cost each of them in the P0 reconciliation and bring a sequenced plan (what is cheap, what needs a new mechanic, what needs networking tests) for the owner to re-confirm the size; nothing is dropped.
- **Scope size RE-CONFIRMED (2026-10-25, after D05):** keep all 83 required, networking (QA-008) included, built in parallel with each phase following Codex's sequencing (authority seams from DD-1, P2 transaction first, cross-cutting verification, listen/dedicated two-client test at P8); nothing dropped, effort is large and not estimated in calendar time.
- **G-6:** not asked; the performance protocol stays as written (60 FPS average, p99 16.67 ms, RTX 3060 proxy, real console session, measured at P8).

## 1. HISTORICAL (superseded by section 0): the decisions that were asked

> The table below is the original request. Section 0 holds the owner's actual answers and governs: G-1 and G-3 approved, G-4 and G-5 NOT approved (do not re-request, do not treat as pending), no N/A rows (all 83 required). Nothing here may be used to remove or defer a required feature.


| # | Decision | Recommendation |
|---|---|---|
| G-1 | Approve the architecture and the order in section 3 and 4 (data foundation DD-1 first, behaviour-identical; then P1 to P7 as data-driven features; P8 proves it with a second boss) | Approve |
| G-2 | N/A list (section 6): confirm, change or reject each candidate | Confirm QA-008, HIT-012; decide ANM-003, AWR-008, SEL-004 as owner design questions; keep SEL-008 as implemented bounded safety |
| G-3 | Allow ONE scratch-folder asset write to prove adapter route (a): a project-owned `BP_EnemyInfo` + minimal project BehaviorTree selected through the placed boss's `EnemyInfoRef`; no pack asset edit | Allow |
| G-4 | Allow a Development-only diagnostic (log a script call stack from `Montage_Stop` on the boss mesh) to find who cancels the A2 slam (gameplay-code instrumentation, removed after use) | Allow |
| G-5 | Allow a Development-only test hook that can start the three pack moves Mid01, sprint, retaliation on demand (needed for captures and tests; `TryActivateByTag` has no Python entry today) | Allow |
| G-6 | Confirm the performance protocol stays as is: 60 FPS average, p99 16.67 ms, RTX 3060 proxy, real console session, measured at P8, not now | Confirm |

## 2. What the P0 evidence says (short; raw files cited)

1. **Boss, weapons, builds are not data today.** Tracker rows are constructed in C++ (`RPGAttackTracker.cpp:24-103`), A4, A5 and A6 each have their own component, the three builds are a fixed C++ table (`RPGBuildRules.h:50-52`), weapons are partly data (`URPGWeaponAttackTable`). Codex D01: 61 architectural entries, 191 editable properties, 252 anchors (60 of 60 spot-checked correct).
2. **Three live damaging pack moves are outside the project's attack model** (Mid01, sprint follow-up, retaliation; E-002), with their own notify timings (E-002-10); Mid01 was seen once in five valid bot fights.
3. **The A2 slam rarely reaches its damage window** (E-005): 9 of 11 observed instances stopped before the tracked damage window (nine in Windup, one inside the open window at 1.99 s, one replaced by another attack in Recovery; 5 of 6 fights' first slam at 0.03 to 0.06 s: a sample count, not a frequency), and in the traced case a cut slam left its ability active for about 1.4 s, which blocks the next attack and looks like the boss standing idle. The canceller is not identified; no project code and no player hit explains it.
4. **A4: no natural route found in the inspected native, BT and style evidence (a Blueprint caller of the public `StartMove` is not excluded), and in one forced run its production query does not match the visible blade** (E-008): planar arc of 380 cm reach against a largest sampled estimated tip reach of 312 cm, angular differences of about 51 to 174 degrees (shortest circular); none of six tested socket names exists on the visible sword component (a bounds-axis tip estimate was used).
5. **A5 is released 0.05 s (nominal) or 0.07 s (observed) after the sidecar's intended 0.40 s release marker** (E-007; 1 to 1.4 frames at 20 fps; no pose capture), a feel question, not a defect.
6. **Harness fact:** a minimized editor window makes PIE run at about 3 fps and invalidates every timing run (E-004).
7. **Independence limit:** Codex independently reviewed my evidence (D04, six findings, all adopted); my own E-005 to E-008 await Codex review.

## 3. Architecture (Codex D02, adopted with the changes in section 5)

- Six data definitions plus a catalog: `BossDefinition`, `BossMoveDefinition`, `WeaponDefinition`, `BuildDefinition`, `EncounterDefinition`, `PresentationDefinition`; stable IDs, no C++ enum for content; nested structs instead of an asset per number; `URPGWeaponAttackTable` is the pattern.
- **One shared combat runtime**, no per-boss code: a request adapter that every pack and native attack start passes through before playback (accepted-action token, legal-request gates), a compiled timeline per animation variant evaluated with crossed intervals and a watchdog, shared effect executors (weapon sweep, planar sweep, projectile, radial wave, paired action) with data parameters, one damage/defense resolver. Per-instance mutable state never lives in a data asset or a singleton keyed by move name.
- **Animation is data.** Active window and heading window already exist as notifies in the montages; the missing semantics (commit, recovery end, branch gate, telegraph cue, hyperarmor and i-frame windows) use two project notify types: `AN_CombatEvent` and `ANS_CombatWindow`. Pack montages stay unedited (project wrappers or manifests); only project-owned montages carry the new markers.
- **Pack stays the execution backbone.** Adapter route (a): a project-owned `BP_EnemyInfo` and BehaviorTree selected per instance through `EnemyInfoRef` (E-006: the pack controller runs the tree named by the pawn's info), with generic C++ tasks that ask the shared runtime and then call the pack abilities; route (b), a pre-activation hook in the pack, was not found. G-3 permits TESTING (a) in a scratch experiment (not yet run; it proves nothing until it does).
- Existing per-move components (A4/A5/A6) stay as diagnostic facades during migration; exactly one path may damage, move or unlock at each step.

## 4. Order and gates

1. **P0 close** (this document, the evidence set, D03 dispositions) -> **owner gate G-1 to G-6**.
2. **DD-1, behaviour-identical** (D02 steps 0 to 3): pin baseline and source hashes; catalog, weapon and build assets behind a legacy facade (a fourth entry added as data); boss, encounter and presentation hydration; timeline shadow-compared against the current tracker (mismatches are findings, never auto-tuned). **Parity includes today's behaviour as measured**: the A2 early cuts, the untracked pack moves, the A4 query. Any corrected behaviour is a P1 to P7 change that needs its own approval.
3. **P1 to P7** on the data model, each with the smallest specification, an exclusive file claim, a Codex diff review, my focused tests, AG visual review: P1 readable telegraphs and a production wave cue (RV-01); P2 request adapter, accepted-action identity before play, cancellation policy per move ("a move declares its protected window and its legal cancellers"), crossed-interval events, finalisation and watchdog (A2 mechanism, RV-02/05); P3 one damage and defense contract for pack and native paths (RV-04); P4 geometry honesty and natural coverage of ALL live moves incl. Mid01, sprint, retaliation, A4 (RV-06/07/11); P5 combo, commitment and recovery with measured punish windows; P6 decision and movement; P7 phase pacing.
4. **P8:** full registered regression, packaged performance on the accepted protocol, owner feel test, the second-boss canary (D02 pass record 1 to 8: different boss, three differently parameterised moves, two phases, new weapon, fourth build, no `.cpp/.h` edit, Boss01-Canary-Boss01 order, two instances in diagnostics), final 83-ID recount.

Every DD-1 step: current code and project asset manifest pinned, the user's dirty tree preserved (no reset, clean, stash, checkout), rollback = switch the encounter's versioned binding back to the previous complete path (never mid-fight), no step starts while the previous has a blocking regression.

## 5. Changes to D02 and the authoring contract

- AG's contract (Revision 02) is a proposal; its rules for permanent commitment, poise-break immunity, tip-socket snapping, default 20 cm radius, universal in-place motion and indefinite hold are NOT adopted (Codex D02 section "A-44 review"). Adopted: explicit motion ownership, bounded holds, the existing 50 cm trace radius, A5 release kept at 0.45 s until approved.
- Add to D02: cancellation policy per accepted action (A2 evidence); the visible-blade/query relation as a validated data field with a stated offset (E-008); sockets must exist on the project mesh or be named as an offset (the greatsword has none at run time); the legacy-parity baseline lists the behaviours in section 2.

## 6. HISTORICAL (superseded by section 0): N/A candidates

> The owner decided no N/A: every row below is required and is costed in `Codex/D05_CONDITIONAL_ROWS_COSTING.md`. The original text is kept for provenance.


QA-008 multiplayer authority (single-player duel; shared encounter IDs stay); HIT-012 boss grabs (none approved, the riposte stays tested); ANM-003 variable chosen hold (stable authored A2 apex stays the target; indefinite hold never accepted); AWR-008 adaptive pattern memory; SEL-004 comparable utility scoring (current ordered pack selector); SEL-008 empty-pool policy (recommend keep a bounded fallback). Also decide or confirm: ANM-006 conditional warping (a no-warp design needs a rationale), DEF-005 boss defensive actions. Everything else in the 83 must end IMPLEMENTED with evidence.

## 7. Risks and limits

Dirty working tree (about 20 files) and a Blueprint-only pack that must not change; the pack selector's behaviour is only partly graph-proven (edge-level evidence incomplete, E-006); the A2 canceller is unknown; the 60 FPS target is far from today's packaged number (28 to 29 FPS, PERFORMANCE_LOG) and is a separate Claude-owned track; one editor and one machine, timing runs need a restored window; Claude's own P0 evidence has only Codex's review and AG's challenge as independence; no phase is accepted by this document.

## 8. If approved

Claude writes the DD-1 step 0 baseline manifest (hashes, config, test table) and the step 1 specification for Codex review, claims the files in the mailbox, and starts step 1 only after Codex accepts the specification. If the owner later changes a decision, the dependent order is restated in the mailbox before anything is built; a required feature is never dropped by a rejected request.
