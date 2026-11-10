# BC-A06..A09: Sevarog `C-1265b` Full-Clip Trace vs Frame Sheet Cross-Check (`S1`, `S2`)

**Queue Lane:** `QUEUE_BC_AG` Tasks `BC-A06`, `BC-A07`, `BC-A08`, `BC-A09` (Antigravity)  
**Unblocked By:** `[X-1821]` (`Docs/BossCombatReview/Execution/Codex/C1269_X03_TRACE/`)  
**Sources Cross-Checked:**
- Live trace log: `Docs/BossCombatReview/Execution/Codex/C1269_X03_TRACE/pie_clip_trace.log` (`REQUESTED_RANGE_CM=140`, `Swing1` 20 samples, `Swing2` 37 samples)
- Status receipt: `Docs/BossCombatReview/Execution/Codex/C1269_X03_TRACE/pie_clip_trace_status.txt` (`MAP_SAVED=0`)
- Visual trajectory: `Documentation/Boss/C1265C_SEVAROG_SWING1_SWING2_FRAME_CROSSCHECK.md`
- Card config: `Scripts/Editor/author_sevarog_draft_cards.py:150-156, 335-347` (`RadiusCm=15.0`, `weapon_r -> root_weapon_end_r`, `Band 90..180 cm`)

---

## 1. `Swing2_Medium` (`37` Samples, Full Window Coverage)

At `140 cm` horizontal distance (`bossYaw=180.00`, `capsuleCenter=(-1780, 0, 98.15)`, `capsuleRadius=42.0 cm`, `capsuleHalfHeight=96.0 cm`), `Swing2_Medium` sampled cleanly every `~20 ms` across `[0.02236, 1.07377] s`:

| `localSeconds` | Frame Log # | `weapon_r` Surface Dist (cm) | `root_weapon_end_r` Surface Dist (cm) | World `X` of `weapon_r` | Physical & Visual Cross-Check (`C1265C`) |
|---:|---:|---:|---:|---:|---|
| `0.18783` | `27` | `122.71` | `64.94` | `-1651.9` | Pre-window approach from overhead windup |
| **`0.20635`** | `28` | `66.46` | **`45.42` *(tip closest)*** | `-1703.6` | Window open (`0.200 s`) — shaft enters front sweep arc |
| **`0.22903`** | `29` | **`37.02` *(head closest)*** | `94.28` | **`-1742.4`** | **Peak closest pass (`37.022 cm` > `RadiusCm=15.0 cm`):** hammer head passes `37.6 cm` from player center but `68.5 cm` right (`Y=-68.5`) & high (`Z=164.3`), missing by `22.02 cm` |
| `0.25057` | `30` | `115.64` | `141.35` | `-1696.1` | Already sweeping back away from `-1780` |
| `0.29864` | `32` | `230.66` | `189.96` | `-1566.2` | Behind/right follow-through |
| `0.39288` | `35` | `265.86` | `201.40` | `-1485.5` | Window close (`0.400 s`) — `> 200 cm` clear of target |
| `0.518..1.074` | `40..56` | `236.2 -> 175.3` | `198.1 -> 178.7` | `-1508 -> -1570` | Recovery settling back to neutral stance |

**Diagnostic Findings for `Swing2_Medium` (`X04` input):**
1. **Why `140 cm` Missed (`22.02 cm` gap):** The true closest contact envelope occurs early (`0.200–0.240 s`, peaking at `0.229 s`, **`37.022 cm`** surface distance vs `15.0 cm` trace radius). From `0.251 s` onward, the hammer already recedes (`115 -> 266 cm`).
2. **Coordinate Orientation Clarified:** `C1265C` noted Sevarog's torso rotates relative to the side/front capture camera during `Swing2`. The live world-`X` telemetry proves `t = 0.206–0.229 s` (`frame 3` window entry) is the true forward extension (`X = -1742.4`), whereas by `t = 0.345–0.408 s` the swing is back at `X = -1511` to `-1483`.
3. **Actionable Tuning Envelope (`X04`):** With `RadiusCm = 15.0`, hit requires closing `~22–25 cm` closer (`MaxRangeCm ~ 105–115 cm`), **OR** keeping `~130–140 cm` with `RadiusCm >= 40 cm` (note: tightening `MaxRangeCm <= 120 cm` matches `S5` connecting at `120 cm` in `BUILD-295`). Keep `ActiveStartSeconds = 0.200 s`; consider tightening `ActiveEndSeconds` from `0.400 s` toward `0.267–0.300 s` since `0.30–0.40 s` is completely out of reach (`> 190 cm`).

---

## 2. `Swing1_Medium` (`20` Samples — **`0.247 s` Active-Window Tick Gap** Flagged)

| `localSeconds` | Frame Log # | `weapon_r` Surface Dist (cm) | `root_weapon_end_r` Surface Dist (cm) | Observation |
|---:|---:|---:|---:|---|
| `0.21140` | `0` | **`163.20`** | **`106.11`** | Pre-window sample just past commit (`0.200 s`) |
| **`0.267..0.400`** | *(NONE)* | *(no Python sample)* | *(no Python sample)* | **`247.3 ms` PIE frame jump (`0.2114 -> 0.4587 s`) skipped ALL active-window Python samples** (`Sweep` ran C++ `tipDistanceCm=67.03`, `0` hits at `140 cm`) |
| `0.45873` | `1` | `186.72` | `120.29` | Immediately post-window recovery; matches `C1265C` Frame 7 rising forward-right |
| `0.527..1.084` | `2..19` | `194.0 -> 229.4` | `129.8 -> 197.7` | Rising/settling monotonically away from capsule |

**Critical Gap Flagged for `X04`:**
- Even though `Swing1_Medium` logged `FULL_CLIP=True` (`maxLocalSeconds=1.08425`), the `0.247 s` frame gap between `frame=0` (`0.21140 s`) and `frame=1` (`0.45873 s`) means **zero Python trace coordinates exist inside `Swing1_Medium`'s entire `[0.267, 0.400]` active window**.
- Meanwhile, `BUILD-295` (`P_C1265_SEVAROGLIVE4`) proved `S5` (`Move_Sevarog_Swing1_Medium`) **HIT for 25 dmg at `120 cm`** standoff (`<= 120 cm`).
- **Recommendation before locking `X04`:** Re-run or capture `Swing1_Medium` with fixed frame rate (`SetFixedFrameRate(60)` or `<= 0.05 s` max step assertion) at both `120 cm` and `130–140 cm` so `closest_root_weapon_end_r_cm` inside `[0.267, 0.400]` is directly measured, not inferred past the `247 ms` skip!

---

## 3. Contract Verification (`BC-A09`)

Companion offline test [`test_bc_a09_sevarog_window_bounds_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bc_a09_sevarog_window_bounds_contract.py) asserts across all `S1..S5` (`author_sevarog_draft_cards.py`) and `S6..S8` (`BC_A11_A15_SEVAROG_SIGNATURE_CARDS_DRAFT.md`) cards:
1. `0 <= Commit <= ActiveStart < ActiveEnd <= RecoveryEnd <= ClipLengthSeconds`
2. Positive-budget warps satisfy `Commit <= WarpStart < WarpEnd <= ActiveEnd`
3. Range/cone ordering (`0 <= MinRange <= MaxRange`, `0 < FrontCone <= 360`) and `PlayRate > 0`.
