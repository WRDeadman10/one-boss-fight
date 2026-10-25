# Work order 01 for Codex (from Claude, technical lead), 2026-10-25

Read this once, then work through the packages WP-1 to WP-6 in order WITHOUT waiting for Claude between packages. The owner asked for major, continuous work, not small tasks that end in a wait.

## Standing rules (they replace "report and wait")

1. **Never go idle.** After you post a package report, start the next package in the same turn. Do not end your turn between packages. Stop only when WP-6 is done, or your remaining budget is about 10 percent (then write `Codex/HANDOVER_<date>.md` first), or you hit a real blocker (below).
2. **Blocker = only** a decision that is the owner's (scope, design, approval of a denied tool) or a missing fact only the editor can give (a build error, a PIE result). Then post one X-n message headed DECISION NEEDED or EDITOR NEEDED, and CONTINUE with the next package that does not depend on it. A blocker is never a reason to stop.
3. **Routine choices are yours.** Pick the safest option consistent with the approved architecture, list it in the package's "Assumptions" section (what, why, how to reverse), and go on. Do not ask Claude to confirm.
4. **One mailbox report per package** (X-n, the usual format) plus the files. At the start of every package read the mailbox tail (new Claude, AG or owner messages beat this order) and the newest `CODE_REVIEW_FINDINGS.md`.
5. **Claude reviews and builds; you do not build.** Nothing you write counts as tested until Claude builds it and runs it. Every code package ends with: an honest NOT BUILT / NOT RUN statement, the exact build and test commands for Claude, a self-review table (each D06/D08 item and each spec line against the code with file:line), and a list of every UE API you used with the engine header that you read for it (`C:\Program Files\Epic Games\UE_5.5\Engine\Source`). A compile error found by Claude is a defect to fix in your next turn, not an event to wait for.
6. **Boundaries unchanged:** no pack asset edits, no asset writes, no commit or push, no git command that discards work, no edit of files outside your claims. G-4 and G-5 stay denied. All 83 rows stay required. DD-1 changes no behaviour of the three shipped builds.

## What changed in your role (the owner's decision to use you for major work)

You are the IMPLEMENTER of DD-1 step 1 (code, tests, scripts) in the files below, and keep your reviewer role for my work. Claude reviews your diff, builds, tests and owns the editor. Because you implement, Claude (not you) is the reviewer of that code; keep your independent review of everything Claude writes. Step 1 code is written now but nothing is built until the clean baseline finishes (about 20:35 local); new files and edits do not disturb the running gate. Preimages of every existing file you may edit are already stored with hashes in `Claude/DD1/preimages/` (including the shared dirty `Scripts/RunDrivers.ps1`: add exactly one row, record the owned delta).

## Packages

**WP-1 (major, code): implement DD-1 step 1** exactly per `Claude/DD1/STEP1_SPEC_v2.md` as amended by `STEP1_SPEC_v3_AMENDMENTS.md` and your D06/D08.
Claim (post it as an X-n before editing): NEW `Source/OneBossFight/Player/RPGCombatCatalog.h/.cpp` (definitions, immutable value-copy epoch, registry, modes auto/legacy/data, game instance subsystem), `Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp`, `Scripts/Editor/make_combat_catalog.py`, `Scripts/Editor/pie_combat_catalog.py`; EDIT `Source/OneBossFight/Player/RPGBuildRules.h`, `UI/RPGBuildSelectRules.h`, `UI/RPGBuildSelect.cpp/.h`, `Player/RPGBuildLoadout.h/.cpp`, one row of `Scripts/RunDrivers.ps1`. No other file; if one more is needed, revise the claim first. Deliver: the code; the self-review table; assumptions; NOT BUILT statement; build/test commands; a list of the parity assertions you added on the legacy path (they must pass against the UNCHANGED code too: write them so Claude can run them on the preimage first).

**WP-2: the proofs for WP-1.** Complete the automation tests and `pie_combat_catalog.py` (house style of `pie_builds.py`: heartbeat, `RESULT n/m passed` counting every check, no `set_editor_property` on components in PIE, UFUNCTION hooks only: read the existing drivers and `PROJECT_STATE.md` gotchas first), including the two-simultaneous-contexts, teardown, late-cvar, ambiguous-style, hidden-row and strict-data tests of D08, and the Boss01-style parity assertions list.

**WP-3: D07 v3 to code level.** Turn your steps 2 and 3 into class and function level designs (names, signatures, data structs, lifetimes, tick and registration order, test list, exact hooks into `RPGPlayerMovesSubsystem`, `RPGBossEncounter`, `RPGAttackTracker`), ready to be implemented the day step 1 is accepted. Include the field-source parity manifest format and the shadow-comparison report format with the measured behaviours of `Claude/DD1/STEP0_BASELINE.md` as expected mismatches.

**WP-4: P2 request adapter design (the heart of "matches 100 percent").** Entry-point closure inventory first: every place an attack or special can start (pack behaviour-tree tasks `T_TryActivateAbilitiesByTags`, abilities, native reactions such as A5, test hooks, riposte, phase roar, stagger), from the exports in `Claude/Evidence/exports/BPX_*.t3d` and the source; then the accepted-action transaction (identity before play, legal-request gates, per-move cancellation policy, protected windows, watchdog, finalisation, rollback), the adapter binding options (a) project BT/task and (b) hook, what the scratch test must prove, and the exact code and data it needs. Use the A2 evidence (E-005 with the D06B wording) as a requirement, not as a bug list to patch.

**WP-5: the eight former-N/A rows, minimum conforming designs.** For QA-008, HIT-012, ANM-003, AWR-008, SEL-004, SEL-008, ANM-006, DEF-005: one document each under `Codex/D09_<ID>.md` with data structs, runtime classes, authority/replication points (QA-008 first: where each existing component would need server gating), content needed (list, no authoring), the proving tests (automation, PIE, two-client), phase of delivery and dependency on WP-4.

**WP-6: the 83-row implementation matrix.** One table, all 83 IDs: ID, requirement clause, owning definition field (D02), shared runtime component, phase (P1 to P8), implementation unit (file/class), proving test (existing driver or new, with its assertion), evidence needed for IMPLEMENTED, status today (D03). This becomes the single working checklist for "100 percent". Output `Codex/D10_IMPLEMENTATION_MATRIX.md` (and a `.csv` next to it). Check that every row of D03 appears exactly once.

## Reporting format and cadence

X-n per package (TASK, STATUS, FINDINGS, DECISION NEEDED, NEXT ACTION, VALIDATION as in the mailbox rules). Claude's watcher reads each post within minutes and answers at package boundaries, not between them: keep working. If a Claude review of an earlier package arrives while you work, finish the current package, then fix the findings first.

## Definition of done for this order

WP-1 and WP-2 reviewed and built by Claude with the baseline parity witnesses green; WP-3 to WP-6 accepted as the specification set for DD-1 steps 2 and 3, P2 and the eight rows.
