# BO-31..35: argv pre-scan parity with argparse and nested-scope cleanup (lane BO, batch 7 of 10, per X-2254)

C (implementer), 2026-11-12. Synthetic only.

**Not done:** no source change was needed in this batch; no Unreal, build, PIE or asset work; no KNOWN_ISSUES status change; no commit or push.

## Coverage

New test file: `Scripts/Tools/test_bo_redaction_argv.py`, 9 tests.

| Task | Tests |
|---|---|
| BO-31 | `_resolves_to` is compared with argparse's own resolver (`parser._parse_optional`, with ambiguity shown as a SystemExit) over 8 option sets × `allow_abbrev` on and off × 17 tokens. The option sets cover aliases (`--rep`/`--report`, `-r`/`--recursive`), prefix collisions (`--require-complete-run`, `--redaction-level`, `--redact-paths-only`), `=value`, single-dash tokens, case and triple dashes. **0 mismatches.** Two quirks are documented: argparse's internal resolver would accept a bare `--` as a prefix, but real parsing consumes `--` as the separator, so the pre-scan correctly never treats it as the flag; and with `prefix_chars="+"`, `--redact` becomes a positional, so nothing pre-enables |
| BO-32 | Repeated flags, flags among positionals, a bare `--` before or after, `argv=[]`, an abbreviation and `=value` each agree with `parse_known_args`' parsed `redact` value. `--root --redact` pre-enables, as argparse also reads it as the flag. `--root=--redact` does not, because the `=value` belongs to `--root`. An explicit `argv=` overrides `sys.argv` in both directions |
| BO-33 | **Caller wraps stdout only:** a main run with `--redact` adds just the stderr wrapper and removes it afterwards; an injected exception gives a redacted traceback plus `SystemExit(1)` and the caller's streams back. **Caller wraps both streams with distinct wrappers:** an exception propagates unchanged (the caller owns stderr, so the caller's excepthook path decides), `SystemExit(7)` passes through, the streams are restored, and nothing leaks |
| BO-34 | **All seven real mains** (extended per X-2256) run under a harness that sets `allow_abbrev=False` on every parser. The harness records early activation directly, writing a `PREENABLED=` marker to file descriptor 1 right after `add_redact_argument`. For every tool, `--reda` is rejected by argparse (exit 2, `unrecognized arguments: --reda`) and is **not** pre-enabled; the exact `--redact` **is** pre-enabled and nothing leaks. For the 5 tools whose argparse error echoes the extra path, the rejected-abbreviation output is verbatim, as without the flag. `token_coverage` and `summarize_framework_log` consume the path as a log, so for them the marker is the evidence |
| BO-35 | `BO_26_30_REDACTION_CLI.md` (hotfix section) and `BO_LANE_REDACTION_ACCEPTANCE.md` are updated with the hotfix verification and this batch |

## Evidence

**Non-vacuity, by mutation in temp copies.** There was no fix to revert, so I mutated the resolver instead:
- The C-1492 length rule substituted for `_resolves_to`: **5 failures** (the parity matrix, prefix_chars, and BO-34 ×3).
- `allow_abbrev` ignored: **4 failures** with the original 3-tool BO-34. Against the extended test, `Bo34AllowAbbrevFalse` alone fails **7 of 7** tool subtests.

| Command | Result |
|---|---|
| `python -m unittest test_bo_redaction_argv` (from `Scripts/Tools`) | Ran 9, OK |
| the 28 other related suites | all OK |
| `python -m unittest Scripts.Tools.test_summarize_framework_log` (from the repo root) | OK |
| `python -m py_compile Scripts/Tools/*.py` | OK |

**Total: 30 suites, 220 tests, 0 failures.**

## Limits

- **The parity oracle is argparse's private `_parse_optional`.** Its return shape changed in Python 3.12 (a list), and the oracle handles both shapes; it was run only on Python 3.10.
- **Options added after `add_redact_argument`** would not be seen by the pre-scan. The 7 tools call it last; a new tool must do the same.
- **The other lane limits are unchanged;** see `BO_LANE_REDACTION_ACCEPTANCE.md`.

## X-2256 rework (C-1499)

BO-34 was incomplete: it covered only 3 of the 7 mains. It now covers all seven: `proof_report`, `asset_provenance`, `evidence_summary`, `token_coverage`, `suite_log_report`, `summarize_framework_log` and `plot_framework_timeline`.

- No source change was needed: there was no mismatch.
- `test_bo_redaction_argv` still has 9 tests; the BO-34 test now has 7 tool subtests.
- The full run is still 30 suites and 220 tests, 0 failures.
