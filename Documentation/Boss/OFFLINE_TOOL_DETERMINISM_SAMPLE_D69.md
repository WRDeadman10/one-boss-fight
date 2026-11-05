# Offline tool determinism sample (D69)

Date: 2026-11-03. Ran three maintained tools twice each against identical isolated temporary inputs; no project outputs were used.

| Tool | Repeated output comparison | Result |
|---|---|---|
| `make_source_manifest.py` | Two manifests for the same temporary `Source` tree. | Byte-identical. |
| `suite_log_report.py --json` | Two JSON summaries of the same one-row temporary suite log. | Byte-identical, including the same input path field. |
| `evidence_pack.py` | Two output roots from the same `same_name.log`; compared copied payload, SHA256 text, and JSON manifest. | All three artifacts byte-identical; generated output-root path appears only in stdout, not retained manifest. |

This is a bounded sample, not a claim that every maintained CLI is deterministic. Path-bearing report fields can vary when the input location changes. All fixtures and generated outputs were confined to a temporary directory and removed automatically.
