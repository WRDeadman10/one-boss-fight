# Queue S16–S18 — D3 ledger and MoveCard comparison

Date: 2026-11-05. Source ledger: `Docs/BossCombatReview/Execution/Claude/D3/D3_MEASURED_LEDGER.json`. D3 is closed at 5/10 measured, as directed in C-879; the other five rows are withdrawn or inconclusive because the available footage does not establish attack identity and milestone boundaries.

## S16 — ledger consistency

Ran `fill_ledger.py --sync-only` using the current Claude D3 ledger as input and a temporary output, then regenerated the findings table with `D3_findings_table.py`. The source ledger was not modified. Result: 10 rows, 5 measured, 5 unmeasured/withdrawn, and no incomplete measured rows. The measured priorities are 1, 6, 8, 9, and 10. Each has all six frame IDs and the recorded confidence value.

| Priority | Reference move | W/C/A/E/R/RE frames | Confidence | Canonical frames present |
|---:|---|---|---|---:|
| 1 | `REF_CurvedSwordCombo_Chain1` | 447 / 456 / 465 / 472 / 479 / 500 | medium | 6/6 |
| 6 | `REF_HolySwordRain_Setup` | 2381 / 2423 / 2566 / 2602 / 2620 / 2818 | low | 6/6 |
| 8 | `REF_OmenCurseBurst_Phase2` | 5189 / 5270 / 5347 / 5612 / 5624 / 5732 | medium | 6/6 |
| 9 | `REF_MaceSlam_Sweep` | 1703 / 1787 / 1796 / 1801 / 1835 / 1871 | medium | 6/6 |
| 10 | `REF_GapPounce_Close` | 3951 / 3981 / 4005 / 4023 / 4047 / 4065 | low | 6/6 |

The census found all 30 referenced frame filenames present after C-881 follow-through. P1 and P6's twelve missing PNGs were restored from the registered WebM using the canonical timestamp formula, with fresh SHA-256 and byte counts added to `S12_S14_frame_manifest.json` and `S12_S14_evidence_sha256.txt`. The extraction method was pixel-calibrated against an existing P8 frame at its recorded timestamp. No row's measurement fields changed. This resolves the stale P36/P46 claim that all 30 referenced PNGs were absent; P6 remains low confidence because its camera shows the sky-sword hazard rather than the boss body.

## S17 — reference vs. Ember Warden native attack-tracker timing (by analogy)

C-881 clarified the available comparison source: `FRPGAttackTrackerConfig` constructor defaults in `Source/OneBossFight/Player/RPGAttackTracker.cpp` are live on both routes (D5 has 100 tracker leaves MATCH). These are attack-tracker windows, not MoveCard fields. The cross-boss matches below are analogies, not identity claims. Durations use four explicit intervals: W→C, C→A, A→E, E→RE. For native timing, W=0, C=`CommitTime`, A=`ActiveStartTime`, E=`ActiveEndTime`, RE=`RecoveryEndTime`.

| Priority / reference | Reference W→C / C→A / A→E / E→RE (s) | Closest native move | Native intervals (s) | Analogy / reason |
|---|---|---|---|---|
| 1 `REF_CurvedSwordCombo_Chain1` | 0.150 / 0.150 / 0.117 / 0.467 | A3a | 0.380 / 0.020 / 0.200 / 0.200 | MEDIUM: sword combo stage; A3a is a two-hit combo stage, while the reference is a curved-sword chain and its visible boundaries are approximate. |
| 6 `REF_HolySwordRain_Setup` | 0.701 / 2.386 / 0.601 / 3.604 | no analogue | — | The measured object is an arena-wide sky-sword hazard, not a boss attacker's animation window. |
| 8 `REF_OmenCurseBurst_Phase2` | 1.352 / 1.285 / 4.421 / 2.002 | no analogue | — | The row is a phase-transition explosion/hazard; it does not identify a native attack-tracker move. |
| 9 `REF_MaceSlam_Sweep` | 1.401 / 0.150 / 0.083 / 1.168 | A2 | 1.680 / 0.250 / 0.180 / 1.030 | MEDIUM: both are delayed overhead ground slams; A2 is the pack's rare close slam, whereas P9 includes a follow-up sweep and observed boundaries are visual. |
| 10 `REF_GapPounce_Close` | 0.501 / 0.400 / 0.300 / 0.701 | A6 | 0.160 / 0.590 / 0.420 / 0.630 | LOW: both are aerial gap-closing attacks, but P10 is a different boss and its RE boundary is the next move's start. |

Native values are source-backed: A2 uses Commit 1.68, Active 1.93–2.11, RecoveryEnd 3.14; A3a uses 0.38, 0.40–0.60, 0.80; A6 uses 0.16, 0.75–1.17, 1.80. P1/P6/P8/P9/P10 frame IDs and confidence remain as recorded in the ledger; restored canonical PNGs now exist for all 30 references.

## S18 — bounded tuning proposals

Only the MEDIUM analogies P1/A3a and P9/A2 qualify for consideration. Proposal for both: **retain current native timing; make no numeric change from cross-boss footage alone.** P1's approximate visible chain timing and A3a's authored two-stage combo do not establish a target-value mismatch. P9 combines a slam and follow-up sweep, while A2's active window represents a different pack move with two damaging trace windows. Require same-route telemetry or a move-specific authored spec before changing either native timing. P6/P8 have no analogue; P10 is LOW confidence, so none of them yield tuning proposals.
