# Boss strafe-resume property-test audit (Queue D D49)

## Rule and limits

`RPGBossStrafeResume::ShouldRestart` returns true only when an interruption occurred, a restart has not already been used, and the remaining budget is finite and strictly positive (`RPGBossStrafeResumeRules.h:8-11`). The helper is pure and explicitly unwired: it does not restart a strafe, persist the one-shot flag, or subtract elapsed time.

The five assertions in `RPGBossStrafeResumeRulesTests.cpp:6-11` cover one positive budget, no-interruption control, already-used restart, zero budget, and positive infinity. `RPGBossStrafeResumeNegativeBudgetMutationTests.cpp:6-14` separately asserts a finite negative budget is rejected. These are named examples, not a generated property test; the fixture uses no seed or generated event stream. The broader coverage matrix records the same focused rule scope (`COVERAGE_MATRICES_S61_S65.md:130`).

## Property candidates

| Invariant candidate | Current witness | Remaining gap |
|---|---|---|
| Restart requires interruption | One false-interruption example. | Generated false-interruption combinations across used flag and budget classes. |
| Restart is one-shot | One already-used positive-budget example. | Caller state transition is outside helper; no sequence proves first accepted restart flips the flag and second is refused. |
| Budget must be finite and positive | Examples for positive, zero, negative, and +infinity. | NaN, negative infinity, smallest positive representable value, and broad finite-positive range are not explicit here. |
| Pure decision does not mutate state | Signature takes scalar inputs and returns bool. | No stateful strafe caller exists; no runtime/resume behavior should be inferred. |

A useful deterministic property fixture can use a fixed local PRNG seed and record it in assertion labels or failure output. Generate input triples `(interrupted, used, remaining)` from boundary classes (negative, negative zero, zero, smallest positive finite, ordinary finite, largest finite, NaN, ±infinity), and compare the result against the exact conjunction `interrupted && !used && isfinite(remaining) && remaining > 0`. Keep generator state local to the test, avoid global random APIs, and add fixed explicit edge examples so failures remain easy to diagnose. This is a proposal, not an implementation or executed test.

No integration/caller/property claim is supported by the existing tests; rule is currently unwired. Static source/test/doc review only; no tests/build/Editor run.
