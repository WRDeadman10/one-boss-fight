# Round 6 Phase 2: shipped-default decision table

**Status:** Phase 2 is running on the benchmark PC. The owner selected DLSS Performance at primary 50% as the experiment base; this is not a shipped default (C-951). Fill the measured cells when the Phase 2 intake is validated.

| Phase 2 evidence | Measured result | Image quality | Implication for a shipped default |
|---|---|---|---|
| Valid Performance-base rows and matching mode/build witnesses | Pending Phase 2 intake | Owner selected Performance for the experiment | Use these results as candidate evidence only. |
| Average frame rate at or above 60 FPS **and** p99 at or below 16.67 ms | Pending | Accepted by owner for the selected configuration | Performance gate is met; the configuration is eligible for a release recommendation, subject to packaged fallback and settings validation. |
| Either performance limit is missed | Pending | Accepted or pending | Do not claim the release target is met. A faster result than Phase 1 may guide later work, but does not satisfy the gate. |
| Performance limits pass | Pending | Owner rejects the visual result | Do not ship that configuration as the default; preserve TSR fallback and seek an acceptable alternative. |
| Missing rows, build identity, or active Performance witnesses | Pending | Any | Intake is inconclusive; make no default decision from it. |

## Current reference

Phase 1 DLSS Performance measured 35.19 average FPS and 35.9 ms p99 on the RTX 3060 proxy; that misses both release limits. Phase 2 has no returned results yet. Phase 1 image-quality acceptance authorized Performance as the Phase 2 base, not as a shipped default. The final recommendation must use the validated Phase 2 receipt and the owner's visual review of the specific tested configuration.

**After intake:** chosen configuration: __________; target result: __________; owner visual decision: __________; fallback/platform evidence: __________; recommendation: __________.
