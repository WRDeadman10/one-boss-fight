# BP-26..30: text-input encodings for log and Markdown readers (queued scope) plus additive JSON BOM hardening (Queue BP, batch 6 of 10)

C (implementer), 2026-11-13. Validation per X-2295: **static and in-process only**. No tool `main()` and no subprocess was run.

Revised per X-2305 and X-2307. The first submission (C-1527) changed only JSON reads, and the lead correctly rejected it against the queue row: "log, Markdown and CSV readers; UTF-8 BOM, UTF-16, invalid bytes". **Part A below is the queued scope. Part B is the earlier additive JSON work**, kept separate.

**Not done:** no Unreal, build, PIE or asset work, no KNOWN_ISSUES status change, no commit or push.

## Part A: queued scope (log and Markdown readers)

**CSV readers: none exist.** There is no production `csv.reader`, `DictReader` or `read_csv` call in `Scripts/Tools`. `evidence_summary` uses `csv` for output only, and `round4_benchmark_report` only names `frames.csv` in an expected-input inventory. No CSV target was invented (consistent with the lead's X-2307 pointer).

**Line-oriented reader inventory** (the 91 allowlisted tools plus `scan_doc_citations`; `read_text` calls that do not feed `json.loads`): **85 reads in 61 tools.**

| Encoding / errors | Tools | Effect on bad input | Tools |
|---|---|---|---|
| `ascii` / `replace` | 1 | **conceals invalid UTF-8** | `check_stage_identity` |
| `utf-8` / `ignore` | 1 | **conceals invalid UTF-8** | `find_orphan_docs` |
| `utf-8` / `replace` | 40 | **conceals invalid UTF-8** | `asset_provenance`, `audit_editor_map_loads`, `audit_editor_save_safety`, `audit_framework_schemas`, `audit_pie_command`, `audit_tool_index`, `check_doc_links`, `check_headers_selfcontained`, `check_ki_references`, `check_mailbox_ids`, `check_shipping_guards`, `check_ue_python_enum_conventions`, `check_validator_tokens`, `compare_framework_tokens`, `compare_parry_runs`, `detect_duplicate_pie_runs`, `diff_manifests`, `diff_suite_logs`, `fight_capture_receipt`, `framework_results`, `inventory_editor_asset_writers`, `lint_expected_sheets`, `list_automation_tests`, `list_cvars`, `list_todo_markers`, `log_failures`, `mailbox_stats`, `make_fight_video`, `plot_framework_timeline`, `proof_report`, `source_metrics`, `suite_log_report`, `summarize_er_guard_counter`, `summarize_framework_log`, `summarize_memory_soak`, `token_coverage`, `validate_owner_approval_envelope`, `validate_pending_definition_inputs`, `verify_c1278_x26_live_log`, `write_a4_parity_receipt` |
| `utf-8` / `strict` | 15 | fails on invalid UTF-8 (UnicodeDecodeError, not always named) | `audit_a5_driver_registration`, `audit_framework_schemas`, `audit_tool_index`, `check_bench_kit_manifest`, `check_g2_selection_refusal_expected`, `check_ki_references`, `check_test_plan_ids`, `check_validator_tokens`, `discover_focused_player_tests`, `scan_pie_driver_safety`, `token_coverage`, `validate_owner_approval_envelope`, `validate_pending_definition_inputs`, `validate_queue_batches`, `verify_evidence_manifest` |
| `utf-8-sig` / `replace` | 5 | **conceals invalid UTF-8** | `audit_source_error_token_coverage`, `check_bench_kit`, `check_evidence_sha256`, `check_g044_cook_manifest`, `verify_bk56_60_receipts` |
| `utf-8-sig` / `strict` | 3 | fails on invalid UTF-8 (UnicodeDecodeError, not always named) | `check_g044_cook_manifest`, `check_packaged_smoke_receipt`, `diff_a5_nightly_reports` |

**Every reader above decodes a UTF-16 file as UTF-8 without complaint,** which yields garbage, or with `replace` mostly U+FFFD. **The `replace` and `ignore` readers also conceal invalid UTF-8.**

**New helper `Scripts/Tools/text_input.py` with `read_text_input(path, errors="strict"|"replace")`:**
- universal newlines, identical to `Path.read_text`;
- a leading UTF-8 BOM is stripped;
- UTF-16 (an FF FE or FE FF byte-order mark, or NUL bytes within the first 4 KiB) **always** fails closed with `TextInputError: <path>: UTF-16 or binary input is not supported…`;
- `strict` turns invalid UTF-8 into `TextInputError: <path>: invalid UTF-8 at byte N`;
- `replace` keeps the lenient behaviour for third-party logs only;
- an unreadable path gives a named error.

**Applied to the candidate readers** (the lead's X-2307 list):

| Tool | Before | After |
|---|---|---|
| `mailbox_decision_digest` (Markdown mailbox) | `utf-8` strict; a BOM hid the first `###` header | `read_text_input` strict; `TextInputError` is a `ValueError`, already routed to `parser.error` (exit 2) |
| `mailbox_open_items` (Markdown mailbox) | `utf-8` strict | `read_text_input` strict; `TextInputError` added to the `parser.error` handler |
| `scan_doc_citations` (Markdown docs; NO_RUN tool) | `errors="ignore"`, which **silently dropped bytes** | strict. An undecodable doc becomes an `UNREADABLE` finding naming the file, instead of being skipped or mangled |
| `evidence_summary` (editor logs) | `utf-8` / `replace` | `read_text_input(..., errors="replace")`, kept lenient because these are third-party Unreal logs. A BOM is stripped, and UTF-16 now fails closed via `parser.error` before any CSV is written |

**The remaining `replace` and `ignore` readers are classified above but unchanged:** 47 tool entries in the table, built after the conversions; a tool can appear in more than one row. Converting them is a per-tool contract decision (strict versus lenient), and it is listed for the lead.

**New `Scripts/Tools/test_bp_text_inputs.py`, 7 in-process tests.** The matrix covers:
- plain text equal to `Path.read_text` in both policies;
- BOM stripping (the old decode kept U+FEFF);
- UTF-16 LE/BE with a BOM and UTF-16 LE without one, failing closed in both policies;
- invalid UTF-8 (strict gives a named error at the byte offset; replace equals the old behaviour);
- an unreadable path and a bad policy.

It also checks `scan_doc_citations.scan_all_va_docs` on a temp folder (UTF-16 and invalid docs become `UNREADABLE` findings), and statically checks that each converted call site has its documented policy.

**Results and red check:**
- `python -m unittest test_bp_text_inputs`: Ran 7, OK.
- All 9 BP static and in-process suites: OK, 1 skipped.
- The pre-change versions of the 4 readers in a temp copy give **5 failing results** (4 failures and 1 error).
- `text_input` is registered as a helper module in `test_bp_cli_smoke.py` (completeness).

**Paths touched by the tests:** a `TemporaryDirectory`, plus the four tools' source files, read only.

---

## Part B: additive JSON BOM hardening (C-1527, outside the queued criteria)

| Task | Result |
|---|---|
| BP-26 | **Inventory:** the 91 allowlisted tools make 108 `read_text` calls (96 `utf-8`, 11 `utf-8-sig`, 1 `ascii`) across 74 tools. A plain `utf-8` decode only matters for a leading BOM, and it **breaks** a file exactly where the text goes to `json.loads`, which rejects a BOM with "Unexpected UTF-8 BOM". Windows PowerShell 5.1 writes BOM files by default (`Out-File`, `Set-Content -Encoding utf8`). There are **23 such sites in 18 tools**; one tool is the untracked `verify_bf_x05_selected_route`, preserved per X-2300 |
| BP-27 | **Fix:** in the 17 tracked tools, exactly the `encoding="utf-8"` argument of each `json.loads(<path>.read_text(...))` read becomes `"utf-8-sig"`. That is **22 call sites, a one-token change each, located by AST position**. A BOM is never valid JSON content, so no valid file changes meaning; files without a BOM decode identically. All 17 still satisfy the static contract (91 PROVEN) |
| BP-28 | **New `Scripts/Tools/test_bp_bom_json_reads.py`, 3 tests:** (1) a static guard that no allowlisted tool, the exempt file aside, parses JSON from a plain `utf-8` `read_text`; (2) the per-tool converted-site counts pinned; (3) in-process on temp files, `utf-8-sig` equals `utf-8` for BOM-free files, a BOM file now parses to the same value, and the former decode raised `JSONDecodeError` |
| BP-29 | **Limits recorded** (below) |
| BP-30 | This report |

**Changed files (`Scripts/Tools/`):** `a7_release_gates`, `audit_pie_command`, `check_g044_cook_manifest`, `compare_encounter_parity`, `normalize_cook_package_manifest`, `normalize_encounter_selection_graph`, `proof_report` (a BO file), `round4_benchmark_report` (×3), `summarize_encounter_cost`, `summarize_packaged_metrics`, `validate_a5_receipt_directory` (×3), `validate_encounter_manifest`, `verify_bk7_shipping_receipt`, `verify_encounter_package_graph` (×2), `verify_evidence_manifest`, `verify_framework_perf_receipt` and `write_a4_parity_receipt`.

**Earlier working-tree edits** in several of these files, from the BK lane and earlier BP batches, were preserved; only the encoding token changed.

**Paths touched by the tests:** a `TemporaryDirectory`, plus the allowlisted tools' source files (read and parsed only).

| Command (from `Scripts/Tools`, `BP_SMOKE_EXECUTE` unset) | Result |
|---|---|
| `python -m unittest test_bp_bom_json_reads` | Ran 3, OK |
| all 7 BP static suites (`test_bp_cli_smoke`, `test_bp_static_contract`, `test_bp_json_inputs`, `test_bp_missing_inputs`, `test_bp_atomic_writes`, `test_bp_exit_codes`, `test_bp_bom_json_reads`) | OK, 1 skipped (the execution class) |
| `python -m compileall -q .` | OK |

**Red check:** the original versions of the 17 files in a temp copy give **18 failures**: the static guard, and the 17 pinned site counts.

## Limits

- **Only BOM handling on JSON-parsing reads is covered.** UTF-16 inputs are still not decoded; they fail closed or with a decode traceback, depending on each tool's error handling.
- **Line-oriented text readers** (logs, Markdown) keep plain `utf-8`. A leading BOM there only affects a first-line match, which no current tool depends on in a way I could prove statically.
- **Not verified by running the tools.** Existing suites that execute these tools (including the BO runner, which covers `proof_report`) were **not run**.
