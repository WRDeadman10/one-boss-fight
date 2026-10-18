# Test Plan

Acceptance matrix is in `Idea/IDEA.md` section 14. Record results here per build.

| Test ID | Area | Procedure | Pass criteria | Build | Result | Evidence |
|---|---|---|---|---|---|---|
| BLD-01 | Build | Headless UBT build of `OneBossFightEditor` | 0 errors | M0 | PASS (2026-10-18) | UBT log |
| MOV-01 | Movement | Walk, run, sprint, jump | No stuck state | | | |
| COM-02 | Hit detection | Hold weapon through active frames on a target | One hit per swing | | | |
| ENC-02 | Reset | Die, retry, repeat | All state resets | | | |
| PERF-01 | Performance | Packaged 1080p full fight | Avg >= 120 FPS, p99 <= 8.33 ms | | | |
