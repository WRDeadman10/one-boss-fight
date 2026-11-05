# D142 — proof run-ID uniqueness and log association audit

Date: 2026-11-03  
Scope: static audit of driver run-ID creation, command/log paths, and evidence identity checks. No driver, editor, game, or test was run.

## Findings

### General PIE proof runs

Most retained PIE evidence is associated by an evidence-folder label and a `command.json` containing an absolute `-abslog=...\editor_raw.log` target, not by a run ID embedded in every raw log. A static scan of the current Claude execution tree found 579 `command.json` files / 579 `-abslog` entries. 97 target a log outside the command record's own directory; those 97 records target 70 distinct external log paths. Examples:

| Command record | Recorded `-abslog` target |
|---|---|
| `Claude/F4/dodge_run1_NavApiError/command.json` | `Claude/F4/dodge_run1/editor_raw.log` |
| `Claude/B_AGGRO/content_run1_FAIL_property_name_b_aggro_enabled/command.json` | `Claude/B_AGGRO/content_run1/editor_raw.log` |
| `Claude/B_ANM006/pie_warp_clamped_FAIL_no_map/command.json` | `Claude/B_ANM006/pie_warp_clamped/editor_raw.log` |

These may be deliberate retries/variants, but the command records alone do not prove which version of a shared target log belongs to each command. Re-running a command whose `-abslog` points at a shared path risks replacing or confusing the evidence associated with another folder label. Preserve each attempt's raw log immutably and record its hash alongside the exact command/result before retrying to an already-used target. Existing F4 final runs have timestamped backup logs, showing a mitigation in those specific folders; that does not establish a tree-wide rule.

### Drivers with explicit IDs

`Scripts/Editor/pie_build_fight.py:42-45` creates one `RUN_ID` per script process from a UTC timestamp to seconds plus the first eight hex characters of a UUID4 (32 random bits). It is shared across the three build variants in that process, which is an intentional batch identity; each archive JSON filename includes both run ID and build and opens with exclusive mode `"x"` (`:1404-1415`). Collision therefore fails the archive write rather than replacing that JSON record, though the catch path reports a persistence error and `build_fight_result_<BUILD>.txt` uses overwrite mode (`:1415-1423`). The ID is not a global engine-session ID, and the recorded source hash covers this driver script only (`:43-45`), not all compiled source/content. Its `METRIC run_id` is logged by the driver (`:1317-1328`), outside the FrameworkProof schema stream.

### Identity validation and duplicate-run tooling

`Scripts/Tools/proof_report.py` compares map/profile/run_id and optional source identity when the caller supplies expected values and can verify an optional evidence manifest. A mismatch or missing expected field contributes to failure. `run_id` accepts `runId`; source identity accepts `source`, `source_hash`, or `source_id`. The FrameworkProof schema contract does not require a universal run identity.

`Scripts/Tools/detect_duplicate_pie_runs.py:12-29,44-53` detects byte-identical engine-run chunks within a concatenated raw log, keyed by a content hash. It does not establish uniqueness across separate log files or bind an external command record to a particular log version. `Scripts/Tools/compare_parry_runs.py:14-31` compares token counts/outcomes and RESULT fields from two caller-supplied paths, but does not check that the paths are unique runs or paired by identity.

## Acceptance summary

Run-ID scope is documented: explicit driver IDs can be process/batch scoped, while ordinary PIE records rely on paths and metadata. Collision/association risks are concrete: shared absolute log targets, 32-bit random suffix within a timestamp second, and fixed-name result output. C-763 closed the fail-open expected-identity gap: `proof_report.py` now returns an identity failure when a requested field is absent. Offline tool suite: 48 tests run, 47 passed, 1 skipped. No driver, Editor, Unreal build, or project test suite was run.
