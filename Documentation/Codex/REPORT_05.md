# Report 05 — Static C++ Audit and Pure-Rule Tests

## Scope

Completed Brief 05 using static source inspection only. I read the project
context, decisions, known issues, test plan, and the audit groups recorded in
`AUDIT_01.md`. The named reviewed files total **18,363 physical lines**;
sixty-three Player lines outside the explicit groups are not claimed as
line-by-line coverage. The full file lists and per-group counts are in
`Documentation/Codex/AUDIT_01.md`.

No editor, build, package, game, PIE, or git command was run. No test is
claimed to compile or pass.

## Audit Summary

| ID | Severity | Evidence | Finding |
|---|---|---|---|
| A01 | Latent performance / wrong behaviour | `Source/OneBossFight/Player/RPGBossStagger.cpp:91-92`, `:549-550`; `RPGBossPhases.cpp:266`, `:296-297` | `LoadSynchronous` is on first-use break, riposte, and phase-transition paths. |
| A02 | Latent wrong behaviour | `Source/OneBossFight/Boss/RPGSevarogDirector.cpp:82-88` | Retired director queues a delayed lambda with no retained timer or encounter-generation guard. |
| A03 | Unmeasured frame-time risk | `Source/OneBossFight/Arena/RPGEmberField.cpp:100-109`, `:126`; `RPGArenaDressing.cpp:85-111` | Ember and sway ticks allocate fresh transform arrays and upload them every frame. |
| A04 | High release-validation defect | `Source/OneBossFight/Benchmark/RPGBenchmarkRunner.h:79`; `RPGFrameStats.h:9`, `:40` | Benchmark defaults still enforce the retired 120-FPS/8.33-ms gate rather than the documented 60-FPS/16.67-ms release gate. |

Every finding includes exact quoted evidence, a failure scenario, confidence,
and a concrete fix in `Documentation/Codex/AUDIT_01.md`. No other real defect
was reported from static inspection.

## New Tests

Created `Source/OneBossFight/Tests/RPGCodexTests.cpp` with six independent,
world-free automation registrations:

| Test | What it proves |
|---|---|
| `OneBossFight.Codex.AttackKindEdges` | Prefix case sensitivity and airborne classification boundaries. |
| `OneBossFight.Codex.BossMathEdges` | Zero-posture hold/regen boundary, cap, riposte range equality, and sweep boundaries. |
| `OneBossFight.Codex.BossRulesEdges` | Dead/cooldown/transition priority and threshold equality. |
| `OneBossFight.Codex.BleedEdges` | Precedence, exact threshold proc, same-frame suppression, and never-kill clamp. |
| `OneBossFight.Codex.SwingRulesEdges` | Inclusive hyperarmor endpoints, invalid window, stamina clamp/refund, and refresh boundary. |
| `OneBossFight.Codex.BuildRulesEdges` | Parse, enum clamp, verification boundary, decision defer, update cycle, lock, and HUD truth line. |

The file follows the existing `IMPLEMENT_SIMPLE_AUTOMATION_TEST` flags and
uses no world, actor, asset, reflection call, or pack API.

### Signatures Relied On

- `RPGClassifyAttack(const FName&, bool)` — `Source/OneBossFight/Player/RPGAttackKind.h:41`.
- `RegenStep(...)`, `RiposteGeometry(...)`, `SweepTouches(...)` — `Source/OneBossFight/Player/RPGBossMath.h:15`, `:35`, `:72`.
- `ResolveBreak(const FFlags&, bool)`, `ResolveTransition(const FFlags&, double, double, float)` — `Source/OneBossFight/Player/RPGBossRules.h:60`, `:72`.
- `Apply(FState&, const FConfig&, float, bool, bool, bool, bool)`, `ProcDamage(float, float, const FConfig&)` — `Source/OneBossFight/Player/RPGBleedRules.h:48`, `:67`.
- `WindowOpen(float, float, float)`, `StaminaExtra(float, float, double)`, `NeedsRefresh(double, double, float)` — `Source/OneBossFight/Player/RPGSwingRules.h:32`, `:39`, `:54`.
- `Parse(const FString&, ERPGBuild&)`, `IsVerifying(const FDecideInput&)`, `Decide(const FDecideInput&)`, `UpdateTypeForAttempt(int32)`, `ShouldLockSlot(bool, bool, bool)`, `BuildLine(const FName&, EDecision)` — `Source/OneBossFight/Player/RPGBuildRules.h:107`, `:193`, `:205`, `:238`, `:246`, `:284`.

## DISAGREES WITH CODE

- **A04 only.** The intended release benchmark is 60 FPS with p99 <= 16.67 ms
  (`AGENTS.md:3`, `Documentation/DECISIONS.md:384`), but current benchmark
  defaults are 120 FPS and 8.33 ms (`RPGBenchmarkRunner.h:79`,
  `RPGFrameStats.h:9`, `:40`). I did not encode an alternative expected value
  in the new rule tests because the benchmark implementation is not a
  header-only pure rule.

## Static Validation Performed

- Counted the new test registrations: **six** `IMPLEMENT_SIMPLE_AUTOMATION_TEST`
  declarations under `OneBossFight.Codex.*`.
- Counted literal braces in the new file: **7 opening / 7 closing**.
- Searched the new test file for `NewObject`, `SpawnActor`, `GetWorld`,
  `LoadObject`, `FindObject`, `RPGPack`, `UWorld`, `AActor`, and
  `set_editor_property`: **no matches**.
- Re-read the referenced header signatures and source-line evidence.

Not verified: C++ compilation, UE automation discovery/execution, actual
frame hitches, component order under PIE, package cooking, and target-hardware
performance. Claude must build and run the tests before accepting them.
