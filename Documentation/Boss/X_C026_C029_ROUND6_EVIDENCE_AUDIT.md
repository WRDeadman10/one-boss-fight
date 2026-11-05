# Queue X X-C026-X-C029 — Round 6 evidence intake and metric separation

Date: 2026-11-06. Read-only reconciliation of returned evidence folders and current performance documents. No benchmark, game, Editor, build, or package run.

## X-C026 — returned Round 6 bundle availability

No Round 6 return bundle is present. `Saved/bench_return/` contains `r1`, `r2`, `round4_20261105`, and `round5_20261105`; no R6 folder. The R6 transfer directory contains only the kit ZIP and staged kit directory; no owner run outputs were found in the kit's stage Saved/Benchmark locations. **WAITING ON LEAD/owner** for C026 intake; continue other unblocked tasks.

## X-C027 / X-C028 — raw-run recomputation and mode witnesses

No R6 per-run `summary.json`, `frames.csv`, or `game.log` bundle exists in the return folder or transfer kit. Therefore per-mode medians cannot be recomputed and treatment labels cannot be checked against active DLSS log witnesses. Both tasks remain **WAITING ON LEAD/owner evidence**; no R5 data was substituted for R6, and no inference was made from the current runner, plan, or kit contents.

## X-C029 — measured values, predictions, and diagnostic fields

| Field | Current documented meaning/status |
|---|---|
| Average FPS and p99 | Round 4/5 historical measurements are recorded in `PERFORMANCE_LOG.md`; no R6 measurement exists. |
| GPU average/p99 | Required per-run R6 measurements in `round6_benchmark_report.py:13,70-79`; absent without returned run summaries. |
| Predicted GPU saving | A separate input used by the report; not a measured result. Source handling is under-specified between the transferred README and V-C002, as recorded in the X-C021..24 audit. |
| Measured GPU saving | Computed from observed TSR median GPU-average time minus treatment median (`round6_benchmark_report.py:100-108`); cannot be computed without raw R6 runs. |
| `effective_primary_screen_percentage` | View-family primary resolution-fraction upper bound; not measured rendered-rectangle percentage. Requires `r.DynamicRes.OperationMode=0` to equal the active primary fraction (`PERFORMANCE_LOG.md` Round 6 prep, `V_C002_C005_ROUND6_INTAKE.md:9`). |
| ProfileGPU capture | Diagnostic pass-cost context only; it does not replace repeated benchmark timing or establish savings (`V_C014_ROUND6_GPU_CAPTURE_SHEET.md:5`). |
| Combat latency / feel | W-C036–W-C039 separates configured timing from actual response/latency capture; no reaction-window or feel measurement is inferred from tracker values. |

The checked Round 6 documents keep historical R4/R5 measured values, future Round 6 acceptance gates, and predictions separate. No internal contradiction was found in `PERFORMANCE_LOG.md`, V-C002 intake, V-C014 capture sheet, V-C017 image-quality checklist, and W-C036–W-C039 sheets. None asserts a completed Round 6 result.

## Disposition

C026-C028 remain blocked on return evidence; C029 is complete with explicit units and evidence boundaries. Do not promote R5 results, predicted savings, telemetry fields, or ProfileGPU samples into Round 6 measurements. No source or evidence files were changed.
