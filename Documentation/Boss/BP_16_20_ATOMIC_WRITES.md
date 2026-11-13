# BP-16..20: non-atomic output writes converted to `atomic_io` (Queue BP, batch 4 of 10)

C (implementer), 2026-11-12. Validation per X-2295: **static and in-process only**. No tool `main()` and no subprocess was run.

**Not done:** no Unreal, build, PIE or asset work, no KNOWN_ISSUES status change, no commit or push.

| Task | Result |
|---|---|
| BP-16 | **Static inventory** of the 91 allowlisted tools for direct `write_text`, `write_bytes` or `open(..., "w")`. **7 found.** Two of them, `verify_bf_x05_selected_route` and `verify_c1278_x26_live_log`, are **untracked files** that are probably someone else's work in progress, so they were left untouched and are flagged for the lead |
| BP-17 | **Converted 5 tools**, keeping the exact bytes each call wrote. Each gained the exact BP `sys.path` guard before importing `atomic_io`, and all five are still **PROVEN** by the static contract. Details below |
| BP-18 | **New `Scripts/Tools/test_bp_atomic_writes.py`, 6 tests.** Static: no direct writes remain; the report writer keeps no-overwrite; the static contract still holds. In-process on temp files: LF-pinned equivalence, platform-newline equivalence for both `make_fight_video` helpers (5 samples, including CRLF, Unicode and empty), and `atomic_create_text` refusing an existing file with no temp leftovers |
| BP-19 | **Limits recorded** (below) |
| BP-20 | This report |

**BP-17 conversions:**
- **`audit_source_error_token_coverage`** now uses `atomic_create_text`: atomic and no-overwrite, matching its existing refusal to overwrite.
- **`mailbox_decision_digest`, `normalize_cook_package_manifest` and `normalize_encounter_selection_graph`** now use `atomic_write_text`. Each was previously `write_text(..., newline="\n")`, so the LF bytes are identical.
- **`make_fight_video`'s three writes** (the ffconcat file, the `.ass` subtitles and `ffmpeg_command.txt`) used text mode with no `newline=`, which on Windows writes `\r\n`. The new `_platform_newlines()` translates `\n` to `os.linesep` before `atomic_write_text`, so the bytes are unchanged. `import os` was added after `pyflakes` would have caught its absence: I briefly had it missing during the edit, and fixed that before any test ran.

**Changed files:** `Scripts/Tools/audit_source_error_token_coverage.py` (also BP-03), `mailbox_decision_digest.py`, `normalize_cook_package_manifest.py`, `normalize_encounter_selection_graph.py` and `make_fight_video.py`. **New:** `Scripts/Tools/test_bp_atomic_writes.py`.

**Paths touched by the tests:** a `TemporaryDirectory`, plus the five tools' source files, read only. `make_fight_video` and `atomic_io` are imported, which their proven import-time safety allows. No `main()` was called and no real project path was written.

| Command (from `Scripts/Tools`, `BP_SMOKE_EXECUTE` unset) | Result |
|---|---|
| `python -m unittest test_bp_atomic_writes` | Ran 6, OK |
| `python -m unittest test_bp_cli_smoke test_bp_static_contract test_bp_json_inputs test_bp_missing_inputs test_bp_atomic_writes` | OK, 1 skipped (the execution class) |
| `python -m pyflakes` on the 5 edited files | no output (clean) |

**Red check:** the pre-change versions of the five tools in a temp copy give **11 failing results**: 6 failures (the static checks) and 5 errors (the `_platform_newlines` helper missing).

## Limits

- **Not verified by running the tools.** The bytes each tool writes are verified through the helper-level equivalence above, not by executing the tools. Running them needs your approval under X-2295.
- **Existing suites that execute these tools were not run** (for example any normalize or mailbox suites).
- **The two untracked writers** keep their direct `write_text`.
