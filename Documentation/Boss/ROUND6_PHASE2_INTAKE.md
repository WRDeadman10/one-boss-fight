# Round 6 Phase 2 intake

## Status

Awaiting the Phase 2 return bundle from the benchmark PC. Do not enter or infer results before its receipt arrives. Phase 2 uses the owner-selected DLSS Performance base; the selection is not a shipped default (C-951).

## Bundle identity

- Source archive: ______________________________
- Archive SHA-256: ____________________________
- Development build ID: _______________________
- Machine / GPU / driver: ______________________
- Selected route and fight-start evidence: ______

## Receipt validation

Run `python Scripts/Tools/round6_phase2_intake.py <receipt.json>`. The gate checks the Phase 2 schema shape, all planned rows, the owner-selected Performance mode and primary fraction, exact R6b Development build ID `OBF-DEVELOPMENT-20261106T071240Z-ed06b4d6`, and a per-treatment `NGXPerfQuality=MaxPerf` creation witness. If the returned bundle names another build, stop intake and reconcile it against that build's `BUILD_INFO.txt` before accepting rows. Keep the source summaries and game logs with the return bundle.

## Results

| Arm | Trials | Avg FPS | p99 ms | GPU avg ms | GPU p99 ms | Mode witness | Image-quality note |
|---|---:|---:|---:|---:|---:|---|---|
| TSR anchor | — | — | — | — | — | — | — |
| Performance base + `rpg.Perf.FireShadows=4` | — | — | — | — | — | — | — |
| Performance base + `rpg.Perf.FireShadows=0` | — | — | — | — | — | — | — |
| Performance base + `rpg.Perf.FireRadiusScale=0.65` | — | — | — | — | — | — | — |
| Performance base + `r.SkyLight.RealTimeReflectionCapture=0` | — | — | — | — | — | — | — |

## Interpretation and gate

- Verified valid rows: _________________________
- Baseline drift / comparison: _________________
- Does any measured configuration meet both release performance limits? ______
- Owner image-quality disposition: _____________
- Recommendation and remaining evidence: _______

Do not change a shipped graphics default from this intake alone. Record whether the data supports an owner-approved candidate, and retain the fallback and packaged-validation requirements.
