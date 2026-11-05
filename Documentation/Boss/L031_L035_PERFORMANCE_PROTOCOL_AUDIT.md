# Queue L Batch 7 — packaged performance protocol and metrics

## Existing target and method

- Product target remains a packaged 1920×1080 full-encounter run on RTX 2060
  Super, average at least 60 FPS, p99 frame time at most 16.67 ms. 120 FPS / 8.33
  ms is stretch telemetry only. A 3060 is documented as a proxy, not target pass.
- `GATE4_RUNBOOK.md` specifies an active Windows `console` session, one
  disposable warm-up fight, then three recorded baseline fights on the same
  hardware/map/launch mode/CVars. Each benchmark discards 5 seconds and records
  60 seconds. Validate the GPU and `fight_started` from each run.
- This is an existing baseline protocol, not an owner-approved selected-route
  cold/warm protocol. Cold/warm definitions/counts, current selected content
  identity, and memory collection method remain unfrozen.

## Task disposition

| Task | Status | Result |
|---|---|---|
| L031 | **PARTIAL — OWNER + CLAUDE** | Existing target and baseline run method are recorded; selected-route cold/warm protocol, target adapter/session confirmation, and memory method/counts still need explicit agreement. |
| L032 | **LEAD-RUN BLOCKED** | No comparable packaged legacy cold/warm samples with current build/content/log identities are present. |
| L033 | **LEAD-RUN BLOCKED** | Selected G044 package/cook and matched inputs are absent. |
| L034 | **TOOL READY; NO RECEIPT** | Added `Scripts/Tools/summarize_packaged_metrics.py`. It validates per-run build/binary/content/settings/input/map/launch/hardware/CVar identity, unique run/sample IDs, per-metric scope/unit, raw-log SHA-256, and summarizes nearest-rank p50/p95/p99 separately by cold/warm phase and metric. It sets no budgets, never merges distinct metric scopes, and refuses report destinations that alias evidence inputs by path or hard link. |
| L035 | **OWNER-GATED** | No new numeric budget or no-budget disposition is inferred. |

The generic metric list is declared in each receipt's `required_metrics` array;
the owner/Lead must choose a memory metric and capture method before declaring
memory complete. The tool validates cited log bytes but does not parse logs or
prove that a supplied metric value was measured from them. Missing/mixed run
identity, missing metrics, absent phase, or absent raw logs produce
INCONCLUSIVE. No benchmark samples were created; no tests, build, package, or
Unreal execution was run.
