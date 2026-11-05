# Baked sample endpoint mutation audit (Queue D D47)

## Source semantics

The MoveCard validator accepts baked sample coverage when there are at least two samples, each with finite/in-domain values and strictly increasing times, and the first sample is at or before `StartSeconds` while the last is at or after `EndSeconds` (`RPGBossMoveCard.cpp:140-153`). Equality is allowed at either boundary; samples outside the contact window are allowed if they remain valid within the clip. This is inclusive coverage.

At runtime, the sweep builder clips each tick to `[max(PrevPosition, StartSeconds), min(Position, EndSeconds)]` and returns no overlap when the clipped high endpoint is not strictly greater than low (`RPGBossSweepSampling.cpp:25-30`). For baked data it samples the clipped endpoints and includes only interior stored samples with `Lo < TimeSeconds < Hi` (`:32-39`). `PoseAt` uses the first pose for query times `<= first.TimeSeconds`, interpolates through the first sample whose time is `>= query`, and falls back to the last pose after the last timestamp (`:10-22`). With a valid full-window bake, the last sample therefore supplies the exact window-end pose; exact last-sample queries are reached by interpolation with factor 1. The runtime fallback after the last time is a clamp, but valid validation should keep the bake endpoint at/after window end.

## Existing tests and limits

`RPGBossBakedSampleEndpointMutation` validates exact start/end samples, then mutates the first time to the next representable float above window start and expects rejection (`Tests/RPGBossBakedSampleEndpointMutationTests.cpp:38-48`). `RPGBossBakedLastEndpointBoundary` validates exact end, then moves the last time to the adjacent representable float below end and expects rejection (`Tests/RPGBossBakedSampleLastEndpointBoundaryTests.cpp:38-47`). These tests establish inclusive exact coverage and reject the two immediate inward gaps at the validator boundary.

The inspected endpoint tests call only `RPGBossMoveCards::Validate`; they do not call `RPGBossSweep::BuildKeyPoses`/`PoseAt`. No focused assertions were found for exact sampled-time interpolation, exact clipped `Hi == EndSeconds`, a sample strictly after the window end, or malformed/missing endpoint ordering through the sweep consumer. Thus runtime interpolation behavior above is source-derived, not separately automation-witnessed. Existing general move-card/sweep tests may cover ordinary overlaps, but do not replace those named endpoint cases.

## Suggested bounded follow-up

If a later test task adds sweep-consumer coverage, reuse a valid synthetic window with non-constant endpoint poses and assert: (1) exact full window overlap returns first/last sample poses, (2) a tick ending exactly at the window end produces `Hi == EndSeconds`, (3) an interior exact sample is preserved, and (4) a valid sample after the end is interpolated back to the window end. Keep validator endpoint mutation tests separate from runtime interpolation assertions. Source/test inspection only; no tests, build, or Unreal run.
