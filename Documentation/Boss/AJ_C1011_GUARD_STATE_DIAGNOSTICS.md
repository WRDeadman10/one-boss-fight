# C-1011 guard-state diagnostics

Date: 2026-11-07  
Owner: Codex  
Runtime/build owner: Claude (Lead)

## Lead finding

C-1011 reports BUILD-250 GREEN 484/484, but both-route PIE still failed. The prior monitor showed `abilityFound=0 reactionActive=0 statusBlocking=0` in 55/55 samples despite per-tick `IA_Block` injection. This means the C-1008 `GA_BlockReaction_C` guess is not supported by the live run, and `IA_Block` still is not producing the expected block state. Do not wire another guessed ability name.

## Diagnostic added

Added `URPGDodgeTiming::DescribeGuardState()` as a Development-only Blueprint-callable diagnostic. It lists every object in the pack ASC's `CreatedAbilities` array with its Blueprint class name and active flag; block/guard-named ability classes are also listed separately. It asks the actor's pack `GetOwnedGameplayTags` interface for its full tag container (with direct `GameplayTags` property fallback) and reports the exact tag list plus `Status.Blocking`, `State.Blocking`, and `Ability.Block` checks using the same `RPGBossDamage::HasTag` reflection path.

The PIE probe calls the diagnostic every 0.5 s while injecting `IA_Block`, and once after `RPGHitIntake` records the first real boss hit after the guard phase begins. The prior periodic `guard contact monitor` line is now `Verbose` as requested. The diagnostic never writes Blueprint, ability, tag, or asset state.

## Verification and next step

Codex performs only an AST parse of the updated probe and scoped `git diff --check`; no build, native automation, Unreal, or PIE. Lead must build and run both routes, inspect the full diagnostic output, and then wire the guard hook to the ability/event/state that the runtime data actually shows. Until that evidence arrives, no guard event source is considered confirmed.
