# Queue AO-C21–C25: first-dodge diagnostic boundaries

**Status:** Offline testability review complete; no root-cause conclusion. Codex did not run Unreal, build, PIE, or alter the accepted recovery. Lead owns runtime diagnostics and any future instrumentation requiring an input-binding change.

## One bounded Lead diagnostic card

Use `Scripts/Editor/probe_first_dodge_after_draw.py` with no runtime montage assignment and keep the accepted one-shot retry enabled. For the selected route, use a fresh PIE process for the immediate standing-first-press case, then retain the two normal repeats as controls. If a moving replicate is needed, run it in a separate fresh PIE process with `FIRST_DODGE_CASE=moving`; each first-press case requires a clean process because the retry/press state is one-shot. Preserve the complete raw log, route/build identity, driver arguments, and result folder. Do not use the same PIE process as a second hypothesis arm after its first press.

The probe now observes the already exposed `BP_InputBufferComponent_C` `Get Buffered Input Tag` before/after the input tick and at 50 ms sampling intervals; it logs active montage name and position alongside movement and backstep count. Existing Development output supplies CanActivate/active/stamina/tag state at the next component tick and the one-shot retry result. These reads add no input binding, context mutation, activation call, montage assignment, or extra wait; the key-down/key-up sequence and timing are unchanged.

## What a run can and cannot discriminate

| Hypothesis | Safe evidence in this run | Limit |
|---|---|---|
| Pack montage InputBuffer | Buffered input tag and active montage position around the original press/retry; compare the observed position with the saved montage's `ANS_InputBuffer` interval in `AA_A08_NOTIFY_FRAMES_TABLE.md`. | `Get Buffered Input Tag` reports buffered input, not the notify state's live open/closed flag. Correlation with montage time or a retry is not proof that the notify swallowed the original activation. |
| Started vs Triggered | `RPGDodgeTiming::TryBind` binds IA_Dodge to `ETriggerEvent::Started` (`RPGDodgeTiming.cpp:257-270`); the normal callback/press trace shows the project's Started path was reached. | There is no existing read-only callback reporting both Started and Triggered for one action instance. Adding a second Enhanced Input binding could change dispatch order/behavior, so no Triggered observer is added. Root cause remains unattributed. |
| Mapping-context re-add | `TryAddEldenRingContext` loads once, checks `HasMappingContext`, adds only when absent, then latches `bEldenRingContextAdded` (`RPGDodgeTiming.cpp:603-632`). Preserve the existing context-active log and fresh-process start state. | The probe has no reliable read-only active-context-change feed; removing/re-adding a context would modify the tested path. Static idempotent code plus no observed post-draw call is not proof of the pack's context behavior. |

The three hypotheses are independent and a passing retry does not resolve the underlying event path. A single clean process can capture the accepted first press plus repeats; a hypothesis-specific intervention or a second observer is not safe inside that same first-press run. Any future proposal to add a `Triggered` observer or mutate contexts requires a separately reviewed diagnostic build and a stated invalidation boundary.

## Review disposition

- C-1068's both-route standing/moving distances remain the accepted workaround evidence; this offline queue adds no new PIE result.
- KI-199 remains: workaround proven in PIE on both routes, standing and moving; root cause not isolated; package open.
- The probe is still default-wired/no-assignment and retains the current recovery. This is not a package test or proof of input-buffer, trigger-phase, or context behavior.
- `test_first_dodge_probe_observation_contract.py` checks the added observations and rejects activation/input-binding/context mutation in the probe.
