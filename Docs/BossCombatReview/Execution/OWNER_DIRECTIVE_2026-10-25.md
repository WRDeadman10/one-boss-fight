# Owner directive of 2026-10-25 (relayed in chat to Claude, acting technical lead)

Recorded by Claude. This is the owner's words as relayed; it adds a priority and a design requirement to the P0-P8 program. It does not by itself approve any code change: scope approval still comes from the owner on the documents named below.

## What the owner said (paraphrased closely)

1. Roles: Claude is in charge (technical lead and reviewer, editor/build/PIE owner). Codex's usage limit has reset: Codex works again, together with Antigravity.
2. **First priority: the boss audit must match 100 percent in our code.**
3. **The game must be data driven, as Elden Ring is:** hundreds of bosses, one combat code. Bosses, weapons and player builds are all data. Adding a new boss must need only data and animation (plus weapon and player-weapon data likewise), with no new combat code.
4. Claude and the two agents talk through `Documentation/TEAM_MAILBOX.md`.

## How Claude reads it (binding for the plan until the owner corrects it)

**"Matches 100 percent"** = all 83 reference requirement IDs (the 83 unique rows of `P0_BASELINE_RECONCILIATION.md`) reach a final disposition of IMPLEMENTED with evidence (source proof for structural properties, observed runtime/visual evidence for behavioral ones), or NOT APPLICABLE with a cited rationale that the owner has confirmed. Candidates for owner-confirmed N/A that Claude will list for decision rather than decide: QA-008 (multiplayer authority), HIT-012 (boss grabs), ANM-003 (variable hold delay, versus the approved stable A2 hold), adaptation/utility rows (AWR-008, SEL-004/008). Percentages of "partial" are not used; compliance, evidence confidence and authorization stay separate fields, as in `CODEX_HANDOFF.md`.

**"Data driven"** is added as a requirement that every attack, phase, hit shape, timing and presentation fact of a boss comes from data assets and animation assets, never from C++ constants or per-move C++ classes. Same for weapons (per-weapon attack tables, combat style, art) and player builds (which weapon, which stats, which HUD line). Acceptance test, the "second boss canary": a second boss with different attacks, phases and look is created by authoring data assets and animation only (no `.cpp`/`.h` edit, no new component class), fights correctly in the existing encounter, passes the same regression drivers, and a new weapon and a new build are added the same way.

## Current state, from a source scan on 2026-10-25 (read-only)

- **Boss: code, not data.** Per-move timing rows (commit, active, recovery, turn rate, clip path, branch flag) are constructed in `URPGAttackTracker::URPGAttackTracker()` (`RPGAttackTracker.cpp:24-103`); moves A4, A5, A6 each have a bespoke component (`RPGBossLowSweep`, `RPGBossHealPunish` + `RPGBossJavelin`, `RPGBossShockwave`); phase two, stagger, posture, death, wake, look and music are per-boss components with constants; the boss is found by `URPGPlayerMovesSubsystem::IsPackBoss` (one great-sword boss class); the pack's behaviour tree and abilities are the selector. About 79 hard-coded `/Game/...` or `Boss01`/`Ember` references sit in non-test C++.
- **Weapons: partly data.** `URPGWeaponAttackTable` is a data asset keyed by (combat-style asset name, attack kind) with posture, stamina, bleed, health multiplier and hyperarmor (`RPGWeaponAttackTable.h`); the default rows are still filled by the constructor.
- **Builds: code.** The three builds (Starter, Strength, Dex), their weapon assets, actor classes and ability names are a fixed table in `RPGBuildRules.h:50-52`; `ERPGBuild` is an enum.
- **Animation already carries timing.** Live notify tracks of the authored montages contain the same trace windows the tracker rows duplicate (E-002-10: `ANS_CollisionTrace`, `ANS_SetDesiredRotation`, `AN_PerformFollowUp`, `AN_EndAnimatingAbility`), so the animation can be the source of active window and heading window; commit and recovery points have no notify today.

## Documents that implement this directive

- `P0_CODEX_BRIEF_DATA_DRIVEN.md` (Codex: hard-code inventory, data schema design, 83-ID reconciliation, independent review).
- `P0_AG_BRIEF_AUTHORING_CONTRACT.md` (Antigravity: animation and data authoring contract, machine-readable move sheets, the corrections of review 04).
- `DATA_DRIVEN_ARCHITECTURE_GATE.md` is written by Claude after both deliver; it is the one document the owner approves before any code change.
