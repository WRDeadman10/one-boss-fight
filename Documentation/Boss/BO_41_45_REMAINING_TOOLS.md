# BO-41..45: the lane tools outside the KI-167 set, plus a closeout plan (lane BO, batch 9 of 10; scope C-1504 under X-2267)

C (implementer), 2026-11-12. Synthetic only.

**Not done:** no Unreal, build, PIE or asset work, no KNOWN_ISSUES status change, no commit or push.

## Defect found and fixed (BO-41)

**`python -m Scripts.Tools.evidence_pack` and `python -m Scripts.Tools.make_source_manifest` failed** with `ModuleNotFoundError: No module named 'atomic_io'`. This is the same defect class as BO-28, which fixed `token_coverage` and `evidence_summary`. Both tools now insert their own folder into `sys.path` before importing `atomic_io`. Script invocation is unchanged.

**Files changed:** `Scripts/Tools/evidence_pack.py` and `make_source_manifest.py` (import guard only). **New test file:** `Scripts/Tools/test_bo_remaining_tools.py`, 11 tests.

**All 13 lane tools now work under both invocation styles** (BO-42).

## Coverage

| Task | Tests |
|---|---|
| BO-41 | `evidence_pack`, `make_source_manifest`, `profile_dump`, `card_table`, `validate_baked_cards` and `plugin_dependencies`: `python -m` and a direct script give exit 0 and the same stdout (output names normalized) |
| BO-42 | All 13 lane tools × {script, `-m`}: `--help` exits 0 with usage and no traceback; a no-argument run exits 2 with usage and no traceback. `token_coverage` and `plugin_dependencies` have no required argument and are excluded from the no-argument check |
| BO-43 | `make_source_manifest`: a `Source` that is a file is refused (exit 2, no manifest); an **empty** `Source` gives a valid empty manifest (pinned: KI-165 requires only that `Source` exists); nested and hidden files are listed, sorted and in POSIX form with a relative `--root`; an output inside `Source` is refused (exit 2, no file) |
| BO-44 | `evidence_pack` (KI-164): an output root that is a file (exit 2, the file untouched), a non-empty folder (exit 2, its contents untouched), or a missing raw or state file (exit 2, **no folder created**) are all rejected. A relative output root works. The same file given as raw and pre-state is pinned: it is copied twice, as `r.log` and `pre_r.log` |
| BO-45 | Acceptance checklist rows, plus the BO-46..50 closeout plan below |

## Tests run

**Red check:** the old import order restored in a temp copy gives **4 failures**: `-m` for `evidence_pack` and `make_source_manifest` in BO-41 and BO-42.

| Command | Result |
|---|---|
| `python -m unittest test_bo_remaining_tools` (from `Scripts/Tools`) | Ran 11, OK |
| the 30 other related suites | all OK |
| `python -m unittest Scripts.Tools.test_summarize_framework_log` (from the repo root) | OK |
| `python -m py_compile Scripts/Tools/*.py` | OK |

**Total: 32 suites, 241 tests, 0 failures.**

## Limits

- **An empty `Source` passing** and **the same file as raw and pre-state** are pinned as current behaviour, not judged to be defects. Changing either is a lead decision.
- **`-m` invocation needs the repo root as the working directory,** which is standard for `Scripts.Tools.*`.

## Proposed BO-46..50 closeout (for the lead to confirm or replace)

| Task | Proposal |
|---|---|
| BO-46 | **One-command lane runner** `Scripts/Tools/run_bo_lane_tests.py`: runs the 32 suites in both styles where relevant, prints a pass/fail table, and exits nonzero on any failure. Offline; it replaces the ad hoc shell loop used in every BO batch |
| BO-47 | **Lane static pin:** a test that checks every KI-167 tool keeps `@redaction_scope`, `add_redact_argument` as the last option, and the gated install call. Similar to `test_bl_lane_static_checks` |
| BO-48 | **Documentation pass:** a "Redaction and fail-closed tool behaviour" section in `Scripts/Editor/README.md` or the Boss TOOLS doc (flags, exit codes, limits), with links from TEST_PLAN and KNOWN_ISSUES notes, without changing KI statuses |
| BO-49 | **KI-163..167 closure evidence pack:** for each KI, the fix, its test names, red-check counts and residual limits, so the lead can decide the KNOWN_ISSUES status |
| BO-50 | **Lane BO cumulative closeout report,** plus a final full run |
