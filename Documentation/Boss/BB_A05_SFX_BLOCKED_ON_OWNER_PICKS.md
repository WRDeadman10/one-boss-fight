# BB-A05: SFX Readiness & Exact List Blocked on Owner Reel Picks

**Authority:** `Documentation/Boss/QUEUE_BB.md` (`BB-A05`), [`Documentation/Boss/QUEUE_SFX.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_SFX.md), `[C-1265]` Item 3.  
**Owner:** Antigravity (`offline audio specs; zero wiring until Owner picks`).  
**Status:** Batch 8 (`SFX-36..40`) and Batch 9 (`SFX-41..45`) candidate specs are authored, fail-closed (default `nullptr` silence), and held ready. Zero Blueprint, AnimNotify, or C++ audio wiring is authorized until the Owner submits audition selections.

---

## 1. Delivered Audition Reels & Staged Specs (Held Ready)

| Batch | Tasks Covered | Spec / Manifest Document | Off-Repo Audition Reel (`D:/FightVideo/SFX_audition/`) | Current State |
| :--- | :--- | :--- | :--- | :--- |
| **Batch 1 (Gap 1–5)** | `SFX-01..05` (Parry, Recoil, Aura Ignite, Backstep, Stance Break) | [`SFX_03_AUDITION_MANIFEST.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/SFX_03_AUDITION_MANIFEST.md), [`SFX_04_WIRING_PLAN.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/SFX_04_WIRING_PLAN.md) | `SFX_Audition_Reel.mp4` / `.mp3` + `Parry_Addendum_Reel.mp4` / `.mp3` | Auditioned & wired plan ready; **Awaiting Owner Pick** |
| **Batch 2** | `SFX-06..10` (Guard Counter, Air Plunge, A4 Sweep, A5 Javelin, Stance Shatter) | [`QUEUE_SFX.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_SFX.md) | Included in priority backlog | **Awaiting Owner Pick / Reel Export** |
| **Batch 3 (Priority a)** | `SFX-11..15` (Boss A1, A2, A3, Mid01, Sprint attack whooshes) | [`SFX_05_BATCH3_CANDIDATE_SPEC.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/SFX_05_BATCH3_CANDIDATE_SPEC.md), [`SFX_06_BATCH3_AUDITION_MANIFEST.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/SFX_06_BATCH3_AUDITION_MANIFEST.md) | `Batch3_Audition_Reel.mp4` / `.mp3` (15 cues exported) | Reel built & verified; **Awaiting Owner Pick** |
| **Batch 4 (Priority d)** | `SFX-16..20` (Phase 2 Roar, Ignite, Aura Loop, Crackle, Stinger) | [`SFX_07_BATCH4_CANDIDATE_SPEC.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/SFX_07_BATCH4_CANDIDATE_SPEC.md) | Spec only (WAV export on Lead/Owner go) | **Awaiting Owner Pick** |
| **Batch 5 (Priority b)** | `SFX-21..25` (Shield Block, Deflect, Flask, Dodge Roll, Draw/Sheathe) | [`SFX_08_BATCH5_CANDIDATE_SPEC.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/SFX_08_BATCH5_CANDIDATE_SPEC.md) | Spec only | **Awaiting Owner Pick** |
| **Batch 6 (Priority e)** | `SFX-26..30` (Posture Warning, Stagger Loop, Riposte, Recovery, Guard Break) | [`SFX_09_BATCH6_CANDIDATE_SPEC.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/SFX_09_BATCH6_CANDIDATE_SPEC.md) | Spec only | **Awaiting Owner Pick** |
| **Batch 7** | `SFX-31..35` (Boss Footsteps, Armor Clank, Cape Rustle, Spectral Hum, Death Collapse) | [`SFX_10_BATCH7_CANDIDATE_SPEC.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/SFX_10_BATCH7_CANDIDATE_SPEC.md) | Spec only | **Awaiting Owner Pick** |
| **Batch 8 (Combat UI)** | `SFX-36..40` (Lock-On Acquire, Retarget, Low Stamina Pant, Critical HP Heartbeat, Defeat Stinger) | [`SFX_11_BATCH8_CANDIDATE_SPEC.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/SFX_11_BATCH8_CANDIDATE_SPEC.md) | Ready in repo packs (0 external downloads) | **Held Ready — Blocked on Owner Pick** |
| **Batch 9 (Arena/Menu)** | `SFX-41..45` (Ruin Wind, Brazier Crackle, Sub-Bass Drone, Wall Collision, Fog/Mist + Menu UI) | [`SFX_12_BATCH9_CANDIDATE_SPEC.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/SFX_12_BATCH9_CANDIDATE_SPEC.md) | Ready in repo packs (0 external downloads) | **Held Ready — Blocked on Owner Pick** |

---

## 2. Exact List Blocked Strictly on Owner Reel Picks

Nothing below may be wired into montages, Blueprints, `URPGPlayerParry`, `URPGTier2BossPresentation`, `URPGBossStagger`, `URPGBossHud`, or `L_SevarogArena` until the Owner selects Option A / B / C (or `None`):

1. **Immediate Unblocked Reel Picks (MP4/MP3 Reels Already Compiled on `D:/FightVideo/SFX_audition/`):**
   - **Gap 1 — Player Parry Success** (`SFX_Audition_Reel` + `Parry_Addendum_Reel` short metallic clangs) -> blocks `URPGPlayerParry` cue wiring (`SFX-04`/`SFX-05`).
   - **Gap 2 — Boss Parry Recoil** (`SFX_Audition_Reel`) -> blocks `AM_Boss01_ParryRecoil` notify wiring.
   - **Gap 3 — Phase 2 Aura Ignite** (`SFX_Audition_Reel`) -> blocks `URPGTier2BossPresentation` spawn SFX.
   - **Gap 4 — Player Backstep Whoosh** (`SFX_Audition_Reel`) -> blocks `AM_ER_Backstep_Mixamo_V2` / Greystone wrapper notify wiring.
   - **Gap 5 — Boss Stance Break Shatter** (`SFX_Audition_Reel`) -> blocks `URPGBossStagger` enter cue wiring.
   - **Boss Whooshes A1 / A2 / A3 / Mid01 / Sprint (`SFX-11..15`)** (`Batch3_Audition_Reel`) -> blocks Ember Boss montage whoosh notifies.
2. **Queued Implementation Batches Held Until Picks Confirm Acoustic Direction:**
   - **Batches 4–7 (`SFX-16..35`):** WAV export & wiring held until Batch 1 & Batch 3 Owner tone preferences are established.
   - **Batch 8 (`SFX-36..40` — Combat UI & Player Feedback):** Held ready (`SFX_11_BATCH8_CANDIDATE_SPEC.md`); blocked on Owner pick before wiring to lock-on/stamina/HP/death events.
   - **Batch 9 (`SFX-41..45` — Arena Environment & Menu UI):** Held ready (`SFX_12_BATCH9_CANDIDATE_SPEC.md`); blocked on Owner pick before placing/wiring ambient cues in `L_SevarogArena` or menu widgets.
3. **Sevarog Framework Audio (`BB-A11..A14`):** Will be authored as spec-only against `/Game/ParagonSevarog/.../Sounds` without wiring until Owner review.
