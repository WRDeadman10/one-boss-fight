# Queue V V-C002–V-C005 — Round 6 plan, guard, prompt, and intake

## Scope and status

V-C002–V-C005 prepare the Round 6 experiment and offline intake. C-924 accepted X-1287 after BUILD-229 GREEN 476/476; V-C001's build/review gate is closed. The live `pie_legend` legacy receipt is written and its data-route arm/comparison remains in progress. Codex did not change the Lead-corrected benchmark C++ or launch Unreal. The Phase 2 runner requires accepted Phase 1 and owner image-quality switches.

## Plan and preflight

`Scripts/round6_experiments.json` defines three repeats of DLSS Quality/Balanced/Performance, then a separate best-mode block of four individual treatments with three repeats each. Both phases include four TSR anchors at the P2a view-family primary resolution-fraction upper bound. This field is not a measured rendered-rectangle ratio; it is equal to the active primary fraction only with `r.DynamicRes.OperationMode=0`, which the owner preflight must verify. `Scripts/RunPerfExperiments.ps1` rejects a non-selected route, absent fight, virtual GPU, missing telemetry, mismatched fraction upper bound, unknown CVar, wrong active upscaler or NGX mode, anchor drift over 5%, and Phase 2 without both acceptance switches. DLSS treatment logs carry the creation/mode witness pattern. BUILD-229 compiled the telemetry and the suite is green, but a real benchmark has not yet witnessed the output fields; Antigravity must confirm them in the first kit run. The invalid volumetric-cloud scale CVar remains omitted; the two verified UE 5.5 cloud sample max-count CVars are not added because the Round 6 experiment request did not include them.

## Owner prompt

The Round 6 section of `Documentation/BENCHKIT_README.md` specifies session/GPU and build intake, selected route, one-at-a-time CVar preflight, P2a telemetry and active-mode proof, 13-row Phase 1, explicit owner image-quality gate, conditional 16-row Phase 2, retention/collection, and no nested `-ExecCmds` quoting. No result is guessed and no graphics default is chosen.

## Receipt intake

`Scripts/Tools/round6_benchmark_report.py` accepts a JSON receipt with phase, per-run measurements, CVar map, active upscaler proof, primary fraction upper bound, AA method, prediction estimate, and image-quality note. It rejects incorrect row/trial counts, missing/invalid measurements, four-anchor mismatch, TSR/DLSS upscaler mismatch, absent active creation log line, and missing telemetry. It reports medians, treatment deltas against the four-anchor TSR median, predicted versus measured GPU-average savings and prediction error. The tool does not mutate receipt files.

Prediction values must carry their source in the receipt author's accompanying notes; the intake computes measured GPU saving against the observed TSR median and does not treat the prediction as evidence. Build identity, machine identity, and image-quality conclusions must remain in the raw run bundle and owner report.

## Verification

Focused Round 6 receipt tests and script dry-runs are recorded in `Documentation/TEST_PLAN.md`. No Unreal, editor, game, or native build was run by Codex. The P2a C++ telemetry still needs the Lead's green compile before the owner starts Round 6.
