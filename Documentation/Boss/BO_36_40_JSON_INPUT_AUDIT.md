# BO-36..40: JSON input edges and exit-code caller audit (lane BO, batch 8 of 10; scope C-1500 under X-2258)

C (implementer), 2026-11-12. Synthetic only.

**Not done:** no Unreal, build, PIE or asset work, no KNOWN_ISSUES status change, no commit or push.

## Defects found and fixed (`Scripts/Tools/json_input.py`)

1. **BO-36, a UTF-8 BOM was rejected.** All four KI-166 tools rejected a UTF-8 BOM file with `malformed JSON at line 1 column 1: Unexpected UTF-8 BOM`. Windows PowerShell 5.1 writes a BOM with `Out-File` or `Set-Content -Encoding utf8`, so valid exports were refused.
   - **Fix:** decode with `utf-8-sig`. A BOM is never valid JSON content, so accepting it cannot change the meaning of a valid file. The parsed output is identical with and without a BOM (tested).
2. **BO-37, deep nesting gave a traceback.** Pathologically deep nesting (for example 200,000 `[`) made `json.loads` raise an uncaught `RecursionError`.
   - **Fix:** it is caught and reported as `ERROR <path>: JSON nesting is too deep to parse`, exit 2, matching the KI-166 contract.

**Investigated and not changed:** `profile_dump.walk` is recursive. A probe showed `json.loads` reaches its own recursion limit (around 1,000 levels) **before** the recursive walk would overflow. So every structure the parser can return also walks safely, and there was no reproducible defect. An iterative rewrite was tried, shown equivalent, and then **reverted** to keep the source change minimal and every change red-checked. A 950-level structure is pinned as printing correctly.

**New test file:** `Scripts/Tools/test_bo_json_inputs.py`, 10 tests (8, plus 2 added for X-2264).

## Coverage

| Task | Tests |
|---|---|
| BO-36 | A BOM file is accepted by `profile_dump`, `card_table`, `validate_baked_cards` and `plugin_dependencies` (`.uproject`); the output is identical to the no-BOM file. UTF-16 and invalid UTF-8 bytes fail closed in all three single-file tools: exit 2, `ERROR … cannot read input`, no traceback, no stdout |
| BO-37 | 200,000 levels of nesting: a named exit-2 failure for the three file tools and for `plugin_dependencies`. A 950-level object prints its full path (the pin above) |
| BO-38 | Pinned characterization, with behaviour unchanged. `NaN`, `Infinity` and `-Infinity` are parsed and printed by `profile_dump`; duplicate keys keep the **last** value (Python `json` semantics); `validate_baked_cards` still rejects non-finite sample times and points (`samples=3 issues=2`, exit 1). Rejecting `NaN` everywhere would be a contract change for a tool such as `profile_dump` that only displays values, so it was not made |
| BO-39 | **Exit-code caller audit** (acceptance limit 8): repo-wide search of `*.py`, `*.ps1`, `*.bat` and `*.cmd` for callers of `token_coverage`, `make_source_manifest`, `profile_dump`, `card_table`, `validate_baked_cards` and `plugin_dependencies`. **There are no code callers;** `audit_source_error_token_coverage.py` matches the name only and does not call it. The Markdown references, outside the BK/BM/BN/BO lane reports and Archive, only describe the old defects (AX-C11..15, BI-A16..20, S173, D68, D72, S195, KNOWN_ISSUES) or one past invocation (TASKS.md:2229, which used default discovery, where a missing log cannot occur). **No runbook depends on the old 0/1 codes.** Follow-up: BO-39 found that `OPEN_CODEX_FINDINGS_DISPOSITION_S195.md` rows 27 and 29 still said "no code fix authorized" for KI-163/165. The lead has since corrected both rows (X-2266/X-2267): they keep the C-737 history and cite the X-2236 authorization and the BO work. KNOWN_ISSUES statuses are unchanged |
| BO-40 | `BO_LANE_REDACTION_ACCEPTANCE.md` gains a BO-36..40 row; limit 8 is updated by the BO-39 result |

## Tests run

**Red checks, in temp copies:**
- `utf-8` restored: **5 failures** (BO-36).
- The `RecursionError` catch disabled: **4 failures** (BO-37, all four tools).
- The walk revert produced 0 failures, which is how I found that the walk was not a defect; see above.

| Command | Result |
|---|---|
| `python -m unittest test_bo_json_inputs` (from `Scripts/Tools`) | Ran 10, OK |
| the 29 other related suites | all OK |
| `python -m unittest Scripts.Tools.test_summarize_framework_log` (from the repo root) | OK |
| `python -m py_compile Scripts/Tools/*.py` | OK |

**Total: 31 suites, 230 tests, 0 failures** (after X-2264).

## Limits

- **Other encodings** (UTF-16, Latin-1) are still refused, by design. They fail closed with a named diagnostic.
- **The `NaN` and duplicate-key behaviour** is Python's `json` default, pinned rather than changed.
- **The BO-39 audit covered in-repo files only.** Scripts outside the repo, or local shell aliases, cannot be checked.

## X-2264 rework (C-1503): BO-38 pinned through all four tools

BO-38 originally pinned `NaN` and duplicate-key behaviour only in `profile_dump` and `validate_baked_cards`. Two tests now cover the other two tools, with behaviour unchanged:

- **`card_table`:** prints `NaN`, `Infinity` and `-Infinity` timings as `nan`, `inf` and `-inf`. The last duplicate key wins, for a scalar (`MoveId` A then B prints B) and for a list (a later `Windows` with 1 sample replaces an earlier one with 2).
- **`plugin_dependencies`:** tested through the real `.uproject` and `.uplugin` paths.
  - A duplicate `Plugins` key in the `.uproject` keeps the last list.
  - In the `.uplugin`, a duplicate `FriendlyName` keeps `New`, and a dependency with duplicate `Name` keys keeps `Dep2`.
  - `"Enabled": NaN` prints `enabled=nan`, and `bool(NaN)` counts it in `enabled_entries`.

**The `NaN` count is pinned, not changed:** Unreal never writes `NaN` in descriptors, and the tool's contract is reporting, not validation. If the lead wants it to fail closed instead, that is a small follow-up.
