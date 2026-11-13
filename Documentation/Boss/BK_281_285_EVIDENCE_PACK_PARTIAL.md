# BK-281..285: evidence_pack.py partial publication, as real CLI runs

Assigned by X-2128 (lead Codex) to C (implementer), 2026-11-12. This is lane BK-271..320, batch 3 of 10. New files only:
- `Scripts/Tools/test_bk281_285_evidence_pack_partial.py`
- this report

**No source change.** No false success or misleading completion was found.

**Method:**
- `evidence_pack.py` runs as a **subprocess** through a `runpy` wrapper. The wrapper counts `atomic_io.atomic_create_copy` or `atomic_create_text` calls and fails the Nth one with `OSError`; every other call runs the real function.
- The inputs are synthetic: a raw log, `state.json` (pre) and `after.json` (post), written into a throwaway OS temp dir.
- No project pack or output, lock, asset, Unreal, build or PIE.

The lead's scope names a `hashes.json`; the actual hash file is `evidence_sha256.txt` (`evidence_pack.py:80,90`).

## BK-281: contract (source)

`evidence_pack.py:83-93` runs in this order:
1. For each planned file: hash the source, `atomic_create_copy`, re-hash the published copy, refuse on mismatch (`:84-88`).
2. Publish `evidence_sha256.txt` (`:90`).
3. Publish **`evidence_manifest.json` last, as the commit marker** (`:91-92`).
4. Print `files=N output=…` (`:93`).

Every publish is exclusive, through `os.link`. Preflight (`:53-60`) refuses an output root that exists and is non-empty. The order is pinned by `test_copies_then_hashes_then_manifest_last`.

## Results

| Task | Injected failure | Exit | stdout | Members left | Verifier |
|---|---|---|---|---|---|
| BK-282 | 2nd `atomic_create_copy` (`pre_state.json`) | 1 (traceback with the `OSError`) | **empty** | `raw.log` only, an exact copy | refuses (no manifest) |
| BK-283 | `atomic_create_text` #1 (hash file) after all 3 copies | 1 | empty | `raw.log`, `pre_state.json`, `post_after.json` | refuses |
| BK-283 | `atomic_create_text` #2 (manifest) after the hash file | 1 | empty | the 3 copies + `evidence_sha256.txt`, **no manifest** | refuses |
| BK-284 | a clean rerun into each partial root | **2** (argparse: `output root must be new or empty`) | empty | **unchanged**, byte for byte; nothing overwritten, still no manifest | — |
| control | a clean run into a fresh root | 0, `files=3 output=<root>` | — | full pack | `verify(require_bytes, strict_membership)` → `[]` |

No temp files are left in any case. The survivors are complete, exact copies, because each copy is published whole or not at all.

## Disposition

- **No false success:** the completion line is printed only after the manifest is published, and every partial state exits non-zero.
- **No misleading completion:** without the manifest, the strict verifier refuses every partial root.
- **Rerun:** it refuses clearly and never overwrites. **Recovery is manual:** delete the partial root and rerun. The tool does not clean up partial roots automatically; that is a design property already noted in BK-226.

## BK-285: tests

- From the repo root: `python -m unittest discover -s Scripts/Tools -p test_bk281_285_evidence_pack_partial.py -v` → **`Ran 6 tests ... OK`**.

| Class | Tests |
|---|---|
| `Bk281ContractFromSource` | `test_copies_then_hashes_then_manifest_last` |
| `Bk282SecondCopyFails` | `test_second_copy_failure` |
| `Bk283HashFileFails` | `test_hash_file_failure_after_all_copies`, `test_manifest_failure_after_hash_file` |
| `Bk284RerunPartialOutput` | `test_rerun_refuses_without_overwrite_or_completion_claim` (3 subtests), `test_clean_run_into_a_fresh_root_completes` |

## Limits

- Windows host only. Faults are injected at the atomic_io function level; the lower-level `os.link`, `fsync` and copy faults are covered by BK-231 and BK-238.
- The rerun message says only "must be new or empty". It does not say the root holds a partial pack; that wording is non-blocking.
