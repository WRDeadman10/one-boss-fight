# SFX Batch 3 Audition Reel Manifest

**Document Version:** 1.0  
**Authority:** Claude Lead Directives `[C-1197]`, `[C-1203]`, `[C-1204]` (2026-11-09).  
**Owner:** Antigravity (`Art/Review/Audit`).  
**Media Delivery Location:** `D:/FightVideo/SFX_audition/` (off-repo per `[C-1181]`).  

---

## 1. Compiled Reel Deliverables

- **Video Audition Reel (1080p, 30fps):** `D:/FightVideo/SFX_audition/Batch3_Audition_Reel.mp4` (1.64 MB, duration ~31.7s)
- **Audio Audition Reel (MP3, 192kbps):** `D:/FightVideo/SFX_audition/Batch3_Audition_Reel.mp3` (436.1 KB)
- **Raw Exported WAVs (15 files):** `D:/FightVideo/SFX_audition/RawWavs/SFX*.wav`

---

## 2. Audition Clips Catalog

| Index | Clip Timestamp | Task ID | Gameplay Event | Candidate Option | In-Repo Source Asset | Duration / Audio Character |
|---|---|---|---|---|---|---|
| **01** | `00:00 - 00:02` | **SFX-11** | Boss A1 Horizontal Slash | **Option A (Preferred)** | `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_1_Cue` | ~0.42s, crisp cutting arc |
| **02** | `00:02 - 00:04` | **SFX-11** | Boss A1 Horizontal Slash | **Option B** | `/Game/RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_1_Cue` | ~0.25s, sharp high-velocity |
| **03** | `00:04 - 00:06` | **SFX-11** | Boss A1 Horizontal Slash | **Option C** | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Sword_Swing_Cue` | ~0.38s, balanced standard |
| **04** | `00:06 - 00:08` | **SFX-12** | Boss A2 Overhead Cleave | **Option A (Preferred)** | `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_3_Cue` | ~0.55s, powerful vertical cut |
| **05** | `00:08 - 00:10` | **SFX-12** | Boss A2 Overhead Cleave | **Option B** | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Axe_Swing_Cue` | ~0.48s, heavy downward mass |
| **06** | `00:10 - 00:12` | **SFX-12** | Boss A2 Overhead Cleave | **Option C** | `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_5_Cue` | ~0.50s, deep bass whoosh |
| **07** | `00:12 - 00:14` | **SFX-13** | Boss A3 Ground Stomp | **Option A (Preferred)** | `/Game/Vefects/Easy_Shockwaves_VFX/Audio/Cues/SFX_Vefects_Shockwave_01_1s_Cue` | ~0.90s, sharp sub-bass crack |
| **08** | `00:14 - 00:17` | **SFX-13** | Boss A3 Ground Stomp | **Option B** | `/Game/StarterContent/Audio/Explosion_Cue` | ~1.10s, low rolling thunder |
| **09** | `00:17 - 00:19` | **SFX-13** | Boss A3 Ground Stomp | **Option C** | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue` | ~0.85s, dense stone impact |
| **10** | `00:19 - 00:21` | **SFX-14** | Boss Mid01 Forward Thrust | **Option A (Preferred)** | `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_1_Cue` | ~0.28s, focused forward pierce |
| **11** | `00:21 - 00:23` | **SFX-14** | Boss Mid01 Forward Thrust | **Option B** | `/Game/RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_4_Cue` | ~0.30s, sharp displacement |
| **12** | `00:23 - 00:25` | **SFX-14** | Boss Mid01 Forward Thrust | **Option C** | `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_7_Cue` | ~0.35s, linear edge slice |
| **13** | `00:25 - 00:27` | **SFX-15** | Boss Sprint Gap-Closer | **Option A (Preferred)** | `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_2_Cue` | ~0.58s, heavy momentum carry |
| **14** | `00:27 - 00:29` | **SFX-15** | Boss Sprint Gap-Closer | **Option B** | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Hammer_Swing_Cue` | ~0.52s, wide air drag |
| **15** | `00:29 - 00:31` | **SFX-15** | Boss Sprint Gap-Closer | **Option C** | `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_8_Cue` | ~0.46s, fast arc whoosh |

---

## 3. Review & Verification Notes

1. **Integration Target:** All candidate whooshes are designed to be hooked via AnimNotifies on boss montages (`AM_Boss01_A1`, `AM_Boss01_A2`, `AM_Boss01_A3`, `AM_Boss01_Mid01`, `AM_Boss01_Sprint`) with fail-closed `nullptr` defaults.
2. **Owner Review Ready:** Lead can present this reel along with the Parry Addendum Reel (`Parry_Addendum_Reel.mp4`) for Owner audition selections.
