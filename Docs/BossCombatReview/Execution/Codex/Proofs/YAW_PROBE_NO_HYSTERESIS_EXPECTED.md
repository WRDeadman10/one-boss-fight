# Yaw probe without cone hysteresis: expected trace

Control profile has `ConeHysteresisDegrees=0`; drive `rpg.BossProofYawProbe 5`. The probe is deterministic: `yaw[i] = center + 5*sin(2πi/24)` where `center` is half the first candidate's authored front-cone angle (`RPGFrameworkBossCharacter.cpp:430–436`; `RPGBossYawProbeRules.h`). Existing sample 0 is 45°, so the current fixture's center/boundary is 45°.

For a bounded full-cycle run, set the same attack count to 24 in both A/B profiles and keep the same target/range/phase. The exact crossing samples around the boundary are:

| Sample | Yaw | Expected relation to 45° boundary |
|---:|---:|---|
| 11 | 46.2941° | outside |
| 12 | 45.0000° | boundary; inclusive cone check |
| 13 | 43.7059° | inside |
| 14 | 42.5000° | inside |
| 23 | 43.7059° | inside |
| 24 | 45.0000° | boundary on next cycle |
| 25 | 46.2941° | outside again |

Because the no-hysteresis branch resets `ConeInside` and gives every model snapshot zero slack (`RPGFrameworkBossMoveSelector.cpp:44–47`), each unchanged candidate must use only its authored cone boundary: samples 12–24 are at or inside 45°; at sample 25 it is outside again and refused as `MoveModel.Cone`. Compare the same candidate across samples, not whichever candidate happens to win the weighted selector.

Required bounded evidence: 26 sequential `yaw_probe` samples (indices 0–25), the raw candidate/refusal/decision rows for one named candidate, and no claim of edge flicker from only the first two samples. Current R5 control logs show only samples 0 and 1; they are insufficient to demonstrate a complete boundary crossing.

## Setup
## Control
## PASS
## FAIL
