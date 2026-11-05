# V-C011 — Performance preset proposal (Round 5 evidence; Round 6 pending)

## Disposition

Proposal only. Do not apply it to project defaults, a packaged profile, or `GameUserSettings`. Round 5 establishes a repeatable mode comparison on the RTX 3060 proxy, but Round 6 has not yet measured or selected a mode, and the owner has not accepted image quality. V-C012's A/B switch must remain gated on explicit measured values; no preset values are asserted here.

## Evidence available

Round 5 used BUILD-224 Development, the selected data route, 1920x1080, RTX 3060, driver 610.88, 16 runs, with baseline drift <=4.1%. Median avg FPS / p99:

| Mode | Avg FPS | p99 ms | Evidence and limits |
|---|---:|---:|---|
| TSR anchor | 28.6 | ~41.6 | Reference for Round 5 only |
| DLAA, 100% | 21.0 | 55.6 | Slower than anchor |
| DLSS Quality, 66.7% | 32.6 | 36.5 | Candidate; active mode later proven from archived logs |
| DLSS Balanced, 58% | 36.4 | 32.9 | Candidate; no image-quality acceptance recorded |
| DLSS Performance, 50% | 38.1 | 31.9 | Highest average in this set; no image-quality acceptance recorded |

Source: `Documentation/PERFORMANCE_LOG.md` Round 5 and retained archive `Docs/BossCombatReview/Execution/Claude/R5_BENCH_20261105/bench_results_round5.zip`. These are proxy medians from BUILD-224; they do not prove a 60 FPS / p99 <=16.67 ms result, behavior on RTX 2060 Super, or an owner-approved visual choice.

## Proposed policy after Round 6

1. Require the Round 6 first-kit telemetry witness and valid active-mode receipts.
2. Candidate mode must pass the experiment p99 gate against repeated TSR anchors and owner image-quality review.
3. Keep mode and screen fraction explicit in this proposal; do not hide them in scalability defaults.
4. If accepted, design a Development-only A/B selector first. Shipping/player setting and persistence need separate review and safe fallback behavior.
5. Retain TSR as the fallback and preserve current shipped defaults until owner approval.

Round 6 selection and owner image-quality acceptance are outstanding. No source, config, or asset change is authorized by this proposal.
