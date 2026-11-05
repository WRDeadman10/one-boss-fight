# Telemetry numeric relation format proposal (S132)

This is a format proposal only. It does not change `proof_report.py` or turn manual expected-sheet prose into machine-checked gameplay claims. Relations run only when an explicit relation file and validated log are supplied.

## Minimal JSON format

UTF-8 JSON object: `{"version":1,"relations":[...]}`. Every relation names a registered token and field. Values are parsed as finite decimal numbers; missing samples, non-finite values, unknown token/field, malformed shape, duplicate relation IDs, or unsupported operators are errors (fail closed), not skipped checks.

- Equality: `{"id":"max_health","op":"eq","token":"boss_health_read","field":"max","value":250}`. Pass if every selected sample equals the decimal value exactly.
- Closed range: `{"id":"latency_bounds","op":"range","token":"flask_reaction","field":"measuredSeconds","min":0.2,"max":0.4}`. Pass iff every selected sample satisfies `min <= value <= max`.
- Ratio: `{"id":"damage_ratio","op":"ratio","token":"hit","numerator":"hpApplied","denominator":"healthBefore","min":0.1,"max":0.2}`. For each sample, require a nonzero denominator and the closed ratio range.
- Monotonic: `{"id":"health_falls","op":"monotonic","token":"hit","field":"healthAfter","order":"line","direction":"nonincreasing"}`. Require at least two ordered samples; equality is allowed. The only order keys are source `line` or an explicitly named numeric field. Groups/instance scoping are deferred; never merge unrelated actors implicitly.

The first version intentionally omits arithmetic expressions, negation, cross-token joins, implicit units, tolerances, aggregates, and inferred baselines. Unsupported keys/operators must be rejected. Empty sample sets and one-sample monotonic relations fail with an actionable diagnostic.

## Conformance fixtures (expected outcomes)

Use a fixture log with two samples per relation:

| Relation | Sample values | Expected |
|---|---:|---|
| `eq` `boss_health_read.max` expected 250 | 250, 250 | PASS |
| `eq` `boss_health_read.max` expected 250 | 250, 249 | FAIL |
| `range` 0.2–0.4 | 0.2, 0.4 | PASS (inclusive edges) |
| `range` 0.2–0.4 | 0.2, 0.41 | FAIL |
| `ratio` 0.1–0.2 | (10,100), (20,100) | PASS |
| `ratio` with denominator 0 | (10,0) | ERROR; fail closed |
| `monotonic` `hit.healthAfter` nonincreasing | 100, 80, 80 | PASS |
| `monotonic` `hit.healthAfter` nonincreasing | 100, 101 | FAIL |
| unsupported `op=approx` | any | ERROR; unsupported operator |
| unknown token/field, missing value, NaN, empty set | any | ERROR; no silent MANUAL/PASS conversion |

Output contract for a future evaluator: one PASS/FAIL/ERROR line per relation with relation ID, source log path/line sample references, parsed values, and the exact comparison. Any ERROR makes the overall relation result INCOMPLETE/invalid; any FAIL makes it FAIL. No relation output may claim a wider proof than the listed telemetry establishes.
