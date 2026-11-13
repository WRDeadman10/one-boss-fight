# BB-A31..A35: Owner Progress Digest Draft (Held for Lead)

**Queue Lane:** `QUEUE_BB` -> `QUEUE_BC_AG` -> `QUEUE_BD_AG` -> `QUEUE_BE_AG` -> `QUEUE_BF_AG` -> `QUEUE_BG_AG` -> Refreshed (`V5`) under `QUEUE_BH_AG` Tasks `BH-A32`..`BH-A33` (Antigravity)  
**Status:** DRAFT ONLY (Held for Lead review & transmission; do not send directly)  
**Quick Unblock Map:** [`BH_A31_UNBLOCK_SEQUENCE_BRIEF.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BH_A31_UNBLOCK_SEQUENCE_BRIEF.md)

---

## 1. Decisions Needed From Owner Now (1-Minute Summary)

- **SFX Audition Picks (Batches 1–3):** Pick preferred cues (Option A/B/C) from `D:/FightVideo/SFX_audition/` (`SFX_03_AUDITION_MANIFEST.md` and `SFX_06_BATCH3_AUDITION_MANIFEST.md`; `119/119` source `.uasset`s verified non-zero on disk) for Parry, Boss Parry Recoil, Phase 2 Aura Ignite, Player Backstep, Stance Break, and Boss Swings (`SFX-01..15`). Later SFX specs (`SFX-16..45`, `BB-A11..A14`) stay unwired (`"cues": []`) until your picks arrive.
- **Sevarog Phase-2 Aura Motif (`BB-A24`):** Pick `Cand A` (Spectral Wraith Mantle — recommended), `Cand B` (Soul Stack Shoulder Mist), or `Cand C` (Cyan BoostLite structural clone) before Lead Niagara authoring starts.
- **Sevarog 4-Move Live Clip Review:** Watch `D:/FightVideo/sevarog_live/Sevarog_4Moves_Live_Review.mp4` (`12 s`, `1080p`, sent by Lead) to confirm Sevarog's `Swing1_Medium`, `Swing2_Medium`, `Swing3_Slow`, and `Speedburst` combat look in `L_SevarogArena`.

---

## 2. Current Milestone Status (`2026-11-11` `V5` — Lead-Accepted vs Provisional Source-Ready)

- **Ember Warden Timing Route — Lead-Accepted / Closed (`C-1240`):**
  - Montage notify timings match legacy table timings across all clean trials (`6/6` pass, `BUILD-285..287`), kept opt-in default-off (`bUseMontageNotifyTimings=false`).
  - Optional composite `AM_Boss01_A2` (`Raise + ApexHold + Slam`) documented as Plan Only (`BB_A21_A23`); pack `GS_ChargedAttack_Montage` stays default unless you approve a visual change later.

- **Sevarog Framework Boss — `S1..S5` Accepted; `S6..S8` & `BE`/`BF` Source-Ready (`[X-1864..X-1891]` Provisional Pending Lead Live Acceptance):**
  - **Accepted baseline (`BUILD-296`):** `S1..S5` draft cards (`Swing1_Medium`, `Swing2_Medium`, `Swing3_Slow` `55` dmg, `Speedburst -> Swing1_Medium` `25` dmg) run in `L_SevarogArena`; `Stun_Start`/`Stun_Loop`/`Stun_End` + `Death_front` (`0–15`, `0.967 s`) frame sheets complete (`LevelStart` tail `41–74` pending Lead capture).
  - **Provisional / Source-Ready (pending Lead authoring & live PIE verification / UHT Shipping `[C-1286+]`):** Codex delivered `S1`/`S2` `90–120 cm` transient dry-run (`509/509`), `S6..S8` (`Ultimate_Swing_120fps`, `Subjugation`, `Soul_Siphon`) & `AdditionalPhaseIds` transient dry-run (`507/507`), `BE` Batches `1–10` (`509/509`), and `BF` Batches `1–8` (`BF-X01..X20` `509/509` generation/nav/Shipping reflection/`MoveCard` preflight + `BF-X21..X40` static audits — zero live/Shipping acceptance claimed).

- **Greystone Player Switch — Wrappers Accepted (`[C-1282]`, SHA-256 Bit-Exact); `_RM` Root-Motion Fix Pending Lead Run (`[C-1285]`):**
  - Approved by you (`47/48`, `97.9%` blind fit score). Local pack footprint + `15` materials + `26` global + `39` hero textures verified (`BD-A03..04`, `BH-A16`, zero foreign leakage).
  - **Accepted (`f97994a7`):** `BP_GreystoneERPlayer` and `4` `_Fit_Greystone` montage wrappers authored (`5/5` disk SHA-256 bit-exact vs Git LFS `HEAD`) & read back `14/14` notify rows (`BUILD-297` `506/506`, `[C-1282]`).
  - **Root-Motion Blocker Root Cause (`[C-1285]`):** Earlier IK retargets defaulted `Root` chain FK `TranslationMode = None`, baking travel into `pelvis` (`180.81 cm` pelvis / `0.00 cm` root). Lead ran `A_C1285_GREYSTONE_ROOTFIX` dry-run (`FIX_dryrun exit=0`, `156.75 cm` source `AN_ER_Backstep_Mixamo_V2` root XY); live `--write`, paired RM4 displacement (`84–98 cm` / `215–290 cm`, `<= 10%`), `GLOBALLY_SCALED` pack re-retarget, `KI-052` linked-layer triage, and your `8`-slot review clip (`C1257C`) remain open. Mannequin remains default until every gate passes.

---

## 3. Parked / Held Items (No Changes Made)

- **Round 6 Phase 2 & Shipped DLSS Default:** Remains parked per `C-954` (TSR default unchanged in `DefaultEngine.ini`).
- **Zero Repo/Asset Policy Violations:** Third-party packs untouched; `0` media staged; `0` autonomous commits or remote pushes (`Queue BF-A` / `BG-A` / `BH-A` held clean for Owner commit manifest).
