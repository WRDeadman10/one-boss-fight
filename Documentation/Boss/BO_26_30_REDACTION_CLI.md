# BO-26..30: command-line, invocation and artifact-failure redaction, plus the lane acceptance checklist (lane BO, batch 6 of 10, per X-2249)

C (implementer), 2026-11-12. Synthetic temp files only.

**Not done:** no Unreal, build, PIE or asset work, no KNOWN_ISSUES status change, no commit or push.

## Defects found and fixed

1. **BO-26, argparse errors leaked under `--redact`.** argparse prints usage errors such as `unrecognized arguments: C:\…\bogus.txt` while parsing, before a tool can install redaction. So `--redact` did not cover them.
   - **Fix:** `redaction.add_redact_argument` now pre-scans argv. If `--redact`, or an abbreviation argparse would accept (5 characters or more, such as `--reda`), appears before any bare `--`, it enables redaction before parsing.
   - The tool's `redaction_scope` removes it again afterwards. **Without the flag nothing changes.**
2. **BO-28, `python -m Scripts.Tools.token_coverage` and `python -m Scripts.Tools.evidence_summary` failed** with `ModuleNotFoundError: atomic_io`. Both imported `atomic_io` before the BO `sys.path` guard.
   - This was already broken at HEAD for `-m` invocation; it was not a regression from this lane.
   - **Fix:** the guard now comes before the `atomic_io` import in both files.

**Files changed:** `Scripts/Tools/redaction.py`, `token_coverage.py` and `evidence_summary.py` (import order only). **New test file:** `Scripts/Tools/test_bo_redaction_cli.py`, 7 tests with per-tool subtests.

## Coverage

| Task | Tests |
|---|---|
| BO-26 | For all seven tools: the required arguments plus one extra absolute-path value. Under `--redact` nothing leaks, the exit code equals the plain run, and `bogus.txt` is still named. The control echoes the absolute path for at least 4 tools, so the test is not vacuous. The abbreviated `--reda` is covered. `--help` contains no absolute path and is identical with and without `--redact` |
| BO-27 | Missing required arguments: exit 2 in both modes for six tools (`token_coverage` has no required positional, so its exit codes are compared instead). An output path whose parent is a file (`token_coverage --samples-output`, `evidence_summary --output`): same nonzero exit code in both modes, the control shows the absolute path, the redacted run does not, and no output is created |
| BO-28 | For all seven tools, with and without `--redact`: a direct script run from the repo root and `python -m Scripts.Tools.<tool>` give the same exit code and the same stdout, with no `ModuleNotFoundError` and no leak under `--redact` |
| BO-29 | `os.replace` inside `atomic_io` is replaced, through a `runpy` harness, with a function that raises `OSError` naming the destination. For `token_coverage` and `evidence_summary`, in both modes: a nonzero exit, the injected error reported, **no artifact and no temp file** in the output folder. Under `--redact`: exit 1 and no leak. Default: the traceback shows the absolute path (control). This passed without changes, confirming the BK `atomic_io` cleanup together with the BO-19 traceback handling |
| BO-30 | `Documentation/Boss/BO_LANE_REDACTION_ACCEPTANCE.md`: the lane-wide contract, evidence, review status and limits |

## Tests run

**Red checks, in temp copies at `<tmp>/Scripts/Tools`:**
- Argv pre-scan removed: **7 BO-26 failures**.
- The old import order restored: **4 BO-28 failures**.
- 3 further failures (BO-27 output paths, BO-29 ×2) appear **even in an unreverted copy**. They come from the copy, whose project root has no validator for `evidence_summary`, and are not signals of either revert.

| Command | Result |
|---|---|
| `python -m unittest test_bo_redaction_cli` (from `Scripts/Tools`) | Ran 7, OK |
| the 27 other related suites | all OK |
| `python -m unittest Scripts.Tools.test_summarize_framework_log` (from the repo root) | OK |
| `python -m py_compile Scripts/Tools/*.py` | OK |

**Total: 29 suites, 206 tests, 0 failures.**

## Limits

- **Abbreviations under 5 characters are not pre-scanned.** `--red` is not, because argparse may treat it as ambiguous; argparse itself decides. A literal `--redact` used as a file name before `--` would enable redaction early, which is harmless: it only masks.
- **`--help`** contains no absolute paths, so its text is the same in both modes.
- **The BO-29 injection replaces `os.replace` for the whole harness process;** a real failure of the operating system's rename was not exercised.

## Hotfix X-2250/X-2251: short unique-prefix leak (C-1494)

**Defect, reproduced by the lead:** `suite_log_report.py <safe> --re <sensitive>`. argparse accepts `--re` as a unique abbreviation of `--redact`, but the C-1492 pre-scan skipped abbreviations shorter than 5 characters. So `unrecognized arguments: <absolute path>` was printed verbatim.

**Fix:** a new `redaction._resolves_to(parser, token, action)` mirrors argparse's own long-option resolution:
- an exact option string; or
- when `allow_abbrev` is on, a prefix (with any `=value` stripped) that matches exactly one action in `parser._option_string_actions`, where that action is `--redact`.

Ambiguous prefixes do not enable redaction early. For example, `proof_report --re` also matches `--require-complete-run`, and argparse rejects it with an "ambiguous option" message that contains no path. Tokens after a bare `--` are ignored. The resolver needs `add_redact_argument` to be called after all other options, which is verified for all 7 tools (it is the last `add_argument` before `parse_args`).

**New tests:** the `Bo26UniquePrefixHotfix` class in `test_bo_redaction_cli.py`, 5 tests:
- the lead's exact repro, with a control;
- every prefix from `--r` to `--redact` × 7 tools, with no leak (42 subtests; 21 or more resolve uniquely, so the test is non-vacuous);
- the ambiguous `proof_report --re` control;
- a resolver unit test (exact, unique, ambiguous, `=value`, `allow_abbrev=False`, a single dash, a bare `--`, `argv=[]` leaves the streams unchanged);
- an unchanged no-flag control.

**Red check:** the C-1492 length-5 pre-scan restored in a temp copy gives **10 failures**: the lead repro plus `--r`/`--re` for 5 tools, and `--re` for evidence_summary.

**Full run:** 29 suites and 211 tests, 0 failures; `py_compile` OK. The acceptance checklist is updated: the hotfix row, the stale BO-16..20 review row is now A-912, and limit 7.
