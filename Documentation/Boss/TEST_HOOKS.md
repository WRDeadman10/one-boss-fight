# Runtime test and measurement console variables

Inventory source: actual `TAutoConsoleVariable` registrations in `Source/OneBossFight` plus the eight `rpg.Perf.*` controls (seven macro expansions and the separately declared FireShadows control). Current source has 45 registered names: 37 non-performance controls listed below and eight performance controls summarized in the performance section. The older reference scan's 49 count included five incomplete caller-string prefixes (`rpg.Legend.`, `rpg.Perf.`, `rpg.ScreenshotAt.`, `rpg.ScreenshotPath.`, `rpg.WakeClip.`); those are not registrations. Six controls (`rpg.BossOverlay`, `rpg.CloseTelegraph`, `rpg.Build`, `rpg.CameraDebug`, `rpg.Legend`, `rpg.LegendShakeScale`) are Shipping-visible runtime controls, not test-only hooks; the prior C-702 mailbox disposition records that set as intentional. The remaining test/proof registrations are excluded from Shipping by `!UE_BUILD_SHIPPING` guards. Defaults below are declaration defaults; confirm the source declaration before use.

## Framework proof hooks

| CVar | Default | Meaning |
|---|---:|---|
| `rpg.BossProofBystander` | 0 | Spawn one non-target pawn beside target at first attack; positive value is offset cm. |
| `rpg.BossProofIFrameSweep` | -1 | Schedule real dodge and resolver probes at seconds after first attack; negative disables. |
| `rpg.BossProofPlayerGuard` | 0 | 1 drives real block, 2 drives repeated real parry input. |
| `rpg.BossProofPlayerGuardSeconds` | 6 | Duration for the guard hook. |
| `rpg.ParryStaminaCost` | 0 | Non-shipping: when above 0 and `URPGPlayerParry::StaminaCost` is 0, the component adopts this stamina cost at its next press (parry stamina proof). |
| `rpg.BossProofPlayerHits` | empty | Comma-separated game-clock seconds for injected target hits. |
| `rpg.BossProofTargetShift` | empty | `seconds:dx,dy,dz` entries separated by `|` teleport target on game clock. |
| `rpg.BossProofTurnLatch` | 1 | 0 disables direction latch for reposition-turn control run. |
| `rpg.BossProofPlayerDrink` | empty | Comma-separated game-clock seconds to play target DrinkingPotion montage. |
| `rpg.BossProofPlayerDodge` | empty | Schedule dodge-like target displacement; `seconds` backward, `seconds:F` forward. |
| `rpg.BossProofTargetFault` | 0 | 1 zeroes target health, 2 destroys target at first attack. |
| `rpg.BossComboDuplicateGate` | 0 | Re-evaluate each combo gate with same ID to exercise duplicate rejection. |
| `rpg.BossProofYawProbe` | 0 | Positive degrees enables period-24 sinusoid selector-yaw probe. |
| `rpg.BossProofCenterBias` | -1 | 0..1 overrides profile arena-center bias; negative uses profile value. |
| `rpg.BossProofRepeatAbort` | 0 | Repeat executor abort N additional times and count duplicate cleanup/releases. |
| `rpg.BossProofMotionIntruder` | -1 | At card time, request controller navigation; negative disables. |
| `rpg.BossProofStaleCallback` | 0 | Send previous attack's late abort callback after next attack starts. |
| `rpg.BossProofSuppressMontageEnd` | 0 | Suppress montage-position feed after 0.3 s to exercise watchdog abort. |

## Other test and measurement controls

| CVar | Default | Meaning |
|---|---:|---|
| `rpg.CatalogSource` | `auto` | Startup selection: `auto`, `legacy`, or `data`; takes effect next session. |
| `rpg.CatalogTestFourth` | 0 | Development startup fixture adds fourth build sharing existing sword. |
| `rpg.CatalogPath` | empty | Startup-only isolated test-catalog object path; requires data source. |
| `rpg.CatalogTestInvalid` | 0 | Development startup-only invalid-input catalog fixture. |
| `rpg.WakeClip` | 1 | 0 skips authored wake clip in tests. |
| `rpg.CloseTelegraph` | 0.4 | Close-attack windup seconds; 0 restores raw pack pacing. |
| `rpg.CameraProbe` | 0 | 1 logs camera framing; 2 stages 300/600/900 cm; 3 adds turned-away negative control. |
| `rpg.ScreenshotAt` | -1 | Game time for screenshot; negative disables. |
| `rpg.ScreenshotShowUI` | 1 | Include Slate UI in screenshot. |
| `rpg.ScreenshotQuit` | 0 | Quit standalone 20 frames after screenshot. |
| `rpg.ScreenshotPath` | empty | Absolute PNG output path for screenshot request. |
| `rpg.BossOverlay` | 0 | 1 on-screen boss overlay; 2 also emits a proof log line each second. |
| `rpg.CameraDebug` | 0 | Draw camera pivot, arm, camera, and clearance. |
| `rpg.Debug` | 0 | 1 overlay; 2 overlay plus one log line per second. |
| `rpg.CueMode` | 0 | 0 visual+sound, 1 visual, 2 sound, 3 both with half-size visual. |
| `rpg.Build` | empty | Startup loadout choice: Starter, Strength, Dex, or empty. |
| `rpg.Legend` | 1 | Enable hit stop, slow motion, shake, and music swap presentation pass. |
| `rpg.LegendShakeScale` | 1 | Shake multiplier, documented range 0..1. |
| `rpg.RemainsFormSeconds` | 2.5 | Seconds for remains monument dissolve-in. |

## Arena performance switches

All `rpg.Perf.*` switches are compiled as runtime controls outside Shipping; their macro default is 1 (on). `rpg.Perf.FireShadows` defaults to -1 (authored); 0 disables fire-light shadows, positive N retains only first N. Other controls: `FireLights` (fire point lights), `FireFx` (fire/smoke/sparks), `GateMist` (fog gate), `DressingAll` (all arena dressing instances), `DressingMist` (mist sheets), `DressingShadows` (dressing shadows), and `Embers` (ember field). Set to 0 to disable the named contribution for performance experiments. `rpg.Perf.*` are not gameplay tuning controls.

Inventory is a source snapshot; update it whenever registrations or guards change. Names found only in comments, tests, or caller strings are not registrations.
