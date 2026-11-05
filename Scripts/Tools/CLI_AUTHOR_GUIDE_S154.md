# Offline tool CLI author guide (S154)

This is the contract index for the maintained Python CLIs in `Scripts/Tools/`. It records the input shape, normal output, deliberate exit status, and whether an invocation writes files. The seven `test_*.py` files are test modules, and `atomic_io.py` is a shared helper; none is a standalone CLI. All 43 maintained commands returned exit 0 for `--help`; that checks argument-parser availability only, not runtime behavior.

For all tools, argparse syntax errors exit 2. Missing or malformed files may produce a tool-specific diagnostic or an uncaught nonzero I/O/parse exception; uncaught JSON decode traces do not consistently name the input path. S173 found additional validation gaps in `token_coverage.py` (missing explicit logs can still yield exit 0 and a samples manifest), `evidence_pack.py` (creates the output directory before all destination checks), and `make_source_manifest.py` (a missing `Source` tree produces an empty manifest). See `Documentation/Boss/CLI_INPUT_VALIDATION_AUDIT_S173.md`. Unless a row says otherwise, output goes to stdout and project inputs are read-only. A report-only exit 0 means the scan completed; it does not certify a heuristic finding or gameplay result.

| CLI | Input | Output | Deliberate issue/error exit | Safety / side effects |
|---|---|---|---|---|
| `asset_provenance.py` | Authoring Python script; repeatable optional evidence path(s). | Declared source/destination asset paths and matching evidence lines. | 2 when script input is missing; otherwise 0 report. | Read-only; never edits assets. |
| `audit_framework_schemas.py` | Optional repository root. | Schema/emitter/index map, retained samples, field and format drift. | 1 for duplicate/missing mappings or literal format mismatch. | Read-only source/docs/log scan. |
| `audit_pie_command.py` | Command JSON and expected sheet. | Required args/CVars/ExecCmds comparison. | 2 invalid input; 1 requirement mismatch. | Read-only. |
| `audit_tool_index.py` | Optional root and index path. | Missing script and `--help` support report. | 1 if any indexed command is missing or help fails. | Read-only; invokes indexed commands with `--help`. |
| `card_table.py` | Card export JSON. | Card timing and baked-sample count table. | No validation code; parse/I/O error is nonzero. | Read-only JSON report. |
| `check_doc_links.py` | Optional documentation root. | Broken relative Markdown links. | 1 when broken links exist. | Read-only. |
| `check_evidence_sha256.py` | Optional evidence root. | Manifest/hash mismatches. | 1 when issues exist. | Read-only. |
| `check_headers_selfcontained.py` | Optional repository root. | Heuristic header include suspects. | 0 even with suspects; not a compile verdict. | Read-only C++ scan. |
| `check_ki_references.py` | Optional repository root. | C++ KI references absent from KNOWN_ISSUES. | 0 report-only, including findings. | Read-only source/docs scan. |
| `check_line_endings.py` | Optional repository root. | Mixed CRLF/LF and lone-CR paths/counts. | 0 report-only. | Read-only; excludes configured generated/archive paths. |
| `check_mailbox_ids.py` | Optional mailbox Markdown file. | Numeric duplicate headers and interior ID gaps. | 1 when issues exist; malformed header prefixes are ignored. | Read-only. |
| `check_move_card_ids.py` | One or more exported card JSON files. | Duplicate MoveIds and counts. | 1 when duplicates exist. | Read-only. |
| `check_shipping_guards.py` | Optional repository root. | Actual CVar registration sites outside detected Shipping guards. | 0 report-only; inspect output manually. | Read-only heuristic source scan. |
| `check_test_plan_ids.py` | Optional repository root. | Duplicate/unsorted BUILD row IDs. | 1 when either condition exists. | Read-only. |
| `check_validator_tokens.py` | Optional repository root. | Emitted/schema/semantic-index/source-index gaps. | 1 when mappings are missing. | Read-only source/schema/docs scan. |
| `compare_framework_tokens.py` | Before log and after log. | Per-token count delta TSV on stdout. | 0 report-only. | Read-only logs. |
| `compare_parry_runs.py` | Baseline and candidate logs. | RESULT/outcome/token comparison. | 0 report-only, even when values differ. | Read-only logs; differences need interpretation. |
| `detect_duplicate_pie_runs.py` | One or more concatenated Unreal logs. | Duplicate engine-run chunks with original line spans. | 2 invalid/no marker; 1 duplicates; 0 none. | Read-only. |
| `diff_manifests.py` | Before and after SHA-256 manifests. | Added/removed/changed path rows. | 0 report-only; invalid rows raise nonzero parse error. | Read-only. |
| `diff_suite_logs.py` | Before and after suite logs. | Added/removed/changed test rows; marks incomplete input `PARTIAL`. | 2 invalid/no rows; 3 partial (missing terminal success marker); 1 changed complete logs; 0 identical complete logs. | Read-only. |
| `evidence_pack.py` | Raw log, output directory, optional pre/post states. | Copies input files and writes SHA-256 manifest(s). | 0 on success; missing inputs and destination collisions use argparse exit 2. | Atomically publishes fresh output files; refuses existing destinations. Caveat: creates output directory before destination collision checks. Manifest is written last as the bundle commit marker. |
| `evidence_summary.py` | Optional root/evidence directory and required CSV output. | One CSV row per retained editor log. | 0 on success; I/O failure is nonzero. | Builds the CSV before atomically replacing the requested output. |
| `framework_results.py` | One FrameworkProof log. | Line-numbered RESULT rows and parse diagnostics. | 1 when ERROR diagnostics exist; WARN/INFO-only diagnostics return 0. | Read-only. |
| `lint_expected_sheets.py` | One or more expected sheets; optional repository root. | Token and required-section findings. | 1 when a sheet fails lint. | Read-only. |
| `list_automation_tests.py` | Optional repository root. | Automation registration names and source locations. | 0 report-only. | Read-only source scan. |
| `list_cvars.py` | Optional repository root. | Project `rpg.*` CVar declarations/references. | 0 report-only. | Read-only source/config scan. |
| `list_todo_markers.py` | Optional scan root. | TODO/FIXME/XXX locations. | 0 report-only. | Read-only; excludes configured generated/archive/vendor trees. |
| `log_failures.py` | One log and optional match limit. | Numbered error/fatal/failure-like lines. | 0 report-only; matches are not automatically verdicts. | Read-only. |
| `mailbox_stats.py` | Optional TEAM_MAILBOX path. | Message counts by party and date. | 0 report-only. | Read-only mailbox scan. |
| `make_source_manifest.py` | Required output path; optional source root. | SHA-256 manifest for Source files. | 0 on success; I/O failure is nonzero. | Atomically replaces requested output after serialization; caveat: a root without a `Source` directory is accepted as an empty manifest. |
| `new_profile_field_scaffold.py` | Required field name; optional error/log tokens and test-control flag. | Prints review checklist to stdout. | Invalid values use argparse exit 2. | Stdout only; no file changes. |
| `new_rule_scaffold.py` | Rule name, requirement ID, slug, output root. | Creates rule header, test placeholder, and reference. | 2 invalid values or existing destination; 0 created. | Atomically creates new paths under output root and refuses existing destinations. Generated test is not a correctness test. |
| `plot_framework_timeline.py` | One log and optional row limit. | Text timeline of recognized FrameworkProof events. | 0 report-only, including no matching rows. | Read-only. |
| `plugin_dependencies.py` | Optional repository root. | Enabled plugins and local descriptor dependencies. | 0 report-only. | Read-only project/descriptor scan. |
| `profile_dump.py` | Profile export JSON. | Flattened nested field/value rows. | No validation code; parse/I/O error is nonzero. | Read-only. |
| `proof_report.py` | Enabled log and expected sheet; optional control/identity/completeness/manifest args. | Checklist rows and input evidence identity/hash. | 1 gameplay checklist failure; 2 incomplete required run; 3 stale/hash-invalid evidence absent harder failure; 0 pass. | Read-only; cannot prove unlogged/manual criteria. |
| `retired_source_names.py` | Optional repository root. | Occurrences of selected legacy names. | 0 report-only; occurrence is not a verdict. | Read-only source scan. |
| `source_metrics.py` | Optional repository root. | Per-folder source/test counts. | 0 report-only. | Read-only. |
| `suite_log_report.py` | One automation log; optional `--json`, `--allow-partial`. | Text or stable JSON test totals/failures/duplicate identities and completion-marker state. | 2 by default if terminal success marker is absent; 1 for failures/duplicates; 0 for a marked-complete clean summary. `--allow-partial` permits intentional partial summaries (not pass certification). | Read-only. |
| `summarize_framework_log.py` | One or more editor/PIE logs. | Per-instance/token/outcome/card summary. | 1 on validator or semantic failures; 0 otherwise. | Read-only. |
| `token_coverage.py` | Optional root and explicit logs; optional samples output. | Schema coverage and first retained real sample per token. | 1 for unknown tokens; missing explicit logs only print `MISSING` and do not independently force nonzero. | Read-only by default; `--samples-output` can still write a manifest after missing logs, atomically replacing the JSON destination. |
| `validate_baked_cards.py` | Baked-card JSON. | Card/sample totals and invalid/unordered sample locations. | 1 when samples are invalid; 0 when clean. | Read-only; does not edit assets. |
| `verify_evidence_manifest.py` | Evidence manifest JSON. | Missing path, size mismatch, and SHA-256 mismatch rows. | 1 when issues exist; 0 when clean. | Read-only; never repairs evidence. |

## Authoring a new CLI

1. Give positional and optional arguments meaningful types and help strings. Use `--help` before changing a caller or README example.
2. State accepted inputs, defaults, output destination, and units/identity assumptions. Keep generated output separate from source evidence.
3. Choose stable statuses: 0 success/clean, 1 findings or failed comparison, 2 invalid CLI/input, and a distinct status only when callers need to distinguish another state. Do not return 0 for a claimed PASS when the script only printed heuristic suspects.
4. Make writes opt-in, name the target path, refuse unexpected overwrites, and scope cleanup to artifacts created by the command. Never modify Unreal assets from an offline report tool.
5. Add the CLI to `README.md` and `Documentation/Boss/TOOLS.md` only after checking its actual parser and write behavior. Record whether it scans, validates, compares, or mutates; these are different claims.
