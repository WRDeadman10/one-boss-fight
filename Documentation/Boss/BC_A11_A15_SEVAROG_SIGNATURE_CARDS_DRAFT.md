# BC-A11..A15: Sevarog Signature Cards (`S6..S8`) Data Prep & Module Gap Matrix

**Queue Lane:** `QUEUE_BC_AG` Tasks `BC-A11`, `BC-A12`, `BC-A13`, `BC-A15` (Antigravity)  
**Authority:** `Documentation/Boss/QUEUE_BC_AG.md`, `[C-1271]`  
**Contract Schema Sources:** `Source/OneBossFight/Player/RPGBossMoveCard.h:32-129`, `Source/OneBossFight/Player/RPGBossMoveCard.cpp:31-165`  
**Timeline Evidence:** `Documentation/Boss/BB_A06_A08_SIGNATURE_MARKS_REFINED.md`, `Documentation/Boss/C1239_SEVAROG_ANIMATION_INVENTORY.md`  
**Status:** SPEC-ONLY / DOC-ONLY (Zero `.uasset` creation, zero C++ edits, zero wiring)  

---

## 1. Draft Field Tables (`DA_Move_Sevarog_{Ultimate,Subjugation,SoulSiphon}`)

All three sequences exist physically on disk under `Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations/`, share `Sevarog_Skeleton` (`P_C1248_SEVAROGREADBACK`), and have `root_motion=False`. Proposed selector IDs use `S6..S8` provisional naming until Lead approves card authoring; numerical damage/cooldown/range bounds remain provisional design candidates pending PIE.

| `FRPGBossMoveCardSpec` / Profile Field | `S6` (`DA_Move_Sevarog_Ultimate_Draft`) | `S7` (`DA_Move_Sevarog_Subjugation_Draft`) | `S8` (`DA_Move_Sevarog_SoulSiphon_Draft`) | C++ Validation Bound (`RPGBossMoveCard.cpp`) |
|---|---|---|---|---|
| `Schema` | `1` | `1` | `1` | Must equal `1` (`:34`) |
| `MoveId` | `Move_Sevarog_Ultimate_Swing` | `Move_Sevarog_Subjugation` | `Move_Sevarog_Soul_Siphon` | Non-`None` (`:34`) |
| `FamilyId` | `Family_09_SignatureCleave` | `Family_10_AreaDenialHex` | `Family_11_ChannelDrain` | Non-`None` (`:34`) |
| `PhaseId` | `Phase_2` *(gate behind 60% HP)* | `Phase_1` | `Phase_2` | Non-`None` (`:34`) |
| `Skeleton` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog_Skeleton` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog_Skeleton` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog_Skeleton` | Must match anim & mesh skeleton (`:42`) |
| `Sequence` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Ultimate_Swing_120fps` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Subjugation` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Soul_Siphon` | Exactly one of `Sequence`/`Montage` (`:37`) |
| `Montage` / `SectionName` | Unset (`nullptr`) / `None` | Unset (`nullptr`) / `None` | Unset (`nullptr`) / `None` | Card executor uses dynamic sequence montage (`RPGFrameworkMoveExecutor.cpp:62-67`) |
| `SlotName` | `FullBody` | `FullBody` | `FullBody` | Non-`None`, present in skeleton/mesh slots (`:44`) |
| `bUsesRootMotion` | `false` | `false` | `false` | Validator refuses `true` (`:47`) |
| `ClipLengthSeconds` *(C1239 probe)* | `2.633` (`000-040`) | `2.867` (`000-043`) | `1.833` (`000-028`) | Must be `> 0`, finite (`:49`) |
| `PlayRate` | `1.0` | `1.0` | `1.0` | Strictly positive finite (`:48`) |
| `CommitSeconds` | `0.600` *(frame `009`)* | `0.733` *(frame `011`)* | `0.200` *(frame `003`)* | `Commit <= ActiveStart` (`:90`) |
| `ActiveStartSeconds` | `0.667` *(frame `010`)* | `0.800` *(frame `012`)* | `0.267` *(frame `004`)* | `ActiveStart < ActiveEnd` (`:90`) |
| `ActiveEndSeconds` | `0.867` *(frame `013`)* | `0.867` *(frame `013`)* | `1.267` *(frame `019`)* | `ActiveEnd <= RecoveryEnd` (`:90`) |
| `RecoveryEndSeconds` | `2.633` *(2.603 w/ 0.03s tail)* | `2.867` *(2.837 w/ 0.03s tail)* | `1.833` *(1.803 w/ 0.03s tail)* | `RecoveryEnd <= ClipLengthSeconds` (`:91`) |
| `TrackDegreesPerSecond` | `120.0` | `180.0` | `90.0` | Finite `>= 0` (`:54`) |
| `MinRangeCm` / `MaxRangeCm` | `100.0` / `320.0` | `300.0` / `900.0` | `250.0` / `750.0` | `0 <= MinRange <= MaxRange` (`:88`) |
| `FrontConeDegrees` | `360.0` *(360-deg signature cleave)* | `140.0` | `90.0` *(frontal drain cone)* | `0 <= Cone <= 360` (`:88`) |
| `MaxVerticalDeltaCm` | `0.0` | `0.0` | `0.0` | `0` = legacy/unrestricted Z (`RPGBossMoveCard.h:116`) |
| `HPDamage` *(provisional)* | `65.0` | `40.0` | `30.0` | Finite `>= 0` (`:59`) |
| `bDefensive` / `bWarpAway` | `false` / `false` | `false` / `false` | `false` / `false` | Non-defensive cards require `>= 1` direct window (`:93,160`) |
| Bounded Warp (`Start/End/MaxDist/MaxDeg/Standoff`) | `0.600` / `0.733` / `80.0` / `30.0` / `140.0` (`Ease=false`) | `0/0/0/0/0` (off — planted ground cast) | `0/0/0/0/0` (off — stationary drain) | `Commit <= WarpStart < WarpEnd <= ActiveEnd`; max `1000 cm`, `180°` (`:65-66`) |
| Primary Window (`SocketA`/`SocketB`/`RadiusCm` or `bRing`) | Direct blade window: `Window_Ultimate_Swing`, `HitGroup_ScytheBlade`, `weapon_r` -> `root_weapon_end_r`, `RadiusCm = 35.0`, `0.667–0.867 s` | *(Gap — see §3)* Temporary validator-safe anchor only if radial ring around boss: `bRing=true`, `RingStartRadiusCm=120`, `RingSpeed=800`, `RingThickness=120`, `RingHeight=60` | *(Gap — see §3)* No swept scythe weapon blade contact; needs dedicated channel add-on module | Blade needs `SocketA != SocketB`, `RadiusCm > 0`; Ring cannot have sockets/baked samples (`:116-140`) |
| `Cues` | **`[]` (empty by default)** | **`[]` (empty by default)** | **`[]` (empty by default)** | See §2 opt-in `FRPGBossCue` finding (`:82-86`) |

---

## 2. Critical C++ Validation Finding on `Cues` (`RPGBossMoveCard.cpp:75-86`)

Inspection of `RPGBossMoveCard.cpp:82-86` shows two strict rules whenever `Spec.Cues` is **non-empty**:
1. `C.CueId.IsNone() || C.Visual == ERPGBossCueVisual::None || C.Sound.IsNull()` -> **FAILS** `MoveCard.Cue` (`id, visual and sound are all required`). You **cannot** serialize an `FRPGBossCue` element with `Sound = nullptr` and expect `RPGBossMoveCards::Validate` to accept the card.
2. `RPGBossCue::DistinctChannels(Keys)` (`:86`) refuses repeated cue IDs OR any two cues on the same card sharing the same `Visual` (`ERPGBossCueVisual` currently exposes only 3 non-`None` values: `HitSpark`, `DodgeDust`, `BloodBurst`) OR the same `Sound`!
- **Drafting Rule (`BB-A11..A13` + `BC-A14`):** Draft card specs must leave **`Cues = []` (empty)** by default (keeping SFX opt-in/unwired without failing validation). When Lead wires SFX after Owner reel picks, each card can carry at most 3 distinct `(Visual, Sound)` `FRPGBossCue` rows unless `ERPGBossCueVisual` is extended.

---

## 3. Module Gap Matrix vs Shared `FRPGBossMoveCardSpec` (`BC-A15`)

| Card / Mechanic | What Shared `FRPGBossMoveCardSpec` + `URPGFrameworkMoveExecutor` Already Handles | Required Custom / Add-On Module Gaps (Not in Shared Card Validator/Executor) | Recommended Engineering Path (C-1177) |
|---|---|---|---|
| **`S6` `Ultimate_Swing_120fps`** (`360°` Signature Cleave) | - `FrontConeDegrees = 360.0` accepted (`RPGBossMoveCard.cpp:88`)<br>- Swept scythe blade window `weapon_r -> root_weapon_end_r` (`0.667–0.867 s`)<br>- Optional secondary ground shockwave ring (`bSecondary=true, bRing=true` sharing `HitGroup_ScytheBlade` dedupe so target takes direct hit only on overlap, `:56-63`)<br>- Bounded step-in warp (`0.600–0.733 s`) & Phase-2 eligibility gate (`Phase_2`) | - Custom radial knockback impulse / physics launch stronger than standard hit reaction *(optional)* | **Pure data card first** (direct blade + optional secondary shockwave ring); add knockback module only if Owner/Lead requests physics launch |
| **`S7` `Subjugation`** (Ranged Ground Hex + Snare) | - `bRing=true` ground expanding wave centered on the **boss** (`RingStartRadiusCm`, `RingSpeedCmPerSecond`, `RingThicknessCm`, `RingHeightCm`, jump-clearable, `:116-123`) | 1. **Target-Positioned AoE Spawn:** `bRing` radiates around boss root, NOT at the player's targeted ground coordinate (`300–900 cm` away)<br>2. **Root / Snare Effect:** No debuff/movement-lock `GameplayEffect` or `Status.Snared` duration field in `FRPGBossMoveCardSpec`<br>3. **Pre-Release Interruption Cancel:** Telegraph cancel hook if staggered before frame `012` (`0.800 s`) *(handled by card abort if ground decal spawns only at active start)* | Reuse `C1239_SEVAROG_DEFINITION_DATA_PLAN.md` item 2: author a small reusable `UPersistentTargetHex` / ground-rune add-on module triggered on card active window open |
| **`S8` `Soul_Siphon`** (Frontal Channel Drain + Self-Heal) | - Pose/animation playback (`Soul_Siphon` `1.833 s`) and frontal eligibility check (`FrontConeDegrees=90.0`, `Min/MaxRangeCm`) | 1. **Continuous Channel Ticks:** Single `HitGroup` deduplicates to 1 damage event per activation (`RPGFrameworkMoveExecutor`); cannot tick drain over `0.267–1.267 s`<br>2. **Frontal Cone Volume Test:** Needs cone-trace / line-of-sight channel check instead of `weapon_r` blade capsule<br>3. **Boss Self-Heal Transfer:** No `HealBossFraction` / health siphon transfer inside `URPGDamageResolver`<br>4. **Stagger/LOS Break:** Needs channel cancel condition if player leaves cone/LOS or staggers Sevarog | Reuse `C1239_SEVAROG_DEFINITION_DATA_PLAN.md` item 4: dedicated `SoulSiphon` special-attack module; never repurpose `RPGBossBleed` (`C1239` rule) |

*Companion Offline Contract Test:* [`test_bc_a14_sevarog_signature_cards_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bc_a14_sevarog_signature_cards_contract.py).
