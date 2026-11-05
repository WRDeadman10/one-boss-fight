# Report redaction audit (S177)

Static review of maintained `Scripts/Tools` reports for environment values, likely credentials, and user-specific paths. No reports were generated from retained user logs during this review.

## Findings

| File:lines | Finding |
|---|---|
| `Scripts/Tools/proof_report.py:128` | Prints `args.log.resolve()` as an absolute path alongside mtime and hash. A copied report can disclose the local project/user directory. |
| `Scripts/Tools/asset_provenance.py:63,73-79` | Prints the resolved authoring script path; external evidence paths are also printed, and each matching raw log line is echoed. Paths and arbitrary log payloads are unredacted. |
| `Scripts/Tools/evidence_summary.py:46-49` | Uses a repo-relative path for logs inside the root, but stores the resolved absolute path for external evidence files in the CSV. |
| `Scripts/Tools/token_coverage.py:36-46` | `MISSING` diagnostics print the supplied path; samples for logs outside `--root` store an absolute resolved path in the JSON manifest. |
| `Scripts/Tools/suite_log_report.py:24-25`; `summarize_framework_log.py:57,85-90`; `plot_framework_timeline.py:53` | Reports include the supplied log path (and can therefore include an absolute user path when invoked with one). |
| `Scripts/Tools/proof_report.py:177,184`; `asset_provenance.py:79` | Selected report rows echo expected-sheet/log text verbatim; any sensitive value already present in those inputs is not redacted. |

No environment-variable access or clear credential fields (`password`, API key, access key, or credential lookup) were found in non-test `Scripts/Tools` Python sources. This is a source search, not a guarantee that arbitrary caller-provided logs contain no secrets.

## Disposition

Acceptance is **not met** for reports intended to leave the local machine: several outputs deliberately preserve absolute input paths and raw source lines. Lead recorded this low-severity sharing risk as KI-167. This audit changes no reporting behavior. No tests/build/Editor/runtime were run.
