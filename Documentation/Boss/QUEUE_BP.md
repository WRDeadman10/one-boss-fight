# Queue BP: CLI robustness for the remaining `Scripts/Tools` tools (50 tasks, 10 batches of 5)

C (implementer), 2026-11-12, per X-2282. Codex is the lead and Antigravity the reviewer.

**Scope:** the roughly 115 offline Python tools in `Scripts/Tools/` that lane BO did not cover. The goal is to bring them to the BO baseline:
- they run under both script and `python -m` invocation;
- missing or bad input fails closed with a named diagnostic;
- outputs are written safely;
- each tool has a consistent exit-code contract;
- there is test coverage for each of the above.

**Excluded:** owner decisions; editor, build, PIE, package and performance gates; asset or value authoring; KNOWN_ISSUES status changes; commits. KI-026 and KI-067 are excluded because they await separate criteria (X-2238). The BO tool files are touched only where a BP finding requires it, and each such change is called out.

**Seed findings** (2026-11-12 probe, every tool run with `--help` and with no arguments, both from `Scripts/Tools/` and as `python -m` from the repo root):
- **7 tools fail under `python -m`** with `ModuleNotFoundError`: `inventory_editor_asset_writers`, `new_rule_scaffold`, `summarize_encounter_cost` and `summarize_packaged_metrics` (`atomic_io`); `audit_editor_save_safety`, `audit_framework_schemas` and `round6_phase2_intake` (sibling imports).
- **4 tools trace back with no arguments outside the repo root**, because their default paths are relative to the current folder: `check_ki_references`, `check_test_plan_ids`, `mailbox_stats` and `token_coverage`.

| Batch | Tasks | Scope (files) | Acceptance |
|---|---|---|---|
| 1 | BP-01..05 | **BP-01:** `python -m` import guards for the 4 `atomic_io` tools. **BP-02:** guards for the 3 sibling-import tools. **BP-03:** the 4 cwd-dependent defaults resolve against the repo root (`Path(__file__).parents[2]`), keeping explicit arguments. **BP-04:** a new `test_bp_cli_smoke.py`: `--help` for every tool in both styles, plus a no-argument run from a foreign folder with no traceback. **BP-05:** batch report | smoke suite green for every tool; red check against the unfixed files; full BO runner still green |
| 2 | BP-06..10 | inventory every `json.loads`/`json.load` site in the non-BO tools; route the input-reading ones through `json_input` (named `ERROR <path>`, exit 2) in priority order; tests per fixed tool | bad JSON → exit 2, named, no traceback, no partial stdout; red checks |
| 3 | BP-11..15 | a nonexistent input path given to every tool that takes file or folder arguments: probe matrix, fix tracebacks into named usage errors | matrix test: no traceback on a missing input for any tool |
| 4 | BP-16..20 | output-write safety: tools that write without `atomic_io`, can overwrite their own inputs, or leave partial files on failure. Audit, fix the confirmed cases, inject failures | no partial or temp leftovers; alias refusal where the tool writes next to inputs |
| 5 | BP-21..25 | exit-code contract inventory (0 = clean, 1 = findings, 2 = bad input or usage) for all tools; fix inconsistent bad-input codes; doc table | inventory test pins every tool's code for each case |
| 6 | BP-26..30 | text-input encodings for the log, Markdown and CSV readers: UTF-8 BOM, UTF-16 and invalid bytes. Either accept a BOM where safe or fail closed with a name | encoding matrix test |
| 7 | BP-31..35 | tools with no test coverage: inventory, then a minimal black-box test per untested tool for its happy path plus one failure path | every tool referenced by at least one test |
| 8 | BP-36..40 | tool index and documentation sync: make the `Scripts/Tools/README.md` table, `audit_tool_index.py` and `Documentation/Boss/TOOLS.md` complete for all tools; a static test that keeps them in sync | sync test green; every tool listed |
| 9 | BP-41..45 | large-input behaviour of log parsers (bounded synthetic logs up to about 50 MB): memory and time sanity, streaming where a tool reads whole files unnecessarily (no behaviour change) | bounded runtime assertions; output parity before and after |
| 10 | BP-46..50 | extend `run_bo_lane_tests.py` (or add a BP runner) to cover the BP suites; static pins for the BP guards; a user guide update; cumulative closeout and final run | final runner green; closeout report |

**Per-batch handoff:** the task IDs, changed files, the commands actually run with their results, red-check counts, and limits. Each batch has its own report, `Documentation/Boss/BP_xx_yy_*.md`. I continue to the next batch without waiting for review.
