# Queue BE — Codex engineering batches

Revised under Claude C-1274/C-1275 after BD-X01–X40. Work test-first in five-task batches. Run a task-specific C-1155 locked Development build and pinned full suite after each source batch, then post READY. The data-route default remains unchanged; framework definition selection is opt-in and default-off. Claude owns acceptance builds, saved asset authoring, and final live acceptance. Never overlap engine use.

## Priority unblocker — C-1275a (before Batch 1)

| Task | Files | Acceptance |
|---|---|---|
| C-1275a: add editor-only C++ montage notify readback (class, trigger time, duration, notify track index, slot, segment animation path and length); fix the readback driver's `Scripts/Editor` import path; run source → transient wrapper → target readback with no saves | `RPGMontageWrapperLibrary.*`, `RPGMontageWrapperLibraryTests.cpp`, `Scripts/Editor/author_greystone_player.py`, `Scripts/Editor/verify_greystone_wrapper_readback.py` | **COMPLETE — Codex READY**; locked build + pinned suite 506/506; all four transient source/target comparisons pass; zero saves; both locks released. Claude's `--write` and saved-package readback remain separate. Receipt: `Documentation/Boss/C1275A_TRANSIENT_NOTIFY_READBACK.md` |

## Batch 1 — framework health/HUD/death integration (C-1274a)

| ID | Task | Files | Acceptance |
|---|---|---|---|
| BE-X01 | Add encounter health-provider seam for pack attributes and native framework health | RPGNativeBossHealth, RPGBossHud | Test pack/native providers and invalid, missing, zero-max states |
| BE-X02 | Bind framework boss to HUD only as selected participant | player attachment, encounter binding, HUD | Same-world/generation checks; default pack attachment unchanged |
| BE-X03 | Deliver framework terminal state to encounter completion once per generation | framework boss, encounter | Test duplicate death and stale generation rejection |
| BE-X04 | Route victory/music/retry through existing encounter/HUD owner | encounter, HUD | One completion; preserve existing retry authority and victory latch |
| BE-X05 | Define/test reset and replacement generation ownership | selection/binding/framework tests | Monotonic generation, stale callback refusal, cleanup; test-first |

## Batch 2 — default-off framework encounter selection (C-1274b) — SOURCE READY

| ID | Task | Files | Acceptance |
|---|---|---|---|
| BE-X06 | Allow selected definition to describe a framework boss | definition, selection subsystem | Explicit opt-in only |
| BE-X07 | Preserve pack selection and no-selection legacy behavior | selection tests | Existing route and defaults unchanged |
| BE-X08 | Add default-off definition CVar gate for framework encounter selection | selection/config/tests | Unset/0 does not select framework boss; no project default change |
| BE-X09 | Bind framework boss and possessed player to one validated generation | selection/binding | Reject mixed route and malformed census before mutation |
| BE-X10 | Add selection tests for opt-in, refusal, pack regression | native selection tests | Deterministic fixtures; no content assets |

## Batch 3 — autonomous selector-driven test route (C-1274c) — SOURCE READY

| ID | Task | Files | Acceptance |
|---|---|---|---|
| BE-X11 | Separate test initialization from forced-card startup | framework test bridge | Selector remains enabled in autonomous test mode |
| BE-X12 | Add test-only autonomous start through production selector | framework/executor | No explicit card ID; record selected move, phase, generation |
| BE-X13 | Build bounded selector-driven live test driver | Sevarog Editor driver | Route witness, card/time cap, counters, cleanup and no-save |
| BE-X14 | Cover no-candidate, cooldown and terminal outcomes | native tests/driver contract | Fail closed; no forced-ID fallback |
| BE-X15 | Verify HUD/death/retry on autonomous route | driver/tests | One outcome and one new generation; Lead acceptance separate |

## Batch 4 — navigation failure diagnostics (C-1274d) — SOURCE READY

| ID | Task | Files | Acceptance |
|---|---|---|---|
| BE-X16 | Capture FPathFollowingResult code/flags on completion | framework controller | Stable result fields for success and failure |
| BE-X17 | Log terminal actor/goal position and remaining distance | controller/proof fixture | Include route/generation identity; no per-frame spam |
| BE-X18 | Add result formatting/diagnostic tests | rules/tests | Success, invalid, blocked, aborted cases |
| BE-X19 | Expose navigation result in Lead live-run summary | Sevarog driver | Missing result fails closed |
| BE-X20 | Draft one-run navigation diagnosis checklist | report/TEST_PLAN | Recast, projection, path result, terminal position and actor IDs |

## Batch 5 — Shipping reflection boundary (C-1274e) — SOURCE READY

| ID | Task | Files | Acceptance |
|---|---|---|---|
| BE-X21 | Guard resolver test UFUNCTION declarations | RPGDamageResolver | Test nodes not reflected in Shipping; production API unchanged |
| BE-X22 | Guard framework test bridge declarations consistently | framework boss | Retain Development tests, hide test declarations from Shipping |
| BE-X23 | Inventory remaining test-only reflected functions | dodge/i-frame/parry headers | Function-to-target reflection policy table |
| BE-X24 | Add offline guard/declaration parity contracts | source contract tests | Catch unguarded hooks and stub drift |
| BE-X25 | Prepare Lead UHT/Shipping proof checklist | TEST_PLAN/report | Exact evidence fields; no local Shipping claim |

## Batch 6 — approved Sevarog S1/S2 range update — SOURCE READY

| ID | Task | Files | Acceptance |
|---|---|---|---|
| BE-X26 | Apply C-1274-approved 90–120 cm range to Swing1/Swing2 only | Sevarog authoring source | Windows unchanged; exact two rows |
| BE-X27 | Recalculate light punish margin | plan/validator | +0.353 with inputs/source |
| BE-X28 | Add validator bounds tests | validator/tests | Exact card IDs and inclusive limits |
| BE-X29 | Run no-save authoring dry-run | task-specific dry-run | PASS, no asset create/save; receipt includes both values |
| BE-X30 | Prepare Lead authoring/live retest handoff | TASKS/TEST_PLAN/report | READY; Lead authors and answers open S2 reach |

## Batch 7 — optional effect follow-through — SOURCE/TEST READY

| ID | Task | Files | Acceptance |
|---|---|---|---|
| BE-X31 | Inspect C-1274 BUILD-296 acceptance feedback before overlap edits | mailbox/status | Do not edit while Lead build is active |
| BE-X32 | Hotfix bounded AreaEffect/ChannelDrain rejects | rules/source/tests | Test-first; only explicit rejection |
| BE-X33 | Cover abort/reset/EndPlay cleanup gaps | add-on tests | Deterministic cleanup cases |
| BE-X34 | Verify capped heal uses accepted damage | channel rule/executor/tests | Damage and max-health boundary cases |
| BE-X35 | Locked Development build and pinned suite | runner/receipt | Both locks, pinned hash, exact result and owner token |

## Batch 8 — owned-tag cleanup resilience — SOURCE/TEST READY

| ID | Task | Files | Acceptance |
|---|---|---|---|
| BE-X36 | Inspect Lead retry-owner feedback before cleanup edits | mailbox/status | No overlapping work during BUILD-296 |
| BE-X37 | Cover invulnerability-tag retry and owner lifetime | cleanup helper/i-frame tests | Invalid owner, transient failure and retry results |
| BE-X38 | Cover parry-tag EndPlay deferred cleanup | cleanup helper/parry tests | Idempotence and stale generation |
| BE-X39 | Fix reproducible ownership/policy defects | helpers/tests | Test-first, minimal change |
| BE-X40 | Locked Development build and pinned suite | runner/receipt | Exact command, lock owner, hash and totals |

## Batch 9 — review, evidence intake, successor queue — COMPLETE (documentation only)

| ID | Task | Files | Acceptance |
|---|---|---|---|
| BE-X41 | Inspect Lead feedback on BE-X01–X40 | mailbox | Verdict matrix; continue without waiting |
| BE-X42 | Hotfix bounded rejects first | rejected files | Focused verification and READY follow-up |
| BE-X43 | Inventory new Lead evidence without raw-output access | mailbox/TEST_PLAN | Path, run/build/hash, route, status only |
| BE-X44 | Sync accepted work and open gates | TASKS/TEST_PLAN/PROJECT_STATE/KNOWN_ISSUES | Consistent ownership and status |
| BE-X45 | Draft next engineering queue | QUEUE_BF.md | Ten five-task batches, scoped files and acceptance |

## Batch 10 — closeout — COMPLETE (source/build evidence reconciled; Lead gates remain open)

| ID | Task | Files | Acceptance |
|---|---|---|---|
| BE-X46 | Reconcile framework integration results | report/TEST_PLAN | Source/native claims separate from Lead acceptance |
| BE-X47 | Reconcile opt-in selector/autonomous driver | report/TASKS | Default unchanged; forced ID not called autonomous |
| BE-X48 | Reconcile path diagnostics and Lead retest | report/KNOWN_ISSUES | Close root cause only on decisive run |
| BE-X49 | Reconcile Shipping/UHT and card-range handoff | report/TEST_PLAN | Development distinct from Shipping/asset authoring |
| BE-X50 | Publish closeout with exact batch build/suite receipts | TASKS/TEST_PLAN/PROJECT_STATE | Batch acceptance listed; no commit/push |

## Engine and ownership gates

Every authorized engine use follows C-1155: task-specific runner, both locks, no active UnrealEditor process before acquisition, owner-token-safe release, and pinned DD27j hash for suites. Do not overlap Claude's BUILD-296/asset-authoring/acceptance run. No default route change, pack asset edit, unapproved authoring, commit or push.
