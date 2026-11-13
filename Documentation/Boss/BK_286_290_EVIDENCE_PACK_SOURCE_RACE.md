# BK-286..290: evidence_pack.py source identity: race between the source hash and the copy

Assigned by X-2130 (lead Codex) to C (implementer), 2026-11-12. This is lane BK-271..320, batch 4 of 10. New files only:
- `Scripts/Tools/test_bk286_290_evidence_pack_source_race.py`
- this report

**No source change.** Integrity refusal holds; nothing gives a false success.

## BK-286: order and race boundary (source)

`evidence_pack.py` handles each planned source in four adjacent steps; the test asserts the four lines are adjacent:

| Step | Line | Action |
|---|---|---|
| 1 | `:84` | `file_identity(source)`: initial size and SHA-256 of the **source** |
| 2 | `:85` | `atomic_create_copy(source, target)`: copy2 into a temp, fsync, exclusive `os.link`; the copy is **published here** |
| 3 | `:86` | `file_identity(target)`: re-hash the **published copy** |
| 4 | `:87-88` | a mismatch → `parser.error` (exit 2) **before** the hash file (`:90`) and the manifest (`:92`) |

**Race boundary:**
- A source change between steps 1 and 2, or a torn read during step 2, makes the copy differ from the step-1 identity → refused.
- A change **after** step 2 does not matter: the published copy is a consistent snapshot equal to the step-1 identity.
- The refusal happens **after** publication, so the mismatched copy stays on disk without a manifest. This was already accepted in the BK-231 review.

## Phase and failure injection

- The runpy wrapper replaces `atomic_io.atomic_create_copy` with a hook. For the selected source only, the hook mutates or removes the file and then calls the real copy.
- Because step 1 runs immediately before step 2, the hook fires exactly between the initial hash and the copy.
- `evidence_pack.py` runs as a real subprocess on synthetic temp-only inputs: a raw log, `state.json` (pre) and `after.json` (post).

## Results

| Task | Injection | Exit | stdout / stderr | Members | Commit files |
|---|---|---|---|---|---|
| BK-287 | `raw.log` **grown** after the hash | **2** | empty / `published copy does not match source` | `raw.log` only, holding the **mutated** bytes | no `evidence_sha256.txt`, no manifest; strict verifier refuses |
| BK-287 | `raw.log` **same-size** byte flip | **2** | same | same | same: the hash catches a same-size change |
| BK-288 | `state.json` **removed** after the hash | **1** | empty / traceback ending `FileNotFoundError ... state.json` (from `shutil.copy2`) | `raw.log` only, the original bytes | none; verifier refuses |
| BK-289 | a clean rerun into each partial root, inputs restored | **2** | empty / `output root must be new or empty` | **unchanged**, byte for byte | still none |
| control | a clean run into a fresh root | 0 | `files=3 output=…` | full pack | `verify(...)` → `[]` |

No temp files are left in any case: atomic_io removes its temp when copy2 fails or after publication.

## Cleanup and disposition

- **Cleanup:** the partial roots need manual deletion before a rerun; the tool refuses until then. A removed source fails as an uncaught traceback (exit 1) rather than a friendly exit 2, but that is still fail-closed and not a success.
- **Disposition:** no false success and no misleading completion. **No fix.**

## Tests

- From the repo root: `python -m unittest discover -s Scripts/Tools -p test_bk286_290_evidence_pack_source_race.py -v` → **`Ran 5 tests ... OK`**.

| Class | Tests |
|---|---|
| `Bk286OrderFromSource` | `test_hash_copy_rehash_order` |
| `Bk287SourceMutatedAfterHash` | `test_mutation_is_refused_before_hash_file_and_manifest` (2 subtests: grow and same_size) |
| `Bk288SourceRemovedAfterHash` | `test_removed_source_traceback_and_partial_members` |
| `Bk289RerunAfterRace` | `test_rerun_refuses_and_survivors_unchanged` (2 subtests), `test_control_clean_run` |

## Limits

- The hook mutates at a function boundary. A true concurrent writer during copy2 (a torn read) is not reproduced, but it is caught by the same re-hash comparison.
- The source is not re-hashed after the copy. A change after step 2 is by design not detected, because the copy is a snapshot.
- Windows host only.
