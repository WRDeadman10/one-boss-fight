# BH-A31: Lead & Owner Unblock Execution Brief (Single-Page Chronology)

**Authority:** [`QUEUE_BH_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BH_AG.md) Task `BH-A31` (`2026-11-11`)  
**Rule:** Offline roadmap only (`0` editor calls, `0` commits). Execute strictly in dependency order once the `[C-1286+]` Unreal Engine slot opens.

---

| Step | Actor | Action / Gate | Exact Entry Point / Evidence Target | Unblocks |
|---|---|---|---|---|
| **1** | **Lead (`[C-1286]`)** | Live `--write` on Greystone IK retarget root-chain (`TranslationMode=GloballyScaled`) & generate `Saved/ERFitRM_*.json` | `Scripts/Editor/fix_greystone_fit_root_motion.py --write` (confirm `output_root_xy_cm > 0.5 * source_root_xy_cm`) | Step 2 (`RM4`) & `test_c1285` closure |
| **2** | **Lead** | Paired Mannequin vs Greystone `RM4` PIE capture (`84–98 cm` backstep / `215–290 cm` roll, `<= 10%` delta) + `KI-052` linked-layer warning triage | `Scripts/Editor/pie_greystone_root_motion.py` + `BF_X31_X35` paired capture schema -> `Saved/ERFitRM_*.json` | Step 3 (`8`-slot clip) |
| **3** | **Lead + Owner** | Capture `C1257C` `8`-slot Greystone clip (`D:/FightVideo/greystone_review/`) -> Owner visual go/no-go | Keep Mannequin default until ALL gates + Owner approval pass | Greystone default-pawn switch (`[C-1287+]`) |
| **4** | **Lead** | Run live `X26` Sevarog `S1–S8` (`AdditionalPhaseIds`, `90–120 cm` `S1/S2`, `S7` `Subjugation`, `S8` `Soul_Siphon`) + capture `LevelStart` tail `Frames 41–74` | `author_sevarog_draft_cards.py --write` / live PIE harness -> `P_C1286_SEVAROGLIVE*` | Codex `BE`/`BF` live verification & `S1..S8` verdict |
| **5** | **Owner** | Pick SFX Options `A/B/C` (`SFX_Audition_Reel`, `Parry_Addendum_Reel`, `Batch3_Audition_Reel`) + `BB_A24` Phase-2 aura (`Cand A/B/C`) | `D:/FightVideo/SFX_audition/` & `BB_A24_SEVAROG_PHASE2_AURA_CANDIDATES.md` | Cue notify wiring + `NS_Sevarog_PhaseTwoAura_*` |
| **6** | **Lead** | UHT / Shipping reflection check (`RestartEncounterForTest`), clean Shipping package stage, & RTX 2060 Super `60 FPS` (`p99 <= 16.67 ms`) telemetry | `Build + UAT Stage + Packaged Run` -> telemetry JSON + doc closeout (`DECISIONS` / `KNOWN_ISSUES` / `TEST_PLAN` / `PROJECT_STATE` / `TASKS`) | Final Shipping RC & Group A/B Owner commits |
