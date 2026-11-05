# Framework proof-hook index (S149)

This inventory covers every C++ console variable whose registered name begins `rpg.BossProof`. Registration and behavior below were checked against source on 2026-11-03. All 16 are declared inside `#if !UE_BUILD_SHIPPING` regions, so they are absent from Shipping builds. This source guard is not a packaged-binary inspection.

Use the listed command after opening the console in a Development/Editor session, before the first boss attack unless noted. Empty strings and the documented sentinel values are the off settings. Values are examples of the exact command grammar; timing is in game-clock seconds where noted.

| Console command | Invocation / argument | Effect | Registration and guard |
|---|---|---|---|
| `rpg.BossProofBystander` | `rpg.BossProofBystander 60` | Spawn a non-target Character 60 cm to the side at first attack. | `RPGFrameworkBossCharacter.cpp:34`, outer `!UE_BUILD_SHIPPING`; consumed at `:556-559`. |
| `rpg.BossProofIFrameSweep` | `rpg.BossProofIFrameSweep 0.5` (negative disables) | At the offset after first attack, inject real dodge input and run 1 HP probes for 1.2 s. | Character `:35`, outer `!UE_BUILD_SHIPPING`; armed/used `:285,537`. |
| `rpg.BossProofPlayerGuard` | `rpg.BossProofPlayerGuard 1` (block), `2` (parry); modes 3–6 include toggle-combat variants described in source. | Drive real player block/parry input after first attack. | Character `:36`, outer guard; read `:269-271,536`. |
| `rpg.BossProofPlayerGuardSeconds` | `rpg.BossProofPlayerGuardSeconds 6` | Sets duration for PlayerGuard input driving. Set together with PlayerGuard. | Character `:37`, same outer guard; read `:269`. |
| `rpg.BossProofPlayerHits` | `rpg.BossProofPlayerHits 0.5,0.9` | Inject one test hit at each comma-separated game-clock offset after first attack. | Character `:38`, outer guard; parse/use `:544-546`. |
| `rpg.BossProofTargetShift` | `rpg.BossProofTargetShift 0.3:0,500,0\|3.5:0,-400,0` | Teleport target by each `seconds:dx,dy,dz` step after first attack. | Character `:39`, outer guard; parse/use `:524-526`. |
| `rpg.BossProofTurnLatch` | `rpg.BossProofTurnLatch 0` (control) or `1` (latched) | Selects direction-latch behavior for reposition turn. | Character `:40`, outer guard; runtime read at `:471-474`. |
| `rpg.BossProofPlayerDrink` | `rpg.BossProofPlayerDrink 0.5,1.0` | Play target drinking montage at each listed game-clock offset. | Character `:41`, outer guard; parse/use `:530-532`. |
| `rpg.BossProofPlayerDodge` | `rpg.BossProofPlayerDodge 0.3,0.8:F` | Launch target backward at 0.3 s and forward at 0.8 s; comma-separated `seconds` or `seconds:F`. | Character `:42`, outer guard; parse/use `:538-540`. |
| `rpg.BossProofTargetFault` | `rpg.BossProofTargetFault 1` (kill) or `2` (destroy) | Inject target health/death or pawn-destroy fault at first attack. | Character `:43`, outer guard; consumed `:550-552`. |
| `rpg.BossProofYawProbe` | `rpg.BossProofYawProbe 30` (positive amplitude; <=0 disables) | Replace selector yaw with a period-24 sinusoid for cone-boundary probing. | Character `:45`, outer guard; read `:430`. |
| `rpg.BossProofRepeatAbort` | `rpg.BossProofRepeatAbort 3` | On abort, repeat abort three times and count duplicate cleanup/release behavior. | `RPGFrameworkMoveExecutor.cpp:50`, nested and outer `!UE_BUILD_SHIPPING`; used `:591-594`. |
| `rpg.BossProofMotionIntruder` | `rpg.BossProofMotionIntruder 0.4` (negative disables) | Issue navigation move request at the specified card time. | Executor `:51`, nested and outer `!UE_BUILD_SHIPPING`; used `:225`. |
| `rpg.BossProofStaleCallback` | `rpg.BossProofStaleCallback 1` | Send prior aborted-token callback immediately after next card starts. | Executor `:53`, outer `!UE_BUILD_SHIPPING`; used `:163`. |
| `rpg.BossProofSuppressMontageEnd` | `rpg.BossProofSuppressMontageEnd 1` | Stop feeding montage position after 0.3 s, simulating missing end notification so watchdog must recover. | Executor `:54`, outer `!UE_BUILD_SHIPPING`; used `:193`. |
| `rpg.BossProofCenterBias` | `rpg.BossProofCenterBias 0.5` (0..1; negative uses profile value) | Override profile center bias for the controller's walk-to-band calculation. | `RPGFrameworkBossController.cpp:7`, `!UE_BUILD_SHIPPING`; used at `:23`. |

## Scope and caveats

- Defaults are inert/off values except `PlayerGuardSeconds` (6 s), `TurnLatch` (1), and the negative sentinels that mean use profile/off. `rpg.BossComboDuplicateGate` is a separate proof control but is excluded because its registered name does not start with `rpg.BossProof`.
- Exact command parsing is controlled by each hook's C++ string parser. Scheduled string hooks accept only their documented separators and tuple forms; this index does not claim malformed-input validation beyond what those parsers implement.
- Historical `TEST_PLAN.md` entries and retained PIE logs contain concrete command examples for many hooks. A command being registered or invoked is setup evidence only; feature proof still depends on the resulting logs and acceptance checks.

## Source lines for review

- `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:33-46,269-286,430-438,523-560` — registrations, first-attack scheduling, parser and use sites.
- `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:49-55,163,193,225,591-594` — executor hook registrations and use sites.
- `Source/OneBossFight/Boss/RPGFrameworkBossController.cpp:6-8,18-24` — center-bias hook and use site.
- `Documentation/TEST_PLAN.md:456-475` — concrete historical invocation examples and retained proof context.
