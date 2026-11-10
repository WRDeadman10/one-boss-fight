# C-1276a / b / c: Sevarog `S6` Reconciliation, Provisional `S7`/`S8` Values & Phase Plan

**Authority:** Claude Lead Directive `[C-1276]` (`2026-11-10`)  
**Owner:** Antigravity  
**Status:** **PROVISIONAL — TUNE AFTER PIE** (Design/audit spec + offline validator contract; zero `.uasset` edits, zero C++ edits; unblocks Codex `X26` upon Lead approval)  

---

## 1. `C-1276a`: `S6` (`Ultimate_Swing_120fps`) Timing Reconciliation

Cross-checked `D:/FightVideo/sevarog_frames/_sheets/Ultimate_Swing_120fps_sheet.png` and individual `15 Hz` high-res frames `Ultimate_Swing_120fps_{009..015}` against `PROBE_DERIVED_TIMINGS.md:39` (`2664.93 cm/s` peak @ `0.7083 s`, 50% speed windows `#1 [0.6583, 0.7833]` & `#2 [0.8333, 0.9167]`) and `BB_X11_X15_SEVAROG_DESIGN.md`:

| Frame (`15 Hz`) | Montage Time (`s`) | Direct Visual Observation (`D:/FightVideo/.../Ultimate_Swing_120fps_*.png`) | Velocity Probe State (`PROBE_DERIVED_TIMINGS.md:39`) |
|---|---:|---|---|
| `009` | `0.600` | Hammer shaft raised upright overhead on right shoulder; torso coiled back; left claw extended horizontally left. **Commit / Windup Peak.** | Pre-acceleration |
| `010` | `0.667` | Right arm drives hammer rapidly downward-right (`torso turning into sweep`). | **Burst #1 (`0.6583–0.7833 s`)** active (`v_peak = 0.7083 s`) |
| `011` | `0.733` | Arm horizontally extended downward-right at hip/thigh level (`hammer sweeping lowest right-front arc`). | Burst #1 decel tail |
| **`012`** | **`0.800`** | **Torso mid-360° spin directly facing away/left; hammer head passes lowest dead-center front arc between shins.** Rotation transfers momentarily from tip extension to waist pivot. | **`50 ms` velocity dip (`0.7833 -> 0.8333 s`)** between 50% speed bursts |
| `013` | `0.867` | Hammer whips out **forward-left & upward at chest/shoulder height** (`hammer head bright green upper-left`), completing the continuous front cleave arc. | **Burst #2 (`0.8333–0.9167 s`)** |
| `014` | `0.933` | Hammer has exited **overhead above left shoulder** (`follow-through open chest pose 014–023`). | Post-strike overhead carry |

### Reconciliation Decision (`C-1276a`): **ONE Continuous 360° Cleave (`0.667–0.900 s`), Single `HitGroup`**
1. Visually (`010 -> 011 -> 012 -> 013`), `Ultimate_Swing_120fps` is **one continuous 360-degree tornado cleave**, NOT two separate attacks. The probe's two `50%` speed intervals reflect the tip briefly pivoting across the dead-center low front apex at `Frame 012` (`0.800 s`) for only `50 ms` (`0.7833–0.8333 s`).
2. Cutting out `0.783–0.833 s` would drop coverage right at `Frame 012` when the hammer passes straight through front center.
3. **Recommended Window (`[provisional, tune after PIE]`):**
   - `CommitSeconds = 0.600` (`Frame 009`)
   - Single continuous blade window: `ActiveStartSeconds = 0.667`, `ActiveEndSeconds = 0.900` (covers `Burst #1` + `012` front pivot + `Burst #2` before overhead exit `014 = 0.933 s`, extending `C-1242`'s `0.867 s` by `33 ms`) under **one `HitGroup_ScytheBlade`** (`1` max hit per activation; optional secondary shockwave ring can share `HitGroup_ScytheBlade`).
   - `RecoveryEndSeconds = 2.603` (`2.633333 s` clip minus `0.03 s` profile blend tail).
   - `FrontConeDegrees = 360.0`, `MinRangeCm = 90.0`, `MaxRangeCm = 150.0` *(corrected per `[C-1277]`: live hammer reach is ~120–130 cm and `S6` has no warp, so `260 cm` was unsupported)*, **`HPDamage = 65.0`** *(provisional, tune after PIE — flagship Phase-2 Ult sitting above `S3` heavy slam `55.0`)*.

---

## 2. `C-1276b`: Provisional `S7` (`Subjugation`) & `S8` (`Soul_Siphon`) Values (For `X26`)

Baseline reference values (`Docs/BossCombatReview/Execution/Antigravity/MoveCards/move_cards_f5_set.json`, `DECISIONS.md:483`):
- `S1` / `S2` / `S5` (`Swing1_Medium` / `Swing2_Medium`): **`HPDamage = 25.0`** (`Cooldown = 1.0 s`)
- `S3` (`Swing3_Slow` Heavy Slam): **`HPDamage = 55.0`** (`Cooldown = 3.5 s`)
- Standard duel arena player HP: `120.0` (proof harness target: `800.0`).
- **Notice:** All numerical values below are marked **`provisional, tune after PIE`** and satisfy all C++ validator rules in `RPGBossMoveCard.h:72-103` & `RPGBossMoveCard.cpp:61-91`.

### 2.1 `S7`: `Move_Sevarog_Subjugation` (`FRPGBossAreaEffect`, Effect-Only Card)

| Field | Proposed Value *(provisional, tune after PIE)* | C++ Contract / Design Justification (`RPGBossMoveCard.cpp:61-75`) |
|---|---|---|
| `CommitSeconds` | `0.733` | `Frame 011` (`BB_A06_A08`) |
| `ActiveStartSeconds` / `ActiveEndSeconds` | `0.800` / `0.867` | `C-1242` Subjugation release window (`Frame 012–013`); `Commit <= ActiveStart < ActiveEnd` |
| `RecoveryEndSeconds` | `2.836` | `2.866667 s` probe clip minus `0.03 s` blend tail |
| `AreaEffect.bEnabled` | `true` | Effect-only spell card (`Windows = []`, `:125`) |
| `AreaEffect.ReleaseSeconds` | `0.800` | Snapshots target's ground location at hammer stamp (`>= CommitSeconds 0.733`) |
| `AreaEffect.DelaySeconds` | `0.750` | `0.75 s` clear ground-ring telegraph before detonation (`<= 10.0 s`; `0.800 + 0.750 = 1.550 <= 2.836`) — dodgeable via `0.30 s` quick roll (`215–290 cm`) |
| `AreaEffect.RadiusCm` | `225.0` | `4.5 m` diameter AoE (`0 < 225 <= 2000`; comfortably clears capsule radius `42 cm`, demands directional roll to exit) |
| `AreaEffect.Damage` | **`35.0`** *(provisional)* | Sits proportionally **between `S5` swing (`25.0`) and `S3` heavy slam (`55.0`)** (matches `SwingSlow` `35.0`), balanced for added snare crowd-control (`~29%` of `120 HP`) |
| `AreaEffect.SnareSeconds` | `2.50` | Brief root/slow punish (`0 < 2.50 <= 30.0`) |
| `AreaEffect.SnareSpeedScale` | `0.55` | `45%` movement speed reduction (`0 < 0.55 < 1.0`, valid per `:72-73`) |
| `MinRangeCm` / `MaxRangeCm` | `300.0` / `900.0` | Mid-to-ranged opener band (`0 <= Min <= Max`) |
| `FrontConeDegrees` / `CooldownSeconds` | `140.0` / `8.0` | Allows tracking setup without overlapping melee combos |

### 2.2 `S8`: `Move_Sevarog_Soul_Siphon` (`FRPGBossChannelDrain`, Effect-Only Card)

| Field | Proposed Value *(provisional, tune after PIE)* | C++ Contract / Design Justification (`RPGBossMoveCard.cpp:76-91`) |
|---|---|---|
| `CommitSeconds` | `0.200` | `Frame 003` (`BB_A06_A08`) |
| `ActiveStartSeconds` / `ActiveEndSeconds` | `0.267` / `1.267` | `C-1242` `1.00 s` frontal drain pose (`Frames 004–019`) |
| `RecoveryEndSeconds` | `1.803` | `1.833333 s` probe clip minus `0.03 s` blend tail |
| `ChannelDrain.bEnabled` | `true` | Channel-only spell card (`Windows = []`, `AreaEffect.bEnabled = false`) |
| `ChannelDrain.StartSeconds` | `0.267` | `>= CommitSeconds 0.200` |
| `ChannelDrain.EndSeconds` | `1.267` | `<= RecoveryEndSeconds 1.803` |
| `ChannelDrain.TickIntervalSeconds` | `0.250` | Produces **`5` deterministic ticks** (`0.267, 0.517, 0.767, 1.017, 1.267`; `1 <= 5 <= 64`) |
| `ChannelDrain.TickDamage` | **`8.0`** *(provisional)* | **`5 x 8.0 = 40.0` max channel total** (between `S5` `25.0` and `S3` `55.0`), while escaping after 1–2 ticks costs only `8.0–16.0` HP |
| `ChannelDrain.HealFraction` | `0.50` | Heals `50%` of actual `HPApplied` (max `20.0` boss HP if all `5` ticks connect; `0` on dodge/block/invulnerable; `0 <= 0.50 <= 1.0`) |
| `ChannelDrain.ConeRangeCm` | `650.0` | Mid-range frontal cone (`0 < 650 <= 2000`) |
| `ChannelDrain.ConeHalfAngleDegrees` | `45.0` | Total `90°` frontal cone (`0 < 45 <= 180`), escapable via side quick roll |
| `ChannelDrain.bTrackFacingEachTick` | `false` | Locks heading at channel start (matches stationary pose `004–019`, rewarding side/rear punish during `1.267–1.803 s` recovery) |
| `MinRangeCm` / `MaxRangeCm` | `220.0` / `620.0` | Fits cleanly inside `650.0` cone reach (`30 cm` interior safety margin) |
| `FrontConeDegrees` / `CooldownSeconds` | `90.0` / `10.0` | Reserved Phase-2 pressure spell |

---

## 3. `C-1276c` / `[C-1277]`: Sevarog Phase Plan Table (`S1–S8`, Consistent with `X14`)

Per `BB_X11_X15_SEVAROG_DESIGN.md` (`X14`, `RPGBossFrameworkProfile.cpp:218-226`, `RPGBossMoveModel::IsEligible`) and Lead verdict `[C-1277]`:
- **Canonical Pool Rule (`[C-1277]`):**
  - `Phase_1`: `S1`, `S2`, `S3`, `S4->S5`, `S7` (`5` eligible cards)
  - `Phase_2` (`<= 60%` HP): keeps `Phase_1` cards (`S1`, `S2`, `S3`, `S4->S5`, `S7` — shared same card assets if selector supports multi-phase eligibility, preserving `>= AttackCount=3` anti-starvation without `_P2` duplicate cards unless Codex confirms single-phase-only `file:line`) and **unlocks `S6` and `S8`** (`7` eligible cards in `Phase_2`).

| Card | Sequence | Phase Availability (`[C-1277]`) | Role | Provis. Damage | Provis. Cooldown (`s`) | Selector Range (`cm`) | Notes / Source |
|---|---|---|---|---:|---:|---:|---|
| **`S1`** (`Move_Sevarog_Swing1_Medium`) | `Swing1_Medium` | **`Phase_1` + `Phase_2`** | Close left-to-right sweep (opener) | `25.0` | `1.0` | `90–120` *(C-1274)* | Core close pressure |
| **`S2`** (`Move_Sevarog_Swing2_Medium`) | `Swing2_Medium` | **`Phase_1` + `Phase_2`** | Close cross-body return sweep | `25.0` | `1.0` | `90–120` *(C-1274)* | Core close pressure |
| **`S3`** (`Move_Sevarog_Swing3_Slow`) | `Swing3_Slow` | **`Phase_1` + `Phase_2`** | Delayed heavy overhead slam | `55.0` | `3.5` | `90–180` | High-punish heavy (`+0.603 s`) |
| **`S4`** (`Move_Sevarog_Speedburst`) + `S5` combo | `Speedburst` -> `Swing1_Medium` | **`Phase_1` + `Phase_2`** | `3.0–6.5 m` forward dash (`0` dmg) + whiff cleave (`25.0`) | `0` / `25.0` | `4.0` | `300–650` | Gap closer (`S4->S5` depth 2) |
| **`S7`** (`Move_Sevarog_Subjugation`) | `Subjugation` | **`Phase_1` + `Phase_2`** | Ranged delayed ground AoE + snare (`AreaEffect`) | **`35.0`** | `8.0` | `300–900` | Anti-kiting mid/far hex (`C-1276b`) |
| **`S6`** (`Move_Sevarog_Ultimate_Swing`) | `Ultimate_Swing_120fps` | **`Phase_2` (`<= 60%` HP)** | **360° Signature Cleave** (`0.667–0.900 s`, `HitGroup_ScytheBlade`) | **`65.0`** | `12.0` | **`90–150`** *(C-1277)* | No warp; live hammer reach `~120–130 cm` |
| **`S8`** (`Move_Sevarog_Soul_Siphon`) | `Soul_Siphon` | **`Phase_2` (`<= 60%` HP)** | **Frontal Channel Drain + Self-Heal** (`ChannelDrain`) | **`8.0 x 5`** | `10.0` | `220–620` | Frontal `45°` half-angle drain (`C-1276b`) |

*Companion Contract Verification:* [`test_c1276_sevarog_s6_s8_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_c1276_sevarog_s6_s8_contract.py).
