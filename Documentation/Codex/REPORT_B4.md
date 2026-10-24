# B4 - Pure-logic coverage inventory

## Result

No new test was added. There are **no pure-logic headers without automation
coverage**, so adding three nominal tests would duplicate existing coverage rather
than reduce risk.

| Rank | Header | Existing automation evidence | Risk |
| --- | --- | --- | --- |
| 1 | `Player/RPGDamageScale.h` | `FRPGCodexDamageScalerTest`, `RPGCodexTests.cpp:193-227`, covers both arrival orders, window boundaries, pruning, cap/floor/dead-health behaviour. | High logic risk, covered |
| 2 | `Player/RPGTelegraphRules.h` | `FRPGCodexTelegraphRulesTest`, `RPGCodexTests.cpp:229-261`, covers invalid inputs, late starts, clamp, cvar targets, and close-move selection. | High timing risk, covered |
| 3 | `Player/RPGBleedRules.h` | `FRPGCodexBleedEdgesTest`, `RPGCodexTests.cpp:78-96`, plus `FRPGBleedRulesTest` in `RPGAutomationTests.cpp:588`. | High combat-risk, covered |
| 4 | `Player/RPGBossMath.h` | `FRPGCodexBossMathEdgesTest`, `RPGCodexTests.cpp:32-50`, plus posture/riposte tests in `RPGAutomationTests.cpp:249` and `:301`. | High geometry/state risk, covered |
| 5 | `Player/RPGBossRules.h` | `FRPGCodexBossRulesEdgesTest`, `RPGCodexTests.cpp:52-76`, plus transition rules in `RPGAutomationTests.cpp:191`. | High priority-order risk, covered |
| 6 | `Player/RPGBuildRules.h` | `FRPGCodexBuildRulesEdgesTest`, `RPGCodexTests.cpp:119-149`, and exhaustive build decision coverage in `RPGBuildTests.cpp:245-382`. | Medium loadout risk, covered |
| 7 | `Player/RPGSwingRules.h` | `FRPGCodexSwingRulesEdgesTest`, `RPGCodexTests.cpp:99-117`, plus `RPGAutomationTests.cpp:529`. | Medium combat-cost risk, covered |
| 8 | `UI/RPGBuildSelectRules.h` | `FRPGCodexBuildSelectRulesTest`, `RPGCodexTests.cpp:151-191`, including the full four-input truth table. | Medium selector risk, covered |
| 9 | `Player/RPGAttackKind.h` | `FRPGCodexAttackKindEdgesTest`, `RPGCodexTests.cpp:17-30`, plus `RPGAutomationTests.cpp:400`. | Low classification risk, covered |
| 10 | `Player/RPGDamageResolver.h` (`RPGDamageRules`) | `FRPGDamageDecideTest`, `RPGAutomationTests.cpp:159-181`. | Medium resolver risk, covered |

`Player/RPGBossClips.h`, `Player/RPGBossDamage.h`, and `Pack/RPGPackReflect.h` are
header-only helpers but are not pure rules: each calls Unreal object, animation,
collision, or reflection APIs. They need integration/PIE coverage rather than a
header-only automation test.

## Re-read evidence

I re-read the current test sources twice without a content change:

```text
RPGCodexTests.cpp     DBFC00AFDF4D73617782BADFC828221997CE0A7EA27F9A52195E8DD6AFC4EC38
RPGAutomationTests.cpp 22299A447CB207B618825981C001CCED3B24D661399CF40ECC8BDC85141101F8
RPGBuildTests.cpp     33BABE57D4030B11AF4F98D34F39965F467AA8A2E4C48C3EA7981AC3070272A2
```

No compile or automation test was run. No editor, build, PIE, package, or game was
run.
