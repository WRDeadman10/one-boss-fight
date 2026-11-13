# Queue BI X01–X05 — Benchmark Receipt Schema Draft

Date: 2026-11-11  
Status: offline proposal only. The benchmark runner and existing receipt formats are unchanged; Lead adoption is required before any captured result uses this as an acceptance contract.

## X01/X04 — Existing producer and consumer map

`RPGBenchmarkRunner.cpp` writes `summary.json` plus `frames.csv`. The summary contains map, fight mode/start flag, engine and build configuration, cvars, GPU/driver, CPU/RAM/OS, resolution, warm-up/duration/sample count, average and frame p95/p99/max, budget misses, thread/GPU aggregates and the Round 6 view metrics. It does not embed source revision/tree, build ID or binary/package hash, host/session type, route witness, run-level artifact hashes, or a runner hash. `SummarizeBenchmark.py` marks remote/virtual GPU names invalid and reports target status, but does not require those missing provenance fields.

Different existing receipt layers provide different coverage. D145's 59 legacy/R1/R2 summary files have no per-run host/session/build ID/binary hash. The Round 4 custom intake validates a per-run build ID/hash, session type, hardware, map/route, warm-up/duration, and summary/frame paths and hashes. Round 6 v1 has a parent build ID and archive SHA-256 plus unique run IDs and source-summary paths; per-row scenario metrics/mode witnesses are present, but the row itself is not a complete build/device/session/artifact identity record. These formats must not be described as equivalent.

## X02 — proposed v1 schema

`BENCHMARK_RUN_RECEIPT_V1.schema.json` is a JSON Schema draft for one immutable measurement. It binds runner and authorization; source revision/tree; build configuration/ID/binary and package manifest hashes; engine; scenario and route witness; device/session/target class; capture interval and sample count; raw artifact paths, byte counts and SHA-256; performance metrics; and a separate validity verdict. The schema intentionally requires explicit context instead of treating absent or inferred fields as known. `validity.verdict` may remain `not_validated`; schema conformance alone does not make the run acceptable.

The canonical acceptance target must be supplied by project policy at validation time: current target is packaged 1920x1080 full fight, average >=60 FPS and whole-frame p99 <=16.67 ms on RTX 2060 Super. The schema does not encode proxy substitution, run-count policy, or phase-specific acceptance. Session type `unknown` is syntactically representable so intake can preserve uncertainty, but a strict acceptance validator must reject it for target claims.

## X03 — fixture plan (not implemented or run)

Proposed positive fixture: all required identities, hashes, absolute/relative artifact references under a declared receipt root, nonzero measured duration/frame count and explicit `not_validated` verdict. Negative cases: missing binary hash; empty build ID; malformed SHA-256; remote GPU/session for target claim; absent route witness; zero frames; non-UTC timestamp; path traversal or resolved symlink escape; `fight_mode=true` with `fight_started=false`; artifact byte/hash mismatch; p99 target pass claimed while average misses; and `validity=valid` with nonempty invalid reasons. No fixture code was added and no test was run.

## X05 — scope and handoff

This draft does not alter `RPGBenchmarkRunner`, the existing R4/R6 schemas, prior evidence, or project defaults. Lead must decide whether to adopt one canonical schema, add a converter for older receipts, and define strict acceptance checks (including minimum sample count, route witness, console session, target/proxy classification and hashes). Round 6 Phase 1 remains accepted RTX 3060 proxy evidence only; Phase 2 remains parked under C-954. Report does not establish an RTX 2060 Super result.
