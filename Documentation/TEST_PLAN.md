# Test Plan

Acceptance matrix is in `Idea/IDEA.md` section 14. Record results here per build.

| Test ID | Area | Procedure | Pass criteria | Build | Result | Evidence |
|---|---|---|---|---|---|---|
| BLD-01 | Build | Headless UBT build of `OneBossFightEditor` | 0 errors | M0 | PASS (2026-10-18) | UBT log |
| BEN-01 | Benchmark stats | Automation: `OneBossFight.Benchmark.FrameStats.*` (percentiles, gate, empty/single sample) | All pass | M1 | PASS (2026-10-18) | UnrealEditor-Cmd |
| ARN-01 | Arena | Automation: `OneBossFight.Arena.Collision` (floor, pillar, wall, open above wall) | All pass | M1 | PASS (2026-10-18) | UnrealEditor-Cmd |
| PLR-01 | Player defaults | Automation: `OneBossFight.Characters.Player.Defaults` (camera, orientation, sprint toggle) | All pass | M1 | PASS (2026-10-18) | UnrealEditor-Cmd |
| AST-01 | Asset pipeline | `L_AssetProof`: play player and boss core animations on their own skeletons | Poses differ per animation and match the intended action | M2 | PASS for attack, deflect, boss swings/stun/death/intro; rest unviewed (2026-10-18) | `Documentation/AssetProof/` |
| MOV-01 | Movement | Walk, run, sprint, jump | No stuck state | | | |
| COM-01 | Attributes | Automation: `OneBossFight.Combat.Attributes` (damage clamp, stamina spend/regen delay/drain, poise break and reset, death once) | All pass | M3 | PASS (2026-10-18) | UnrealEditor-Cmd |
| COM-02 | Hit detection | Automation: `OneBossFight.Combat.HitDetection.*` (one hit per swing, teams, i-frame hit spent, same result at 1 to 480 frames per sweep, hit window arms trace, stagger disarms) | All pass | M3 | PASS (2026-10-18) | UnrealEditor-Cmd |
| COM-03 | State machine | Automation: `OneBossFight.Combat.StateMachine.*` (attack chain and wrap, input buffer and expiry, dodge cancel window, i-frames, stamina once, stagger, block and guard break, death, reset) | All pass | M3 | PASS (2026-10-18) | UnrealEditor-Cmd |
| COM-04 | Lock-on | Automation: `OneBossFight.Combat.LockOn.*` (selection, side switch, toggle, dead/far/ally refused, strafe orientation) | All pass | M3 | PASS (2026-10-18) | UnrealEditor-Cmd |
| COM-05 | Combat in game | PIE with real montages: `Scripts/Editor/pie_combat_smoke.py` (4-hit light chain, heavy, dodge) against the dummy | One hit per swing, dummy dies after 4 light hits and resets, heavy breaks poise | M3 | PASS (2026-10-18) | Output Log `[M3Drive]` |
| COM-06 | Combat feel | Player playtest: attack, combo, dodge, lock-on with mouse and keyboard | Responsive, no stuck state | M3 | Pending playtest | |
| ENC-02 | Reset | Die, retry, repeat | All state resets | | | |
| PERF-01 | Performance | Packaged 1080p full fight | Avg >= 120 FPS, p99 <= 8.33 ms | | | |
