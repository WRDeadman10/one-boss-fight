# Queue BF Batch 1: framework route support

Date: 2026-11-11. This batch supports Lead acceptance with source-backed checks; it does not claim live map acceptance.

## Task dispositions

| ID | Disposition | Evidence |
|---|---|---|
| BF-X01 | Complete | Lead route questions reconciled below against BE-X01–X20 and the selected-route evidence boundary. |
| BF-X02 | Complete — audit finding | Selection refusals have stable `OutError` tokens, but the diagnostic getter is not updated for early game-thread/world/generation failures. Details below. No runtime selector behavior changed. |
| BF-X03 | Complete | Added native coverage for accepting generation 8 after 7, rejecting the old generation after advancement, and rejecting a terminal callback from a different replacement actor. |
| BF-X04 | Complete | HUD delegate unbinding and owner identity checks, plus music component shutdown, were traced in source. No live audio/runtime claim. |
| BF-X05 | Complete | Acceptance sheet supplies exact route, participant, generation, completion, retry/reset, and pack regression fields. |

## BF-X02 audit finding

`URPGEncounterSelectionSubsystem::BuildWorldBindingInternal` returns stable error values through `OutError` for `EncounterSelection.NotGameThread`, `EncounterSelection.WorldState`, and `EncounterActivation.GenerationExhausted` / `ResetCountInvalid` / `GenerationMismatch` (source lines 175–189). Those early failures do not assign `SelectionDiagnostic`, whereas later validation/census failures do (191–265). `SetSelectedDefinition` clears the stored diagnostic (87–91); successful binding also clears it (304). Therefore, if an earlier failed attempt set the getter and a later early refusal occurs, `GetSelectionDiagnostic()` can expose an old token. If no previous failure exists, it can remain empty despite the current `OutError`. This is an observability gap; the caller's `OutError` retains the current refusal reason. No selection logic change was made in this audit batch.

Other current refusal reasons include definition load/manifest, framework opt-in, census, actor state, definition/profile load, phase, and binding spawn. The framework route's CVar is code-default-off (`RPGEncounterSelectionSubsystem.cpp:27–32`); no project route default was changed.

## BF-X04 lifecycle audit

| Component | Bind/start | Replacement/teardown behavior | Boundary |
|---|---|---|---|
| Native HUD | `BeginPlay` binds `HandleNativeTerminal` with an UObject delegate (`RPGBossHud.cpp:383–390`). | `EndPlay` removes its delegate handle and resets it (`:356–366`). The handler rejects invalid actors or events whose actor is not the component owner (`:394–403`), then validates current generation, duplicate-completion state and zero health. | Source/native coverage only; live widget detach/replacement and victory presentation need Lead route acceptance. |
| Boss music | `TickComponent` reads either pack encounter health or native-health interface (`RPGBossMusic.cpp:140–175`). | Dead/dormant state calls `StopAll`; component `EndPlay` stops both owned audio components (`:27–38`). | Audio playback/fade behavior has not been accepted in a live fight; `-nosound` suite runs cannot prove audible output. |

## Lead acceptance sheet (BF-X05)

Lead run should capture one row per pack regression and framework opt-in attempt, with: build/map and route flag; selected definition path/hash; world name; boss/player actor names and object identities; binding participant slots and generation; native current/max health and active/phase state; HUD bound owner and displayed health; terminal callback actor/generation; victory delegate count; retry visibility and delay; reset/rebind count and resulting generation; prior-generation callback refusal; replacement actor callback refusal; and result token for each refusal. Include one default-off launch proving the pack route remains selected. Record PIE and saved-definition evidence separately from Codex Development tests.

## Verification status

Added native boundary assertions to `RPGNativeBossHealthTests.cpp`. `Scripts/Editor/run_bf_x01_x05_locked_build.ps1` completed under C-1155: Development build exit 0; DD27j-pinned suite 509/509, 0 failed, complete; `OneBossFight.BossHealth.PresentationSnapshot` passed with the added generation/replacement assertions; both locks released; no assets. Receipt: `Docs/BossCombatReview/Execution/Codex/BF_X01_X05_FRAMEWORK_ROUTE_SUPPORT/Run_20261110_185435/`. No project asset, map, default route, or owner-selected value was changed. The selector getter finding is recorded for follow-up rather than silently changing diagnostics during this acceptance-support batch.
