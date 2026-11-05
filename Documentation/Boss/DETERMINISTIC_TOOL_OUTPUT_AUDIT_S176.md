# Deterministic tool output audit (S176)

Ran four offline CLIs against synthetic inputs in a fresh temporary root only. No project data was modified; no tests, Unreal Editor, or build were run.

## Repeated-output checks

| Tool | Temporary fixture and comparison | Result |
|---|---|---|
| `make_source_manifest.py` | Two invocations over the same two-file temporary `Source` tree, writing distinct manifest destinations. | Manifest bytes matched exactly; the implementation sorts source paths (`:17-23`). |
| `evidence_pack.py` | Same fixed raw log packed into two separate temporary output directories; compared every generated file by name. | The copied log, hash list, and JSON manifest were byte-identical. Its stdout includes the output directory and therefore varies with destination path (`:62-69`); that path variance is intentional. |
| `suite_log_report.py --json` | Same synthetic two-row log, including one failure, invoked twice at the same path. | Stdout bytes matched and both exits were 1, the expected failure verdict. JSON keys/failure lists are sorted (`:16-25`); report embeds the input path (`:25`). |
| `framework_results.py` | Same synthetic reset/result log invoked twice at the same path. | Stdout bytes and exit status matched (0); field and diagnostic ordering is explicit (`:18-57`). |

## Disposition

These fixed-input temporary fixtures produced byte-stable artifacts/output on repeat. Path-bearing stdout/JSON is deterministic for the same input/output paths but differs when those paths change; the evidence-pack stdout path and suite report `file` field are documented examples. This is a representative fixture audit, not an exhaustive byte-for-byte run of every CLI. No nondeterministic timestamp, random value, or network-derived output is used in the four checked paths.
