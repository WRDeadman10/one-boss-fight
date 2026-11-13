# BK-301..305: output-path aliasing against inputs (five atomic_write_text callers)

Assigned by X-2138 (lead Codex) to C (implementer), 2026-11-12. This is lane BK-271..320, batch 7 of 10.

New files:
- `Scripts/Tools/test_bk301_305_output_input_aliasing.py`
- this report

**SOURCE CHANGED:** `summarize_encounter_cost.py`, `evidence_summary.py`, `token_coverage.py`, `make_source_manifest.py`, each in `Scripts/Tools/`. `summarize_packaged_metrics.py` already had a guard and was not changed.

All runs are real CLI subprocesses on synthetic temp fixtures. No production file, lock, pack, asset, Unreal, build or PIE.

## BK-301: guard inventory (before the change)

| Caller | Inputs | Output-vs-input guard before |
|---|---|---|
| `summarize_packaged_metrics.py` | receipt + cited `source_log`s | **Yes** (`:196-213`): resolved path or `samefile` → `INCONCLUSIVE: report destination aliases an evidence input`, exit 2 |
| `summarize_encounter_cost.py` | the receipt | none |
| `evidence_summary.py` | every `editor_raw.log` + the validator script | none |
| `token_coverage.py` | the logs + the validator script | none |
| `make_source_manifest.py` | every file under `<root>/Source` | none |

## BK-302..304: observed before the fix (output = an input, same path)

| Caller | Exit | Input |
|---|---|---|
| `summarize_encounter_cost.py` (report = receipt) | 2 (INCONCLUSIVE report) | **destroyed**: the receipt is replaced by the report JSON |
| `summarize_packaged_metrics.py` | 2 | intact: refused by its guard |
| `evidence_summary.py` (output = a log) | **0** | **destroyed**: the evidence log is replaced by the CSV |
| `token_coverage.py` (samples-output = a log) | **0** | **destroyed**: the log is replaced by the manifest JSON |
| `make_source_manifest.py` (output = `Source/a.cpp`) | **0** | **destroyed**: a project source file is replaced by the manifest |

**Hard-link alias before the fix:** the input **bytes survive**, because `os.replace` swaps the alias's directory entry rather than writing through it. The link relationship is silently broken, and three of the callers still report success.

## BK-305: disposition and fix

**Same-path aliasing destroys an input with exit 0 or INCONCLUSIVE output, and that is contrary to every one of these CLIs' contracts.**
- Each is a reader of evidence or source that writes a separate derived report or manifest.
- None documents an in-place mode.
- The sibling `summarize_packaged_metrics` explicitly forbids it.

**Narrow fix:** a local `output_aliases(output, inputs)` helper refuses when `resolve()` paths are equal or `samefile` is true. The `samefile` part also covers hard links, matching the packaged-metrics guard. The check runs **before** any write:

| Caller | Guard input set | Refusal |
|---|---|---|
| `summarize_encounter_cost.py` | `[receipt]`, checked before the read, so the read-failure path is covered too | stderr `INCONCLUSIVE: report destination aliases an evidence input`, exit 2 (same wording as its sibling) |
| `evidence_summary.py` | the logs + the validator (`VALIDATOR_REL`, factored out of `load_validator`) | `parser.error`: `output aliases an input; refusing to overwrite it: <path>`, exit 2 |
| `token_coverage.py` | the logs + the validator | `--samples-output aliases an input; refusing to overwrite it`, exit 2 |
| `make_source_manifest.py` | the scanned `Source` files (the list is now computed once) | `output aliases a scanned Source file; refusing to overwrite it`, exit 2; any output inside `Source/` is also refused so it cannot become a new input on the next run |

Non-alias outputs are unchanged: all 5 callers still write a separate output with their normal exit codes.

## Tests

- From the repo root: `python -m unittest discover -s Scripts/Tools -p test_bk301_305_output_input_aliasing.py -v` → **`Ran 5 tests ... OK`**.

| Class | Test |
|---|---|
| `Bk302To304SamePathAlias` | `test_output_equal_to_an_input_is_refused_and_input_survives` (5 subtests), `test_validator_alias_is_refused_for_scanning_callers` (2) |
| `Bk305HardLinkAlias` | `test_hard_link_to_an_input_is_refused` (5) |
| `Bk305NonAliasStillWorks` | `test_separate_outputs_are_written`, `test_source_manifest_output_inside_source_is_refused_before_write` |

**Lead hotfix:** the initial output/input alias fix still allowed a brand-new manifest path inside the scanned `Source/` subtree. That file would enter the next scan and make later outputs self-referential. `make_source_manifest.py` now refuses all output paths under resolved `Source/`; the new temp-only regression confirms exit 2, no output created, and the source bytes unchanged.

**Before and after:** against copies of the four callers saved before the change, 11 subtests fail. The pre-fix `summarize_packaged_metrics` hard-link subtest fails only as a cascade, because the preceding encounter-cost subtest had replaced the shared alias. Run alone, its existing guard refuses correctly, as verified.

**Reruns:** `test_summarize_encounter_cost`, `test_audit_source_error_token_coverage`, `test_bi_a19_cli_tooling_contract`, BK-236, BK-246, BK-271, BK-276 and BK-291 all pass. `py_compile` OK.

## Limits

- Symlink aliases were not exercised, because the host lacks the symlink privilege; `resolve()` would map them to the referent.
- Directory-level aliasing, where the output is inside an input directory but is not itself an input, is allowed. For example, `evidence_summary --output` inside the evidence tree under a non-log name stays allowed.
- **Source-manifest exception:** output anywhere inside its scanned `Source/` subtree is refused because a newly created manifest there would enter the scan on later runs and make the result self-referential.
- Windows host only.
