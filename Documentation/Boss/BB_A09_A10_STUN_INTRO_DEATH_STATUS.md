# BB-A09 & BB-A10: `Stun_Start/Loop/End`, `LevelStart`, and `Death_front` Frame Notes Status

**Authority:** `Documentation/Boss/QUEUE_BB.md` (`BB-A09`, `BB-A10`), [`Documentation/Boss/C1239_SEVAROG_ANIMATION_INVENTORY.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/C1239_SEVAROG_ANIMATION_INVENTORY.md).  
**Owner:** Antigravity (`offline audit`).  
**Status:** **`BLOCKED` for frame-cited visual marks** (zero PNG frames/sheets exist on disk under `D:/FightVideo/sevarog_frames/` for these 5 clips; Lead run `P_C1243_SEVAROGFRAMES` only captured the 8 attack/ability sequences). Probe durations and asset metadata from `P_C1239_SEVAROGPROBE` are preserved below alongside the exact Lead capture list needed to unblock visual marking.

---

## 1. Verified Disk Probe Metadata (`C1239_SEVAROG_ANIMATION_INVENTORY.md`)

| Task | Asset Path (`/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/...`) | Probe Length (s) | Root Motion / Notifies (`C1239`) | Frame Sheet Status (`D:/FightVideo/sevarog_frames/`) |
| :--- | :--- | :--- | :--- | :--- |
| **BB-A09** | `Stun_Start` | `1.700000` | `root_motion=False`, `0 notifies` | **Missing (`BLOCKED`)** — 26 frames @ 15 Hz not yet captured |
| **BB-A09** | `Stun_Loop` | `2.033333` | `root_motion=False`, `0 notifies` | **Missing (`BLOCKED`)** — 31 frames @ 15 Hz not yet captured |
| **BB-A09** | `Stun_End` | `0.733333` | `root_motion=False`, `0 notifies` | **Missing (`BLOCKED`)** — 12 frames @ 15 Hz not yet captured |
| **BB-A10** | `LevelStart_Montage` *(1 section: `Default`)* | `5.000000` | `1 notify: AnimNotify_PlayParticleEffect` | **Missing (`BLOCKED`)** — 76 frames @ 15 Hz (or raw `LevelStart` seq) not yet captured |
| **BB-A10** | `Death_front` | `0.966667` | `root_motion=False`, `0 notifies` | **Missing (`BLOCKED`)** — 15 frames @ 15 Hz not yet captured |

---

## 2. Structural Stagger & Intro/Death Planning Notes (No Visual Fabrication)

1. **BB-A09 (`Stun_Start` / `Stun_Loop` / `Stun_End`):**
   - Combined baseline non-looping duration: `1.700 s` (`Stun_Start`) + `N * 2.033 s` (`Stun_Loop`) + `0.733 s` (`Stun_End`).
   - Vulnerable riposte window open/close markers (exact frame where Sevarog finishes collapsing into `Stun_Start` and begins rising in `Stun_End`) **cannot be cited without visual frames** and remain **BLOCKED** until Lead captures those 3 sequences in [`Scripts/Editor/pie_sevarog_clip_frames.py`](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_sevarog_clip_frames.py).
2. **BB-A10 (`LevelStart_Montage` & `Death_front`):**
   - `LevelStart_Montage` is a `5.000 s` single-section (`Default`) montage carrying 1 legacy `AnimNotify_PlayParticleEffect` (`C1239_SEVAROG_ANIMATION_INVENTORY.md` line 30); evaluate intro skip/dormancy gate alignment once frames are captured.
   - `Death_front` is `0.967 s` (`root_motion=False`); verify end-pose hold / vanish timing vs `URPGBossEncounter` death-destruction delay (`BB-X30`) once captured.

---

## 3. Unblock Prerequisite (Lead Capture List)

Append `"Stun_Start"`, `"Stun_Loop"`, `"Stun_End"`, `"Death_front"` (plus `LevelStart` if a sequence exists alongside `LevelStart_Montage`) to `CLIPS` in [`Scripts/Editor/pie_sevarog_clip_frames.py`](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_sevarog_clip_frames.py) under `ENGINE_LOCK.json` and stitch sheets to `D:/FightVideo/sevarog_frames/_sheets/`. Until then, `BB-A09` and `BB-A10` visual frame marks stay **BLOCKED (missing captures)** per Queue BB rules, and Antigravity proceeds to `BB-A11..A15`.
