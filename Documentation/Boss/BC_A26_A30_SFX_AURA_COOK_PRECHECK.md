# BC-A26..A30: SFX Disk Audit, Sevarog Aura Spec & `DirectoriesToAlwaysCook` Coverage

**Queue Lane:** `QUEUE_BC_AG` Tasks `BC-A26`..`BC-A30` (Antigravity)  
**Authority:** `Documentation/Boss/QUEUE_BC_AG.md`, `[C-1271]`  
**Status:** Offline spec & disk audit complete (`0` asset edits, `0` config edits, `0` wiring)  

---

## 1. Disk Verification Across SFX & Voice-Bark Specifications (`BC-A26..A28`)

Automated filesystem check across `Documentation/Boss/SFX_*.md`, `BB_A11_A13_SEVAROG_CARD_SFX_SPEC.md`, and `BB_A14_SEVAROG_VOICE_BARKS_SPEC.md`:

| Document | `/Game/` Asset Paths Checked | Missing on Disk | Disposition |
|---|---:|---:|---|
| `SFX_05_BATCH3_CANDIDATE_SPEC.md` | `15` | `0` | **PASS** (`100%` on disk) |
| `SFX_07_BATCH4_CANDIDATE_SPEC.md` | `16` | `0` | **PASS** (`100%` on disk) |
| `SFX_08_BATCH5_CANDIDATE_SPEC.md` | `16` | `0` | **PASS** (`100%` on disk) |
| `SFX_09_BATCH6_CANDIDATE_SPEC.md` | `15` | `0` | **PASS** (`100%` on disk) |
| `SFX_10_BATCH7_CANDIDATE_SPEC.md` | `20` | `0` | **PASS** (`100%` on disk) |
| `SFX_11_BATCH8_CANDIDATE_SPEC.md` | `15` | `0` | **PASS** (`100%` on disk) |
| `SFX_12_BATCH9_CANDIDATE_SPEC.md` | `17` | `0` | **PASS** (`100%` on disk) |
| `BB_A11_A13_SEVAROG_CARD_SFX_SPEC.md` | `23` | `0` | **PASS** (`100%` on disk) |
| `BB_A14_SEVAROG_VOICE_BARKS_SPEC.md` | `16` | `0` | **PASS** (`100%` on disk) |
| `SFX_02_CANDIDATE_SELECTION.md` | `19` | **`8`** | **FLAGGED:** omits `Cues/Sword_*` & `Audio/Cues/` subfolder segments in 8 abbreviated paths (e.g. cites `/Game/RealisticSwordSoundEffects/Swoosh_1_Cue` instead of verified `/Game/RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_1_Cue`, `/Game/Vefects/Easy_Shockwaves_VFX/Audio/SFX_Vefects_Shockwave_01_1s_Cue` instead of `Audio/Cues/...`). Reconciled by `SFX_03_AUDITION_MANIFEST.md` and `SFX_04_WIRING_PLAN.md`; flagged here so wiring scripts never copy the abbreviated `SFX_02` shorthand. |

*Blocked Matrix Note:* Owner picks for `SFX-01..45` + Sevarog cards (`BB-A11..A14`) remain held at zero wiring (`nullptr` defaults) per `BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md`.

---

## 2. Sevarog Phase-2 Niagara Parameter & Fixed-Bounds Spec (`BC-A29`)

Building on [`BB_A24_SEVAROG_PHASE2_AURA_CANDIDATES.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BB_A24_SEVAROG_PHASE2_AURA_CANDIDATES.md) and the C-1202/C-1210 Niagara authoring rules (`OneBossFightEditor`):
- **Destination Asset Rule:** Must be a project-owned `UNiagaraSystem` under `/Game/OneBossFight/VFX/NS_Sevarog_PhaseTwoAura_*` (never modify `/Game/ParagonSevarog/FX/`).
- **Mandatory Fixed Bounds (`[C-1202]`):** Both Emitter and System bounds locked to symmetric fixed AABB `[-220.0, 220.0] cm` (scaled for Sevarog `165 cm` capsule half-height vs Ember's `175 cm` bounds) so frustum culling never pops off-center wisps.
- **Required Exposed `User.*` Parameters (uniform with `NS_Boss_PhaseTwoAura_BoostLite_Authored`):**
  - `User.Scale` (`float`, default `1.0`)
  - `User.Opacity` (`float`, default `0.85`, ramped down smoothly on `ClearPhaseTwoVisuals` / death)
  - `User.Color_Primary` (`LinearColor`, spectral emerald/teal or deep violet matching chosen `BB-A24` Cand A/B/C)
  - `User.Color_Secondary` (`LinearColor`, dark shadow mist undertone)
- **Performance Guard (`16.67 ms` RTX 2060 Super budget):** Max active particle budget `<= 120` sprites across all emitters (lower than BoostLite's `152.5/s` peak) to preserve clean readability of Sevarog swing telegraphs.

---

## 3. `DirectoriesToAlwaysCook` Offline Coverage Audit (`BC-A30`)

Inspected `Config/DefaultGame.ini:34-67` (`DirectoriesToAlwaysCook`):

| Content Tree | Status in `DefaultGame.ini` | Packaging Implication |
|---|---|---|
| `/Game/OneBossFight/Data` | **Present (`:37`)** | Covers `DA_Boss_Sevarog_Draft`, `DA_Boss_Sevarog_FrameworkProfile_Draft`, `DA_Move_Sevarog_*`. |
| `/Game/OneBossFight/Player/Greystone` | **Present (`:49`)** | Covers `BP_GreystoneERPlayer` & four `_Fit_Greystone` wrappers (added in `X-1810`). |
| `/Game/OneBossFight/VFX` | **Present (`:40`)** | Covers Ember auras + future `NS_Sevarog_PhaseTwoAura_*`. |
| `/Game/ParagonSevarog` | **Present (`:51`)** | Covers all Sevarog meshes, animations, materials, FX, and `Sounds/SoundCues` + `DialogueWaves`. |
| `/Game/StarterContent/Audio`, `/Game/Essential_Foosteps_SK/CUE/Concrete`, `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX` | **Present (`:63,66,67`)** | Covered for cook. |
| `/Game/RealisticSwordSoundEffects/Cues`, `/Game/Vefects/Easy_Shockwaves_VFX/Audio/Cues`, `/Game/ParagonGrux/...`, `/Game/ParagonSteel/...`, `/Game/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX` | **Absent from `DirectoriesToAlwaysCook`** | **Safe today** while all SFX/voice pointers remain `nullptr` (unreferenced). Once Owner approves SFX Batch 1–9 wiring or dynamic soft-object sound paths, either reference each picked cue directly via a cooked `DataAsset`/montage or add only the selected cue folder(s) to avoid inflating packaged size. |

*Companion Contract Test:* [`test_bc_a26_sfx_specs_disk_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bc_a26_sfx_specs_disk_contract.py).
