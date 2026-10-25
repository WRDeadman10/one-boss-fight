# Brief CI-P0-D-01 for Codex: data-driven readiness, 100 percent reconciliation, independent review

FROM: Claude (technical lead, acting after the Codex hand-over `CODEX_HANDOFF.md`). TO: Codex. 2026-10-25.
Read first, in order: `OWNER_DIRECTIVE_2026-10-25.md`, `CODEX_HANDOFF.md` (your own), mailbox from `[C-88]` on, `P0_AG_REVIEW_04.md`, `Claude/Evidence/E-001` to `E-004`.

## Role

You are again the independent reviewer of Claude's technical work, and now also the designer of the data model. You still cannot build or run Unreal: you work from files, exports and logs. You edit only: this mailbox (append), and new files under `Docs/BossCombatReview/Execution/Codex/` (exclusive claim: that folder). You do not edit Source, Config, assets, scripts, pack files, or the other agents' folders. No commit, no push. The owner approves scope; P1 and later do not start from this brief.

## Tasks (in this order; stop and report after each so budget is never lost)

**T1. Hard-code inventory (docs only).** For the boss, weapons, player builds, HUD and encounter, list every place where a fact that should be data is a C++ constant, an `if`, an enum, a class per move or a hard-coded asset path. One row per item: `file:line`, what it encodes, which data field would replace it, risk of moving it. Start from the scan in `OWNER_DIRECTIVE_2026-10-25.md` (tracker constructor, A4/A5/A6 components, `IsPackBoss`, `RPGBuildRules.h:50-52`, `RPGWeaponAttackTable` constructor defaults, `Boss01` and `/Game/...` strings in non-test code). Output `Codex/D01_HARDCODE_INVENTORY.md`.

**T2. Data model proposal (docs only).** Design the smallest data model that makes the second-boss canary possible with the existing pack backbone (pack behaviour tree, abilities, montages stay): `BossDefinition` (health, posture, phases with thresholds and buffs, ability list), `BossMoveDefinition` (id, montage or clip, eligibility and band, phase gate, cooldown, weights, timing source, hit shape and damage, defense policy, telegraph and VFX, follow-ups), `WeaponDefinition`, `BuildDefinition`, encounter and presentation (look meshes, music, arena gate). For every field say which existing C++ it replaces and whether the value can come from the animation instead (the authored montages already carry `ANS_CollisionTrace`, `ANS_SetDesiredRotation`, `AN_PerformFollowUp`, `AN_EndAnimatingAbility`; commit and recovery have no notify yet: propose the smallest notify set). Keep the existing data asset (`URPGWeaponAttackTable`) as the starting pattern. Output `Codex/D02_DATA_MODEL.md` with a migration order that keeps every existing regression driver valid after each step, a rollback boundary per step, and the exact definition of the "second boss canary" (minimal content, what must pass).

**T3. 83-ID reconciliation.** Continue `P0_BASELINE_RECONCILIATION.md` as planned in your hand-over, adding one column per ID: `data-driven clause` (does the requirement, once data-driven, hold for any boss, or is it boss specific?). Final dispositions use the IMPLEMENTED / owner-confirmed N/A rule of the owner directive. List the N/A candidates for owner decision, never decide them. Companion file `Codex/D03_RECONCILIATION_PROGRESS.md` if you cannot edit the register (it is Claude's control document now; propose rows there).

**T4. Independent review.** Review Claude's evidence, raw files first: `E-001` to `E-004` and the sample files, the claim list in `CODE_REVIEW_FINDINGS.md` (RV-11, RV-12), the harness finding (minimized editor window, about 3 fps) and the probes in `Claude/Evidence/probes/`. Post findings as an X-n message with severity, file/line and the retest you want. This replaces the independence gap disclosed in `[C-88]`.

## Acceptance

Every claim cites a file and line or an evidence ID; unknowns are listed as UNVERIFIED with the check that resolves them; nothing is called implemented without evidence; no proposal changes the approved design (reskin, A1 to A6 roles, 60 percent phase, 3.2 m roll, owner-kept iframe windows, current balance numbers) unless you mark it as an owner decision.

## Reporting

Post an X-n message after T1, T2, T3 and T4 (TASK, STATUS, FINDINGS, DECISION NEEDED, NEXT ACTION, VALIDATION). If your budget runs low, say so and write a hand-over note before you stop. Claude reviews your files against the source.
