# Suite-diff input and exit classification audit (Queue D D60)

## Source classification

`Scripts/Tools/diff_suite_logs.py:14-31` extracts every `Test Completed` row, keys by `Path` or fallback `Name`, and rejects duplicate keys. A log with no completed rows raises `ValueError`; missing file raises `OSError`; CLI prints `INVALID` and returns 2 for either. Partial/truncated logs that contain at least one completed row are accepted because the parser does not require suite-start, completion summary, or expected row count.

For two valid nonempty maps, `compare` classifies added, removed, or changed result text; identical key/result maps return 0, any difference returns 1, and changed includes result string changes (not just Success/Fail transitions). Results are compared as opaque strings. The script does not classify Unreal test failure as a separate status from changed content, and it does not reject unknown result labels. Same-content logs in different row order compare identical because maps are sorted/set-compared.

## Case matrix

| Before/after condition | Current behavior | Exit |
|---|---|---:|
| Missing input file | `OSError`, `INVALID` | 2 |
| Empty log or no `Test Completed` rows | invalid no-record error | 2 |
| Truncated log with one or more completed rows | accepted as a valid partial map; completion not checked | depends on comparison |
| Duplicate completed identity in either log | invalid duplicate identity | 2 |
| Identical identity/result maps | no changes | 0 |
| Added or removed identity | `ADDED`/`REMOVED` | 1 |
| Same identity, different result string | `CHANGED old -> new` | 1 |
| Unknown result string | accepted and compared literally | 0 if identical; 1 if changed |

Fixtures in `test_queue_c_tools.py:181-205` cover a no-record log and identical/changed/invalid CLI classes; comparison unit cases cover same and added/removed/changed maps. The inspected fixtures do not cover missing path at CLI, truncation after some completed rows, duplicate row CLI, or unknown outcome labels.

The tool compares completed-row snapshots only. Exit 0 does not prove both logs represent complete suite runs; compare it with `suite_log_report.py` and the wrapper's run-completion evidence. Tests were inspected, not run.
