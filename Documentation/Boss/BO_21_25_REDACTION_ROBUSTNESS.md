# BO-21..25: redaction robustness across the seven KI-167 tool mains (lane BO, batch 5 of 10, per X-2247)

C (implementer), 2026-11-12. Synthetic temp files only.

**Not done:** no Unreal, build, PIE or asset work, no KNOWN_ISSUES status change, no commit or push.

## Defect found and fixed (BO-23)

**A tool run without `--redact` unwrapped a caller's redaction.** Every tool called `install_stream_redaction(args.redact)`. With the flag absent, that call passed `False`, which unwraps (BO-11 semantics). So a tool `main` running inside a caller-owned redacting wrapper printed **unredacted** output for its whole run, and `redaction_scope` put the caller's wrapper back only afterwards.

**Fix:** the seven call sites now read `if args.redact: install_stream_redaction(True)`. A tool only ever enables redaction, and `redaction_scope` (BO-18) still removes what the tool installed. The `install_stream_redaction` API itself is unchanged.

**Files changed:** the install call site in `proof_report.py`, `asset_provenance.py`, `evidence_summary.py`, `token_coverage.py`, `suite_log_report.py`, `summarize_framework_log.py` and `plot_framework_timeline.py`. **New test file:** `Scripts/Tools/test_bo_redaction_robustness.py`, 8 tests with 7-way subtests, 1 skipped here.

## Coverage

| Task | Tests |
|---|---|
| BO-21 | For all seven mains, in-process, a `RuntimeError` carrying an absolute temp path is injected. With `--redact` it fires right after the tool installs its wrapper: the tool exits `SystemExit(1)`, prints a full traceback with `RuntimeError: injected failure at <tmp>/…`, leaks nothing and restores its streams. Without the flag it fires right after argument parsing: the original `RuntimeError` propagates and the streams are restored |
| BO-22 | For all seven mains, real failure inputs with `--redact` keep the expected outcome: parser.error gives exit 2 for proof_report, asset_provenance, evidence_summary, suite_log_report and plot_framework_timeline; the missing-root traceback in token_coverage gives a redacted exit 1; summarize_framework_log returns 1. Nothing leaks, the streams are restored and no wrapper is left. Without the flag the outcomes match, except token_coverage, which raises its original exception by design |
| BO-23 | A caller installs redaction, then runs `summarize_framework_log.main` four times (without, with, without, with `--redact`). The caller's wrapper survives every call, nothing leaks, output appears exactly 4 times with nothing lost, and the caller's held tail is kept until it disables the wrapper |
| BO-24 | `display_path`: a sibling folder that shares the root's name prefix (`proj2` against `proj`) is external; `..` escaping the root is external, and `..` staying inside is relative; a relative root works; default output is verbatim. Symlink cases (a link inside the root pointing out shows as `<external>/name`; a link outside pointing in shows the repo-relative target) are written but **skipped here**: this Windows account cannot create symlinks |
| BO-25 | A subprocess writes 2,000 mixed single- and multi-line records containing `é`, a CJK character, an emoji and project paths; interleaved stderr records split across two writes; a 200,000-character line; and a final tail with no newline. Result: no project path leaks, exactly 1,000/1,000/1,000 record lines and 8 stderr records, no duplicates, the large line intact, Unicode intact, and the tail flushed at exit |

## Tests run

**Red checks, in temp copies:**
- The C-1488 call sites restored (`install_stream_redaction(args.redact)`): **1 failure**, BO-23.
- `redaction_scope` made a pass-through: **14 failures**, the BO-21 and BO-22 subtests for all seven tools. This confirms the new tests also pin the BO-18 and BO-19 behaviour per tool.

| Command | Result |
|---|---|
| `python -m unittest test_bo_redaction_robustness` (from `Scripts/Tools`) | Ran 8, OK (1 skipped: symlinks) |
| the 26 other related suites | all OK |
| `python -m unittest Scripts.Tools.test_summarize_framework_log` (from the repo root) | OK |
| `python -m py_compile Scripts/Tools/*.py` | OK |

**Total: 28 suites, 199 tests, 0 failures.**

## Limits

- **The symlink cases are unverified on this machine** (skipped: no symlink privilege). They need a run where symlinks can be created.
- **Line-buffering memory:** a single record with no newline is held in memory until a newline or a flush. That is fine for the 200,000-character case tested, but an unbounded newline-free stream would grow without limit. The KI-167 tools print line-oriented output.
- **CRLF:** on Windows, text-mode streams write `\r\n`; redaction runs before that translation and is unaffected.
- The remaining limits from BO-16..20 still apply: space-cut fragments outside known roots, the case-sensitive POSIX allow-list, a mid-path explicit flush, and exceptions becoming `SystemExit(1)` under `--redact`.
