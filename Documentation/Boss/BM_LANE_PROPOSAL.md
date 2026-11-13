# Lane BM proposal: 100 tasks in 20 batches of 5 (draft for lead and AG review)

Drafted by C (implementer) for X-2203, 2026-11-12. **This is a proposal only:** nothing below is started until the lead scopes it.

**Inputs:** 3 read-only auditors (a workflow fan-out) classified the open TASKS items, the Queue F proposal, and the remaining work in PROJECT_STATE, KNOWN_ISSUES, OWNER_DECISIONS_PENDING and F_GAP_AUDIT. I reviewed their output.

## Audit of open work (inputs)

**Open `- [ ]` rows in TASKS.md (29):**

| Class | Rows | Count |
|---|---|---|
| **Stale or superseded** | the BK-146..165 "continue the next batch" rows (`TASKS.md:3268, 3274, 3281, 3288`); the BK lane ended at 320 | 4 |
| **Owner-gated (X-1991)** | the editor executor, envelope binding and C-1155 authoring rows (`TASKS.md:3174-3215`) | 6 |
| **Engine-gated** | the BL-06..100 rows, waiting only on the lead's engine-lock acceptance build and automation run (`TASKS.md:3339-3358`) | 19 |

**Queue F (`QUEUE_100_F_PROPOSAL.md`):**
- **F-A** (5 live witnesses): done.
- **F-C:** done at the tooling and docs level. The Lead's runtime review of C2 and the C3 31-35 runtime evidence were never recorded (`TASKS.md:2647, 2653`).
- **F-T 61-100:** no delivery record. The queue was superseded by Queue G on 2026-11-04 (`TASKS.md:2671`), so I treat F-T as obsolete.
- **Bookkeeping drift:** the reconciliation rows `TASKS.md:2620, 2622` are still unticked although C-799 closed the gaps.

**BM does not repeat Queue F, BK or BL work.**

## Gate legend

| Gate | Meaning |
|---|---|
| **O** | owner-independent offline: source, docs, Python, or new native test files that are not built |
| **E** | engine-gated: the lead runs the build, PIE or automation under the C-1155 engine lock |
| **D** | owner-decision-gated: a brief only; no implementation |

## Batches

| Batch | Tasks | Gate | Scope (concrete files) | Acceptance |
|---|---|---|---|---|
| **1** | BM-01..05 | O | **Ledger hygiene.** (01) a stale-row reconciliation proposal for `TASKS.md` (the 4 BK rows, Queue F `2620/2622`) as a diff for the lead; (02) reconcile KI-163..167 in `KNOWN_ISSUES.md` against the BK-271..320 fixes; (03) refresh `Boss/OWNER_DECISIONS_PENDING.md`, marking rows settled by A7, J049, 11-07 and 11-09; (04) a short Queue F closeout note; (05) a status index proposal for the long BK/BL rows in `PROJECT_STATE.md` | every row change cites its evidence (file:line); no product, source or asset change |
| 2 | BM-06..10 | O | **Python parse census (KI-170/171).** A static `ast.parse` census test over `Scripts/**/*.py`; a per-file classification (fix / quarantine / leave); a syntax-repair proposal only for owner-independent legacy scripts | census test green, with the listed exceptions documented; no script behavior change without lead approval |
| 3 | BM-11..15 | O (fix: D) | **Destructive-cleanup inventory (KI-158..162).** Dry-run characterization tests on temp folders for `Scripts/stitch_*.py` and `MakeBenchKit.ps1` delete paths | tests pin the current deletion scope; the narrowing fix stays owner-gated (`OWNER_DECISIONS_PENDING.md:12`) |
| 4 | BM-16..20 | O | **Characterization tests for KI-165/166:** `make_source_manifest.py` with an empty source tree; malformed JSON into `profile_dump.py`, `card_table.py` and `validate_baked_card*.py` | the exact current exit codes and messages are pinned; fixes are proposed separately |
| 5 | BM-21..25 | O | **Shipping CVar guard census (KI-168 vs the KI-185 pattern):** a static test over `Source/OneBossFight/**/*.cpp` CVar declarations and their `#if` guards | a table plus a regression test; the binary-level Shipping proof stays E |
| 6 | BM-26..30 | O→E | **KI-128 bleed threshold-growth overflow:** a new native boundary test, plus a clamp proposal for the `RPGBossBleed*` sources | the test file is written; the clamp is a lead decision; the run is E |
| 7 | BM-31..35 | O→E | **Parry lifecycle:** a KI-176 refund-cap repro test; a KI-175 `RPGParry::FState` reset audit (`RPGPlayerParry.h:65`, `.cpp:159-170`); a KI-181 subnormal selector-weight boundary test | tests written; source changes only on a demonstrated defect, with lead approval |
| 8 | BM-36..40 | O | **Framework boss source audits:** the KI-174 leash early-return (`RPGFrameworkBossCharacter.cpp:600,788`); KI-154/155 Javelin parry → HealPunish routing; the KI-136 citation correction (`RPGBossDeath.cpp:126`) | a findings report with exact lines; the fixes are proposed |
| 9 | BM-41..45 | O→E | **Hydration preflight completeness (KI-133/134):** a test that the 110 required paths and the restart ceiling are enumerated (`RPGBossHydrationPreflight.*`) | native test written; the run is E |
| 10 | BM-46..50 | O (D if a mismatch) | **Data reconciles:** the KI-190 Strength JumpHeavy 35-stamina table against Freeze v1.2; the KI-145 Swing1_Slow range against measured reach | reconcile tables; any value change needs an owner decision |
| 11 | BM-51..55 | O | **KI-189 W1 Niagara `LoadSynchronous` hitch:** a source review and an async or preload proposal | design note with exact call sites; no source change |
| 12 | BM-56..60 | O | **F_GAP ledger diff proposal for AWR-004, HIT-008 parry and MOV-001** (`F_GAP_AUDIT.md:9,14,15,19`); the ledger JSON is AG-owned, so a proposed diff only | AG applies or reviews it; the HIT-008 scope stays D (`OWNER_DECISIONS_PENDING.md:39`) |
| 13 | BM-61..65 | O | **BL acceptance support:** a deeper pre-compile lint of the 50 BL files (overload and type risks, for example `TestEqual` on bool or uint64 and `FVector2D` comparisons); a draft automation-run script **that is not executed** | lint report; the script is handed to the lead; the run is E |
| 14 | BM-66..70 | D | **X-1991 Sevarog stats decision brief:** one-decision drafts with defaults, for the lead to send (only the Lead emails the owner) | a brief in docs; no authoring |
| 15 | BM-71..75 | O→E | **ER package-gate checklist (KI-193..199):** static checks on `Scripts/Package.ps1` inputs and the AM_ER montage references | checklist plus a static test; the packaging run is E |
| 16 | BM-76..80 | O→E | **KI-179 move-executor watchdog harness extension:** a plan plus a native test skeleton | the skeleton compiles only in the E run |
| 17 | BM-81..85 | E (plan: O) | **P35 cleanup:** an asset-referencer inventory plan for the failed proof assets (`OWNER_DECISIONS_PENDING.md:7`) | plan only; never delete or recreate referenced assets (CLAUDE.md) |
| 18 | BM-86..90 | O | **Re-verification pass over BM batches 2-13** (the BL-86 method: hand-check every claim) | findings report plus confirmed hotfixes only |
| 19 | BM-91..95 | O | **Residual KNOWN_ISSUES sweep:** classify every remaining open KI as O/E/D/closed, with citations | ledger table |
| 20 | BM-96..100 | O | **Closeout:** inventory, re-tally, run lists for the E items | closeout report |

## First proposed batch: BM-01..05 (ledger hygiene, gate O)

1. **BM-01:** a TASKS stale-row reconciliation diff (the 4 BK "continue" rows; Queue F `2620/2622`), proposed to the lead and not applied blindly.
2. **BM-02:** reconcile KI-163..167 against the BK-271..320 evidence (alias guards, O1, replace-caller behavior), with each row's status and citation.
3. **BM-03:** refresh `OWNER_DECISIONS_PENDING.md`, marking rows already decided (A7 retire-legacy, J049=A, 11-07 Tier 2, 11-09 aura/camera) with their decision references.
4. **BM-04:** a Queue F closeout note recording F-A done, F-C static-only (C2/C3 runtime evidence missing), and F-T obsolete or superseded.
5. **BM-05:** a `PROJECT_STATE.md` status-index proposal: one line per lane (BK, BL), pointing to the closeouts, replacing the duplicated long rows; proposed as a diff.

**Acceptance:** evidence-cited doc diffs only. No source, asset, Unreal or build work. The lead applies or approves the TASKS and PROJECT_STATE structural changes.

## Reconciled to 50 tasks (owner instruction, 2026-11-12)

The owner set a 50-task lane (10 batches of 5, all owner-independent; each batch is reported and then continued without waiting for review). It replaces the 100-task table above.

| Batch | Tasks | Scope |
|---|---|---|
| B1 | BM-01..05 | ledger hygiene |
| B2 | BM-06..10 | Python parse census (KI-170/171) |
| B3 | BM-11..15 | destructive-cleanup characterization (KI-158..162; temp folders only) |
| B4 | BM-16..20 | KI-165/166 characterization |
| B5 | BM-21..25 | Shipping CVar guard census (KI-168/185) |
| B6 | BM-26..30 | KI-128 bleed overflow native test (file only) |
| B7 | BM-31..35 | parry lifecycle tests, KI-175/176/181 (files only) |
| B8 | BM-36..40 | framework boss source audits, KI-174/154/155/136 |
| B9 | BM-41..45 | BL pre-compile lint |
| B10 | BM-46..50 | residual KI sweep and closeout |

**Kept out of this lane (gated):** the X-1991 brief (owner decision), the ER package gate, the watchdog harness, P35 cleanup, and the hydration and data reconciles that need engine runs or decisions.
