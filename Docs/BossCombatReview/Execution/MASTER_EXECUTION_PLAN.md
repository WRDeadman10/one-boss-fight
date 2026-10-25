# Combat Intelligence Improvement Program

Date: 2026-10-25. Owner authorizes coordination and read-only P0 only. Technical lead/reviewer: Codex (Astra role); gameplay/editor/build/runtime: Claude; animation/content: Antigravity; final design, feel, commits and release: owner.

## Authority and operating boundary

Current owner mission > approved Master Design Freeze plus explicit subsequent owner decisions > verified architecture/runtime > approved fixes/tests > reference > recommendations. Existing pack backbone remains. No gameplay code by Codex under this assignment. No implementation task may start before P0 acceptance and owner approval of its scope.

Mailbox remains sole communication/acknowledgment record: [TEAM_MAILBOX.md](C:/UnrealProject/OneBossFight/Documentation/TEAM_MAILBOX.md). Initiative files are an index, briefs and review records, not a competing project tracker. Existing project tracker ownership stays with Claude; proposed updates go through mailbox. No instruction-file rewrite.

## Current state

Reference (10 files) and prior audit (12 files) are available in place. Prior 83-row classifications: 8 implemented, 58 partial, 1 missing, 13 unverified, 3 not applicable. They are an evidence snapshot, not current runtime acceptance or a completion percentage.

C-85 and A-38 now explicitly acknowledge roles, active availability and exclusive P0 report/evidence claims. P0 is in progress; reports and independent review remain pending. Claude retains editor/build/performance ownership; AG works offline with Claude-produced captures. Do not launch replacement GPT agents under their names. Owner authorizes recurring mailbox checks and scoped replies; MAILBOX_WATCH_STATE.md records handled messages.

## Binding constraints to carry forward

- Ember Warden / project greatsword, ember javelin and sword leap reskin; do not restore reference hammer/dagger presentation or retired character framework.
- A1–A6 roles; identify additional live pack attacks without silently deleting or blessing them.
- Phase two at 60%; death wins; earned break/riposte resolves before queued transition. Existing transition policy and hit-stun-immunity-versus-HP-protection distinction require evidence, not silent correction.
- Preserve 3.2 m roll, 0.30 s double-tap and owner-kept measured dodge windows. Do not substitute reference frame counts.
- Current balance: 2000 boss HP, 3% bleed, Starter multiplier 0.39, riposte 100; 2–4 minute target is owner-directed. No retune in P0.
- Authored close clips now replace part of the old stand-in set. Read actual montage plus fallback and effective rates; do not assume old telegraph notes still describe every clip.
- One editor owner. Claude retains editor/build/PIE. AG offline analysis may run independently; live capture is serialized through Claude or explicit handoff.
- No pack edits, asset saves/imports, destructive git, commits or pushes. Preserve dirty tree and existing claims.
- Packaged 1080p average >=60 FPS and p99 <=16.67 ms on accepted RTX 3060 proxy; real console session and NVIDIA adapter identity required. 120 FPS is stretch.

## Phase numbering reconciliation

The CURRENT MISSION numbering below controls. Old audit P-n references are historical proposal labels, not current assignments.

| Mission phase | Scope | Old audit package mapping | Gate |
|---|---|---|---|
| P0 | Current graph/runtime/visual baseline | Old P0 plus U01–U12 | Independent reconciliation and owner scope approval |
| P1 | Readability and synchronized telegraphs | Visual part of old P1 | No unfair invisible damage in approved scenarios |
| P2 | Event reliability, identity, lifecycle | Temporal part of old P1 + old P2 | No skipped required event, stale attribution or duplicate hit in bounded tests |
| P3 | Damage/defense semantics | Old P3 | Documented per-move outcomes across all paths |
| P4 | Geometry and natural attack coverage | Old P4 + A4 integration from old P5 | Honest visible reach and eligible natural selection |
| P5 | Conditional combos, commitment, punish windows | Old P6 | Legal branches and measurable intended openings |
| P6 | Decision/movement intelligence | Decision part of old P5 + movement part of old P7 | Context-linked choices; no omniscience or rival planner |
| P7 | Phase intelligence/pacing | Phase part of old P7 + pressure policy | Stable meaningful phase pressure and recovery |
| P8 | Complete validation | Old P8 | Independent review, runtime/package/performance evidence and owner feel acceptance |

## P0 workflow

1. Receive C-n/A-n acknowledgment of X-91 and separate task briefs; confirm no claim conflict and Claude's editor occupancy.
2. Claude maps live world -> info/controller -> BT/BB -> ability -> montage -> collision -> resolved outcome. AG audits exact animations and visual contact using identical evidence IDs.
3. Reuse historical evidence where it answers the question; label build/freshness and harness switches. New read-only probes/captures only within acknowledged scope.
4. Claude publishes current architecture, attack inventory, decision graph, timing/damage matrix, regression baseline and observed defects. AG publishes visual/animation report with measured captures.
5. Codex independently reads raw graphs/logs/diffs/assets evidence; challenges gaps and classifies confirmed implementation, partial behavior, defects, unknowns, design improvements and optional additions separately.
6. Codex finalizes all 83 reference rows against project precedence and proposes minimal P1–P8 scope, costs/dependencies/risks and rollback boundaries.
7. Owner approves improvement scope explicitly. Until then no implementation. Agent absence leaves affected task BLOCKED, not assumed complete.

## Review gate after P0

For each approved implementation: smallest safe specification -> named implementer and exclusive file claim -> actual diff and calling-path review -> focused actual tests -> visual review when applicable -> gate decision. Review verdicts: ACCEPTED, ACCEPTED WITH DOCUMENTED LIMITATIONS, CHANGES REQUIRED, BLOCKED. A limitation cannot waive a critical invariant or owner approval.

Focused regression per change; full required suite before final P8 acceptance. Compiler success is not behavior proof. Test totals do not prove readability, fun or current complete coverage.

## Navigation

- [Phase status](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/PHASE_STATUS.md)
- [Delegations and claims](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/DELEGATION_REGISTER.md)
- [Claude brief](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/P0_CLAUDE_AUDIT_BRIEF.md)
- [Antigravity brief](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/P0_ANTIGRAVITY_VISUAL_BRIEF.md)
- [P0 reconciliation register](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/P0_BASELINE_RECONCILIATION.md)
- [Review findings](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/CODE_REVIEW_FINDINGS.md)
- [Test evidence](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/TEST_EVIDENCE_INDEX.md)
- [Pending design decisions](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/DESIGN_DECISIONS_PENDING.md)
- [Final report status](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/FINAL_COMBAT_QUALITY_REPORT.md)


## Update 2026-10-25 (Claude): directive and parallel work

Technical lead: Claude (after the Codex hand-over); Codex is reviewer and data-model designer again (budget reset); AG is animation/authoring investigator. New first priority from the owner: audit match of 100 percent plus a data-driven framework (`OWNER_DIRECTIVE_2026-10-25.md`). Parallel tracks until the architecture gate: Claude finishes the P0 technical baseline (E-001 to E-004 and onward) and schedules captures; Codex T1 to T4 (`P0_CODEX_BRIEF_DATA_DRIVEN.md`); AG T1 to T4 (`P0_AG_BRIEF_AUTHORING_CONTRACT.md`). Then Claude writes `DATA_DRIVEN_ARCHITECTURE_GATE.md` (scope, order, risk, rollback, regression per step) for owner approval; code changes start only after that approval and each change is reviewed by Codex against the diff and tested by Claude.

## Settled reading and order of work (Claude, 2026-10-25, owner: "take the best call")

The owner's audit with Codex (reference study, existing-boss audit with what is already implemented, the 83 requirement IDs) is the SPINE of everything. There is one program, not two:

- **Target** = the 83 IDs (`P0_BASELINE_RECONCILIATION.md`) all IMPLEMENTED with evidence, or owner-confirmed N/A. This is what "100 percent" is measured on, at P8.
- **Delivery order** = P0 to P8 (the mission numbering table above), each phase closing named IDs.
- **Cross-cutting requirement** = data driven (`OWNER_DIRECTIVE_2026-10-25.md`): every fix lands as data plus animation, not as new per-boss C++. The second-boss canary is the proof, run at P8.
- Nothing in the audit, the briefs, the hand-over or the reviews is dropped: every open item stays in its register (`CODE_REVIEW_FINDINGS.md`, `P0_BASELINE_RECONCILIATION.md`, `DESIGN_DECISIONS_PENDING.md`, `PHASE_STATUS.md`).

Order, with one deliberate call: the data foundation goes BEFORE the behaviour fixes, because fixes written into hard-coded tables (tracker rows, per-move components, the fixed build table) would have to be migrated a second time.

1. **P0 close** (now): Claude technical baseline and captures; AG visual baseline and authoring contract; Codex hard-code inventory, data model, 83-ID reconciliation, independent review. Output: final dispositions per ID, gap list, `DATA_DRIVEN_ARCHITECTURE_GATE.md`.
2. **Owner gate**: approve the gate document (scope, order, risk, rollback, regression per step, the D-10 N/A list). No code before it.
3. **DD-1 foundation** (behaviour-identical): boss, move, weapon, build and encounter definitions as data assets, existing tracker rows and builds migrated into them, every existing regression driver green after each step, rollback per step.
4. **P1 to P7** on top of the data model, each as data-driven features (readable telegraphs and wave cue; event reliability and identity; damage and defense semantics; geometry and natural coverage of ALL live moves including Mid01, sprint, retaliation and A4; combos and punish windows; decision and movement; phase pacing). Each phase: smallest specification, named implementer, exclusive claim, Codex reviews the diff, Claude runs focused tests, AG reviews visuals.
5. **P8**: full regression, packaged performance (60 FPS, p99 16.67 ms, console session), owner feel test, second-boss canary, final 83-ID recount.

Constants that stay fixed unless the owner changes them: reskin and A1 to A6 roles, 60 percent phase, 3.2 m roll, owner-kept iframe windows, current balance numbers, no pack edits, no commit or push by agents.
