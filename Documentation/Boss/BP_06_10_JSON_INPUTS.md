# BP-06..10: fail-closed JSON input for four more tools (Queue BP, batch 2 of 10)

C (implementer), 2026-11-12. Validation policy per X-2295: **in-process unit tests only**. No subprocess, no CLI or `main()` execution, and no real project default or output paths.

**Not done:** no Unreal, build, PIE or asset work, no KNOWN_ISSUES status change, no commit or push.

## BP-06 inventory (static)

`json.load(s)` sites in the non-BO tools with **no** decode handling: `air_light_receipt` and `camera_probe_receipt` (library modules: their callers own error handling, so they were left as they are), `aura_warmup_receipt` and `fight_review_observation` (NO_RUN in the smoke allowlist, so they were deferred), and `check_g2_selection_refusal_expected`, `check_move_card_ids`, `round6_benchmark_report` and `summarize_parity_set` (fixed below). The other 30 sites already catch decode or value errors.

## Fixes (`Scripts/Tools/`)

| Task | Tool | Change |
|---|---|---|
| BP-06 | `check_g2_selection_refusal_expected.py` | a new `load_sheet()` uses `json_input.load_json(path, dict)`; `main` catches `JsonInputError` and calls `fail()`, giving exit 2 with `ERROR <path>: …` |
| BP-07 | `check_move_card_ids.py` | a new `load_cards()` takes a list, or an object with `cards`; every card must be an object. All exports are validated before any line is printed |
| BP-08 | `round6_benchmark_report.py` | a new `load_receipt()`; a malformed receipt fails closed and names the file. The existing `validate()` still reports a wrong shape as `INVALID` (exit 2) |
| BP-09 | `summarize_parity_set.py` | inside `summarize()`, a malformed `parity_report.json` (or a non-object) marks **that pair** `INVALID`, with the file named in its issue, instead of aborting the summary with a traceback. It counts in `failed_or_missing`, so the exit stays nonzero |

Each of the four gained the exact BP `sys.path` guard before importing `json_input`. All four, plus `round6_phase2_intake` (which imports `round6_benchmark_report`), still satisfy the static contract: **91 PROVEN**, unchanged.

## BP-10 tests and evidence

**New `Scripts/Tools/test_bp_json_inputs.py`, 10 in-process tests:**
- the loaders on valid, BOM, malformed, wrong-shape, missing and deeply nested inputs;
- `summarize()` with a malformed and an array report among valid ones;
- a static AST check that each `main` routes `JsonInputError` to `fail()` and no longer calls raw `json.loads`;
- a static-contract re-check.

**Paths touched:** a `TemporaryDirectory` for every fixture; the four tool modules are imported, which proven import-time safety allows; source files are read only for the AST checks. **No real project path is read or written.**

| Command (from `Scripts/Tools`, `BP_SMOKE_EXECUTE` unset) | Result |
|---|---|
| `python -m unittest test_bp_json_inputs` | Ran 10, OK |
| `python -m unittest test_bp_cli_smoke test_bp_static_contract test_bp_json_inputs` | OK, 1 skipped (the execution class) |
| `python cli_static_contract.py` (parses only) | 91 PROVEN |

**Red check:** the pre-change versions of the four tools in a temp copy give **10 of 10 failing** (3 failures, 7 errors). The old `summarize_parity_set.summarize()` raised `JSONDecodeError` on one malformed report.

## Not run (needs your approval under X-2295)

These existing suites execute tools (subprocess, `run_path` or `.main()`), so they were **not** run after these edits:
- `test_g2_selection_refusal_expected`
- `test_round6_benchmark_report`
- `test_round6_phase2_intake`
- `test_summarize_parity_set`
- `test_queue_w_workflows`
- `test_make_bench_kit_dependencies`
- the BO runner

Their behaviour on **valid** input should be unchanged, because only the error paths changed. That is not verified by execution.

## Limits

- **Two NO_RUN tools** (`aura_warmup_receipt`, `fight_review_observation`) and **two library modules** still use raw `json.loads`.
- **`summarize_parity_set`'s new INVALID row** is a behaviour change for malformed reports only: before, it was a traceback with exit 1; now it's a named row with exit 1.

## X-2298 hotfix (C-1525)

The lead's source review found two gaps that still did not fail closed. Both are fixed; in-process temp-fixture tests only.

1. **`check_move_card_ids.load_cards()`:** an object export without a `cards` key (`{}`, or `{"other": 1}`) was accepted as an empty export and could give a clean result. An object export must now carry an explicit `cards` key, whose value must be a list (via `require_objects`). Otherwise there is a named `JsonInputError`, which means exit 2. An explicit `{"cards": []}` is still allowed.
2. **`check_g2_selection_refusal_expected.load_sheet()`:** `audit()` ran `set()` over `cases` and `required_log_tokens` before checking element types, so `{"cases": [{}]}` raised an uncaught `TypeError`. `load_sheet` now validates both keys as **nonempty lists of unique strings** before returning. Every violation is a named `JsonInputError` (exit 2) that states the key and the index.

**Tests added to `Scripts/Tools/test_bp_json_inputs.py`:** 6 new tests, 16 in total.
- **G2:** a valid sheet; 8 malformed cases (an unhashable dict element, a list element, a number element, duplicate cases, duplicate tokens, missing cases, empty tokens, a string instead of a list); and the unhashable path that never reaches `audit()`.
- **Move cards:** `{}` and `{"other": 1}` are rejected; a `cards` object instead of a list is rejected; an explicit empty `cards` list is accepted.
- **Updated:** the earlier G2 valid/BOM fixture, which used empty lists that are now a schema error.

**Paths touched:** a `TemporaryDirectory` only (fixture JSON files); the two modules are imported; no `main()` is called.

**Results:**
- `python -m unittest test_bp_json_inputs`: Ran 16, OK.
- **Red check,** with both fixes reverted in a temp copy: **11 failures.**
- Both tools are still PROVEN by the static contract.

BP-06..10 stays in rework until the lead and AG review this hotfix.
