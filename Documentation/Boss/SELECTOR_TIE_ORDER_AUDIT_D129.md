# Queue D129 — selector tie-order determinism audit

Date: 2026-11-03  
Method: static trace of candidate-order scoring and seeded tie resolution; no tests run.

## Ordering contract

`Select` visits candidates in `Candidates` array order and replaces the current winner only for strictly greater score. With TieBand 0, exact score ties therefore keep the lowest candidate index. With TieBand > 0, it builds the tier by scanning traces in the same order, including each eligible score `>= best * (1 - TieBand)`, and draws a seeded index from that ordered tier using `TieSeed + StartedCount`.

Thus identical candidate order/state/seed is deterministic; candidate permutation can change the zero-band exact-tie winner and can remap seeded tier indices when TieBand is enabled. The code does not promise permutation-invariant identity. `StartedCount` changes only through `NoteStarted` and resets through `Reset`.

## Existing evidence

`RPGBossMoveSelectorTests.cpp` repeats identical zero-band equal-candidate selection and expects index 0. BoundedTie tests record repeated-seed behavior and constrain picks to the score tier. They do not test candidate permutation or identity invariance, which the current contract does not require.

## Result / limits

Ordering behavior is deterministic under stable input order and explicitly order-sensitive. No defect found against the stated contract. No random distribution or unbiasedness claim is made; static review only.
