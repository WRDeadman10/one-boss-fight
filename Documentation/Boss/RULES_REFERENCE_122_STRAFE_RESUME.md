# Designer reference: neutral-strafe budget restart

`RPGBossStrafeResume::ShouldRestart` permits one restart of a neutral-strafe budget after an interruption. It is unwired and does not restart the strafe or alter its state.

| Input | Unit | Default | Requirement |
|---|---|---|---|
| `bWasInterrupted` | boolean | none | must be true |
| `bRestartAlreadyUsed` | boolean | none | must be false |
| `RemainingBudgetSeconds` | seconds | none | finite and greater than 0 |
| Return value | boolean | false | true only when all restart conditions hold |

No interruption, a previously used restart, an exhausted budget, or a non-finite budget returns false. The caller must mark the restart used and apply the remaining time budget; this function does not remember prior calls. Source: [`RPGBossStrafeResumeRules.h`](../../Source/OneBossFight/Player/RPGBossStrafeResumeRules.h:7), unit tests: [`RPGBossStrafeResumeRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossStrafeResumeRulesTests.cpp:6).
