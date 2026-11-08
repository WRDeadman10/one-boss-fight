# AR-C11–C15 — KI-199 first-dodge input-path audit

Status: static audit complete. The available project source describes the project's dodge callback, its one-shot fallback, and a separate Elden Ring attack-input replay path. It does not expose the pack's internal input-buffer decision or prove why the original first dodge sometimes failed. KI-199 remains PIE-workaround-proven, root cause unisolated, and package-open.

## C11 — Project input and retry path

| Stage | Source evidence | What it establishes |
|---|---|---|
| Dodge binding | `RPGDodgeTiming.cpp:258–272` | The component binds the configured pack dodge action to `ETriggerEvent::Started` and `OnDodgePressed`, once a pawn Enhanced Input component/action is available. This is the project's callback boundary; it does not report the action's other trigger events. |
| First-press trace | `RPGDodgeTiming.cpp:507–548` | When that callback is reached, the first press queries the pack ability's `Can Activate Ability?`, records the result/time, and logs active state, stamina and guard state in Development. A missing callback cannot produce this trace. |
| Next component tick | `RPGDodgeTiming.cpp:142–187` | On a later world tick, a one-shot retry is eligible only for press 1 when the recorded CanActivate is true, the ability is still inactive, and retry was not already attempted. It calls `TryActivateAbilityByClass` with force false. |
| Buffer consume | `RPGDodgeTiming.cpp:160–172,347–365` | After the retry, the project consumes the Dodge buffer tag only if activation succeeded or the ability is now active. The roll path also marks that tag consumed (`:442–454`). These project calls do not reveal how the opaque pack buffer chose or rejected the original request. |
| Elden Ring attack route | `RPGDodgeTiming.cpp:603–629,632–679` | The mapping-context helper attempts to add the configured context if absent and then latches its own `bEldenRingContextAdded`; action binding uses Triggered for project light/heavy-tap actions and injects the pack attack actions. This is distinct from the dodge action's Started binding. The latch/log is not a live feed of subsequent subsystem context changes. |

## C12 — Pack boundary and observability

`BP_InputBufferComponent_C` is found by class name and called through reflected Blueprint functions (`RPGDodgeTiming.cpp:347–365,442–454`). `Scripts/Editor/probe_first_dodge_after_draw.py:43–50,102–125` can read `Get Buffered Input Tag`, then sample montage name/position and movement. The readout is a tag snapshot, not the notify state's live open/closed buffer window, and it cannot show why activation was swallowed. The pack implementation is not present as inspectable project C++ in this audit; no internal behavior is inferred from class/API names.

## C13 — Evidence reconciliation

| Receipt | Supported statement | Limit |
|---|---|---|
| C-1061 | First standing dodge after R2 draw failed in 2/2 observations. | Reproduction only; not a mechanism diagnosis. |
| C-1063 / BUILD-261 | Preload/map-prime attempt still failed. | The attempted intervention did not resolve the symptom; it does not isolate a trigger or buffer cause. |
| C-1065 / BUILD-262 | `CanActivate=true` was logged, but the ability was inactive on the next tick; later presses worked. | Rules out a CanActivate rejection in that sampled state only; the report itself says it cannot separate buffer swallow from Enhanced Input trigger/context reset. |
| C-1067 / BUILD-263 | The guarded non-forced one-shot retry passed the reported standing and moving first-use cases on both routes; repeats worked and no duplicate was reported. | Demonstrates the workaround in those PIE cases, not the cause and not package behavior. |

Primary reconciliation: `KNOWN_ISSUES.md:342–343`, `AN_C1065_FIRST_DODGE_RETRY_HOTFIX.md` (“Evidence and bounded change”, “Lead validation”), and `AO_C21_C25_FIRST_DODGE_DIAGNOSTIC_HANDOFF.md:9–17`. These agree that root cause remains unisolated and package proof stays open.

## C14–C15 — Falsifiable next observation and boundary

Use the existing Lead-owned probe in a fresh PIE process for each route. Preserve the current input sequence and runtime defaults. Capture the route/build, context-active readout, first press count, existing `first_dodge_activation_trace`, next-tick retry result, buffer-tag snapshots, montage/position, movement and repeats. Compare the first standing-after-draw case with the existing moving-first and repeat controls. A missing `OnDodgePressed` trace localizes the failure before the project callback; a reached callback with CanActivate true/inactive next tick followed by retry success localizes the symptom after that callback. Neither alone attributes the failure to the pack buffer, Enhanced Input trigger phase, or a context reset. Any such attribution requires a Lead-available, read-only observation of those internals; do not add a second action binding, consume input, force activation, change context, insert delay, or tune the retry as part of this audit.

The probe is a state-changing Lead PIE driver (it enters combat, draws the weapon, and sends key input); only its described observations are read-only. No PIE was run by Codex. No source or probe was changed. No root cause is claimed.

## AR-C06–C10 receipt-tool review follow-through

Claude's C-1094 requests that the receipt reader accept structured hold rows embedded in existing `P_*` Unreal logs, alongside logger prefixes such as `[Showcase]`/`[CamEngage]` and unrelated `LogRPG*` rows, and that one exact runner specification be given at AR-C10. The parser matches the structured sample payload independent of timestamp/category/prefix, but the previous contract only proved a simplified ERControlLatency fixture and its handoff misplaced the Lead rerun instructions. Added a prefixed Unreal-log fixture with unrelated `LogRPGDodge` output; the runner spec is consolidated below and in `AR_C06_C10_KI192_RECEIPT_TOOL.md`.

### Lead runner specification (not executed by Codex)

- **Routes:** `legacy` with `H019_ENCOUNTER_DEFINITION` unset; `data` with `/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter` set before Editor startup. Confirm each log's emitted route before interpreting it.
- **Repetitions:** five fresh Editor processes per route; each process runs the existing four R2 hold cases (0.34, 0.35, 0.36 and 0.70 seconds) once, giving five independent observations per hold/route. Do not loop cases in one process and call them independent runs.
- **Environment:** `L_SevarovArena`, same Lead-controlled machine/configuration, Editor launched with `-nosound`; use the existing `run_probe.ps1` operational safeguards and retain a separate immutable raw log per route/repetition. Record build ID, route, process/run label, environment, and raw-log SHA-256 with each receipt.
- **Parser:** invoke `python Scripts/Tools/ar_charge_receipt.py <one-route-raw-log> --build-id <Lead-reported-build-id>` once per file. The parser expects one sample for each four-case matrix, rejects duplicates/missing/malformed samples and mixed/missing routes, tolerates timestamp/category/logger prefixes and unrelated `LogRPG*` lines, and reports game-tick-bounded observations (not device latency). Never supply a placeholder build ID for an actual Lead run.
- **Stop/return:** stop a run if route/build identity is absent, `input_context_active` is false, a required sample/montage/tick field is missing, or the process does not report normal completion. Return all ten raw logs and ten parsed JSON receipts plus the exact build/config/run manifest; do not discard an outlier. This is a measurement plan, not a threshold change or root-cause claim.

## Validation and disposition

Offline parser contracts now include the existing timestamped Unreal-log envelope, `[Showcase]` and `[CamEngage]` categories, and unrelated `LogRPGDodge` output. Re-run results are recorded in the mailbox completion. No raw run evidence, Source file, asset, Editor state, or runtime result was changed by Codex.
