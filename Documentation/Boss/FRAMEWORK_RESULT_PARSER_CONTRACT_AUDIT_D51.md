# Framework RESULT parser contract audit (Queue D D51)

## Parser and schema boundary

`Scripts/Tools/framework_results.py` scans `[FrameworkProof]` lines, extracts the first whitespace-delimited token and `key=value` pairs, then emits rows only for token `RESULT` (`:10-50`). It requires nonempty `outcome`; for the recognized counter set `{acceptedHits, attacks, parriedHits, guardedHits, appliedDamage}`, present values must satisfy Python `str.isdigit()`. Repeated key/value fields on RESULT produce an error; repeated RESULT rows within an inferred generation produce a warning, not a rejection. Generation context is updated by any proof row carrying `generation`, not just `encounter_reset`, and stays `unknown` until one appears. Counter deltas are returned for shared numeric fields but are not checked for negative deltas.

`QA002_LOG_SCHEMA_SPEC.md:70` documents one legacy fixture shape (`outcome` plus optional `acceptedHits`/`attacks`); it is not a complete authoritative schema for all current emitters. The current parser requires only `outcome`, treats unknown labels/outcomes and arbitrary nonnumeric fields as opaque values, and does not enforce allowed outcome vocabulary, field allowlists, duplicate RESULT policy as an error, terminal placement/order, or one row per actual encounter generation. `proof_report.py` separately offers optional terminal RESULT and orderly-exit checks; those are not part of this parser's contract.

## Behavior table

| Input case | Current behavior | Classification |
|---|---|---|
| No RESULT row | Prints `result_rows=0`, no parser error. | Valid parse with no rows; completeness belongs to caller. |
| Missing/empty outcome | Error on each RESULT row. | Required-field validation. |
| Known numeric counter with `12`, `0` | Accepted. | Nonnegative integer syntax only. |
| Known numeric counter with `-1`, `1.0`, `NaN`, `oops` | Error (`isdigit()` false). | Malformed recognized counter. |
| Unknown field/outcome | Preserved as text without schema validation. | Opaque/forward-compatible. |
| Duplicate RESULT field | Error and last value wins in parsed row. | Diagnostic exists but parsed row still contains overwritten value. |
| Multiple RESULT rows in same inferred generation | Warning. | Duplicate identity is not rejected; intentional multi-segment behavior needs interpretation. |
| Counter decreases across rows | Delta may be negative. | No monotonicity validation; counters may be actor-lifetime or run-dependent. |
| Terminal RESULT after orderly exit | Parser accepts. | Ordering/completeness is handled only by optional separate proof-report logic. |

Tests are embedded in `Scripts/Tools/test_queue_c_tools.py` for required outcome, malformed numeric counter, duplicate field warning/error diagnostics, and delta behavior. The report is source/docs/test inspection only; no tool tests or retained logs were executed.
