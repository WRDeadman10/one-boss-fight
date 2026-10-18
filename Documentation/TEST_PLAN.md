# Test Plan

Acceptance matrix is in `Idea/IDEA.md` section 14. Record results here per build.

| Test ID | Area | Procedure | Pass criteria | Build | Result | Evidence |
|---|---|---|---|---|---|---|
| BLD-01 | Build | Headless UBT build of `OneBossFightEditor` | 0 errors | M0 | PASS (2026-10-18) | UBT log |
| BEN-01 | Benchmark stats | Automation: `OneBossFight.Benchmark.FrameStats.*` (percentiles, gate, empty/single sample) | All pass | M1 | PASS (2026-10-18) | UnrealEditor-Cmd |
| ARN-01 | Arena | Automation: `OneBossFight.Arena.Collision` (floor, pillar, wall, open above wall) | All pass | M1 | PASS (2026-10-18) | UnrealEditor-Cmd |
| PLR-01 | Player defaults | Automation: `OneBossFight.Characters.Player.Defaults` (camera, orientation, sprint toggle) | All pass | M1 | PASS (2026-10-18) | UnrealEditor-Cmd |
| AST-01 | Asset pipeline | `L_AssetProof`: play player and boss core animations on their own skeletons | Poses differ per animation and match the intended action | M2 | PASS for attack, deflect, boss swings/stun/death/intro; rest unviewed (2026-10-18) | `Documentation/AssetProof/` |
| BOS-01 | Boss selection | Automation: `OneBossFight.Boss.Selection` (weights 75/25 over 20000 rolls, range, arc, phase, cooldown, repeat limit, no infinite repeat, phase from health) | All pass | M4 | PASS (2026-10-18) | UnrealEditor-Cmd |
| BOS-02 | Boss flow | Automation: `OneBossFight.Boss.PhaseAndFlow` (dormant and entrance untouchable, one transition for same-frame hits, death, reset) | All pass | M4 | PASS (2026-10-18) | UnrealEditor-Cmd |
| BOS-03 | Boss attacks | Automation: `OneBossFight.Boss.AttackLoop` (30 s simulated: damage equals swings times damage, no back-to-back repeats) | All pass | M4 | PASS (2026-10-18) | UnrealEditor-Cmd |
| BOS-04 | StateTree mirror | Automation: `OneBossFight.Boss.StateTreeMirror` (tree follows dormant, entrance, combat, phase transition, dead, reset) and PIE log `statetree=` next to `boss=` | Tree always equals boss state | M4 | PASS (2026-10-18): automation, plus 2 PIE cycles | UnrealEditor-Cmd, Output Log |
| WPN-01 | Weapons | Automation: `OneBossFight.Weapons.EquipAndCycle` (weapon decides cost and damage, no swap mid-attack, wrap, reset re-equips) | All pass | M5 | PASS (2026-10-18) | UnrealEditor-Cmd |
| WPN-02 | Feedback | Automation: `OneBossFight.Weapons.FeedbackAndHitStop` (empty feedback assets harmless, hit-stop on both fighters, reset unfreezes, block gives none) | All pass | M5 | PASS (2026-10-18) | UnrealEditor-Cmd |
| WPN-03 | Weapons in game | PIE `Scripts/Editor/pie_weapons_smoke.py`: switch through three weapons and hit the boss with each | Damage dealt, time dilation back to 1 | M5 | PASS (2026-10-18) | Output Log `[M5Drive]` |
| ENC-01 | Reset | Automation: `OneBossFight.Boss.Encounter.ResetCycles` (10 mixed win/lose cycles, invariants after each) | All pass | M4 | PASS (2026-10-18) | UnrealEditor-Cmd |
| ENC-03 | Encounter in game | PIE with Sevarog: `Scripts/Editor/pie_boss_smoke.py` (trigger, entrance, attacks, phase 2, death, auto-retry, repeat) | Loop completes without stuck state | M4 | PASS (2026-10-18): 3 cycles, phase 2 once per cycle, no stale-state warnings | Output Log `[M4Drive]` |
| ENC-04 | Fight feel | Player playtest: beat and lose to the boss | Fair, readable telegraphs | M4 | Pending playtest | |
| MOV-01 | Movement | Walk, run, sprint, jump | No stuck state | | | |
| COM-01 | Attributes | Automation: `OneBossFight.Combat.Attributes` (damage clamp, stamina spend/regen delay/drain, poise break and reset, death once) | All pass | M3 | PASS (2026-10-18) | UnrealEditor-Cmd |
| COM-02 | Hit detection | Automation: `OneBossFight.Combat.HitDetection.*` (one hit per swing, teams, i-frame hit spent, same result at 1 to 480 frames per sweep, hit window arms trace, stagger disarms) | All pass | M3 | PASS (2026-10-18) | UnrealEditor-Cmd |
| COM-03 | State machine | Automation: `OneBossFight.Combat.StateMachine.*` (attack chain and wrap, input buffer and expiry, dodge cancel window, i-frames, stamina once, stagger, block and guard break, death, reset) | All pass | M3 | PASS (2026-10-18) | UnrealEditor-Cmd |
| COM-04 | Lock-on | Automation: `OneBossFight.Combat.LockOn.*` (selection, side switch, toggle, dead/far/ally refused, strafe orientation) | All pass | M3 | PASS (2026-10-18) | UnrealEditor-Cmd |
| COM-05 | Combat in game | PIE with real montages: `Scripts/Editor/pie_combat_smoke.py` (4-hit light chain, heavy, dodge) against the dummy | One hit per swing, dummy dies after 4 light hits and resets, heavy breaks poise | M3 | PASS (2026-10-18) | Output Log `[M3Drive]` |
| COM-06 | Combat feel | Player playtest: attack, combo, dodge, lock-on with mouse and keyboard | Responsive, no stuck state | M3 | Pending playtest | |
| ENC-02 | Reset | Die, retry, repeat | All state resets | | | |
| PERF-01 | Performance | Packaged 1080p full fight | Avg >= 120 FPS, p99 <= 8.33 ms | | | |
