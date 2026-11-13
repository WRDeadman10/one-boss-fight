# BO-46..50: lane runner, static pins, user guide, KI-163..167 evidence matrix and the lane BO closeout (batch 10 of 10, per X-2270)

C (implementer), 2026-11-12. Lane BO is the owner's 50-task cadence (10 batches of 5), led by Codex and reviewed by Antigravity.

**Not done in the whole lane:** no Unreal, build, PIE, cook or asset work; no KNOWN_ISSUES status change; no commit or push.

## BO-46..48 deliverables

| Task | Deliverable | Check |
|---|---|---|
| BO-46 | `Scripts/Tools/run_bo_lane_tests.py`: runs every lane suite (11 BO suites, 22 regression suites, 1 package-style suite) in its own subprocess; prints a table; exits nonzero on any FAIL, TIMEOUT or NO TESTS; options `--only` and `--list` | `test_bo_lane_runner.py`, 7 tests: every listed suite exists; every `test_bo_*` file is listed; `--only` works, including the package suite from the repo root; an unknown suite exits 2; a deliberately failing probe suite reports FAIL; `--list` |
| BO-47 | `Scripts/Tools/test_bo_lane_static_pins.py`, 4 AST tests: `@redaction_scope` on all 7 mains; `add_redact_argument` is the last option before `parse_args`; exactly one `install_stream_redaction(True)`, inside `if args.redact:`; the `sys.path` guard precedes sibling-helper imports in all 13 lane tools | **Mutation check:** one violation per rule in a temp copy gives **4 of 4 failures, each at the mutated tool and rule** |
| BO-48 | `Documentation/Boss/BO_TOOL_BEHAVIOUR_GUIDE.md`: the exit-code table, `--redact` usage and output forms, the four user-facing limits, and how to run the tests. Links added to `Scripts/Tools/README.md` and `Documentation/Boss/TOOLS.md` | docs only |

## BO-49: KI-163..167 evidence matrix (recommendations only; KNOWN_ISSUES statuses unchanged)

| KI | Fix | Tests | Red check | Residual limits | **Recommendation to the lead** |
|---|---|---|---|---|---|
| **KI-163** `token_coverage` missing logs | a missing log gives exit 2 and no manifest (BO-01) | `test_bo_tool_hardening` Ki163 ×2; `test_bo_redaction_lifecycle` BO-19; `test_bo_redaction_cli` BO-29 | 17 failures against the HEAD tools (BO-01..05) | exit code 2 is new; no in-repo caller depends on the old code (BO-39) | **Ready to close** |
| **KI-164** `evidence_pack` creates the folder before preflight | `mkdir` runs after every check (BO-02) | `test_bo_tool_hardening` Ki164 ×3; `test_bk226_230` (3 updated assertions); `test_bo_remaining_tools` BO-44 ×5 | included in the 17 above | the same file as raw and pre-state is copied twice (pinned) | **Ready to close** |
| **KI-165** `make_source_manifest` without `Source/` | refused with exit 2 and no manifest (BO-03) | `test_ki165_166_characterization` Ki165 ×2; `test_bo_tool_hardening` Ki165; `test_bo_remaining_tools` BO-43 ×4 | included in the 17 above | an existing but empty `Source/` gives a valid empty manifest (pinned) | **Ready to close**; deciding on the empty-`Source/` case is optional |
| **KI-166** malformed JSON in the 4 tools | `json_input`: named `ERROR <path>`, exit 2, no traceback or partial output (BO-04); UTF-8 BOM accepted, deep nesting fails closed (BO-36/37) | `test_ki165_166_characterization` Ki166 ×5; `test_bo_json_inputs` ×10 | BO-04 in the 17 above; BOM 5 failures; recursion 4 failures | `NaN`/`Infinity` and duplicate keys follow Python `json` (pinned); `"Enabled": NaN` counts as enabled in `plugin_dependencies` (pinned) | **Ready to close**; the `NaN` handling is an optional follow-up |
| **KI-167** report tools expose absolute paths and raw rows | opt-in `--redact` across 7 tools; stream redaction of all output; lifecycle, scope, argparse pre-scan and `-m` fixes (BO-05..35, BO-41) | `test_bo_redaction_matrix` 15, `_boundaries` 12, `_lifecycle` 13, `_robustness` 8, `_cli` 12, `_argv` 9, `test_bo_lane_static_pins` 4 | every behavioural fix red-checked; counts per batch report (9, 5, 6+1, 1+14, 7+4, 10, and the mutations 5/4/7) | partial masking of paths with spaces; POSIX allow-list; it is a sharing aid, not a security boundary; symlink cases unverified here (no privilege); a mid-path flush; `SystemExit(1)` under `--redact` | **Ready to close as "mitigated (opt-in)"**. The remaining limits are documented in the guide; the default output is unchanged by design |

## BO-50: lane BO cumulative closeout

| Batch | Report | Lead | Reviewer | Defects found and fixed |
|---|---|---|---|---|
| BO-01..05 | `BO_01_05_TOOL_HARDENING.md` | X-2238 finding, then fixed | A-909 | KI-163..167 implemented; package-import regression |
| BO-01..05 hotfix + BO-06..10 | `BO_06_10_REDACTION_COMPLETION.md` | X-2241 | A-910 | the `asset_provenance` `value=` leak; all-output redaction |
| BO-11..15 | `BO_11_15_REDACTION_BOUNDARIES.md` | X-2245 | A-911 | no disable; split-write leak; space-cut user-name leak; CSV run identity |
| BO-16..20 | `BO_16_20_REDACTION_LIFECYCLE.md` | X-2247 | A-912 | stale wrapper; unredacted traceback (my regression, caught in the same batch) |
| BO-21..25 | `BO_21_25_REDACTION_ROBUSTNESS.md` | X-2249 | A-913 | a main without the flag unwrapped the caller's wrapper |
| BO-26..30 | `BO_26_30_REDACTION_CLI.md` | X-2250 rework, then fixed | A-914, A-915 | argparse-error leak; `-m` import (already broken at HEAD); the `--re` short-prefix leak |
| BO-31..35 | `BO_31_35_ARGV_PARITY.md` | X-2256 rework, then X-2258 | A-917, A-918 | none (parity proven; BO-34 extended to all 7 mains) |
| BO-36..40 | `BO_36_40_JSON_INPUT_AUDIT.md` | X-2264 rework, then X-2267 | A-919, A-920 | BOM rejected; RecursionError traceback |
| BO-41..45 | `BO_41_45_REMAINING_TOOLS.md` | X-2270 | A-921 | `-m` for `evidence_pack` and `make_source_manifest` |
| BO-46..50 | this file | pending | pending | none (runner, pins, guide, evidence) |

**Totals:**
- **18 distinct defects found and fixed** across the lane: 5 KI implementations, 13 hardening defects or regressions.
- **4 lead reworks,** all closed. One regression of mine (BO-19) was caught inside the batch that introduced it.

**Source files changed by the lane:** `Scripts/Tools/` `token_coverage.py`, `evidence_pack.py`, `make_source_manifest.py`, `profile_dump.py`, `card_table.py`, `validate_baked_cards.py`, `plugin_dependencies.py`, `proof_report.py`, `asset_provenance.py`, `evidence_summary.py`, `suite_log_report.py`, `summarize_framework_log.py` and `plot_framework_timeline.py`.

**New helpers:** `json_input.py`, `redaction.py` and `run_bo_lane_tests.py`.

**New suites (11):** `test_bo_tool_hardening`, `test_bo_redaction_matrix`, `test_bo_redaction_boundaries`, `test_bo_redaction_lifecycle`, `test_bo_redaction_robustness`, `test_bo_redaction_cli`, `test_bo_redaction_argv`, `test_bo_json_inputs`, `test_bo_remaining_tools`, `test_bo_lane_static_pins` and `test_bo_lane_runner`.

**Updated suites:** `test_ki165_166_characterization` (now pins the fixed behaviour) and `test_bk226_230_evidence_pack_audit` (3 assertions).

**The BK lane's earlier working-tree edits** to `token_coverage`, `evidence_pack`, `make_source_manifest` and `evidence_summary` were preserved throughout.

### Final lane run (BO-50)

Command, from the repo root:
```
python Scripts/Tools/run_bo_lane_tests.py
python -m compileall -q Scripts/Tools
```
**Result:** `suites=34 tests=252 failing=0` (runner exit 0; 4 skips, all symlink or platform skips from earlier suites); `compileall` passed.

### Handed back to the lead

- **KNOWN_ISSUES status** for KI-163..167, per the BO-49 recommendations above.
- **Optional follow-ups,** not started:
  - fail closed on `NaN` in `plugin_dependencies`;
  - the empty-`Source/` policy;
  - symlink verification on a machine with symlink privilege.
- **Still waiting for separate criteria (X-2238):** KI-026 and KI-067.
- **Commit:** no lane changes were committed or pushed. Alongside `Scripts/Tools/` and `Documentation/Boss/` lane reports, Codex updated `Documentation/TASKS.md`, `Documentation/PROJECT_STATE.md`, `Documentation/Boss/OPEN_CODEX_FINDINGS_DISPOSITION_S195.md`, and the BO review-status rows in `Documentation/Boss/BO_LANE_REDACTION_ACCEPTANCE.md`; the team coordination trail is in `Documentation/TEAM_MAILBOX.md`. Claude also added one tool-guide link line each in `Scripts/Tools/README.md` and `Documentation/Boss/TOOLS.md`.
