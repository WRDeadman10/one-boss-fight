# Offline report tools: fail-closed behaviour and `--redact` (user guide)

This is the user-facing summary of lane BO (KI-163..167, 2026-11-12). It covers what the 13 tools now do on bad input and how to share their output safely. **No Unreal is needed** for any of this. The design history and evidence are in `BO_LANE_REDACTION_ACCEPTANCE.md` and `BO_46_50_KI163_167_EVIDENCE_AND_CLOSEOUT.md`.

## Exit codes on bad input

| Tool (`Scripts/Tools/`) | Bad input | Exit | What you see |
|---|---|---|---|
| `token_coverage.py` | any listed log missing | **2** | `MISSING <path>` lines plus `ERROR missing_logs=N; no samples manifest written`; no manifest file |
| `evidence_pack.py` | name collision, an output that is a file or a non-empty folder, a missing input | **2** | a usage error; **no output folder is created** |
| `make_source_manifest.py` | no `Source/` folder under `--root`, or output inside `Source/` | **2** | a usage error; no manifest. An existing but empty `Source/` gives a valid empty manifest |
| `profile_dump.py`, `card_table.py`, `validate_baked_cards.py`, `plugin_dependencies.py` | unreadable file, malformed JSON, wrong shape, nesting too deep | **2** | one line on stderr: `ERROR <file>: <reason>`. No traceback, and nothing on stdout. A UTF-8 BOM is accepted |

**Unchanged:** `validate_baked_cards.py` still exits **1** when it finds bad samples, and the other tools keep their own "issues found" codes. Usage errors from argparse exit **2**.

## Sharing output: `--redact`

**Available on:** `proof_report.py`, `asset_provenance.py`, `evidence_summary.py`, `token_coverage.py`, `suite_log_report.py`, `summarize_framework_log.py` and `plot_framework_timeline.py`.

```
python Scripts/Tools/suite_log_report.py path/to/suite.log --redact
python -m Scripts.Tools.suite_log_report path/to/suite.log --redact   # same result, from the repo root
```

**What it does (opt-in; without the flag the output is unchanged):**
- **Absolute machine paths** in every printed line, including errors and tracebacks, are rewritten:
  - files inside the project become repo-relative (`Source/X.cpp`);
  - the temp folder becomes `<tmp>/…` and your home folder becomes `<home>/…`;
  - any other drive, network or Unix machine path becomes `<external>/<file name>`.
- **Raw log or source lines** that a tool would echo become `<row redacted>`. Line numbers and parsed values stay.
- **Generated files:**
  - the `token_coverage --samples-output` manifest gets redacted paths and samples;
  - the `evidence_summary --output` CSV shows runs as `<evidence>/run1/editor_raw.log`.
- **Kept as they are:** Unreal object paths (`/Game/...`, `/Script/...`, plugin mounts), telemetry values and test names.
- **Short forms** such as `--reda` work wherever argparse accepts them.

**Known limits: check before sharing.**
1. **A path containing a space,** outside the project, temp and home folders, is only masked up to the space (for example `D:\My Files\x.log` becomes `<external>/My Files\x.log`).
2. **Unix paths** are recognised only under the usual machine folders (`/home`, `/tmp`, `/var`, `/opt`, `/usr`, `/Users`, `/Volumes` and others). `/data2/...` or `/Home/...` are left as they are.
3. **It is a sharing aid, not a security boundary.** Identifiers parsed from logs are still printed. Read the output before posting it.
4. **Under `--redact`, a crash prints a redacted traceback and exits 1.**

## Running the lane tests

```
python Scripts/Tools/run_bo_lane_tests.py            # every suite; exits nonzero if any fails
python Scripts/Tools/run_bo_lane_tests.py --list
python Scripts/Tools/run_bo_lane_tests.py --only test_bo_json_inputs
```

## Queue BP additions (2026-11-13)

Behaviour added across the other `Scripts/Tools` tools. The full history is in `QUEUE_BP.md` and the `BP_*.md` reports.

**Running tools:**
- All 13 BO tools, plus every tool on the `test_bp_cli_smoke` ALLOWLIST, run as a script **or** with `python -m Scripts.Tools.<tool>` from the repo root.
- Tools whose defaults name repo files (TEAM_MAILBOX, TEST_PLAN, Source and similar) resolve them against the repo root, so they work from any folder.

**Bad input:**
- **A missing input file:** `fight_capture_receipt`, `log_failures`, `mailbox_stats` and `make_fight_video` stop with `input file not found: <path>` (exit 2) instead of a traceback.
- **A malformed JSON input:** `check_g2_selection_refusal_expected`, `check_move_card_ids` and `round6_benchmark_report` exit 2 with `ERROR <path>: …`. `summarize_parity_set` marks just that pair `INVALID` and names the file.

**Encodings:**
- **JSON:** 17 tools accept a UTF-8 BOM, which Windows PowerShell 5.1 writes by default.
- **Markdown and log readers that use `text_input`:** `mailbox_decision_digest`, `mailbox_open_items`, `scan_doc_citations` and `evidence_summary` strip a BOM and refuse UTF-16 with a named error. The mailbox and doc readers also refuse invalid UTF-8; `evidence_summary` tolerates stray bytes in Unreal logs.
- **The remaining lenient readers** (`errors="replace"` or `ignore`) are listed in `BP_26_30_BOM_JSON_READS.md`.

**Output files:** `mailbox_decision_digest`, `normalize_cook_package_manifest`, `normalize_encounter_selection_graph`, `make_fight_video` and `audit_source_error_token_coverage` write atomically, with the same bytes as before. The last one still refuses to overwrite.

**Exit codes:** 0 = clean, 1 = findings, 2 = bad input or usage, 3 = "incomplete" (`proof_report` and `diff_suite_logs` only). The `test_bp_exit_codes` snapshot pins them per tool.

**Safety:** tests never execute tools by default. Only statically proven tools may run, and only with `BP_SMOKE_EXECUTE=1` plus lead approval. The reel builders (`build_*_reel`) overwrite media and are never run by tests.

**BP tests:** run `python -m unittest` on the `test_bp_*` suites from `Scripts/Tools`, or use `python Scripts/Tools/run_bp_lane_tests.py`, which runs them in-process.
