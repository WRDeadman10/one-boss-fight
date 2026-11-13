# BQ-96..100: Queue BQ batch 20, cumulative evidence, playable-build gate list, owner digest, lane closeout

C (implementer), 2026-11-13. Queue: `QUEUE_BQ.md`. Lead: Codex. Reviewer and committer: Antigravity.

**What "accepted" means in this lane:** source, planning or in-process review only. **No C++ from this lane has been compiled**, no Editor/PIE/package run was made by C, and no runtime behaviour is claimed. Commit `e96a8fd1` (A-980) holds the accepted BQ-01..80.

## BQ-96: cumulative evidence (per batch)

| Batch | Tasks | State | Code delivered (uncompiled C++ / in-process Python) |
|---|---|---|---|
| 1-4 | BQ-01..20 | accepted | abort budget; posture finite guards; riposte input flush; dodge seams; A6 landing bounds (with -inf hotfix); default-off project hit reaction; get-up immunity re-apply |
| 5 | BQ-21..25 | accepted | `run_identity` in summary.json; receipt validator (22/23, symlink case unverified); KI-168 disposition |
| 6 | BQ-26..30 | accepted | opt-in return to weapon before the lock (KI-091) |
| 7-8 | BQ-31..40 | accepted | plans and analysis; S4 110 cm standoff as an ENG trial candidate only |
| 9-10 | BQ-41..50 | accepted (lead hotfixes X-2353, X-2358) | S6-S8 saved-card readback; Greystone `_RM` repoint (dry run by default) |
| 11-12 | BQ-51..60 | accepted (lead hotfixes X-2362/2363, X-2366) | saved-wrapper notify readback; Greystone pawn gate wired into the hit and parry drivers; F4b checklist; guarded layer-parent repair; montage and socket inventory |
| 13-14 | BQ-61..70 | accepted (lead fixes X-2376, X-2379) | fatigue-boundary native test; pack poise pin test switch (KI-057); KI-106 telegraph hypothesis |
| 15-16 | BQ-71..80 | accepted (lead fix X-2383/2384) | Shipping CVar expectations (43 absent / 7 present), wired into `CheckShippingBinary.py`; performance, benchmark and shader triage plans |
| 17 | BQ-81..85 | **BLOCKED, O1** | not started |
| 18 | BQ-86..90 | accepted | SFX cue-slot plan and pick validator; O3 found already resolved |
| 19 | BQ-91..95 | accepted after A-982 | legacy retirement/O4 packages; O5 is resolved and removed as a gate |
| 20 | BQ-96..100 | accepted after A-983 | cumulative evidence and gates; closeout |

**Tally after A-983:** 95 of 100 tasks are delivered and accepted at source/planning level across 19 batches. BQ-81..85 remain blocked and not started; they are not counted as delivered.

**Review lesson:** the Lead found 9 real defects in my handoffs before acceptance:
- false-pass paths: the resident Blueprint readback, an unchecked package reload, a temporary-copy delete failure, the window count only, a loose mannequin match;
- a `-inf` radius;
- a `#ifndef` polarity error;
- an override-sensitive assertion;
- wrong factual claims: a missed texture, "legacy only by opt-in", resetting user settings.

These concerns were identified during independent review; focused tests were added for some fixes. The source and planning reviews, in-process tests, and the still-pending engine/build gates provide different evidence and should not be conflated.

## BQ-97: updated playable-build gate list (Greystone vs Sevarog duel)

| # | Gate | Owner of next step | Prepared by this lane |
|---|---|---|---|
| 1 | **C-1155 build plus pinned suite** with all BQ C++ (about 10 new native tests). Nothing in this lane is binary-proven until this runs | Lead (ENG) | test lists BQ-31, BQ-61..63 |
| 2 | Sevarog values (X-1991), then definition authoring and deferred PIE | **Owner O1**, then ENG | BQ-81..85 prepared, not started |
| 3 | Saved Sevarog cards read back (S1/S2 C-1274, S6-S8) | ENG | BQ-44 readback |
| 4 | S4 to S5 boundary trial (110 cm) and Arm A rerun | ENG | BQ-39 |
| 5 | S8 cone-escape arm; S7 snare instance id | ENG / Lead | BQ-34, BQ-43 |
| 6 | Greystone: RM4 roll, KI-040 layers, hits and parry pair, saved notifies | ENG | BQ-46..60 |
| 7 | Greystone sockets and visual review | **Owner** | BQ-58, F4b-7 |
| 8 | Greystone as the default player | **Owner O4**, after 6-7 | BQ-92/93 |
| 9 | SFX picks, then cue authoring | **Owner O2**, then ENG | BQ-86 |
| 10 | Shake and music values, M14 balance | **Owner O7** | BQ-88/89 |
| 11 | Shipping package, smoke, binary CVar check (KI-168) | ENG | BQ-71..74 |
| 12 | Cook closure: KI-080 `T_Water_N_2` missing | Lead / Owner | BQ-79 |
| 13 | Performance ≤ 16.67 ms p99 on the RTX 2060 Super (DLSS plan) | **Owner O6**, then ENG | BQ-76..78 |
| 14 | Legacy code removal | after gates 11-13 | BQ-91 |

## BQ-98: owner decision digest (current)

**Open:**
- **O1:** Sevarog values (X-1991). Blocks Batch 17 and gate 2. *Oldest and most blocking.*
- **O2:** SFX picks. The validator is ready.
- **O4:** Greystone as the default player. Not ready to ask until gates 6-7 pass.
- **O6:** benchmark hardware and reopening performance work.
- **O7:** M14 balance and the shake/music values.
- **O8:** KI-174 leash and pause intent (Lead).
- **O9:** equivalence of the C-1511 reels.
- **L1:** the KI-110 rescope.
- **L2:** the KI-170/171 working-tree repairs.

**Resolved since the queue was written:** O3 aura (Boost Lite, C-1168, live) and O5 camera (option C, C-1168, live).

## BQ-99: status sync

TASKS.md has one line per batch, with the Lead's acceptance wording; this report adds the closeout line. Batch 17 is recorded as BLOCKED, not complete.

## BQ-100: lane closeout

Queue BQ is **closed for source work at 95/100**. The remaining 5 tasks (BQ-81..85) reopen when O1 lands. The next real progress is engine-side: gate 1, the C-1155 build and suite, then the ENG gates in order. **Recommendation to the Lead:** schedule gate 1 before any new source lane, because about 10 native tests and several C++ changes from this lane are still unproven.
