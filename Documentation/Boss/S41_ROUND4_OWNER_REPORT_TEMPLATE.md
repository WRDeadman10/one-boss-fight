# Round 4 owner report template

Fill this in only from the owner's retained Round 4 kit output. Keep the two build variants and each measured run distinct. A blank field means evidence has not been supplied; it is not a pass.

## Run identity

- Owner / machine:
- Capture date and local time:
- GPU / driver:
- Resolution / display mode:
- Package build IDs and hashes (Development, Shipping):
- Kit version / scripts-only patch applied:
- Encounter and route per run (legacy or selected data):
- Warm-up and run duration:
- Raw output directory:

## Results

| Variant / run | Avg FPS | p99 frame time (ms) | Startup / selection | Gameplay result | Log / receipt path |
|---|---:|---:|---|---|---|
| Legacy / 1 | | | | | |
| Legacy / 2 | | | | | |
| Legacy / 3 | | | | | |
| Selected / 1 | | | | | |
| Selected / 2 | | | | | |
| Selected / 3 | | | | | |

## Gate interpretation

- Target: packaged 1920×1080, average at least 60 FPS, p99 at most 16.67 ms on RTX 2060 Super or the owner-approved RTX 3060 stand-in.
- Selected-route p99 is at most 0.5 ms worse than the comparable legacy average p99: PASS / FAIL / UNKNOWN
- Every run has `fight_started=true` and its `gpu` field matches the reported physical NVIDIA card: PASS / FAIL / UNKNOWN
- Round 4 comparison valid (same machine, resolution, duration, warm-up, and encounter): Yes / No / Unknown
- Any failed or missing run and exact reason:
- Shipping startup, selector behavior, recovery, and log checks:
- Benchmark tool/comparator version and invocation:
- Evidence hashes verified:
- Owner conclusion / decision needed:

Do not infer a missing value from a screenshot or another run. Attach the raw log and generated receipt for every row before marking a gate passed.
