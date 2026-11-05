# Designer reference: one-shot death and phase-roar gates

`RPGBossPresentation` contains pure gates for death presentation and phase-transition roars. It is unwired and does not play an animation or update the one-shot flags.

| Function/input | Unit | Default | Result |
|---|---|---|---|
| `ShouldPlayDeath(bDead, bDeathAlreadyPlayed)` | booleans | none | true only when dead and death has not played |
| `ShouldPlayPhaseRoar(bDead, bPhaseChanged, bRoarAlreadyPlayed)` | booleans | none | true only when alive, phase changed, and roar has not played |

Both gates return false when their condition is absent or the corresponding one-shot flag is already set. The caller must set the flag after playback begins/succeeds and reset it at the appropriate encounter lifecycle boundary. Source: [`RPGBossPresentationRules.h`](../../Source/OneBossFight/Player/RPGBossPresentationRules.h:7), unit tests: [`RPGBossPresentationRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossPresentationRulesTests.cpp:6).
