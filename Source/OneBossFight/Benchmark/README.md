# Benchmark module

`FRPGFrameStats` computes frame-time summaries; `ARPGBenchmarkRunner` collects and writes a repeatable camera-orbit run. The release gate is average FPS at least 60 and P99 frame time at most 16.67 ms. 120 FPS is stretch telemetry (`RPGFrameStats.h:8-12,35-48`).

## Run flow

Place a runner in a test map or use `bAutoStart`, then launch with `-RPGBenchmark`; `-RPGBenchmarkQuit` exits after completion (`RPGBenchmarkRunner.h:12-18`). It removes the frame-rate cap/VSync, discards warmup, captures frame times, restores the original cap state, and writes `frames.csv` plus `summary.json` under `Saved/Benchmark` (`RPGBenchmarkRunner.cpp:62-152,313-345,416-459`). `StartBenchmark` ignores duplicate starts; an early abort does not publish completed results (`RPGBenchmarkRunner.h:28-37`).

`FRPGFrameStats::Compute` filters invalid samples, calculates percentiles and budget misses, and `MeetsTarget` checks both the average-FPS and P99 gates (`RPGFrameStats.cpp:8-74`).

## Project scripts and limits

Use `Scripts/RunBenchmark.ps1`, `Scripts/SummarizeBenchmark.py`, and `Scripts/CheckShippingBinary.py` per the Gate 4 runbook. A valid hardware run needs an active local session, target resolution/settings, the named GPU in summary output, warmup, and comparable repeated samples. The C++ component's existence alone is not a performance result.
