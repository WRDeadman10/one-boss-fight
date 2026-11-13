# BP-11..15: missing input files become named usage errors (Queue BP, batch 3 of 10)

C (implementer), 2026-11-12. Validation policy per X-2295: **static and in-process only**. No tool, `main()` or subprocess was run.

**Not done:** no Unreal, build, PIE or asset work, no KNOWN_ISSUES status change, no commit or push.

| Task | Result |
|---|---|
| BP-11 | **Static inventory** over the 91 allowlisted tools (parse-only). It looked for `main()` code that reads an `args.<name>` path (`read_text`, `read_bytes`, `open` or `load_json`) with no `is_file`/`exists`/`is_dir` check on that argument and no `OSError`-family or `JsonInputError` handler. **Found 4:** `fight_capture_receipt` (`--log`), `log_failures` (`log`), `mailbox_stats` (`mailbox`) and `make_fight_video` (`--log`). Each would raise a `FileNotFoundError` traceback on a missing path |
| BP-12 | **Fix:** immediately after `parse_args()`, `if not args.<input>.is_file(): parser.error(f"input file not found: …")`. That gives exit 2, a usage line and the named path, with no traceback. The check sits after parsing, so all four still satisfy the static contract (**91 PROVEN**, unchanged) |
| BP-13 | **New `Scripts/Tools/test_bp_missing_inputs.py`, 2 tests, static:** (1) for each fixed tool, the guard is the statement right after `parse_args()`, it calls `parser.error` and it precedes every read of that input; (2) a permanent allowlist-wide regression guard, which fails if any allowlisted `main()` reads an `args` path unchecked and unhandled |
| BP-14 | **Limits recorded:** the inventory and the guard see **direct** reads in `main()` only. Tools that pass `args.<name>` into a helper function that reads it are out of scope here. Some of those already fail closed (for example via `json_input` from BP-06..09); the rest need execution-based probing, which waits on your approval |
| BP-15 | This report |

**Changed files:** `Scripts/Tools/fight_capture_receipt.py`, `log_failures.py`, `mailbox_stats.py` (on top of its BP-03 default change) and `make_fight_video.py`, two inserted lines each. **New:** `Scripts/Tools/test_bp_missing_inputs.py`.

**Paths touched by the tests:** the source files of the allowlisted tools, read only and parsed with `ast`. Nothing else is touched.

| Command (from `Scripts/Tools`, `BP_SMOKE_EXECUTE` unset) | Result |
|---|---|
| `python -m unittest test_bp_missing_inputs` | Ran 2, OK |
| `python -m unittest test_bp_cli_smoke test_bp_static_contract test_bp_json_inputs test_bp_missing_inputs` | OK, 1 skipped (the execution class) |
| `python cli_static_contract.py fight_capture_receipt.py log_failures.py mailbox_stats.py make_fight_video.py` | 4 PROVEN |

**Red check:** the pre-change versions (HEAD copies of three tools, and `mailbox_stats` with the guard removed) in a temp copy give **5 failures**: the 4 per-tool guard checks plus the allowlist regression test.

**Not verified by execution:** the actual exit-2 message on a missing file. It is standard `argparse.error` behaviour; confirming it by running the tools needs your approval under X-2295.
