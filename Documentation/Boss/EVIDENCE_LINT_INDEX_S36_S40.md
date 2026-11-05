# Evidence freshness, EXPECTED lint, and tool index (Queue C S36–S40)

Offline evidence tooling and proof-sheet documentation updates; no gameplay code or proof claims changed.

- Added `verify_evidence_manifest.py` for the JSON format written by `evidence_pack.py`. It verifies safe relative paths, uniqueness, file existence, byte counts, and SHA-256. Failures name the missing/changed path.
- `proof_report.py --manifest` now reports `EVIDENCE STALE/INVALID` separately from checklist telemetry PASS/FAIL. It compares manifest hashes and sizes and flags a log mtime later than its manifest snapshot. A stale report returns 3 when gameplay checks have no harder failure; checklist failures still return 1.
- Added `lint_expected_sheets.py`: unknown `[FrameworkProof]` token names fail, and Setup/Control/PASS/FAIL sections are required. Untagged numeric/gameplay checklist items remain manual. Added explicit controls and the missing Setup section to the ten Codex proof sheets; all ten pass the lint.
- Added `audit_tool_index.py` and reconciled `Documentation/Boss/TOOLS.md` and `Scripts/Tools/README.md`. It checks each referenced script exists and answers `--help` successfully.

## Validation

- 22 offline Python tests pass, including valid/altered/missing/escaping evidence paths, stale-mtime detection separate from gameplay, expected-sheet typo/missing-section fixtures, tool-path parsing, and refusal of evidence inputs colliding with reserved manifest outputs.
- Linter passes all 10 current `*_EXPECTED.md` sheets.
- Tool index audit: 31 indexed scripts, 0 missing paths or unsupported `--help` commands.
- `check_doc_links.py .`: 0 broken links; Python compile passes; scoped diff check has no whitespace errors.
- No Unreal build, automation suite, PIE, commit, or push.
