# BO-01..05: offline hardening of the KI-163..167 Python tools (lane BO, batch 1 of 10, per X-2236)

C (implementer), 2026-11-12. These are the lane BN follow-ups (C-1480, accepted in A-908), implemented on lead authorization.

**Not done:** no Unreal, build, PIE or asset work, no KNOWN_ISSUES status change, no commit or push. The BK-lane edits already in the working tree for `token_coverage.py`, `evidence_pack.py`, `make_source_manifest.py` and `evidence_summary.py` (the `output_aliases` guards) are preserved unchanged.

## Changes

| Task | KI | File(s) | Behaviour now |
|---|---|---|---|
| BO-01 | KI-163 | `Scripts/Tools/token_coverage.py` | Any `MISSING` log exits **2** with `ERROR missing_logs=N; no samples manifest written`, and the manifest is not written. Previously it returned 0 or 1 and could write a success manifest |
| BO-02 | KI-164 | `Scripts/Tools/evidence_pack.py` | `out.mkdir` moved after all source, reserved-name, collision and destination checks. A rejected invocation leaves **no** new output directory |
| BO-03 | KI-165 | `Scripts/Tools/make_source_manifest.py` | A root without `Source/` is rejected (`parser.error`, exit 2, `no Source directory under root`) and no manifest is written |
| BO-04 | KI-166 | new `Scripts/Tools/json_input.py`; `profile_dump.py`, `card_table.py`, `validate_baked_cards.py`, `plugin_dependencies.py` | Malformed JSON, an unreadable file or a wrong top-level or nested shape gives exit **2** with a one-line `ERROR <path>: <reason>` on stderr: no traceback and no partial stdout. The whole shape is validated before any row is printed. `card_table` accepts the same object or list shapes as before. `plugin_dependencies` parses every descriptor up front |
| BO-05 | KI-167 | new `Scripts/Tools/redaction.py`; `proof_report.py`, `asset_provenance.py`, `evidence_summary.py`, `token_coverage.py`, `suite_log_report.py`, `summarize_framework_log.py`, `plot_framework_timeline.py` | An opt-in `--redact` flag. Paths are printed repo-relative (or relative to `--root`), otherwise as `<external>/<name>`. Echoed raw rows are replaced by `<row redacted>` (asset_provenance evidence lines, the token_coverage `sample`, and the plot_framework_timeline raw-payload fallback). **Without `--redact`, output is unchanged** |

**Package-import safety:** the tools add their own folder to `sys.path` before importing a helper. Without this, `test_summarize_framework_log.py`, which imports `Scripts.Tools.summarize_framework_log`, failed with `No module named 'redaction'`. I caused that regression in this batch and fixed it.

## Tests

- **New:** `Scripts/Tools/test_bo_tool_hardening.py`, 14 tests (KI-163 ×2, KI-164 ×3, KI-165, KI-167 ×8, including "default output keeps the absolute path" controls).
- **Updated:**
  - `test_ki165_166_characterization.py` was flipped from pinning the defects to pinning the fixed, fail-closed behaviour (7 tests, including new uplugin and valid-input controls).
  - In `test_bk226_230_evidence_pack_audit.py`, three assertions that expected an empty output directory to be left behind now expect no directory. This is the intended KI-164 change.

**Red check:** the new and updated tests run against the HEAD versions of the 11 tools (copied to a temp folder) give **17 failures**. So the tests detect the old behaviour.

**Commands run, all from `Scripts/Tools` unless marked:**

| Command | Result |
|---|---|
| `python -m unittest test_bo_tool_hardening` | Ran 14, OK |
| `python -m unittest test_ki165_166_characterization` | Ran 7, OK |
| `python -m unittest test_bk226_230_evidence_pack_audit` | Ran 13, OK (1 skipped) |
| the 20 other suites that exercise these tools (`test_audit_source_error_token_coverage`, `test_bi_a19_cli_tooling_contract`, `test_bk221..test_bk316*`, `test_evidence_pack_hashes`, `test_path_normalization_s170`, `test_plot_framework_timeline`, `test_queue_c_s36_s40`, `test_queue_c_tools`) | all OK (2 skipped in all) |
| `python -m unittest Scripts.Tools.test_summarize_framework_log` (from the repo root) | Ran 1, OK |
| `python -m py_compile Scripts/Tools/*.py` | OK |

**Total: 24 suites, 153 tests, 0 failures.**

## Limits

- **Exit codes changed:** `token_coverage` now returns 2 when a log is missing; the four JSON tools return 2 on bad input (1 was an uncaught traceback before). A caller that treated 1 as "bad input" will now see 2. I found no in-repo caller that depends on this, but I only checked the test suites.
- **`--redact` is a sharing aid, not a security boundary.** Tokens and identifiers that the tools parse out of logs are still printed. `proof_report` prints other diagnostics beyond the cited input line, and those were not audited. Only the KI-cited lines are covered.
- **`evidence_pack`:** the source-race and partial-publication behaviour (BK-281..290) is unchanged; only the directory creation moved.
- The KI-163..167 rows are left Open, per the instruction. Closing them is the lead's call after review.
