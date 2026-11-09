# SFX-03: Owner Audio Audition Manifest & Delivery Pack

**Document Version:** 1.0  
**Authority:** Project Owner Order & Claude Directives `[C-1169]`, `[C-1181]`  
**Owner:** Antigravity (`Art/Review/Audit`)  
**Media Delivery Target:** `D:/FightVideo/SFX_audition/` (strictly off-repo; no binary media in git).

---

## 1. Audition Manifest & Cue Catalog

| Event / Gap ID | Option | Candidate Cue Name | Source Asset Path in Repo | Expected Duration | Audio Role & Aesthetic |
|---|---|---|---|---|---|
| **GAP 1: Player Parry Success** | **A** | `Sword_Sharpening_Fast_Speed` | `/Game/RealisticSwordSoundEffects/Wavs/Sword_Sharpening/Sword_Sharpening_Fast_Speed` | 7.62s | *DEFECT (C-1186):* 7.62s scraping loop, too slow for deflect impact; 'Preferred' label dropped. |
| | **B** | `Sword_Attack_Short_1` | `/Game/RealisticSwordSoundEffects/Wavs/Sword_Attack/Sword_Attack_Short_1` | ~0.25s | Crisp blade contact ring with fast attack. |
| | **C** | `ShieldImpact4` | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/ShieldImpacts/ShieldImpact4` | ~0.30s | Heavy buckler deflection thump. |
| **GAP 2: Boss Parry Recoil** | **A (Pref)** | `Sevarog_Effort_Block_01` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundWaves/Sevarog_Effort_Block_01` | ~0.55s | Authentic Sevarog vocal deflection grunt + wind intake during 0.6s recoil. *(Note: Must match boss character identity).* |
| | **B** | `Sevarog_Effort_PainHeavy_01` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundWaves/Sevarog_Effort_PainHeavy_01` | ~0.60s | Deep guttural stagger effort sound. |
| | **C** | `Sevarog_Effort_Frustration_01` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundWaves/Sevarog_Effort_Frustration_01` | ~0.50s | Frustrated growl indicating lost balance. |

---

## 1.1 Parry SFX Addendum (C-1186 Deliverable)

Per Lead directive `[C-1186]`, souls-like parry success requires a sharp metallic clang/deflect of 0.2–0.6 s with a fast attack (<0.05 s). Compiled into `D:/FightVideo/SFX_audition/Parry_Addendum_Reel.mp4` and `.mp3`:

| Addendum Candidate | Source Asset Path | Active Transient | Sound Character |
|---|---|---|---|
| **Candidate 1 (Fast Clash)** | `/Game/RealisticSwordSoundEffects/Wavs/Sword_Attack/Sword_Attack_Short_2` | 0.40s | Fast, biting metallic clash with immediate 0.01s attack transient. |
| **Candidate 2 (Blade Ping)** | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/SwordImpacts/SwordImpact1` | 0.35s | Sharp, high-frequency sword deflect ping with clear metallic resonance. |
| **Candidate 3 (Heavy Clang)** | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/SwordImpacts/SwordImpact3` | 0.40s | Resonant heavy iron blade clang for weightier greatsword deflection. |
| **GAP 3: Phase 2 Aura Ignite** | **A (Pref)** | `SFX_Vefects_Shockwave_04_1s` | `/Game/Vefects/Easy_Shockwaves_VFX/Audio/Waves/SFX_Vefects_Shockwave_04_1s` | ~1.00s | Deep supernatural energy burst with sub-bass drop and fiery tail. |
| | **B** | `Explosion01` | `/Game/StarterContent/Audio/Explosion01` | ~1.20s | Heavy concussive explosion. |
| | **C** | `SFX_Vefects_Shockwave_01_1s` | `/Game/Vefects/Easy_Shockwaves_VFX/Audio/Waves/SFX_Vefects_Shockwave_01_1s` | ~0.90s | Snappy high-frequency energy snap. |
| **GAP 4: Player Backstep Whoosh** | **A (Pref)** | `Swoosh_1` | `/Game/RealisticSwordSoundEffects/Wavs/Sword_Swoosh/Swoosh_1` | ~0.22s | Swift, clean air displacement matching Mixamo root-motion backstep. |
| | **B** | `Swoosh_3` | `/Game/RealisticSwordSoundEffects/Wavs/Sword_Swoosh/Swoosh_3` | ~0.18s | Whipping, higher-pitched air displacement. |
| | **C** | `Sword_Unsheathe_1` | `/Game/RealisticSwordSoundEffects/Wavs/Sword_Unsheathe/Sword_Unsheathe_1` | ~0.30s | Quick metallic friction slide. |
| **GAP 5: Boss Stance Break** | **A (Pref)** | `Collapse01` | `/Game/StarterContent/Audio/Collapse01` | ~1.10s | Souls-style stone/armor fracture and shattering collapse. |
| | **B** | `A_Guardian_Impact01` | `/Game/AdvancedARPGCombat/RangedCombatSystem/DemoAssets/Effects/ArrowSounds/A_Guardian_Impact01` | ~0.85s | Resounding heavy iron chime/clash. |
| | **C** | `Sevarog_ProfileDizzy_010` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundWaves/Sevarog_ProfileDizzy_010` | ~1.20s | Ringing spectral disorientation drone. |

---

## 2. Compilation & Verification Pipeline

1. **Extraction Tool:** `Scripts/Editor/export_sfx_candidates.py` loads each native `SoundWave` asset in-engine via `unreal.AssetExportTask` and `unreal.SoundExporterWAV` under `ENGINE_LOCK`. Output directory: `D:/FightVideo/SFX_audition/RawWavs/`.
2. **Reel Assembler:** `Scripts/Tools/build_sfx_audition_reel.py` generates 1080p visual cards with gold/amber Souls styling, event titles, candidate option labels, and audio waveforms, concatenated into:
   - `D:/FightVideo/SFX_audition/SFX_Audition_Reel.mp4` (Full 1080p Video + AAC Audio)
   - `D:/FightVideo/SFX_audition/SFX_Audition_Reel.mp3` (Standalone MP3 Audio)
3. **Licensing & Repo Discipline:**
   - Raw extracted WAV files and rendered MP4/MP3 media remain **exclusively off-repo** at `D:/FightVideo/SFX_audition/`.
   - Git tracks only the Python authoring scripts and this documentation manifest.
