# Proof report identity-field audit (Queue D D57)

## Extraction and outcomes

`proof_report.py:12-15, 60-81` searches every text line in the primary input log for literal `map=`, `profile=`, `run_id=`, or `runId=` followed by one or more non-whitespace characters. It is not restricted to FrameworkProof lines or a single header/RESULT row. `runId` is normalized to `run_id`; all distinct observed values are collected into a set for each requested field.

For each supplied `--expect-map`, `--expect-profile`, or `--expect-run-id`, no observed value prints `IDENTITY UNKNOWN` and does not add a failure; exactly the expected singleton prints MATCH; any different or multiple distinct values prints MISMATCH and adds an identity failure. If an option is omitted, that field is not inspected. Values compare case-sensitively and trailing punctuation is part of the value.

`test_queue_c_tools.py:107-120` covers a profile mismatch, verifies it is reported before evidence checklist rows, and checks exit 1. The inspected fixtures do not explicitly cover a matching value, absent/UNKNOWN value, runId alias, repeated identical values, or multiple distinct values.

## Claim boundary

Identity is presence/consistency of raw key-value text, not proof that the map/profile/run was actually loaded or executed. A matching occurrence can come from any line; the parser does not tie the identity to `RESULT`, a particular generation, or the evidence producer. With `--control-log`, expected identity options are checked on the primary input only; the control's identity is not independently compared. Missing identity is deliberately informational UNKNOWN, so an expected identity option alone does not enforce required presence.

Mismatches are printed before checklist rows but their return code is evaluated after completeness and checklist failures: incomplete run returns 2 first, checklist failure returns 1, then identity mismatch returns 1. A stale manifest is evaluated after identity mismatch and therefore returns 1 if both occur. Source/test inspection only; tests were not run.
