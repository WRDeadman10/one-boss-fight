# BO-01..05 hotfix + BO-06..10: KI-167 redaction completion (lane BO, batch 2 of 10, per X-2238/X-2240)

C (implementer), 2026-11-12. It responds to the lead's review finding (X-2238): `asset_provenance --redact` printed SOURCE/DESTINATION `value=` declarations verbatim. X-2240 scopes BO-06..10.

**Not done:** no Unreal, build, PIE or asset work, no KNOWN_ISSUES status change, no commit or push. KI-026 and KI-067 were not started (X-2238).

## Approach

The fix is one mechanism instead of per-line patches. `Scripts/Tools/redaction.py` gains:
- **`redact_text`:**
  - Project-root paths become repo-relative.
  - The temp and home roots become `<tmp>/` and `<home>/`. Each is matched raw, with forward slashes, and JSON-escaped, ignoring case.
  - Any other absolute path becomes `<external>/<name>`: a drive path (optionally JSON-escaped), a UNC path, or a POSIX path under `/home`, `/Users`, `/tmp`, `/var`, `/mnt`, `/opt`, `/root`, `/private`, `/media`, `/srv` or `/etc`.
  - **Unreal object paths (`/Game/...`, `/Script/...`, plugin mounts), parsed telemetry and plain ratios such as `1/2` are not touched.**
- **`install_stream_redaction(redact)`:** wraps stdout and stderr when `--redact` is set. It is a no-op otherwise, so default output stays byte-for-byte unchanged. All seven KI-167 tools call it right after argument parsing.

| Task | Tool | Gap closed |
|---|---|---|
| **BO-01..05 hotfix** | `asset_provenance.py` | absolute SOURCE/DESTINATION `value=` declarations (Windows and POSIX) and the error path. `/Game/...` values are kept |
| BO-06 | `proof_report.py` | the `--expected` checklist path in the MANUAL/FAIL/PASS lines, control and diagnostic paths, `proof report error:` messages and STALE reasons. Only the directory part is masked; the checklist file name stays readable |
| BO-07 | `suite_log_report.py` | absolute `Path={...}` values in the text and JSON `tests`, `failures` and `duplicate_names` aggregates, plus the missing-log error. Non-path test identifiers are kept |
| BO-08 | `evidence_summary.py` | the `output=` confirmation and the error paths (missing evidence directory) |
| BO-09 | `summarize_framework_log.py`, `plot_framework_timeline.py` | path-valued structured fields (for example `source=` and `reason=`), raw payloads and error paths. Audit: any field holding an absolute path is masked; telemetry fields are kept |
| BO-10 | new `Scripts/Tools/test_bo_redaction_matrix.py` | black-box matrix: 15 tests covering the success and error paths of all seven tools (detail below) |

## BO-10 matrix

**Leak check:** each tool runs with and without `--redact`. Under `--redact`, no absolute form of the temp root may appear: raw, forward-slash or JSON-escaped, compared without case.

**Controls** in every case:
- `--redact` must not change the exit code.
- The default output must actually contain the absolute path, so a weak fixture cannot pass vacuously. The one exception is `proof_report`'s missing-log error, which prints a generic message with no path.

**Content checks:**
- `/Game/...` paths are preserved.
- The checklist file name is kept.
- `OneBossFight.Framework.B` and `A.cpp` stay in the aggregates.
- Telemetry such as `accepted=1` and the `decision` token is kept.
- `install_stream_redaction(False)` is a no-op.

## Tests run

**Red check:** the matrix run with the stream filter disabled (the BO-05 state) gives **9 failures**. They cover the asset_provenance hotfix case and the error paths, proof_report, suite_log_report (text and JSON) and evidence_summary.

| Command | Result |
|---|---|
| `python -m unittest test_bo_redaction_matrix` (from `Scripts/Tools`) | Ran 15, OK |
| the 23 other related suites (the BO-01..05 set, including `test_bo_tool_hardening` and `test_ki165_166_characterization`) | all OK |
| `python -m unittest Scripts.Tools.test_summarize_framework_log` (from the repo root) | OK |
| `python -m py_compile Scripts/Tools/*.py` | OK |

**Total: 25 suites, 166 tests, 0 failures.**

## Limits

- **A space ends a path token.** An absolute path containing a space, outside the project, temp and home roots, is masked only up to the first space. The project, temp and home roots are matched whole, so the user-profile name is covered.
- **POSIX detection uses an allow-list of machine roots.** An absolute POSIX path under some other root (for example `/data/...`) is not masked. This is deliberate, to avoid rewriting Unreal object paths.
- **Files the tools write are not stream-filtered.** The token_coverage manifest and the evidence_summary CSV rely on the BO-05 `display_path` and `display_row` handling.
- **Redaction remains a sharing aid, not a security boundary.**
