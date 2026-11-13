# Queue BQ: project-feature lane toward a playable Sevarog duel (100 tasks, 20 batches of 5)

C (implementer), 2026-11-13, per X-2318. Codex is the lead and Antigravity the reviewer.

**Sources:** a read-only milestone inventory of `TASKS.md`, `PROJECT_STATE.md`, `KNOWN_ISSUES.md` and the BE/BF/BI/BJ/BK queue reports. IDs A*, B*, C*, D* and E* below refer to the inventory areas:
- **A:** Sevarog / framework encounter;
- **B:** Greystone / animation;
- **C:** Gate 3 feel;
- **D:** Gate 4 performance / package;
- **E:** audio / VFX / arena.

## Gates

| Gate | Meaning |
|---|---|
| **SRC** | source-only. It can start now, but C++ is **written, not compiled**: the Lead's C-1155 build and suite are required before acceptance |
| **ENG** | needs a Lead engine build, PIE run or asset write under the C-1155 lock |
| **OWN** | needs an owner decision, named per task |
| **ART** | needs art or asset authoring |
| **LEAD** | needs a lead scoping decision first |

**Execution boundary (inherited X-2295 practice):** no tool `main()`, CLI, subprocess, editor or engine run by C. Validation is static and in-process only.

## Decision register (only pending rows gate tasks)

| ID | Decision |
|---|---|
| O1 | X-1991: Sevarog Stats, Phase_1 and posture regen, identity multipliers |
| O2 | SFX picks |
| O3 (resolved 2026-11-09; C-1168/C-1210) | Boost Lite authored and live; not a pending gate |
| O4 | Greystone as the default player |
| O5 (resolved 2026-11-09; C-1168) | Camera option C only; lock-on framing is live |
| O6 | benchmark hardware |
| O7 | M14 balance knobs |
| O8 | KI-174 leash/pause intent (Lead) |
| O9 | equivalence of the C-1511 reels |
| L1 | KI-110 fix: X-245 kept it as an accepted limit, so it is not scheduled without lead rescope |
| L2 | KI-170/171: uncommitted working-tree repairs await lead review (BM-06..10) |

## Queue

| Batch | Tasks (scope · files · acceptance · gate · starts without owner?) |
|---|---|
| **1** | **BQ-01** A22 KI-155: an encounter/profile validation that refuses a profile whose candidate set cannot cover its attack budget while cooldowns run (NoCandidate starvation). `RPGBossFrameworkProfile.cpp` validation, plus a native test. SRC, yes. **BQ-02** A20 KI-174: a native characterization test for leash during combo pause, returning before and after expiry; it pins the current behaviour, and no production change waits on O8. SRC, yes. **BQ-03** A17: a native regression test for the retry-ownership generation fence on a reused actor (BF-X21..25 risk). SRC, yes. **BQ-04** A27 KI-128: arithmetic guard tests for threshold growth and narrowing at the BM-26..30 sites, extending them to the posture and bleed accumulators. SRC, yes. **BQ-05** batch report |
| **2** | **BQ-06** A28 KI-139: the `authoring_core.py` FNAME_PROPERTIES soft-class conversion fix, plus an offline unit test that stubs `unreal`. SRC, yes. **BQ-07** A2: the Sevarog repair executor skeleton on top of the BK planner, binder and receipt contracts, in dry-run only, with no writes until O1. SRC, yes. **BQ-08** A3: finish the BK-116..120 audit. SRC, yes. **BQ-09** A24: the RPGBossDeath citation fix (KI-083 to KI-136, comments only). SRC, yes. **BQ-10** batch report |
| **3** | **BQ-11** B4 helper: a C++ `RPGMontageUtils` notify-track helper for the C-1257a `_Fit_Greystone` wrappers (UE 5.5 Python lacks the track structs). SRC, yes. **BQ-12** B4: an editor script plan that uses the helper, statically checked. SRC (ENG to run). **BQ-13** B14 KI-085: re-sync latched input on the post-riposte `EnableInput`, with a native test seam. SRC, yes. **BQ-14** B13 KI-059: dodge input-direction and double-payment characterization tests. SRC, yes. **BQ-15** report |
| **4** | **BQ-16** C7 KI-065: a landing-bounds validation helper for the A6 leap, plus a test. SRC, yes. **BQ-17** C7 KI-067/068: route the A4, A5 and A6 hits through the hit-reaction path instead of writing health directly (source behind a default-off CVar). SRC, yes. **BQ-18** C6: the A4 low-sweep selection weight hook (KI-067), default-off. SRC, yes. **BQ-19** C10 KI-074: re-apply stance-break immunity at get-up, default-off, plus a test. SRC, yes. **BQ-20** report |
| **5** | **BQ-21** D4: per-run machine, session and build identity in the benchmark summary producer, following `BENCHMARK_RUN_RECEIPT_V1` (a proposal awaiting adoption). SRC, yes. **BQ-22** D4: a receipt validator with in-process fixtures. SRC, yes. **BQ-23** D9 KI-168: a review of the six Shipping-visible CVars with a disposition table. SRC, yes. **BQ-24** D2 KI-108: GPU-cost attribution notes from the existing Shipping evidence (read-only analysis, no run). SRC, yes. **BQ-25** report |
| **6** | **BQ-26** C12: build-selector HUD indicator source (G3-5). **BQ-27** C12: flask counter source. **BQ-28** C13 KI-091: keep the default weapon slot out of MagicCombatStyle. **BQ-29** source tests for 26–28. All SRC, yes, with PIE later as ENG. **BQ-30** report |
| **7** | **BQ-31** A9: native test list for the selector early-refusal and cleanup fence (BK-26..30), with the Lead build checklist. SRC. **BQ-32** A8: a BF-X05 one-run acceptance driver plan, static. SRC, with the run as ENG. **BQ-33** A13: X26 matrix gap list per arm. SRC. **BQ-34** A14: S8-first arm runner configuration. SRC, with the run as ENG. **BQ-35** report |
| **8** | **BQ-36..39** A11/A12: S1/S2 140 cm miss and S4→S5 boundary analysis from the existing traces; card-range proposal C-1274 as a data diff, unsaved. SRC analysis, with ENG to apply. **BQ-40** report |
| **9** | **BQ-41..44** A15/A16: S6/S7/S8 acceptance checklists and saved-asset readback scripts, statically checked. SRC, with the run as ENG. **BQ-45** report |
| **10** | **BQ-46..49** B1–B3: `_RM` write and repoint scripts readied from FIX_dryrun, and the RM4 paired-trial driver, statically checked. SRC, with the run as ENG. **BQ-50** report |
| **11** | **BQ-51..54** B5/B6/B15: notify-readback validation, combat-trace and parry confirmation drivers, and F4b checklist automation. SRC, with the run as ENG. **BQ-55** report |
| **12** | **BQ-56..59** B8/B11/B9: missing layer-ABP base, broken enemy-montage references and socket transform review. Repair scripts are SRC; applying them is ENG. **BQ-60** report |
| **13** | **BQ-61..64** C2/C3: QUEUE_50 and QUEUE_200 Q21–Q30 build-and-suite checklists, plus missing native tests. SRC, with acceptance as ENG. **BQ-65** report |
| **14** | **BQ-66..69** C5/C11: close-attack 90 cm driver-setup analysis and HEAVY poise victim test. SRC, then ENG. **BQ-70** report |
| **15** | **BQ-71..74** D5/D6/D7: Shipping pipeline command sheet, packaged smoke checklist and stage-provenance checker inputs. SRC, with the runs as ENG. **BQ-75** report |
| **16** | **BQ-76..79** D3: perf attribution test plan; D1/D10 benchmark and shader-failure triage plans. SRC, with ENG/OWN O6. **BQ-80** report |
| **17** | **BQ-81..84** A1/A5–A7: Sevarog definition authoring and deferred PIE once O1 lands; prepared, and **not started without O1**. OWN, then ENG. **BQ-85** report |
| **18** | **BQ-86..89** E1/E3/E8: SFX cue-plan scaffold for O2, aura decision reconciliation (Boost Lite already authored/live), and shake/music tuning knobs for O7 (scaffolds SRC, hookup OWN/ART). **BQ-90** report |
| **19** | **BQ-91..94** A19/B10/C8: legacy retirement and default-player switch packages for O4 and release gates; reconcile O5 (option C already decided/live). OWN/ENG. **BQ-95** report |
| **20** | **BQ-96..99** cumulative evidence, an updated playable-build gate list, owner decision digest refresh, and status sync. SRC. **BQ-100** lane closeout |

**Per-batch handoff:** the task IDs, changed files, the commands actually run with their results, red checks, gates still open, and an explicit "not compiled / not run" statement where it applies.
