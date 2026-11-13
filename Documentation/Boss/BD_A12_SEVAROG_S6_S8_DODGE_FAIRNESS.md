# BD-A12 & Batch 3 (`BD-A11..BD-A15`): Sevarog `S6–S8` Timing & Dodge Fairness Audit

**Authority:** [`QUEUE_BD_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BD_AG.md), `[X-1872]` (`0` commits made, `0` push, `0` editor calls)  
**Baseline Player Mobility Inputs (`SWITCH_PLAN.md`, `C-1284` Mannequin Ref):**
- Directional Quick Roll (`single-tap`): `215–290 cm` (`243.6–253.8 cm` in `P_C1282_GREYSTONE_RM3_MANNEQUIN`)
- Neutral Backstep: `84–98 cm` measure-to-rest (`72.1–80.4 cm` / `76.3 cm` mean at montage end)
- Capsule Radius: `42 cm` player (`Sevarog` selector/AreaEffect target clearance)

---

## 1. Batch 3 Status Matrix (`BD-A11..BD-A15`)

| ID | Task | Status | Disposition / Missing Input |
|---|---|---|---|
| `BD-A11` | Frame-cite Lead live PIE visual capture sheets for `S6`, `S7`, `S8` | **`BLOCKED`** | Lead live PIE capture sheets not yet generated (`[X-1864]` pending `[C-1286]` PIE). |
| `BD-A12` | Audit `S6`, `S7`, `S8` theoretical telegraph readability & dodge fairness vs `215–290 cm` roll | **COMPLETE** | Geometric & timing counterplay table verified below (`BD_A12`); live PIE check remains open. |
| `BD-A13` | Draft post-PIE tuning delta table (`S1–S8`) | **`BLOCKED`** | Depends on `BD-A11` & Lead live PIE (`BD-A08`). |
| `BD-A14` | Update offline `S1–S8` fairness & geometry contract suite | **COMPLETE** | [`test_bd_a14_sevarog_s1_s8_fairness_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bd_a14_sevarog_s1_s8_fairness_contract.py). |
| `BD-A15` | Prepare Owner-ready Batch 3 file manifest (`0` commits made) | **COMPLETE** | Section 3 below. |

---

## 2. `BD-A12` Analytical Counterplay & Dodge-Fairness Audit (`S6–S8`)

| Card | Windup / Telegraph Duration | Active Hazard Geometry | Counterplay Clearance vs Player Kit | Analytical Verdict *(Pre-PIE)* |
|---|---|---|---|---|
| **`S6` `Ultimate_Swing_120fps`** (`90–150 cm`, `360°`, `65.0` dmg) | `0.600 s` clear overhead hammer coil (`Frame 009`) before `0.667–0.900 s` sweep | `150 cm` max selector reach (plus hammer/capsule sweep); `0.233 s` single continuous cleave (`1` hit) | **Out-spacing or Block/Dodge:** At `120 cm` neutral engagement, a backward quick roll (`215–290 cm`) clears `335–410 cm`, safely outside `150 + 42 = 192 cm`; `0.600 s` windup gives clear react-block/i-frame entry (`0.323 s` backstep i-frame covers the entire `0.233 s` cleave). | **FAIR** — high `65` HP risk cleanly counterbalanced by `0.600 s` tell & tight `150 cm` radial envelope |
| **`S7` `Subjugation`** (`300–900 cm`, `AreaEffect`) | `0.800 s` cast (`Commit 0.733`) + **`0.750 s` ground-ring detonation delay** (`1.550 s` resolve) | Snapshots target ground at `0.800 s`; detonates in `225 cm` radius (`225 + 42 = 267 cm` effective edge) | **Directional Roll Exit:** `215–290 cm` quick roll from dead-center leaves `48 cm` headroom (`267` vs `290 cm` max) even with `0` walk lead, and any `0.25 s` lateral run + roll moves `> 300 cm` before `0.750 s` expires. | **FAIR** — `0.750 s` delay cleanly rewards single-tap directional roll instead of tanking `35` dmg + `2.5 s` `0.55x` snare |
| **`S8` `Soul_Siphon`** (`220–620 cm`, `ChannelDrain`) | `0.200 s` commit; heading locks at `0.267 s` (`bTrackFacingEachTick = false`); first tick fires at **`0.467 s`** | `650 cm` cone range, `45°` half-angle (`90°` full cone); `5` ticks (`0.200 s` apart) | **Lateral Cone Escape:** Even at `300 cm` midrange, half-width of the locked `45°` cone is `300 * tan(45°) = 300 cm` (and `220 cm` at close `220 cm`). A `215–290 cm` lateral roll exits the `45°` cone before/between early ticks, capping loss to `0–16` HP (saving boss `12–20` HP heal) and opening `1.267–1.803 s` (`0.536 s`) rear punish. | **FAIR** — locked `facingYaw` makes lateral dodge decisive while keeping punishment mild (`8` dmg / tick) on late reaction |

---

## 3. Owner-Ready Batch 3 File Manifest (`BD-A15`)

Antigravity deliverables ready for Owner review/commit (`0` commits made per `[X-1872]`):
- `Documentation/Boss/BD_A12_SEVAROG_S6_S8_DODGE_FAIRNESS.md`
- `Scripts/Tools/test_bd_a14_sevarog_s1_s8_fairness_contract.py`
