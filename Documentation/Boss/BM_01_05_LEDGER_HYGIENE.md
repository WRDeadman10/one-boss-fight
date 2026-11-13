# BM-01..05: ledger hygiene (lane BM, batch 1 of 10)

C (implementer), 2026-11-12, per the owner's 50-task instruction (C-1458).

**Documentation only.** No source, asset, Unreal, build, commit or push. Structural edits to TASKS and PROJECT_STATE are **proposed** below for the lead; they are not applied.

## BM-01: TASKS.md stale-row reconciliation (proposal)

| Row | Current text | Evidence | Proposed change |
|---|---|---|---|
| `TASKS.md:3268` | BK-146..150 "continue the next batch" | the BK lane ran on to BK-320 and was closed (`BK_271_320` closeout) | tick `[x]`, noting it was superseded by BK-151..320 |
| `:3274` | BK-151..155 "continue" | same | tick, superseded |
| `:3281` | BK-156..160 "continue" | same | tick, superseded |
| `:3288` | BK-161..165 "continue" | same | tick, superseded |
| `:2620`, `:2622` | Queue F reconciliation and count correction (unticked) | C-799 closed the live gaps (`TASKS.md:2715`); the counts were corrected to 5/55/40 at `:2622` itself | tick, citing C-799 |
| `:3174-3215` (6 rows) | executor and envelope contracts | blocked on owner decision X-1991, which is still open | **keep open** (owner-gated) |
| `:3339-3358` (19 rows) | BL-06..100 | waiting on the engine-lock acceptance build and run | **keep open** (engine-gated) |

## BM-02: KI-163..167 against the BK-271..320 fixes (current code, re-read)

| KI | Current code | Related BK work | Status |
|---|---|---|---|
| KI-163 | `token_coverage.py:49` still prints `MISSING` and continues; `:86` returns 1 only for unknown tokens | BK-276/291 characterized write failures only; nothing gates on missing logs | **Open** (the fix is owner-gated per `OWNER_DECISIONS_PENDING`, the KI-163–168 row) |
| KI-164 | `evidence_pack.py:61` `out.mkdir` still runs **before** the collision and reserved checks (`:64-75`) | BK-231 added the non-empty-root refusal and normcase checks, but a rejected run can still leave a new empty directory | **Open**, partly mitigated (the line cite moves from 40-61 to 61/64-75) |
| KI-165 | `make_source_manifest.py:29-31`: `<root>/Source` is not required to exist; `rglob` on a missing directory gives an empty manifest | BK-301 added the alias and Source-subtree guards, not root validation | **Open** (cites move to 29-31) |
| KI-166 | `profile_dump.py:28`, `card_table.py:14`, `validate_baked_cards.py:15`, `plugin_dependencies.py:18,22`: bare `json.loads`, so malformed input gives a traceback | none | **Open**, unchanged (characterized in BM-16..20) |
| KI-167 | path echo remains, for example `evidence_summary.py:102` prints the output path | none | **Open**, unchanged |

**Proposed KNOWN_ISSUES edits:** cite updates for KI-164 and KI-165, plus an "AX/BK note" on KI-164 recording the BK-231 partial mitigation. All five remain Open.

## BM-03: OWNER_DECISIONS_PENDING refresh (proposal)

- The A7 and J049 rows are **already marked DECIDED** in the file. No change is needed.
- The 2026-11-07 decisions (Tier 2 = A, L1 block, untracking 14 assets, DLSS default after Phase 2) and the 2026-11-09 decisions (aura = Boost Lite, camera = C) are recorded in the decision memory and the mailbox. **None of them maps to an existing row in this table**, so no row closes. Adding a "Decided since consolidation" footer that lists them with their references would stop anyone re-asking.
- The `BOSS-HIT-008 scope` and `KI-158..168` rows **stay pending**.

## BM-04: Queue F closeout note

| Part | Status |
|---|---|
| **F-A** live witnesses (AG1-AG5) | **done** (BUILD-199..208, `QUEUE_100_F_PROPOSAL.md:13-17`) |
| **F-C** tasks 6-60 | **static/tooling only.** The C2 Lead runtime review (`TASKS.md:2647`) and the C3 31-35 runtime evidence (`:2653`) were never recorded; they are engine-gated if revived. |
| **F-T** tasks 61-100 | **no delivery record; obsolete.** Queue F was superseded by Queue G (`TASKS.md:2671`), and its native-test intent is now served by the BL lane. |

**Proposed:** tick `TASKS.md:2620/2622` (see BM-01) and add a one-line "Queue F closed: F-A done, F-C static, F-T obsolete" note.

## BM-05: PROJECT_STATE status index (proposal)

The `PROJECT_STATE.md` latest section carries one long row per BK/BL batch (`:856-893`). Proposed replacement: a **lane index** of one line each, each pointing to its closeout. The per-batch rows would move to an archive appendix.

| Lane | Status | Closeout |
|---|---|---|
| BK-171..270 | closed | `BK_171_270_LANE_CLOSEOUT.md` |
| BK-271..320 | closed | `BK_271_320_LANE_CLOSEOUT.md` |
| BL-01..100 | delivered and reviewed clean; native build and run pending | `BL_96_100_LANE_CLOSEOUT.md` |
| BM-01..50 | in progress | `BM_LANE_PROPOSAL.md` |

## Checks actually performed

- Re-read the cited code lines for KI-163..167 with `grep`.
- Read `OWNER_DECISIONS_PENDING.md` in full and the open TASKS rows.
- Planning-audit citations come from the C-1457 audit, reviewed. No test was run, because none applies.

## Limits

These are proposals: the TASKS ticks, KNOWN_ISSUES cite edits and the PROJECT_STATE index are for the lead to approve or apply.
