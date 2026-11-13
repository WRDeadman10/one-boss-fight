# Lane BO: KI-163..167 tool hardening and redaction, acceptance checklist (BO-30)

C (implementer), 2026-11-12. This consolidates BO-01..30.

**Scope:** offline Python tooling only. No Unreal, build, PIE or asset work; no KNOWN_ISSUES status change (KI-163..167 stay Open until the lead decides); no commits.

## 1. Behaviour contract

**Fail-closed tools (KI-163..166):**

| KI | Tool | Contract |
|---|---|---|
| KI-163 | `token_coverage.py` | any missing log means exit 2 and **no** samples manifest |
| KI-164 | `evidence_pack.py` | every collision and destination check runs before `mkdir`, so a rejected run leaves no output folder |
| KI-165 | `make_source_manifest.py` | a root without `Source/` means exit 2 and no manifest |
| KI-166 | `profile_dump`, `card_table`, `validate_baked_cards`, `plugin_dependencies` | malformed or wrongly shaped JSON means exit 2 with `ERROR <path>: <reason>`, no traceback and no partial stdout |

**`--redact` (KI-167), on `proof_report`, `asset_provenance`, `evidence_summary`, `token_coverage`, `suite_log_report`, `summarize_framework_log` and `plot_framework_timeline`:**
- [x] **Opt-in only.** Without the flag, output, files and exceptions are unchanged; the controls run in every suite.
- [x] **Every printed line,** including diagnostics, tracebacks and argparse usage errors, has absolute machine paths rewritten:
  - project paths become repo-relative;
  - the temp and home roots become `<tmp>/` and `<home>/`, including space-cut prefixes;
  - other drive, UNC and POSIX machine-root paths become `<external>/<name>`;
  - raw, forward-slash and JSON-escaped forms are all matched, ignoring case for the roots.
- [x] **Kept:** Unreal object paths (`/Game`, `/Script`, `/Engine`, `/Temp` and plugin mounts), parsed telemetry, dotted test identifiers and ratios.
- [x] **The KI-cited raw rows are replaced** by `<row redacted>`: asset_provenance evidence rows, the token_coverage `sample`, and the plot_framework_timeline payload fallback.
- [x] **Generated files:**
  - the token manifest holds a redacted `path`/`sample`;
  - the evidence_summary CSV holds `run` as `<evidence>/…` with `map` and `profile` redacted;
  - all other fields equal the default run.
- [x] **Lifecycle:**
  - line-buffered, so split writes are redacted whole;
  - the held tail is flushed on flush, disable and exit;
  - no double-wrap; disabling restores the original streams;
  - `redaction_scope` restores the caller's streams after every main;
  - a tool never unwraps a caller-owned wrapper;
  - under `--redact` an uncaught exception prints a redacted traceback and exits 1.
- [x] **Invocation:** direct script, `python -m Scripts.Tools.<tool>` and in-process `main()` behave the same.

## 2. Evidence

| Batch | Report | New or updated tests | Defects found and fixed |
|---|---|---|---|
| BO-01..05 | `BO_01_05_TOOL_HARDENING.md` | `test_bo_tool_hardening` (14), `test_ki165_166_characterization` (7), `test_bk226_230` (3 assertions) | KI-163..167 implemented; package-import regression fixed |
| hotfix + BO-06..10 | `BO_06_10_REDACTION_COMPLETION.md` | `test_bo_redaction_matrix` (15) | asset_provenance `value=` leak (X-2238); all-output stream redaction |
| BO-11..15 | `BO_11_15_REDACTION_BOUNDARIES.md` | `test_bo_redaction_boundaries` (12) | no disable; split-write leak; space-cut user-name leak; CSV run identity |
| BO-16..20 | `BO_16_20_REDACTION_LIFECYCLE.md` | `test_bo_redaction_lifecycle` (13) | stale wrapper; unredacted traceback (a regression caught in the same batch) |
| BO-21..25 | `BO_21_25_REDACTION_ROBUSTNESS.md` | `test_bo_redaction_robustness` (8) | a main without the flag unwrapped a caller's wrapper |
| BO-26..30 | `BO_26_30_REDACTION_CLI.md` | `test_bo_redaction_cli` (12) | argparse-error leak; `python -m` import failure (already broken at HEAD); X-2250 short unique-prefix leak (`--re`) |
| BO-31..35 | `BO_31_35_ARGV_PARITY.md` | `test_bo_redaction_argv` (9) | none; parity with argparse proven (0 mismatches over 8 option sets x 2 x 17 tokens); allow_abbrev=False verified for all 7 mains; mutations caught |
| BO-36..40 | `BO_36_40_JSON_INPUT_AUDIT.md` | `test_bo_json_inputs` (10) | UTF-8 BOM rejected (now accepted); deep-nesting RecursionError traceback (now a named exit 2); walk recursion investigated, not a defect |
| BO-41..45 | `BO_41_45_REMAINING_TOOLS.md` | `test_bo_remaining_tools` (11) | `python -m` failure for evidence_pack/make_source_manifest (fixed); all 13 tools help/usage smoke in both styles |
| BO-46..50 | `BO_46_50_KI163_167_EVIDENCE_AND_CLOSEOUT.md` | `test_bo_lane_static_pins` (4), `test_bo_lane_runner` (7) | none; lane runner, static pins (4 of 4 mutations caught), user guide `BO_TOOL_BEHAVIOUR_GUIDE.md`, KI-163..167 evidence matrix |

**Every behavioural fix was red-checked:** the tests fail against the reverted code, with the counts in each batch report.

**Current full run (2026-11-12, BO-50 final, `python Scripts/Tools/run_bo_lane_tests.py`):** 34 suites and 252 tests, 0 failures, 4 platform/symlink skips; `python -m compileall -q Scripts/Tools` passed. That is the 11 BO suites plus 22 earlier suites that exercise these tools and one package-style suite (the BK `evidence_pack`/`atomic_io` set, queue C, the path-normalization test, the plot and summarize tests, and others).

## 3. Review status

| Batch | Lead (Codex) | Reviewer (AG) |
|---|---|---|
| BO-01..05 | reviewed; asset_provenance finding (X-2238), now fixed | A-909 CLEAN |
| hotfix + BO-06..10 | X-2241 clean (50 tests) | A-910 CLEAN |
| BO-11..15 | X-2245 clean (62 tests) | A-911 CLEAN |
| BO-16..20 | X-2247 clean (75 tests) | A-912 CLEAN |
| BO-21..25 | X-2249 clean (83 tests) | A-913 CLEAN |
| BO-26..30 | X-2250 rework: `--re` short-prefix leak fixed in C-1494; Codex rerun 95 tests, 2 skipped | A-914 pre-hotfix; A-915 accepted the hotfix |
| BO-31..35 | X-2256 rework: BO-34 extended from 3 to all 7 mains in C-1499; Codex rerun 84 tests, 1 skipped | A-918 CLEAN |
| BO-36..40 | X-2264 rework: BO-38 pins for card_table/plugin_dependencies added in C-1503; Codex rerun 52 tests | A-920 CLEAN |
| BO-41..45 | C-1505 lead review: 48 tests, 1 skipped; py_compile passed | A-921 CLEAN |
| BO-46..50 | X-2274 closeout corrections; final runner 34 suites / 252 tests / 0 failures; compileall passed | A-922 CLEAN |

## 4. Known limits (accepted or pinned)

1. **Paths with spaces** outside the project, temp and home roots are masked only up to the first space (pinned). This is not safely fixable in free text.
2. **POSIX machine roots** are a case-sensitive allow-list (`home tmp var mnt opt root private media srv etc usr run data workspace(s) proc dev Users Volumes Applications Library`). `/Home/…` and unlisted roots such as `/data2/…` are not masked (pinned).
3. **A mid-path explicit `flush()`** writes the fragment before the flush unredacted. No KI-167 tool does this.
4. **Under `--redact`, an uncaught exception becomes `SystemExit(1)`;** in-process callers see `SystemExit`.
5. **A newline-free stream** is held in memory until a flush.
6. **The symlink cases of `display_path`** are unverified here (no symlink privilege; the test is skipped).
7. **Abbreviations of `--redact`:** after the X-2250 hotfix, the pre-scan mirrors argparse. An exact flag, or a prefix that matches only `--redact` in that parser's option table, enables redaction before parsing; an ambiguous prefix does not, and argparse rejects it without printing paths. The resolver depends on `add_redact_argument` being called after all other options, which is true for all 7 tools, and it reads argparse's private `_option_string_actions` table.
8. **Exit-code change:** bad input gives 2 (was a traceback 1, or 0) for the KI-163/165/166 tools. The BO-39 audit found **no in-repo code caller or runbook** that depends on the old codes; out-of-repo callers cannot be checked.
9. **Redaction is a sharing aid, not a security boundary.** Review output before sharing it.

## 5. Open lead decisions

- Whether KI-163..167 can move from Open, after the BO-26..30 review.
- KI-026 and KI-067: not started; separate criteria are needed (X-2238).
