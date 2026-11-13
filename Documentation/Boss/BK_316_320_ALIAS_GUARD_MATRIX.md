# BK-316..320: consolidated runs, five-writer guard matrix, fixture containment, limits

Assigned by X-2151 (lead Codex) to C (implementer), 2026-11-12. This is lane BK-271..320, batch 10 of 10.

New files only:
- `Scripts/Tools/test_bk316_320_lane_static_checks.py`
- this report
- `Documentation/Boss/BK_271_320_LANE_CLOSEOUT.md`

**No source edits.** No Unreal, build, PIE, commit or push.

## BK-316: consolidated focused runs (this session, from the repo root)

| Suite | Result |
|---|---|
| `test_bk271_275_caller_failure_semantics.py` | 10 OK |
| `test_bk276_280_replace_caller_failures.py` | 4 OK |
| `test_bk281_285_evidence_pack_partial.py` | 6 OK |
| `test_bk286_290_evidence_pack_source_race.py` | 5 OK |
| `test_bk291_295_replace_caller_early_faults.py` | 5 OK |
| `test_bk296_300_post_preflight_collisions.py` | 3 OK |
| `test_bk301_305_output_input_aliasing.py` | 5 OK (includes the lead's Source-subtree regression) |
| `test_bk306_310_alias_normalization.py` | 4 OK, **1 skip** (symlink privilege) |
| `test_bk311_315_alias_edges.py` | 5 OK (junctions available, so no skip) |
| **Total, BK-271..315** | **47 tests, 46 passed, 1 skipped, 0 failures** |
| `test_bk316_320_lane_static_checks.py` (new) | 5 OK |

The command for each suite is `python -m unittest discover -s Scripts/Tools -p <file> -v`.

**Caveat (X-2151):** `git diff --check` repo-wide reports whitespace in unrelated, pre-existing files. Only the lane's own new and changed files were checked: `py_compile` passes and they have no trailing whitespace. **No global clean claim.**

## BK-317: five-writer guard matrix

| Writer (`Scripts/Tools/`) | Input set guarded | Guard location | Writes | Guard before every write | Refusal |
|---|---|---|---|---|---|
| `summarize_encounter_cost.py` | receipt | `:125` (`output_aliases`), before the receipt read | `:135` (read-failure path), `:140` | yes | `INCONCLUSIVE: report destination aliases an evidence input`, exit 2 |
| `summarize_packaged_metrics.py` | receipt + every cited `source_log` | `:204-213` (resolved set + `samefile`; an `OSError` gives `cannot safely compare`) | `:217` | yes | the same INCONCLUSIVE message, exit 2 |
| `evidence_summary.py` | every `editor_raw.log` + the validator | `:92` | `:101` | yes | `parser.error` `output aliases an input …`, exit 2 |
| `token_coverage.py` | the logs + the validator | `:70` | `:84` | yes | `parser.error` `--samples-output aliases an input …`, exit 2 |
| `make_source_manifest.py` | the scanned `Source` files, **plus** any output under resolved `Source/` | `:32` (alias), `:35` (containment, the lead's hotfix) | `:41` | yes | `parser.error`, exit 2 |

The ordering is pinned by `Bk317GuardBeforeWrite.test_guard_precedes_every_write` and `test_manifest_source_containment_precedes_write`.

**Verified alias forms:**
- same path in 6 spellings (BK-307);
- hard link (BK-305, BK-311);
- junction (BK-313);
- each cited `source_log` (BK-311 and BK-312);
- `samefile` `OSError`, which fails closed (BK-314).

## BK-318: fixture containment (static)

`Bk318FixtureContainment` covers all **9** lane test files, BK-271 through BK-315:
- Each builds its fixtures in `tempfile.TemporaryDirectory()`.
- **No string literal** is an absolute path (`X:\`, `/c/`, `/Users/`, UNC), names `UnrealProject` or `OneBossFight`, or starts with `Saved/`, `Content/` or `Documentation/`.
- Script locations come only from `HERE / "<script>.py"`. Every output, input and `cwd` is under the temporary root.

## BK-319: host limits and open edges (reconciled)

| Item | Status | Where |
|---|---|---|
| Platform | Windows 11 / NTFS / Python 3.10 only; **no POSIX run** | all batches |
| Symlink privilege | unavailable (`OSError 22`, WinError 1314) → BK-308 is **skipped**; symlink aliases are **unverified** | BK-306, BK-311 |
| Junction capability | available; BK-313 ran with a capability probe that skips only if `CreateJunction` fails | BK-311 |
| `samefile` failure | **injected only**, through a wrapper; no real `stat` failure was produced | BK-311 |
| Exit style on a `samefile` error | packaged_metrics exits 2 (INCONCLUSIVE); the other four exit 1 (traceback). Both fail closed; parity is a lead option | BK-311 |
| Alias message | generic; it does not name the aliased input (pinned); wording is a lead option | BK-311 |
| Directory-level aliasing | an output inside an input *directory* under a non-input name is allowed, except under `Source/` for the manifest | BK-301, BK-306 |
| `token_coverage` exit 1 | overloaded (unknown tokens vs an uncaught write failure); stderr distinguishes them | BK-276, BK-291 |
| Partial roots | scaffold and evidence_pack leave per-file survivors; a rerun refuses; cleanup is manual | BK-271, BK-281..300 |
| Junction / `\\?\` / UNC output spellings beyond BK-313 | not exercised | BK-306 |

## BK-320

The lane closeout is in `Documentation/Boss/BK_271_320_LANE_CLOSEOUT.md`.
