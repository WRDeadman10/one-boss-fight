# BK-311..315: output-alias edge cases (source_logs, junctions, samefile failure)

Assigned by X-2147 (lead Codex) to C (implementer), 2026-11-12. This is lane BK-271..320, batch 9 of 10. New files only:
- `Scripts/Tools/test_bk311_315_alias_edges.py`
- this report

**No source change.** Every case fails closed.

All runs are real CLI subprocesses through a `runpy` wrapper, with `cwd` set to the temp fixture root. No production data, lock, pack, asset, Unreal, build or PIE.

## BK-311 / BK-312: summarize_packaged_metrics, cited source_logs

- The receipt cites **3** `source_log`s, relative to the receipt directory, so the evidence set is the receipt plus 3 logs (`summarize_packaged_metrics.py:196-201`).
- **Same path:** `--report-json` = each of the 3 logs → **all refused** with exit 2 and `INCONCLUSIVE: report destination aliases an evidence input`. stdout is empty; the receipt and all logs are byte-identical; no temp.
- **Hard link:** `--report-json` = a hard link to each log → **all refused** the same way. The link stays intact (`samefile` is still true), which proves nothing was written.
- **Refusal precedes the write.** The guard sits at `:203-213` and `atomic_write_text` at `:217`.
- **Observation, non-blocking:** the message is generic and does **not** say which evidence path was aliased; a test pins the current exact text. Adding the path would be a one-line wording change; that is the lead's call, so I made no change.

## BK-313: Windows junction aliases

Three junctions are created inside the fixture: `j_ev` → `ev/run1`, `j_src` → `Source`, and `j_root` → the fixture root. A capability probe precedes them and skips only if junction creation fails; it did not skip here.

| Writer | Output through a junction | Result |
|---|---|---|
| `summarize_encounter_cost.py` | `j_root/receipt.json` | refused, exit 2 (`aliases an evidence input`); receipt intact |
| `summarize_packaged_metrics.py` | `j_root/receipt.json` | refused, exit 2; intact |
| `evidence_summary.py` | `j_ev/editor_raw.log` | refused, exit 2 (`aliases an input`); log intact |
| `token_coverage.py` | `j_ev/editor_raw.log` | refused, exit 2; intact |
| `make_source_manifest.py` | `j_src/a.cpp` | refused, exit 2; source file intact |
| `make_source_manifest.py` | `j_src/new.txt` (new) | refused, exit 2 (`output must be outside the scanned Source directory`); nothing created |

`Path.resolve()` follows junctions on this host, and `samefile` matches as well. Teardown removes only the junction entries (`os.rmdir`), never the referents.

## BK-314: samefile raising OSError

The wrapper replaces `pathlib.Path.samefile` with a function raising `OSError(5)`. Every output targets an **existing, separate** file (`OLD` bytes), because `samefile` is only reached when the output exists.

| Writer | Exit | stderr | Output | Inputs / temps / claim line |
|---|---|---|---|---|
| `summarize_packaged_metrics.py` | **2** | `INCONCLUSIVE: cannot safely compare report/evidence paths: …`, caught at `:208-210` | unchanged (`OLD`) | intact / none / none |
| `summarize_encounter_cost.py` | **1** | uncaught traceback `OSError: [Errno 5] synthetic samefile failure` from `output_aliases` | unchanged | intact / none / none |
| `evidence_summary.py` | 1 | same | unchanged | intact / none / no `logs=` |
| `token_coverage.py` | 1 | same | unchanged | intact / none / no `sample_manifest=` |
| `make_source_manifest.py` | 1 | same | unchanged | intact / none / no `files=` |

**Disposition:** all five fail closed before any write. The difference in style (an explicit INCONCLUSIVE exit 2 versus a traceback exit 1) is non-blocking. The four `output_aliases` users could catch `OSError` and refuse with exit 2 for parity, which is a lead decision.

## BK-315: tests

- From the repo root: `python -m unittest discover -s Scripts/Tools -p test_bk311_315_alias_edges.py -v` → **`Ran 5 tests ... OK`**. There are no skips on this host: junctions are available.

| Class | Tests |
|---|---|
| `Bk311And312PackagedMetricsSourceLogs` | `test_every_cited_log_same_path_is_refused` (3), `test_every_cited_log_hard_link_is_refused` (3), `test_refusal_message_does_not_name_the_aliased_input` |
| `Bk313JunctionAlias` | `test_output_through_a_junction_to_an_input_is_refused` (6) |
| `Bk314SamefileOSErrorFailsClosed` | `test_samefile_failure_never_writes` (5) |

## Limits

- Windows 11 / NTFS / Python 3.10 only.
- The junction skip applies only off Windows or when `_winapi.CreateJunction` fails.
- Symlinks were not tested; they remain unverified, as in BK-308.
- The `samefile` failure is injected; a real `stat` failure was not produced.
