# BB-A31..A35: Owner Progress Digest Draft (Held for Lead)

**Queue Lane:** `QUEUE_BB` Tasks `BB-A31`..`BB-A35` -> Refreshed under `QUEUE_BC_AG` Tasks `BC-A34`..`BC-A35` (Antigravity)  
**Status:** DRAFT ONLY (Held for Lead review & transmission; do not send directly)  

---

## 1. Decisions Needed From Owner Now

- **SFX Audition Picks (Batches 1–3):** Pick preferred cues (Option A/B/C) from `D:/FightVideo/SFX_audition/` (`SFX_03_AUDITION_MANIFEST.md` and `SFX_06_BATCH3_AUDITION_MANIFEST.md`) for Parry, Boss Parry Recoil, Phase 2 Aura Ignite, Player Backstep, Stance Break, and Boss Swings (`SFX-01..15`). All later SFX specs (`SFX-16..45` plus Sevarog `BB-A11..A14`) stay unwired until your picks arrive.
- **Sevarog 4-Move Live Clip Review:** Watch `D:/FightVideo/sevarog_live/Sevarog_4Moves_Live_Review.mp4` (`12 s`, `1080p`, sent by Lead) to confirm Sevarog's `Swing1_Medium`, `Swing2_Medium`, `Swing3_Slow`, and `Speedburst` combat look in `L_SevarogArena`.

---

## 2. Current Milestone Status (As of 2026-11-10 `[C-1277]`)

- **Ember Warden Timing Route — Closed (`C-1240`):**
  - Montage notify timings match legacy table timings across all clean trials (`6/6` pass, `BUILD-285..287`), kept opt-in default-off (`bUseMontageNotifyTimings=false`).
  - Optional composite `AM_Boss01_A2` (`Raise + ApexHold + Slam`) documented as Plan Only (`BB_A21_A23`); pack `GS_ChargedAttack_Montage` stays default unless you approve a visual change later.

- **Sevarog Framework Boss — Live in Arena (`BUILD-296`, `505/505` tests):**
  - `S1..S5` draft cards (`Swing1_Medium`, `Swing2_Medium`, `Swing3_Slow`, `Speedburst -> Swing1_Medium`) run live in `L_SevarogArena`; `S1`/`S2` selector `MaxRangeCm` tightened to `90–120 cm` per Lead `[C-1274]` (`140 cm` whiff fixed).
  - Heavy Slam (`S3`) hits for `55` dmg; Dash (`S4` `Speedburst`, `330 cm` warp) chains cleanly on whiff into `S5` (`Swing1_Medium`) for `25` dmg.
  - Signatures `S6` (`Ultimate_Swing_120fps`, one continuous 360° cleave `0.667–0.900 s`, `90–150 cm`, `65` dmg), `S7` (`Subjugation` AoE + snare, `35` dmg), and `S8` (`Soul_Siphon` 5-tick cone drain + heal) approved as provisional values (`[C-1277]`) for Codex `X26` card authoring and subsequent PIE tuning.
  - Sevarog card SFX, voice-bark, and Phase-2 Niagara aura specs stay staged offline (`BB-A11..A14`, `BC-A26..A30`). `Stun_Start`/`Stun_Loop`/`Stun_End` frame sheets complete (`BC-A10`); `LevelStart` tail & `Death_front` await next free engine window.

- **Greystone Player Switch — Approved & Under Technical Gates (`[C-1257]`..`[C-1275]`):**
  - Approved by you (`47/48`, `97.9%` blind fit score). Third-party local pack policy closes repo reproducibility (`[C-1261]`, `~312 MB` local functional footprint; zero pack edits).
  - Roll fidelity gate aligned to your single-tap directional quick roll (`215–290 cm`, within `10%` of mannequin) + neutral backstep (`84–98 cm`), keeping double-tap long roll disabled (`[C-1265]`).
  - Editor-only C++ `URPGMontageWrapperLibrary` landed & green (`[C-1275]`, `BUILD-296` `505/505`); Codex is completing `C-1275a` readback logging before paired PIE + your 8-slot review clip (`BB_A03` storyboard). Mannequin remains default until every gate passes.

---

## 3. Parked / Held Items (No Changes Made)

- **Round 6 Phase 2 & Shipped DLSS Default:** Remains parked per `C-954` (TSR default unchanged).
- **Zero Repo/Asset Policy Violations:** Third-party packs untouched; `0` media staged; `0` remote pushes.
