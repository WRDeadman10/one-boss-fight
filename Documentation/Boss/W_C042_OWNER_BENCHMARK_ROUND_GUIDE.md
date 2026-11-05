# Owner guide: running a benchmark round

This is a short operator checklist for the owner and Claude on the benchmark PC. Follow the detailed current Round 6 instructions in `Documentation/BENCHKIT_README.md` rather than reconstructing commands from memory.

## Before launching

1. Use a validated, identity-stamped Round 6 kit. The last risk register says the available R6 kit failed its required support-file/build-stamp check; do not run until Claude repairs it and `check_bench_kit.py` passes (`Documentation/Boss/V_C098_CURRENT_RISK_REGISTER.md`, Kit provenance row).
2. Sit at the physical console. Capture `query user` and `nvidia-smi` output (GPU name, driver, and pre-run utilization). Stop if the session is Remote Desktop, the GPU/build identity is wrong, or another heavy process is using the GPU (`Documentation/BENCHKIT_README.md`, Round 6 steps 1–2).
3. Close other GPU-heavy apps. Keep the kit's `Saved` content intact. Do not change drivers, Windows settings, assets, or project settings during the benchmark (`BENCHKIT_README.md`, Round 6 introduction and steps).
4. Confirm the staged Development build and selected-data route. Keep the build ID, resolution, route-selection line, and raw preflight log with the results (`BENCHKIT_README.md`, Round 6 steps 2–4).

## Run and return

1. Run Round 6 Phase 1 exactly as the readme specifies, including its dry run, measured TSR fraction from the P2a receipt, and all 13 anchor/treatment rows. Do not subset the ordered experiments. Stop on unknown CVars, wrong upscaler/mode/fraction, invalid fight/GPU, anchor drift, or runner refusal.
2. Do not start Phase 2 unless Phase 1 has three valid witnesses for the candidate, the Lead accepts the receipt, and the owner accepts image quality. The Phase 2 command requires explicit mode/fraction and both acceptance flags.
3. Preserve per-run `summary.json`, `game.log`, frame CSVs, console/CVar help, and exact errors. Never silently replace failed runs or edit files inside `Saved`.
4. Run `Scripts\BenchKit_Collect.ps1`, return its zip path and size plus the written report, and leave the project defaults unchanged. The development PC validates the bundle before any decision or tuning.

## What the results can establish

Report GPU/driver/session, build and route identity, each run's averages and p99, active upscaler/mode evidence, primary fraction upper bound, CVar map, failures, and image-quality notes. Do not call the view-family primary fraction a measured rendered rectangle. A measured candidate remains a proposal until image quality and confirmation are accepted; the release target is 1920×1080, average at least 60 FPS and p99 at most 16.67 ms (`BENCHKIT_README.md`, target and Round 6 steps 4–8; `PERFORMANCE_DECISION_BRIEF_ROUNDS_1_6.md`, final paragraph).
