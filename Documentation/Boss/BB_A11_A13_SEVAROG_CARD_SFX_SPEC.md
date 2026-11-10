# BB-A11..A13: Sevarog Card SFX Specification (`S1..S5` + Candidate Signature Moves)

**Queue Lane:** `QUEUE_BB` Tasks `BB-A11`, `BB-A12`, `BB-A13` (Antigravity)  
**Authority:** `Documentation/Boss/QUEUE_BB.md`, `[C-1267]`, `FRPGBossCue` (`Source/OneBossFight/Player/RPGBossMoveCard.h:32-42`)  
**Status:** SPEC-ONLY (Zero runtime/card asset mutations; `FRPGBossCue.Sound` defaults remain unassigned/`nullptr` until Lead/Owner approval)  

---

## 1. Disk Audit Finding (`ParagonSevarog/Sounds`)

Inspection of `Content/ParagonSevarog/` on disk confirms:
- Folder audit: `Content/ParagonSevarog/` on disk:
  - `Content/ParagonSevarog/Audio/` is empty; `Content/ParagonSevarog/FX/` contains zero audio `.uasset` files.
  - `Content/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/` contains **vocal efforts and UI/lore cues only** (`Sevarog_Effort_Swing`, `Sevarog_Effort_Attack`, `Sevarog_Effort_Ability_Primary`, `Sevarog_Effort_Ability_Q`, `Sevarog_Effort_Ability_E`, `Sevarog_Effort_Ability_RMB`, `Sevarog_Effort_Ability_Ultimate`, `Sevarog_Effort_LandHeavy`, `Sevarog_Effort_PainHeavy`, `Sevarog_Ability_E_Engage`, etc.). It contains **zero** weapon metallic whoosh or hammer impact Foley cues.
- Therefore, card SFX combines:
  1. **Vocal/Effort Layer** from disk-verified `Content/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/` (unique Sevarog voice identity, kept separate from Boss01 Ember per `SFX_07_BATCH4_CANDIDATE_SPEC.md` Section 2).
  2. **Weapon Whoosh / Heavy Impact Layer** from disk-verified `Content/RealisticSwordSoundEffects/Cues/` and `Content/AdvancedARPGCombat/*/DemoAssets/SoundFX/`.

---

## 2. Architecture Binding (`FRPGBossCue` & `URPGFrameworkMoveExecutor`)

- **Struct:** `FRPGBossCue` (`Source/OneBossFight/Player/RPGBossMoveCard.h:32-42`) with `CueId`, `TimeSeconds`, `bAtHoldRelease`, `Visual` (`ERPGBossCueVisual`), `TSoftObjectPtr<USoundBase> Sound` (**must remain `nullptr` / unassigned by default**), and `Socket`.
- **Execution:** `URPGFrameworkMoveExecutor::PreloadCues()` (`Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:497-501`) synchronous-loads `C.Sound` at card start; `FireCue()` (`RPGFrameworkMoveExecutor.cpp:531-555`) enforces paired audio + flipbook visual channels (`ChannelsFor(Mode)`) and uses `None` socket for boss-feet origin or bone/socket name such as `weapon_r` / `root_weapon_end_r` (`author_sevarog_draft_cards.py:340-341`).
- **Accessibility & Silence Safety:** When `Sound` is unassigned (`nullptr`) or `-nosound` is passed, `FireCue` emits the visual cue cleanly without failing validation (`bAudio=0`).

---

## 3. Card-by-Card SFX Mapping (Disk-Verified Paths)

Timing baselines follow `TIMING` in `Scripts/Editor/author_sevarog_draft_cards.py:150-156` (`S1..S5`) and refined sheet marks in `Documentation/Boss/BB_A06_A08_SIGNATURE_MARKS_REFINED.md` (`S6..S8` candidates). Zero pack assets modified.

### 3.1 Authored Draft Move Cards (`S1..S5`, `author_sevarog_draft_cards.py`)

| Card / MoveId | Phase / Timing (s) | Cue Role | Socket | Verified SoundCue Path (On Disk) | Companion Flipbook Visual | Default Wiring State |
|---|---|---|---|---|---|---|
| `S1` (`Move_Sevarog_Swing1_Medium`) | Telegraph/Swing `0.200` (commit `0.200`, window `0.267-0.400`) | Vocal Effort | `None` (torso/feet) | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_Swing` | `DodgeDust` | `nullptr` (opt-in spec) |
| `S1` (`Move_Sevarog_Swing1_Medium`) | Swing Arc `0.267` | Weapon Whoosh | `root_weapon_end_r` | `/Game/RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_1_Cue` | `HitSpark` | `nullptr` (opt-in spec) |
| `S1` (`Move_Sevarog_Swing1_Medium`) | Contact/Impact `0.333` | Heavy Weapon Impact | `weapon_r` | `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_3_Cue` | `HitSpark` | `nullptr` (opt-in spec) |
| `S2` (`Move_Sevarog_Swing2_Medium`) | Telegraph/Swing `0.133` (commit `0.133`, window `0.200-0.400`) | Vocal Effort | `None` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_Attack` | `DodgeDust` | `nullptr` (opt-in spec) |
| `S2` (`Move_Sevarog_Swing2_Medium`) | Return Sweep `0.200` | Weapon Whoosh | `root_weapon_end_r` | `/Game/RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_2_Cue` | `HitSpark` | `nullptr` (opt-in spec) |
| `S2` (`Move_Sevarog_Swing2_Medium`) | Contact/Impact `0.267` | Heavy Weapon Impact | `weapon_r` | `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_5_Cue` | `HitSpark` | `nullptr` (opt-in spec) |
| `S3` (`Move_Sevarog_Swing3_Slow`) | Delayed Windup/Effort `0.400` (commit `0.467`, window `0.533-0.667`) | Heavy Effort Call | `None` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_Ability_Primary` | `DodgeDust` | `nullptr` (opt-in spec) |
| `S3` (`Move_Sevarog_Swing3_Slow`) | Overhead Cleave `0.500` | Heavy Hammer Whoosh | `root_weapon_end_r` | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Hammer_Swing_Cue` | `HitSpark` | `nullptr` (opt-in spec) |
| `S3` (`Move_Sevarog_Swing3_Slow`) | Ground/Target Slam `0.600` | Slam Impact | `weapon_r` | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue` | `BloodBurst` | `nullptr` (opt-in spec) |
| `S4` (`Move_Sevarog_Speedburst`) | Phantom Surge Start `0.200` (commit `0.200`, warp `0.267-0.800`) | Spectral Dash Effort | `None` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_Ability_Q` | `DodgeDust` | `nullptr` (opt-in spec) |
| `S4` (`Move_Sevarog_Speedburst`) | Gap-Close Glide `0.267` | Spectral Whoosh | `None` | `/Game/RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_5_Cue` | `DodgeDust` | `nullptr` (opt-in spec) |
| `S4` (`Move_Sevarog_Speedburst`) | Dash Deceleration `1.000` | Heavy Skid / Step | `None` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_Land` | `DodgeDust` | `nullptr` (opt-in spec) |
| `S5` (`Move_Sevarog_Swing1_FAST_v2`) | Fast Counter Effort `0.133` (commit `0.200`, window `0.267-0.333`) | Quick Counter Effort | `None` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_Swing` | `DodgeDust` | `nullptr` (opt-in spec) |
| `S5` (`Move_Sevarog_Swing1_FAST_v2`) | Snap Swoosh `0.200` | Short Air Cut | `root_weapon_end_r` | `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_1_Cue` | `HitSpark` | `nullptr` (opt-in spec) |
| `S5` (`Move_Sevarog_Swing1_FAST_v2`) | Fast Strike Hit `0.267` | Crisp Blade Impact | `weapon_r` | `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_7_Cue` | `HitSpark` | `nullptr` (opt-in spec) |

### 3.2 Signature Move Candidates (`BB-A06..A08` Timeline Baselines)

| Candidate Move | Refined Mark Window (s) | Cue Role | Socket | Verified SoundCue Path (On Disk) | Notes | Default Wiring State |
|---|---|---|---|---|---|---|
| `S6_Cand` (`Ultimate_Swing_120fps`) | Telegraph `0.533`, Cleave `0.867-1.200` | Ultimate Bellow / Effort | `None` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_Ability_Ultimate` | 360-deg windup tell; loud clear cue | `nullptr` (opt-in spec) |
| `S6_Cand` (`Ultimate_Swing_120fps`) | Cleave Sweep `0.867` | Massive Hammer/Axe Whoosh | `root_weapon_end_r` | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Axe_Swing_Cue` | Distinct low sweep weight | `nullptr` (opt-in spec) |
| `S6_Cand` (`Ultimate_Swing_120fps`) | Heavy Cleave Impact `1.000` | Heavy Signature Impact | `weapon_r` | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue` | Knockback/cleave peak | `nullptr` (opt-in spec) |
| `S7_Cand` (`Subjugation`) | Cast Peak `0.667`, Slam Release `0.733-1.133` | Cast Effort / Command | `None` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_Ability_E` | Pairs with hammer plant | `nullptr` (opt-in spec) |
| `S7_Cand` (`Subjugation`) | Ground Stamp `0.800` | Heavy Land Impact | `None` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_LandHeavy` | Ground contact transient | `nullptr` (opt-in spec) |
| `S7_Cand` (`Subjugation`) | Dark Hex Detonation `0.867` | Arcane Rupture Burst | `None` | `/Game/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/HitSounds/ExampleMagicHitCharacter_Cue` | Spectral snare cue | `nullptr` (opt-in spec) |
| `S8_Cand` (`Soul_Siphon`) | Aim Gather `0.267`, Siphon Channel `0.400-1.200` | Siphon Vocal Effort | `None` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_Ability_RMB` | Distinct from melee swings | `nullptr` (opt-in spec) |
| `S8_Cand` (`Soul_Siphon`) | Drain Pulse `0.467` | Cosmic Rift Drain Swell | `None` | `/Game/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/CosmicRift/A_Ability_CosmicRift_Cue` | Spectral drain aura bed | `nullptr` (opt-in spec) |
| `S8_Cand` (`Soul_Siphon`) | Siphon Finish `1.133` | Soul Reap Chime | `None` | `/Game/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/Replenishment/CastReplenishment_Cue` | End-of-channel completion | `nullptr` (opt-in spec) |

---

## 4. Gain, Concurrency & Contract Rules

1. **Opt-in Zero-Default Guarantee:** No C++ constructor, `URPGBossFrameworkProfile`, or `DA_Move_Sevarog_*` draft card wires these paths automatically. Every cue table field stays `nullptr` unless Lead authorizes wiring post-owner review.
2. **Parry & Ducking Priority:** Guard/deflect and parry feedback cues (`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/ShieldImpacts/ShieldImpacts_Cue` on block) duck Sevarog continuous whoosh/vocal channels cleanly via concurrency limits (`MaxCount <= 2` active attack whooshes).
3. **Contract Test:** Verified by [`test_bb_a11_sevarog_sfx_spec_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bb_a11_sevarog_sfx_spec_contract.py), checking physical `.uasset` existence on disk for every `/Game/` cue cited above and opt-in `nullptr` default compliance.
