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
| COM-02 | Hit detection | Hold weapon through active frames on a target | One hit per swing | | | |
| ENC-02 | Reset | Die, retry, repeat | All state resets | | | |
| PERF-01 | Performance | Packaged 1080p full fight | Avg >= 120 FPS, p99 <= 8.33 ms | | | |
