# Queue K K031–K035 — selected-route performance evidence readiness

## K031 — existing target versus missing run protocol

The project target is packaged 1920x1080, average at least 60 FPS and p99 frame time at most 16.67 ms during the full encounter; 120 FPS / 8.33 ms is stretch telemetry only (`PERFORMANCE_LOG.md`, `DECISIONS.md`, and current project instructions). The target GPU is RTX 2060 Super. `PERFORMANCE_LOG.md` records a 5 s warmup and 60 s measurement for earlier benchmark runs, but that does not establish an approved cold/warm sample count or selected-route protocol. Prior readings from an RDP remote-display adapter are invalid for GPU target claims; the log requires the NVIDIA adapter to be identified.

Thus K031 is **PARTIAL / OWNER + CLAUDE**: target resolution/rates/hardware are documented; sample count, console-vs-RDP execution, cold/warm split, selected-run identity, memory collection and repeat pairing still need to be frozen before capture. Do not infer a selected-route budget from CPU instrumentation.

## K032–K035 disposition

- **K032–K033 LEAD-RUN BLOCKED:** no packaged selected route or current typed selection/cook exists; cold/warm samples require distinct IDs, binary/content hashes and raw-log hashes.
- **K034 TOOL READY / NO RECEIPTS:** `Scripts/Tools/summarize_encounter_cost.py` computes nearest-rank p50/p95/p99 separately by cold/warm class and rejects missing/mixed build/binary/content identities. It does not establish memory or a performance pass.
- **K035 OWNER GATE:** no selected-route budget is proposed. Decide only after comparable target/proxy samples, agreed method and memory evidence; absent disposition leaves the performance gate open.

No performance run or sample was created. Static review only; no tests, build or Unreal execution.
