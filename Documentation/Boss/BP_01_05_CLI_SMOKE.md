# BP-01..05: `python -m` guards, repo-root defaults and a static CLI safety contract (Queue BP, batch 1 of 10)

C (implementer), 2026-11-12, per X-2282. The queue is in `QUEUE_BP.md`. Revised per X-2290: this report keeps three things separate:
- **A.** what was run before the incident;
- **B.** the incident;
- **C.** the static-only hotfix.

**Not done:** no Unreal, build, PIE or asset work, no KNOWN_ISSUES status change, no commit or push.

## A. Pre-incident work and evidence (executed before 22:08)

| Task | Files | Change | Evidence actually run |
|---|---|---|---|
| BP-01 | `inventory_editor_asset_writers.py`, `new_rule_scaffold.py`, `summarize_encounter_cost.py`, `summarize_packaged_metrics.py` | a `sys.path` guard before the `atomic_io` import | `python -m Scripts.Tools.<tool> --help` exited 0 for each, after first failing with `ModuleNotFoundError` |
| BP-02 | `audit_editor_save_safety.py`, `audit_framework_schemas.py`, `round6_phase2_intake.py` | the same guard before sibling imports | the same `-m --help` check |
| BP-03 | `check_ki_references`, `check_test_plan_ids`, `mailbox_stats`, `token_coverage` (a BO file), `check_doc_links`, `check_evidence_sha256`, `check_headers_selfcontained`, `list_automation_tests`, `list_cvars`, `plugin_dependencies` (a BO file), `retired_source_names`, `source_metrics`, `audit_tool_index`, `check_mailbox_ids`, `audit_source_error_token_coverage` | path defaults resolve against the repo root instead of the current folder. `audit_source_error_token_coverage` prints repo-relative paths (`_display`) | **parity runs:** the repo-root stdout, stderr and exit code are byte-identical before and after for the read-only tools, and the `audit_source_error_token_coverage` report is byte-identical from the repo root and from `Scripts/Tools/` (temp `--output`). Three tools whose output changed were reverted and deferred: `check_line_endings`, `list_todo_markers` and `check_shipping_guards` |

**Earlier working-tree edits** in `audit_editor_save_safety`, `inventory_editor_asset_writers`, `summarize_encounter_cost` and `plugin_dependencies` were preserved; only lines were inserted or changed in place.

**Pre-incident side effect:** a no-argument probe I ran from `Scripts/Tools/` made `audit_source_error_token_coverage` write a 1 KB fragment report to `Scripts/Tools/Documentation/Boss/U_C08_ERROR_PATH_AUDIT.md`. It wrote there because the default output path was relative to the current folder, which is a BP-03 defect. The untracked fragment was removed. The tracked report `Documentation/Boss/U_C08_ERROR_PATH_AUDIT.md` was not modified (checked with `git status`).

## B. Incident (C-1511)

**What happened:** the first smoke-test version ran `--help` for every file with a `__main__` block. Five tools have no argument parsing and ran for real. Three of them used `ffmpeg -y` and, between **22:08 and 22:09**, **overwrote** the owner's reels in `D:/FightVideo/SFX_audition/`: `Parry_Addendum_Reel`, `SFX_Audition_Reel` and `Batch3_Audition_Reel`, each `.mp4` and `.mp3`.

**Verified:**
- The new timestamps (22:08/22:09).
- The source is 33 RawWavs, which the scripts read.
- The other two of the five, `audit_source_test_coverage` and `diff_phase_two_auras`, contain no write or subprocess calls (source inspection).

**Not verified:** whether the regenerated reels match the earlier ones. There is no backup available to me. The owner has been asked to check them (X-2285).

**After the incident:** the media and reel scripts were not touched again. The re-run that showed unchanged reel timestamps was the pre-hotfix second run. Since X-2286, **no tool or test that executes tools has been run.**

## C. Static-only hotfix (X-2288, reworked per X-2290)

**New `Scripts/Tools/cli_static_contract.py`:** the analysed tool is never imported or executed. The contract is **sequential and fail-closed**:
- **Import time:** only stdlib imports, or local siblings that pass the same rules recursively, resolved next to the analysed file. Third-party imports fail. Other allowed statements:
  - docstrings and the `sys.path` guard;
  - assignments limited to pure constructors, plus one narrow `getattr(<stdlib module>, "<const>", <const>)` form;
  - function and class definitions with pure decorators, defaults, bases and class bodies.

  Any if, try, for or with block, or any top-level call, fails.
- **`__main__`:** only dispatches to `main()`.
- **`main()`:** read statement by statement. Before the parse, only direct assignments or expression statements made of parser-setup calls are allowed: no control flow, and no nested def, class, lambda or comprehension. The parse must be a direct statement whose outermost call is `parse_args`, `parse_known_args` or `parse_intermixed_args`.

**New `Scripts/Tools/test_bp_static_contract.py`, 15 tests.** It writes synthetic sources to a temp folder, and they are only parsed. It covers:
- **Codex's X-2291 counter-example:** a nested uncalled `parse_args` before an `ffmpeg -y` call, which is rejected;
- a branch before the parse;
- a parse inside a branch;
- a write before the parse;
- a lambda before the parse;
- an unsafe local import (rejected) versus a safe one (accepted);
- a third-party import;
- top-level calls and blocks;
- an impure decorator, default or class body;
- a `__main__` block that does more than dispatch;
- the narrow `getattr` form;
- the incident tools failing the contract;
- `atomic_io`, `json_input` and `redaction` passing as import-safe.

**`test_bp_cli_smoke.py` was regenerated from the new contract:**
- `ALLOWLIST` holds **91** tools (each re-proven), `NO_RUN` **14** with the contract's exact failure reasons (including the 5 incident tools), `LIBRARIES` **13**, and helpers **5**.
- A completeness test fails if any file is unclassified.
- **The no-argument execution class and its bounded read-only scan were removed:** that claim is not provable statically. The BP-03 parity results in section A stand as pre-incident evidence only.
- **The only execution class, `HelpExecution`, is skipped** unless `BP_SMOKE_EXECUTE=1`, which needs lead approval.

**Commands run in section C (static only; `BP_SMOKE_EXECUTE` unset; no tool executed):**
- `python -m unittest test_bp_cli_smoke test_bp_static_contract -v` (from `Scripts/Tools`): **Ran 21, OK, 1 skipped** (`HelpExecution`).
- `python cli_static_contract.py` (from `Scripts/Tools`) parses sources only: **91 PROVEN**.

## Limits

- **The 14 NO_RUN tools** include 9 that are probably safe but fail the strict rules: `spec_from_file_location` module loads, imports inside `main` before parsing, top-level comprehensions, a call in a default value, and a `try` before parsing. They stay unexecuted until reviewed or refactored.
- **The stdlib list** comes from `sys.stdlib_module_names` (Python 3.10). Standard-library modules are assumed to be import-safe.
- **Whether the reels match their earlier versions** is unknown (section B).
