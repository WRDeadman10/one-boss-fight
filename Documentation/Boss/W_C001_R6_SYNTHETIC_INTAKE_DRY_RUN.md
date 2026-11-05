# W-C001 Round 6 synthetic return intake dry run

Synthetic only: a temporary ZIP was assembled from the retained Round 5 return layout (8,239,044 bytes across its source files) plus a test-generated 13-row Phase 1 receipt containing `temporal_upscaler`, `effective_primary_screen_percentage`, and `anti_aliasing_method`. The Round 6 report validator read the receipt from the ZIP and emitted three mode rows (Quality, Balanced, Performance) with zero exceptions. The synthetic ZIP lived in a temporary directory and was removed automatically. No Round 6 measurements, owner choices, game run, or GPU result are represented.

Round 6 phase1 — medians; deltas vs four-anchor TSR median
| Mode | Trials | Avg FPS | p99 ms | GPU avg ms | GPU p99 ms | Active DLSS proof | Δ avg FPS | Δ p99 | Pred. GPU ms saved | Measured GPU ms saved | Error ms |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| Quality | 3 | 40.0 | 30.00 | 28.00 | 29.00 | yes | +33.33% | -25.00% | 8.00 | +10.00 | +2.00 |
| Balanced | 3 | 42.0 | 30.00 | 27.00 | 29.00 | yes | +40.00% | -25.00% | 10.00 | +11.00 | +1.00 |
| Performance | 3 | 42.0 | 30.00 | 27.00 | 29.00 | yes | +40.00% | -25.00% | 10.00 | +11.00 | +1.00 |
- Quality trial 1 image-quality note: Observed clear edges
- Quality trial 2 image-quality note: Observed clear edges
- Quality trial 3 image-quality note: Observed clear edges
