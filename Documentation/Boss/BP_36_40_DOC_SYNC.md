# BP-36..40: tool documentation and index sync (Queue BP, batch 8 of 10)

C (implementer), 2026-11-13. Validation per X-2295: **static only**. Tool docstrings were read with `ast`; no tool was imported or executed.

**Not done:** no Unreal, build, PIE or asset work, no KNOWN_ISSUES status change, no commit or push.

| Task | Result |
|---|---|
| BP-36 | **Inventory:** 118 classified `Scripts/Tools` files (91 ALLOWLIST, 14 NO_RUN, 13 LIBRARIES; 6 helper modules excluded). The `Scripts/Tools/README.md` table had **66** rows, so **58 tools were missing**; there were **0 stale rows**. `Documentation/Boss/TOOLS.md` did **not mention 73** of them |
| BP-37 | **README:** 58 rows were appended inside the existing table, each with the first line of the tool's module docstring (pipes escaped); every tool has a docstring. **TOOLS.md:** a new section, "Index of tools without a usage section above (BP-37)", lists the 73 tools with kind (command, command not test-executed via NO_RUN, or library module) and purpose, and points to the README and the BO behaviour guide. Existing content in both files is unchanged; only additions were made (142 lines in total) |
| BP-38 | **New `Scripts/Tools/test_bp_doc_sync.py`, 4 static tests:** every classified tool has a README row; no README row points at a missing file; every README purpose is non-empty; every tool is mentioned in TOOLS.md. Combined with `test_bp_cli_smoke`'s completeness check, a new tool now has to be classified **and** documented before the suites pass |
| BP-39 | **Limits:** `audit_tool_index.py`, the existing index auditor, was **not run**, because it spawns `--help` subprocesses, which X-2295 forbids. The purposes are docstring first lines and were not reviewed for accuracy against behaviour. The two untracked tools (`verify_bf_x05_selected_route`, `verify_c1278_x26_live_log`) are listed by name and docstring only; their files are unchanged |
| BP-40 | This report |

**Changed files:** `Scripts/Tools/README.md` (+58 table rows) and `Documentation/Boss/TOOLS.md` (+ the BP-37 index section). **New:** `Scripts/Tools/test_bp_doc_sync.py`.

**Paths touched by the tests:** `Scripts/Tools/README.md` and `Documentation/Boss/TOOLS.md`, read only, plus the classification lists in `test_bp_cli_smoke.py`.

| Command (from `Scripts/Tools`, `BP_SMOKE_EXECUTE` unset) | Result |
|---|---|
| `python -m unittest test_bp_doc_sync` | Ran 4, OK |
| all 10 BP static and in-process suites | OK, 1 skipped (the execution class) |

**Red check:** with the pre-change README and TOOLS.md in a temp copy, **2 failures**: the README rows and the TOOLS.md mentions.
