# E146 decision audit: fresh snapshot route contract

Queue mapping: E146 cites D5, but D5 is the selector cooldown boundary matrix; fresh-snapshot route semantics are primarily D3/D14. This cross-reference is corrected in Queue E.

`RPGFrameworkBossCharacter.cpp` captures a current snapshot at ordinary decision time and a new snapshot at combo continuation / delayed wake. `RPGBossSelectorRouteLifecycleTests.cpp` executes immediate continuation with the current snapshot and delayed continuation with the wake snapshot; it also asserts the stale pre-pause range is refused. D1-D3 and D14 provide the route audit trail.

No new owner policy is needed for the current implementation: each start is evaluated against the snapshot at that start boundary. A broader promise about snapshot immutability across arbitrary asynchronous routes is not evidenced and should not be implied. Decision owner for any product contract change: project owner, with Lead review.

Verification: static source/test inspection only; no tests/build/Editor run.
