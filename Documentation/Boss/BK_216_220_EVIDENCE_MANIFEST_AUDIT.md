# BK-216..220: adversarial audit of verify_evidence_manifest.py

Assigned by X-2066 (lead Codex) to C (implementer), 2026-11-12. This is batch 10 of 20. New files only:
- `Scripts/Tools/test_bk216_220_evidence_manifest_audit.py`
- this report

**`Scripts/Tools/verify_evidence_manifest.py` was not modified.** It is byte-identical to the copy saved before the audit.

Its working tree already differs from HEAD by one line: `UnicodeError` added to the manifest-read `except` at `:32`. That change predates this batch, is not mine, and is left as found.

Synthetic packs were written to throwaway OS temp directories only, as the existing verifier suite does. No real evidence file was read or changed, and there was no Unreal, build or PIE.

## Held (6 tests)

| Task | What holds |
|---|---|
| BK-216 | Malformed JSON, a non-object top level, a wrong schema value, a non-list `files` and a missing `files` are each invalid. |
| BK-217 | `../`, `sub/../../` and absolute paths are refused as "unsafe path". Strict mode refuses symlink members (existing code, `:81-83`). |
| BK-218 | A hash mismatch, a size mismatch and a missing file are each reported. A `source_log` reference must be listed, inside the pack root, lowercase 64-hex, and must match its hash. |
| BK-219 | An identical duplicate entry name is refused. Strict mode refuses unlisted members. Non-dict entries, and entries without a string `file` and `sha256`, are refused. |

## Confirmed gaps (8; pinned as `expectedFailure`, each confirmed to fail on its own assertion)

| Id | Task | Gap | Fix rule |
|---|---|---|---|
| E1 | BK-216, `:31` | **Duplicate JSON keys:** the last one wins, so `{"files":[<bad>],"files":[]}` verifies an empty list and **PASSES**. | An `object_pairs_hook` that refuses duplicate keys. |
| E2 | BK-216, `:31` | `NaN` and `Infinity` are accepted anywhere. | A `parse_constant` that raises, as in `validate_owner_approval_envelope.loads_strict`. |
| E3 | BK-216, `:34` | `schema` of `True` or `1.0` passes as `1`. | Require `type(schema) is int and schema == 1`. |
| E4 | BK-219 | **Empty `files` passes**: it prints PASS while verifying nothing. | Require at least one file, unless the caller explicitly allows an empty pack. |
| E5 | BK-219, `:50` | **The same file can be listed twice under different spellings** (`a.txt`, `./a.txt`, and `A.TXT` on Windows). | Deduplicate on the normalized resolved path (`os.path.normcase`). |
| E6 | BK-218, `:63` | The entry hash is compared case-insensitively and never shape-checked, unlike `source_log_sha256` at `:98`. | Entry `sha256` must match `[0-9a-f]{64}` exactly. |
| E7 | BK-219 | Unknown top-level and entry keys are ignored: a typo (`sha_256`) or an unrelated claim (`"verdict": "PASS"`) passes silently. | Exact key sets. Top level: `schema`, `files`. Entry: `file`, `sha256`, optional `bytes` and the optional string `label` used by `evidence_pack.py`. |
| E8 | BK-218, `:61` | Without `--require-bytes`, `"bytes": true` equals 1 and passes for a 1-byte file. | When present, `bytes` must satisfy `type(x) is int` and be ≥ 0. |

**Highest impact: E1 and E4.** Each lets a manifest PASS while verifying nothing. E5 lets one file stand in for two entries.

## BK-220: results and parity

- **This audit,** run from `Scripts/Tools`: `python -I -m unittest discover -s . -p "test_bk216_220_evidence_manifest_audit.py" -v` → **`Ran 14 tests ... OK (expected failures=8)`**.
- **Existing suite:** `python -m unittest discover -s Scripts/Tools -p "test_verify_evidence_manifest.py"` (from the repository root) → OK (1 skip). As A-854 noted, that suite imports `Scripts.Tools…`, so it needs `python -m` rather than `-I`.
- **Callers:** `Scripts/Tools/proof_report.py` imports `verify`. Tightening E1–E8 could turn previously passing packs into failures, so the lead should check real packs before enabling the fixes.
- **Checks:** `py_compile` OK; no trailing whitespace.

## Limits

- Synthetic packs only. No real evidence pack was found under `Docs/` (no `evidence_manifest*.json`), so the impact on real packs is not measured.
- The E5 case-folding variant is Windows-specific. The test uses `./a.txt`, which reproduces on every platform.

## BK-221..225: E1-E8 implemented (X-2068, 2026-11-12)

**SOURCE CHANGED:** `Scripts/Tools/verify_evidence_manifest.py`. The `verify()` signature and its list-of-issues return value are unchanged, and the existing message phrases ("cannot read manifest", "invalid schema", "unsafe path", "duplicate file entry", "hash mismatch") are kept.

| Gap | Fix |
|---|---|
| E1, E2 | `load_manifest_json()` refuses duplicate keys (`object_pairs_hook`) and `NaN`/`Infinity` (`parse_constant`); either is reported as "cannot read manifest". |
| E3 | `schema` must satisfy `type(schema) is int` and equal 1. |
| E4 | An empty `files` array is refused ("files array is empty"). |
| E5 | Duplicate identity uses `os.path.normcase(str(resolved path))`, so `a.txt`, `./a.txt` and, on Windows, `A.TXT` are one file. |
| E6 | The entry `sha256` must match `[0-9a-f]{64}` exactly and is compared exactly. |
| E7 | Exact key sets. Top level: `files`, `schema`. Entry: `file`, `sha256`, optional `bytes` and optional string `label` (emitted by `evidence_pack.py`). |
| E8 | When `bytes` is present it must satisfy `type(x) is int` and be ≥ 0, whether or not `--require-bytes` is set. |

**Tests:**
- **Audit suite:** the 8 `expectedFailure` markers in `test_bk216_220_evidence_manifest_audit.py` are removed, and it now reports **`Ran 14 tests ... OK`**. Run against the copy saved before the fix, **all 8 gap tests fail**, which confirms each one targets real pre-fix behavior.
- **New compatibility suite:** `test_bk221_225_evidence_manifest_hotfix.py` → **5/5**. It checks that the signature and defaults are unchanged; that a valid pack returns `[]` and an invalid one returns string issues containing the existing phrases; and that `proof_report.evidence_stale_reasons()` returns `[]` for a fresh valid pack and reports an empty-`files` manifest.
- **Consumer suites,** run with `python -m unittest discover -s Scripts/Tools`:

  | Suite | Result |
  |---|---|
  | `test_verify_evidence_manifest.py` | 5 (1 symlink skip) |
  | `test_path_normalization_s170.py` | 1/1 |
  | `test_queue_c_s36_s40.py` | 7/7 |
  | `test_queue_c_tools.py` | 24 (1 skip) |
  | `test_bi_a19_cli_tooling_contract.py` | 1/1 |
- **Intentional consumer change:** `test_queue_c_tools.py::test_evidence_manifest_documents_dot_alias_as_separate_entries` used to assert that a `./run.log` alias was accepted as a second entry. That is exactly E5, so the test now asserts the alias is refused, with a comment citing X-2068.

**Limits:**
- No real evidence pack exists under `Docs/`. A scan for JSON with a non-empty `files` list of `file`/`sha256` entries found none, so the compatibility of stored packs could not be measured.
- `normcase` is case-insensitive only on Windows. On other platforms `A.TXT` and `a.txt` are different files, which is correct for those filesystems.

### BK-221..225 correction: optional `label` (X-2070 / A-857, patched by the lead in X-2074)

- **What went wrong:** the first E7 key set (`file`, `sha256`, `bytes`) rejected `label`, which `Scripts/Tools/evidence_pack.py:64` writes on every entry. That made every pack it generates fail `verify()` and the `proof_report` freshness check. I had checked the consumers of `verify()` but not the producer of the manifests.
- **The lead's patch** (kept as is):
  - `ENTRY_ALLOWED_KEYS = {file, sha256, bytes, label}`.
  - `label`, when present, must be text ("label must be text").
  - The unknown-key error now lists `bytes, file, label, sha256`.
- **Producer check:** `evidence_pack.py` is the only script in the repository that writes `evidence_manifest.json`; `grep` over `Scripts/**/*.py` and `*.ps1` found no other writer.
- **Regressions:**
  - `test_bk221_225_evidence_manifest_hotfix.py::test_evidence_pack_output_is_accepted_and_malformed_label_refused` runs `evidence_pack.main()` on a temp fixture. The output verifies cleanly, and a list-valued `label` is refused.
  - Reruns (`python -m unittest`):

    | Suite | Result |
    |---|---|
    | audit | 14/14 |
    | compatibility | 6/6 |
    | existing verifier | 5 (1 skip) |
    | path normalization | 1/1 |
    | Queue C S36-S40 | 7/7 |
    | Queue C tools | 24 (1 skip) |
    | BI-A19 | 1/1 |
    | `test_evidence_pack_hashes.py` | OK |
