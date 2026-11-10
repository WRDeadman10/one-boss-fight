# BB-A31..A35: Owner Progress Digest Draft (Held for Lead)

**Queue Lane:** `QUEUE_BB` Tasks `BB-A31`..`BB-A35` (Antigravity)  
**Status:** DRAFT ONLY (Held for Lead review & transmission; do not send directly)  

---

## 1. Decisions Needed From Owner Now

- **SFX Audition Picks (Batches 1–3):** Pick preferred cues (Option A/B/C) from `D:/FightVideo/SFX_audition/` (`SFX_03_AUDITION_MANIFEST.md` and `SFX_06_BATCH3_AUDITION_MANIFEST.md`) for Parry, Boss Parry Recoil, Phase 2 Aura Ignite, Player Backstep, Stance Break, and Boss Swings (`SFX-01..15`). All later SFX specs (`SFX-16..45` plus Sevarog `BB-A11..A14`) stay unwired until your picks arrive.
- **Sevarog 4-Move Live Clip Review:** Watch `D:/FightVideo/sevarog_live/Sevarog_4Moves_Live_Review.mp4` (`12 s`, `1080p`, sent by Lead) to confirm Sevarog's `Swing1_Medium`, `Swing2_Medium`, `Swing3_Slow`, and `Speedburst` combat look in `L_SevarogArena`.

---

## 2. Current Milestone Status (As of 2026-11-10)

- **Ember Warden Timing Route — Closed (`C-1240`):**
  - Montage notify timings match legacy table timings across all clean trials (`6/6` pass, `BUILD-285..287`), kept opt-in default-off (`bUseMontageNotifyTimings=false`).
  - Optional composite `AM_Boss01_A2` (`Raise + ApexHold + Slam`) documented as Plan Only (`BB_A21_A23`); pack `GS_ChargedAttack_Montage` stays default unless you approve a visual change later.

- **Sevarog Framework Boss — Live in Arena (`BUILD-291..295`, `501/501` tests):**
  - Draft cards (`S1..S5`), profile, and test spawn bridge run live in `L_SevarogArena`.
  - Heavy Slam (`S3`) hits for `55` dmg; Dash (`S4` `Speedburst`, `330 cm` warp) chains cleanly on whiff into `S5` (`Swing1_Medium`) for `25` dmg.
  - **Two active engineering items (no owner action needed):** fixing `S1`/`S2` swing trace alignment at `140 cm` (`C-1265b` full-clip trace in progress) and diagnosing elevated-spawn `MoveFailed` path-follow termination (`X09`/`BB-A25`).
  - Sevarog card SFX, voice-bark, signature timing marks, and Phase-2 Niagara aura candidates are specced offline with zero runtime wiring (`BB-A06..A14`, `BB-A24`).

- **Greystone Player Switch — Approved & Under Technical Gates (`[C-1257]`..`[C-1269]`):**
  - Approved by you (`47/48`, `97.9%` blind fit score). Third-party local pack policy closes repo reproducibility (`[C-1261]`, `~312 MB` local functional footprint; zero pack edits).
  - Roll fidelity gate aligned to your single-tap directional quick roll (`215–290 cm`, within `10%` of mannequin) + neutral backstep (`84–98 cm`), keeping double-tap long roll disabled (`[C-1265]`).
  - Hit UE 5.5 Python montage API limit (`composite_sections`); Lead ordered editor-only C++ `URPGMontageWrapperLibrary::CreateRetargetWrapper` (`[C-1269]`) so exact source notify timings copy before paired PIE + your 8-slot review clip (`BB_A03` storyboard). Mannequin remains default until every gate passes.

---

## 3. Parked / Held Items (No Changes Made)

- **Round 6 Phase 2 & Shipped DLSS Default:** Remains parked per `C-954` (TSR default unchanged).
- **Zero Repo/Asset Policy Violations:** Third-party packs untouched; `0` media staged; `0` remote pushes.
