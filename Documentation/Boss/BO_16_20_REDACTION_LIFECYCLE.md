# BO-16..20: redaction lifecycle, JSON, artifact and near-miss boundaries (lane BO, batch 4 of 10, per X-2245)

C (implementer), 2026-11-12. Synthetic temp files only.

**Not done:** no Unreal, build, PIE or asset work, no KNOWN_ISSUES status change, no commit or push.

## Defects found and fixed

1. **Stale wrapper (BO-18).** No tool `main` ever removed its redacting wrapper, so a later in-process caller kept getting redacted output. The plain runs only looked right because `install_stream_redaction(False)` unwraps.
   - **Fix:** a new `redaction.redaction_scope` decorator on all seven KI-167 mains. It restores the streams the caller passed in when `main` returns, raises or exits. A wrapper the caller installed itself is left alone.
2. **Unredacted traceback (BO-19).** This was a regression from fix 1, introduced and caught in this batch. Once the scope restored the streams in `finally`, Python's default excepthook printed an uncaught exception's traceback afterwards, unredacted. Example: `evidence_summary` on an unreadable log printed the absolute temp path.
   - **Fix:** while `main`'s own wrapper is active, the scope prints the traceback through the wrapper and exits with `SystemExit(1)`, the same code an uncaught exception gives. **Without `--redact` the exception propagates unchanged.**

**Files changed:** `Scripts/Tools/redaction.py`, plus the `@redaction_scope` line on the mains of `proof_report.py`, `asset_provenance.py`, `evidence_summary.py`, `token_coverage.py`, `suite_log_report.py`, `summarize_framework_log.py` and `plot_framework_timeline.py`. **New test file:** `Scripts/Tools/test_bo_redaction_lifecycle.py`, 13 tests.

## Coverage

| Task | Tests |
|---|---|
| BO-16 | `suite_log_report --json --redact` stdout still passes `json.loads`. The keys and counts equal the plain run. Masked values: `<external>/B.cpp`, `<tmp>/…/A Spaced.cpp` (a space inside the temp root is masked whole) and `<external>/suite.log`. Dotted test paths are kept |
| BO-17 | partial tails on both stdout and stderr are flushed at exit; an exception traceback is redacted; `sys.exit(3)` keeps its code and the held tail; mixed newlines with an explicit flush in mid-path (pinned: the early flush writes only the fragment, never the whole path); `parser.error` after install is redacted; argparse usage errors before install are unchanged |
| BO-18 | `suite_log_report`, `summarize_framework_log` and `plot_framework_timeline` mains run in one process through the sequence on, off, on, off: streams are restored after every call, redacted runs leak nothing, plain runs print verbatim paths, and the process ends unwrapped |
| BO-19 | `evidence_summary` with a missing evidence folder, and with an unreadable log (a folder where the log should be): no CSV and no temp leftovers, with and without `--redact`, and no leak under `--redact`. `token_coverage` with a missing log fails closed with no manifest, in both modes |
| BO-20 | near-miss matrix through `redact_text` and through `summarize_framework_log` and `plot_framework_timeline`. Kept verbatim: `/homework/…`, `/Home/…` (case-sensitive), a bare `/usr`, `/data2/…`, `/Game/…`, plugin mounts, `/Script/…`. Masked: `/var/log/x.log`. Pinned space limits: `D:\My Files\x.log` becomes `<external>/My Files\x.log`, and `/opt/My App/bin` becomes `<external>/My App/bin` |

## Tests run

**Red checks, in temp copies:**
- `redaction_scope` made a pass-through (the C-1486 state): **6 failures**, all from the BO-18 test.
- Only the redacted-traceback branch removed: **1 failure**, the BO-19 unreadable-log test.

| Command | Result |
|---|---|
| `python -m unittest test_bo_redaction_lifecycle` (from `Scripts/Tools`) | Ran 13, OK |
| the 25 other related suites (BO matrix, boundaries, hardening, the BK set, the characterization suite and others) | all OK |
| `python -m unittest Scripts.Tools.test_summarize_framework_log` (from the repo root) | OK |
| `python -m py_compile Scripts/Tools/*.py` | OK |

**Total: 27 suites, 191 tests, 0 failures.**

## Remaining limits

- **Spaces:** outside the project, temp and home roots, a path with a space is masked only up to the first space, so the trailing fragment can remain (pinned in BO-20). Not safely fixable in free text.
- **POSIX roots** are a case-sensitive allow-list. `/Home/…` and unlisted roots such as `/data2/…` are not masked; both are pinned.
- **Explicit mid-path `flush()`:** a tool that flushes in the middle of writing a path writes the fragment before the flush unredacted. No KI-167 tool does this; their output uses `print`.
- **Exit code under `--redact`:** an uncaught exception becomes `SystemExit(1)` instead of propagating. An in-process caller of a tool `main` sees `SystemExit` rather than the original exception type, but only under `--redact`.
- Redaction remains a sharing aid, not a security boundary.
