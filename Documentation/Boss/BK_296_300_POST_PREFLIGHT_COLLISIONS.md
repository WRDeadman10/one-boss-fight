# BK-296..300: destination collisions raced in after preflight (O1 callers, scaffold, evidence_pack)

Assigned by X-2135 (lead Codex) to C (implementer), 2026-11-12. This is lane BK-271..320, batch 6 of 10. New files only:
- `Scripts/Tools/test_bk296_300_post_preflight_collisions.py`
- this report

**No source change.** Every raced collision is refused without overwriting, and none produces a false success.

## Injection point

- A `runpy` wrapper replaces `atomic_io.atomic_create_text` or `atomic_create_copy` with a hook.
- On the **Nth call** the hook writes `RACER` bytes at that call's destination, then calls the **real** exclusive function, which publishes through `os.link`.
- The effect is that another writer wins the path after the caller's own preflight and before its publication.
- Every caller runs as a real subprocess in a throwaway temp dir.

## Results

| Task | Caller, raced call | Exit | Output | On disk afterwards | Rerun |
|---|---|---|---|---|---|
| BK-296 | `inventory_editor_asset_writers.py`, create #1 | **2** | `REFUSED existing inventory output: <path>` (correct: the path now exists) | racer bytes intact; no temp | — |
| BK-296 | `audit_editor_save_safety.py`, create #1 | **2** | `REFUSED existing audit output: <path>` | racer bytes intact; no temp | — |
| BK-297 | `new_rule_scaffold.py`, create #1 (header) | 1 (`FileExistsError` traceback) | no paths, no "Scaffold created" | the racer's file only | exit 2, lists 1 target; tree byte-identical |
| BK-297 | create #2 (test file) | 1 | 1 published path | 1 own file + the racer's | exit 2, lists 2; byte-identical |
| BK-297 | create #3 (reference doc) | 1 | 2 published paths | 2 own files + the racer's | exit 2, lists 3; byte-identical |
| BK-298 | `evidence_pack.py`, copy #2 (`pre_state.json`) | 1 (`FileExistsError`) | empty | `raw.log` + the racer's `pre_state.json`; no manifest; strict verifier refuses | exit 2, `new or empty`; byte-identical |
| BK-298 | `evidence_pack.py`, create-text #1 (`evidence_sha256.txt`) | 1 | empty | the 3 copies + the racer's hash file; no manifest; verifier refuses | exit 2; byte-identical |

BK-299 is covered by the rerun column: every partial root is refused on rerun and stays byte-identical, racer files included.

## Dispositions

| Caller | Disposition |
|---|---|
| **O1 callers** | Correct. After the BK-271 fix, "existing" is printed exactly when the path exists, which it does here. |
| **Scaffold** | Same per-file contract as BK-273 (O2). A raced target fails the run (exit 1) with the earlier files left; the rerun preflight refuses. **No fix.** |
| **evidence_pack** | The manifest-last rule holds. A racer can plant a non-evidence file in the root, but without a manifest the strict verifier refuses the root. **No fix.** |

## Tests

- From the repo root: `python -m unittest discover -s Scripts/Tools -p test_bk296_300_post_preflight_collisions.py -v` → **`Ran 3 tests ... OK`** (8 subtests).

| Class | Test |
|---|---|
| `Bk296O1Callers` | `test_raced_destination_is_refused_as_existing_and_racer_bytes_survive` |
| `Bk297Scaffold` | `test_collision_on_first_and_later_target` (nth 1, 2, 3, with reruns) |
| `Bk298EvidencePack` | `test_collisions_after_root_preflight` (copy #2 and hash file, with reruns) |

## Limits

- The race is simulated at a function boundary; a true concurrent process race was covered for atomic_io itself in BK-257.
- Windows host only.
