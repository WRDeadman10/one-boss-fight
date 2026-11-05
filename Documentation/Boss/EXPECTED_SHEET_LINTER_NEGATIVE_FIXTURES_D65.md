# Expected-sheet linter negative fixtures (D65)

Date: 2026-11-03. Extended `Scripts/Tools/test_queue_c_s36_s40.py`; ran `python -m unittest test_queue_c_s36_s40 test_queue_c_tools test_check_doc_links_s64` from `Scripts/Tools`: 30 tests passed, 1 host-dependent symlink test skipped.

## Cases covered

- Existing tests cover a misspelled/unregistered token and a missing Control heading, while preserving manual-only checklist items.
- New subtests remove each of Setup, Control, PASS, and FAIL individually and assert the precise missing-section diagnostic.
- A CLI-level negative fixture verifies an unknown token at line 4 prints `FAIL <path>: line 4: unregistered FrameworkProof token 'typo_token'` and returns 1.
- A CLI-level positive fixture confirms a structurally complete manual-only sheet passes with exit 0 and no registered tokens.

Missing input is handled by the CLI as a per-file FAIL and overall return 1; argparse/schema-load errors use argparse's exit 2. No schema files or project expected sheets were changed, and no project-wide linter run was performed.
