# Suite-log duplicate identity audit (Queue D D59)

## Summary parser behavior

`Scripts/Tools/suite_log_report.py:12-25` parses every `Test Completed` line and keys duplicate detection by `Path` when nonempty, otherwise by display `Name`. It retains every row in `tests`, and `finished`, `passed`, and `failed` count all rows. Repeated identities are surfaced in sorted `duplicate_names` output (text and JSON), but they are still counted as separate rows; duplicate-only successful logs return exit 0 because CLI exit status is based only on failed result rows.

`Scripts/Tools/diff_suite_logs.py:14-27` uses the same path-or-name identity rule but rejects a repeated key with `ValueError`, causing CLI exit 2 (`INVALID`) rather than treating duplicates as independent tests. Thus the report and diff tools have intentionally different duplicate handling: diagnostic/counting vs fail-closed comparison.

## Fixture coverage and limits

`test_queue_c_tools.py:162-179` tests deterministic summary output and a failed named row, but it does not include duplicate `Test Completed` identities or assert `duplicate_names` behavior/exit code. Diff fixtures test no-record input and same/changed identities; the inspected tests do not add a repeated identity case for `load` despite its source rejection.

The identity is test `Path` or `Name`, not a run/session/generation-qualified identity. Repeated names from legitimate repeated suite segments therefore surface as duplicates, even if they were separate executions; conversely a missing-path row and a pathful row with the same display name have different keys. On summary output duplicates are visible, so they are not silent, but totals are record counts, not deduplicated distinct-test counts, and a success exit alone does not prove unique identities.

Source and fixture inspection only; no suite tools/tests were run.
