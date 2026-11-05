# V-C014 — Round 6 GPU pass capture sheet

## Purpose

Capture one reproducible Development `ProfileGPU` snapshot for context alongside the Round 6 per-run frame metrics. The snapshot diagnoses pass cost; it does not substitute for the 60-second repeated benchmark or establish an optimization's savings.

## Capture protocol

1. Use the Round 6 Development kit on the owner's console session, RTX 3060 proxy (record exact GPU/driver), 1920x1080, selected data route, and the accepted Round 6 mode/fraction. Preserve BUILD_INFO and CVar help output, including `r.DynamicRes.OperationMode=0`.
2. Confirm the first run has all three P2a summary fields before any treatment. Keep the corresponding `summary.json`, `game.log`, `frames.csv`, and GPU utilization/clock log.
3. After warm-up and during a representative steady-state fight, request `ProfileGPU` once through the existing Development benchmark path (`-RPGBenchmarkProfileGPUAt` where supported). Record the exact run label and trigger time/frame. Do not profile startup or a transition unless that is the stated question.
4. Save the complete GPU event tree/screenshot and raw log. Record pass names, inclusive/exclusive labels as shown, resolution, active upscaler, and primary fraction upper bound. Do not sum nested inclusive pass rows.
5. Repeat the capture at least once with the same build/settings if the first result is an outlier. A comparison between settings requires matched runs and the same capture point; use the regular benchmark suite for p99 and deltas.

## Receipt fields

| Field | Value to record |
|---|---|
| Build / engine / route | BUILD_INFO, UE 5.5.4, selected data route |
| Hardware / session | GPU, driver, console/RDP, resolution |
| Render state | temporal upscaler, AA method, primary fraction upper bound, DynamicRes operation mode |
| Capture location | run ID, trigger seconds/frame, fight phase |
| Raw evidence | game.log, ProfileGPU tree, summary, frames, GPU telemetry, hashes |
| Interpretation | top pass labels with their displayed inclusive/exclusive meaning; uncertainty and whether repeat agreed |

Do not change visuals or infer root cause from a single pass sample. Use timestamped Insights traces if pass-level timing must be correlated to a hitch.
