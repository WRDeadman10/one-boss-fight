# 16 — Debug Views, Automated Tests, Telemetry, Profiling

## Build debug tools before adding difficult AI

An unexplainable boss cannot be balanced reliably. The debugging interface should show *why* the boss attacked, *why* the hit connected, and *why* player retaliation succeeded or failed.

## Debug overlay: always-readable

```text
ASHEN BELLWARDEN | Phase 2 | HP 44% | Posture 56/100
MODE: Attack | State: Committed | Instance: 175 | ComboDepth: 2
TARGET: 285 cm | SignedYaw: +39deg | LOS: yes | Player: Rolling
ATTACK: A02 Crescent Sweep | Section: SlashA | MontagePos: 0.71s
TRACKING: locked at 0.50s | Rotation cap 12 deg/sec
HIT WINDOW: Sweep01 OPEN | Victims Hit: 0
NEXT GATE: Branch01 at 0.97s
LAST CHOICE: A02=0.78, A01=0.64, A05=REJECT(RearAngle)
PRESSURE: 41/100 | REACTION CD: 1.7s | REGULAR COMBO CD: 0.6s
```

Allow debug toggles by category, e.g. `Boss.Debug.Decisions`, `Boss.Debug.Traces`, `Boss.Debug.Timing`, `Boss.Debug.Navigation`, `Boss.Debug.Cooldowns`. Names are example user-defined commands, not built-in UE console commands.

## Key event schema

```json
{"encounter_id":"test_seed_123", "t":11.253, "type":"decision", "distance_cm":282, "yaw_deg":40, "gate":"Neutral", "chosen":"A02", "candidates":[{"id":"A02","score":0.78},{"id":"A01","score":0.64}]}
{"encounter_id":"test_seed_123", "t":11.753, "type":"attack_commit", "attack":"A02", "instance":175, "rotation_cap_deg_s":12}
{"encounter_id":"test_seed_123", "t":11.943, "type":"hit_window_open", "attack":"A02", "instance":175, "window":"Sweep01"}
{"encounter_id":"test_seed_123", "t":12.013, "type":"contact", "attack":"A02", "instance":175, "victim":"Player", "damage_applied":0, "reason":"DodgeIFrames"}
{"encounter_id":"test_seed_123", "t":12.221, "type":"combo_gate", "attack":"A02", "chosen":"Recovery", "reason":"OutOfFollowupRange"}
```

## Test matrix

`../tests/qa_scenarios.csv` contains concrete pass/fail scenarios. Mandatory tests cover:

- 0°, 45°, 100°, 170° target positions around boss.
- Player move behind during *early* wind-up vs *after* commit.
- Player dodge during early, middle, last frames of active window.
- 30/60/120 FPS; high animation play rate; hitstop; latency simulated if networking.
- Attack interrupted at first active frame; montage blend-out; hit window no longer exists.
- Two simultaneous overlapping weapon collision samples resolve one logical hit.
- Phase trigger mid-swing; attack graph remains legal.
- Player heals beyond sight; no impossible counter.
- Boss near edge, wall, staircase and moving ramp.
- QA for slow player weapon startup and shortened recoveries.

## Analytics for balancing

| Metric | What it diagnoses |
|---|---|
| `UseRate(Axx)` | Dead attacks vs spam |
| `HitRatePerAttackAndRange` | Geometry, timing and fairness |
| `UnpunishableDuration` | Excessive aggression / no recovery |
| `DamageBeforeReadableCue` | Broken telegraph sync |
| `RepeatSameFamilyPct` | Low move variety |
| `CommitRotationOvershootDeg` | Midair tracking cheating |
| `PlayerDeathsWithin0_3sOfPunishAttempt` | Fake openings |
| `NoEligibleAttackEvents` | Bad attack coverage / gates |
| `HitTraceTunnelingEvents` | Collision update too sparse |
| `ArenaWallClips` | Bad movement/warp targets |

## Tools

- **AI Debugging / Gameplay Debugger:** inspect BT, perception, nav and selected actors.
- **Visual Logger:** store position and diagnostic records spatially.
- **Rewind Debugger:** replay montage/animation state transitions around bugs.
- **Animation Insights:** inspect montage and animation evaluation costs.
- **Unreal Insights:** frame timing, events, long trace/game thread spikes.
- **Automation Tests:** write gameplay functional tests for collision once/iframes and interrupted montage cleanup.

## Performance

Aim for low-frequency utility reevaluation at neutral/branch gates; don't evaluate full list every frame. Bound sweep sample count (e.g., 4–8 blade locations plus adaptive substeps) and query only active windows. Pool cosmetic effects. Precache montages/FX before arena entry. Profile in packaged builds as well as PIE.

## Reproducibility

Record RNG seed, starting positions, player activity script, game time, phase and attack IDs. A repeatable encounter replay is more useful than a video alone for debugging decision problems. Capture GPU/CPU FPS and input latency separately; animation events occur in engine time and player perception occurs on rendered frames.
