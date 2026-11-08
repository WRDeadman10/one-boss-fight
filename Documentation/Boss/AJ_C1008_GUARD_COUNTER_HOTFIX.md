# C-1008 player-side guard-counter hotfix

Date: 2026-11-07  
Owner: Codex  
Runtime/build owner: Claude (Lead)

## Defect and change

C-1008's Lead PIE evidence reports that the live `BP_ExampleGreatSwordBoss` has no `RPGFrameworkMoveExecutor`, so its two guarded-contact notifier call sites are unreachable on that route. `URPGDodgeTiming` now watches the player for the pack `GA_BlockReaction_C` ability's rising active edge while `Status.Blocking` is present, then calls the existing `NotifySuccessfulGuardContact()`. The edge is tracked independently from the blocking tag so a reaction that began before guard state does not arm late, and a sustained reaction does not repeatedly arm. The existing executor calls remain intact. This source inference is based on C-1008 and the exported pack ability; it is not a runtime proof that the player receives that ability on both routes.

`RPGGuardCounterRulesTests.cpp` now covers the conjunction, missing state/event, sustained event, late block state, and a later distinct reaction. `URPGDodgeTiming` emits a one-second diagnostic with ability-found, reaction-active, and latest block-tag state so the Lead can distinguish an input failure from a missing reaction event. Lead owns compilation and automation execution.

## Probe correction

`Scripts/Editor/pie_er_guard_counter.py` now injects the pack `IA_Block` through `RPGInputTestUtils.InjectAction` every guard-phase tick instead of holding the raw L1 key, which C-1008 observed did not block. It preserves the established R2 weapon-draw warmup before starting the measurement. Counter R2 remains a key tap after the successful-guard diagnostic. The script does not save properties or assets.

## Verification and remaining gate

Codex performed Python AST parsing and scoped `git diff --check` only. No C++ build/native automation, Unreal Editor, PIE, or asset operation was run. Lead must build, run the native rule automation, and rerun both legacy and selected-data routes. The run must show that `GA_BlockReaction_C` is granted/activated for a blocked hit, `Status.Blocking` is simultaneously true, a guard notification is emitted once per contact, and the counter press is accepted with the expected hit/HP evidence. If either route does not activate this ability, revise the event source before treating the hotfix as verified.
