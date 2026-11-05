# P14 — parity production change proposal (FLAGGED)

Status: proposal only; no production C++ component-attach change is applied here. Based on Claude's BUILD-219 A5 results in C-839 and the source triage in `P13_PARITY_MISMATCH_TRIAGE.md`.

## Confirmed data correction (Lead asset edit)

The selected boss definition currently records `Stats.MaxHealth = 1500.0` in `Saved/G044/encounter_manifest.json:1764`; native `URPGBossEncounter::BossMaxHealth` defaults to 2000 (`Source/OneBossFight/Player/RPGBossEncounter.h:42`). The selected encounter adapter copies the authored value (`RPGBossEncounterClusterAdapters.cpp:72`) and runtime applies it (`RPGBossEncounter.cpp:114-130`). To preserve the established legacy behavior, Claude should update the existing selected boss draft's `Stats.MaxHealth` to `2000.0`, regenerate the manifest and rerun the death-reset pair. This is an asset overwrite and is Lead-owned.

## Test-first selected/legacy attach parity (proposed Source change)

The selected `BossCore` plan is exactly thirteen authored/configured component factories (`RPGBossHydrationPreflight.cpp:76-97`). The legacy path independently attaches/configures five additional boss components: `RPGFootsteps`, `RPGBossMusic`, `RPGTraceGuard`, `RPGBossHud`, and `RPGBossLegend` (`RPGPlayerMovesSubsystem.cpp:618-659, 726-742`). The current selected activation path does not call those legacy attach functions (`RPGPlayerMovesSubsystem.cpp:188-198`). This makes the attach-set mismatch real, but it does not prove the missing components caused the S9 i-frame boundary results.

Before changing production behavior, add a native automation test that builds an expected legacy boss attach-class set and compares it to the selected attach plan/set, with separate asserted expectations for the five currently omitted classes. Test the current mismatch first. Then implement an explicit selected-route attach bundle for those five classes with one owner/lease lifecycle and idempotent setup; do not call the legacy bundle wholesale because it would duplicate configured BossCore components. Preserve the exact Footsteps sounds/scales and Music track fallback from the legacy setup. If any component is intentionally excluded, require a written reason and an expected-set assertion for that exclusion. Build/suite and Lead live parity reruns are required before acceptance.

Classification: `RPGTraceGuard` is gameplay safety; Footsteps is audio feedback; Music, HUD, and Legend are presentation/audio. The latter four should not be dropped solely because BossCore currently describes combat configuration. Whether every presentation component is required in selected mode is a Lead parity decision; until decided, the proposal follows the measured legacy component-set contract.

## S9 timing mismatch investigation (no timing fix proposed yet)

The selected route and legacy route differ in component attachment and therefore may differ in component registration/tick chronology. `RPGIFrameMonitor` explicitly ticks at `TG_PostUpdateWork` (`RPGIFrameMonitor.cpp:20-21`); `RPGBossLowSweep` uses the default component tick group (`RPGBossLowSweep.cpp:20-23`). The present data does not prove this explains the jump/roll observations. First add a controlled diagnostic/test that records player montage position, invulnerability tag edges, attack-tracker position and relevant component tick groups/order on both routes for the exact S9 times. Re-run the four arms. Only then propose a separate timing change if a mechanism is demonstrated; do not tune i-frame windows from the current evidence alone.

## Telegraph exact-value comparator disposition (Lead decision)

The finalized BUILD-219 telegraph receipts compare FAIL on four check messages, even though both drivers pass 26/26 and each reported windup is inside its authored tolerance (`pie_telegraph.py`: 0.40 ±0.06 s, 0.35 ±0.06 s, 1.93 ±0.12 s). The v2 comparator compares observable `value` objects exactly, so it correctly surfaces the recorded values. Do not change comparator semantics globally or discard observations: propose either treating those exact measured values as required parity (then explain the variation) or changing this driver's receipt schema to carry raw numeric measurements plus an explicitly Lead-approved tolerance. No waiver is implied.

## Damage-path diagnostic hotfix

The data route has no `RPGDamageResolver` factory in its BossCore plan, while legacy calls `FindOrAdd`. `pie_damage_path.py` already logged a traceback but its failed `tick raised` check discarded the details. The driver now adds that traceback to the failed check detail, preserving its existing scenario/setup behavior. Missing resolver is the leading explanation based on source, pending the next Lead run's captured exception.
