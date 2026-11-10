# BB-A03: Greystone Owner Review-Clip Storyboard (8 Slots) & Lead Capture List

**Authority:** `Documentation/Boss/QUEUE_BB.md` (`BB-A03`), [`Documentation/Boss/C1257C_GREYSTONE_OWNER_REVIEW_CHECKLIST.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/C1257C_GREYSTONE_OWNER_REVIEW_CHECKLIST.md), and `[C-1265]` Decision 1/2.  
**Owner:** Antigravity (`offline storyboard & capture spec`; Lead executes live PIE captures under `ENGINE_LOCK.json`).  
**Output Discipline:** Captured frames and assembled review MP4 live strictly on `D:/FightVideo/greystone_review/` (**never staged in git**).

---

## 1. Storyboard Sequence (8 Slots, ~24–32 s Total Reel)

Target resolution: **1920x1080** (or 960x540 Lanczos-upscaled to 1080p), 30 fps, H.264 `yuv420p`, `+faststart`, dark title header per slot matching `C1265D`. All captures use `rpg.GreystonePlayerTestPawn=1` in `L_SevarogArena` after the two-frame bright warmup (`> 300,000 B`).

| Slot # | Checklist Slot (`C1257C`) | Target Montage / Animation Asset (`GreystonePack` / `Greystone/`) | Camera Framing & Angle | Duration / Action Cue to Capture | Evaluation Focus |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | **Idle** | `ABP_CombatCharacter_Grey` idle state | 3/4 front-right, full-body + shadow | 2.5 s (stand still in combat-ready stance) | Feet grounding, sword/shield grip, cloak drape vs leg armor |
| **02** | **Run** | Locomotion BlendSpace (`BS_1H_Run_Grey` / walk-sprint) | Side-follow / trailing 3/4 camera | 3.0 s (forward/strafe run loop) | No foot skate, pelvic sway, sword/shield locked to hands |
| **03** | **Light Attack** | `AM_1H_Attack_A_Grey` / primary light combo | 3/4 front-side combat distance | 3.0 s (R1 combo press against dummy/boss) | Hand-to-hilt grip, arc clarity, shoulder-plate vs chest clipping |
| **04** | **Heavy Attack** | `AM_1H_Attack_Heavy_D_Grey` / charged R2 | 3/4 side-front at 180 cm | 3.5 s (R2 tap/hold overhead/thrust) | Windup grounding, apex silhouette, follow-through blend |
| **05** | **Quick Roll** *(C-1265 Decision 1)* | `Dodge_Small_Forward_Roll_Montage_Grey` | Side view (`yaw + 90` or wide trailing) | 3.0 s (single-tap directional dodge; **215–290 cm** band) | Shoulder tuck, cape non-inversion, zero floor clipping, no double-tap |
| **06** | **Backstep** | `AM_ER_Backstep_Mixamo_V2_Fit_Greystone` | Side view (`yaw + 90`) | 3.0 s (neutral single-tap dodge; **84–98 cm** band) | Crisp backward hop, foot plant stability, blade ready |
| **07** | **Guard Counter** | `BlockLoop` -> `AM_ER_Attack_GuardCounter_Fit_Greystone` | 3/4 front-side | 3.5 s (hold block + rising R2 counter) | Shield hold -> upward counter transition, zero shield pop |
| **08** | **Plunge / Air Light & Heavy** | `AM_ER_Attack_Air_Light_Fit_Greystone` & `AM_ER_Attack_Air_Heavy_Plunge_Fit_Greystone` | Wide side/3/4 capturing jump apex to landing | 4.0 s (jump -> plunge strike -> recovery) | Vertical blade alignment, cape billow, landing compression |

---

## 2. Lead Capture List (`D:/FightVideo/greystone_review/`)

Prerequisite before capturing:
1. Run `author_greystone_player.py` (Codex `BB-X01`) in real-asset mode under `/Game/OneBossFight/Player/Greystone/` with post-save reload notify readback PASS.
2. Run `pie_greystone_root_motion.py` (`BB-X02`) to verify Backstep (`84–98 cm`) and Quick Roll (`215–290 cm`) within 10% of mannequin baseline.
3. Capture 8 slot clips (or burst stills at 15–30 fps) under `D:/FightVideo/greystone_review/slot_01_idle/` through `slot_08_plunge/` using the bright-streak warmup pattern (`> 300,000 B` x 2 before capture).

### Stitch Template (Output on `D:`, Never Staged)
Once the 8 slot MP4s (`slot_01.mp4` .. `slot_08.mp4`, normalized to `1920x1080`, `30 fps`, `yuv420p`) are captured under `D:/FightVideo/greystone_review/`:
```powershell
# Concatenate normalized slot_01..slot_08 MP4s listed in slots.txt
ffmpeg -y -f concat -safe 0 -i "D:\FightVideo\greystone_review\slots.txt" -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart "D:\FightVideo\greystone_review\Greystone_8Slot_Owner_Review.mp4"
```
(Where `slots.txt` contains `file 'slot_01.mp4'` .. `file 'slot_08.mp4'`, each pre-stamped with `drawtext` slot label matching `C1257C_GREYSTONE_OWNER_REVIEW_CHECKLIST.md`.)
