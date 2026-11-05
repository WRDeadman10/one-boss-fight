# Proof report complete-run boundary audit (Queue D D58)

## Opt-in completeness checks

`proof_report.py:83-95` performs run-completeness checks only with `--require-complete-run`. It requires at least one line containing `[FrameworkProof] RESULT` and at least one exact `LogExit: Exiting.` marker; it flags ordering only when the last RESULT occurrence is after the last orderly-exit marker. It does not require exactly one RESULT, a recognized winning outcome, or that RESULT be the final telemetry line. Schema validation runs separately on the full primary/control logs and can report syntax/semantic warnings.

`test_queue_c_tools.py:122-141` covers missing RESULT despite orderly exit and missing orderly exit despite a RESULT. The inspected fixtures do not test valid complete run, RESULT after exit, multiple terminal rows, an invalid RESULT payload, or gameplay failure combined with incomplete/stale evidence.

## Status distinction and precedence

With the option enabled, completeness defects return exit 2 / `INCOMPLETE RUN`, separately from checklist telemetry failures (exit 1 / `FAIL`) and stale manifest evidence (exit 3 / `STALE EVIDENCE`). Code ordering matters: completeness returns first; checklist or identity failure returns 1 next; stale evidence returns 3 only after those checks pass; parser syntax/semantic warnings or manual checklist rows return 2 after stale evaluation. Without `--require-complete-run`, missing terminal/process markers do not prevent an otherwise presence-only PASS. Gameplay loss/failure is not inferred from a `RESULT` outcome here; expected token rows and human review establish the feature criteria.

## Limit

The flag establishes the presence/order of a terminal token and shutdown marker, not successful gameplay, a clean result schema, exactly-once terminal emission, or that no log content was appended after shutdown. Callers should preserve the INCOMPLETE classification separately from gameplay FAIL and stale-evidence status, while reading the printed diagnostics because combined problems are resolved by precedence. Source/test inspection only; no tests were run.
