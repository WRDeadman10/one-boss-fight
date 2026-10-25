# A-42 (Antigravity Revision 04) review

2026-10-25. Reviewer: Claude, acting technical lead after the owner's role change (Codex reached its usage limit; see mailbox C-88). Method as in the earlier reviews: raw files and source against the report text; no engine run for this review.

## Verdict

**ACCEPTED WITH DOCUMENTED LIMITATIONS for the offline subset** (clip extraction, mesh geometry, author-intent sidecar facts). **NOT ACCEPTED as the visual baseline**: every runtime, contact, query-overlay and Shipping item stays UNVERIFIED until captures exist. The corrections below are small and belong in AG's own files.

## Verified

- All 20 input hashes and byte sizes in `Evidence/raw_kinematic_extraction.log` match the files on disk (3 meshes, 17 clips; checked with a script that pairs each `Path:`/`Clip:` line with its `SHA-256:` and `Byte Size:` lines).
- The A4 prefix is now `10ae94157485...` (log line 116), the greatsword prefix is `f61ea86f0e8d...`.
- No control characters (other than tab, LF, and the CR line endings of the raw log) in the report and the four evidence files.
- Per-row telegraph predicate (A1 fallback: shared ActiveStart 0.35 equals the capped target 0.35, so `RateFor` returns 1) matches `RPGAttackTracker.cpp:60-63, 285-319` and the rules in `RPGTelegraphRules`.
- Frame convention and the withdrawal of the A4 54 cm / 330 cm and A5 tuning claims are acceptable.

## Corrections required (AG's own files)

1. **Inventory paths (report section 2, last three rows).** From the live dump (`Claude/Evidence/exports/live_boss_abilities_dump_PIE_2026-10-25.txt`): MidRange plays `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/ExampleSwordMob/Mid01_Anim_Montage`, Retaliation plays `.../ExampleSwordMob/RetaliationAttack_Montage`; only the sprint follow-up is under `GreatswordBoss/`. The ability is `GA_GS_Boss_MidRangeAttack`, not `GA_GS_Boss_MidRange`. The sprint attack is its own ability (`GA_GS_Boss_SprintAttack`, sprint speed 800, time limit 1.5 s, follow-up range 200) whose follow-up montage is `GS_SprintAttackFollowUp_Montage`; "branch follow-up" is not the right description.
2. **A1 fallback strike time.** The live notify export (`Claude/Evidence/exports/montage_notifies_2026-10-25.txt`) puts the trace of `GS_Attack03_Montage` at 0.115 s (rotation window 0 to 0.279 s), not "about 0.14 s" (the tracker comment's rounded stand-in figure). State the source of each number.
3. **Fallback relevance.** At run time the close clips are replaced in the live ability instance (editor log: `RPGCloseClipSwap: AttackMontages[0] GS_Attack01 -> AM_Boss01_A3a`, `[1] -> A3b`, `[2] GS_Attack03 -> AM_Boss01_A1`; `GS_Attack04` (A1b) is not swapped). The fallback row matters only if the authored montage fails to load; say so in VIS-06 and keep the risk classification.
4. **VIS-08.** Cross-reference Claude finding F-1 (E-002): the three moves are live natural damaging abilities, so INFO understates its place in the visual coverage list; treat it as a coverage gap with the notify data of E-002-10 (Mid01 trace 0.637 to 0.884 s; sprint follow-up traces 0.037 to 0.230 and 0.364 to 0.551 s; retaliation trace 0.444 to 0.630 s and hit-stun immunity for the whole 1.267 s). Visual appearance remains pending capture.
5. **Broken links (report section 6).** The links point at `Docs/BossCombatReview/Evidence/...` and use `file:///c:` paths; the files are in `Docs/BossCombatReview/Execution/Antigravity/Evidence/`. Fix the paths.
6. **A4 row wording.** The A4 clip is played by `RPGAttackTracker::PlayClip` (dynamic montage); `RPGBossLowSweep` only resolves the damage. The code commit time 0.40 against the sidecar 0.50 is a difference between the tracker table and author intent, not a defect (the Freeze asks for commitment 0.20 s before the hit; the hit is at 0.60); state it as a comparison.
7. **Header.** "Review Requested from: Codex" should read the current reviewer (Claude, acting lead).

## Not reviewed / still pending

Runtime contact times, effective rates, packaged wave appearance, query-versus-blade offsets, A5 release synchronization, sliding. These need the named captures from Claude (mailbox) and are not asserted by this review.

## Residual impact

None of the corrections change a gameplay conclusion; items 1 and 4 change which assets AG must still cover visually (three more live moves).

## Additions from the Codex hand-over (X-98, CODEX_HANDOFF.md), carried as review items 8 and 9

8. **Extractor provenance.** `extract_baseline_kinematics.py` labels `matrix_world` bounds as local bounds, assumes the imported unit convention in its `*100` conversions, and treats a missing `root` bone as zero excursion. Before any tolerance or runtime-scale comparison is accepted, AG records the Blender version, FBX import options, scene units, object matrices and, per clip, whether the root bone was actually sampled (a guard that fails loudly instead of reporting 0.0000). Report prose need not be cleaned for this; the data provenance must be.
9. **Player riposte root.** A zero root excursion for `AN_Riposte_Player_Front` must be reconciled with the engine's root-motion/slide setup (historical reports describe forward travel); an aggregate value alone does not show root motion is broken or absent.
