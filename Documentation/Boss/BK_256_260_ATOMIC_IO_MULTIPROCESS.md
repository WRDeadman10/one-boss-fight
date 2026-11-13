# BK-256..260: atomic_io.py multi-process contention and kill-before-publish

Assigned by X-2110 (lead Codex) to C (implementer), 2026-11-12. This is batch 18 of 20. New files only:
- `Scripts/Tools/test_bk256_260_atomic_io_multiprocess.py`
- this report

**No source change.** No defect was demonstrated; `atomic_io.py` was not edited in this batch.

**Method:**
- Child processes use `multiprocessing` with the `spawn` start method.
- Each child installs a **test-only gate** on atomic_io's own `os.replace`, `os.link` or `Path.mkdir`, in its own process only. The gate is a `Manager().Barrier(6)`, so all 6 children reach the contended step together.
- Every failure is classified by type, WinError and the `atomic_io.py` line where it surfaced.
- Throwaway OS temp directories only. No caller, project output, lock, pack, Unreal, build or PIE.

## Results (Windows 11, NTFS, Python 3.10)

| Task | Scenario | Result |
|---|---|---|
| BK-256 | 6 processes, `atomic_write_bytes`, distinct 2 MiB payloads, gated at `os.replace` | The final file is **one full payload**: length is exact, it is single-valued, and it comes from a writer that reported `ok`. Losers fail only with `PermissionError` (WinError 5) at `os.replace(temporary, target)`, 2-4 of 6 per run. **0 temps.** |
| BK-257 | 6 processes, `atomic_create_text`, absent path, gated at `os.link` | **Exactly 1 `ok`**; 5 `FileExistsError` at `os.link`; the file holds the winner's text; 0 temps. |
| BK-258 | 6 processes create the same missing `a/b/c/` chain, gated at `Path.mkdir` | **No parent-creation or temp-creation failure in any run.** The only failures are `PermissionError` at `os.replace` (replace contention, as in BK-256). The final payload is complete; 0 temps. |
| BK-259 | The child writes, flushes and fsyncs its temp, then stalls at a test-only `os.replace` gate and is killed | The destination **keeps its old bytes**. **An orphan temp is expected and present**: 1 file, holding the complete new bytes. atomic_io has **no crash cleanup**; this documents the state and is not a cleanup guarantee. The test removes the orphan itself. |

**R1 (from BK-254) is confirmed across processes:** on Windows, concurrent `os.replace` to one target makes some writers fail with `PermissionError`, while another writer's complete file is in place. A replace caller that must win should serialize or retry; that is a caller or lead policy decision.

## BK-260: commands

- From the repo root: `python -m unittest discover -s Scripts/Tools -p test_bk256_260_atomic_io_multiprocess.py -v` → **`Ran 4 tests ... OK`**, about 1.2 s.
- Repeated 20 times: **20/20 OK**.
- Neighbor suites still OK: BK-251 (3 symlink-specific skips; the junction `O_EXCL` observation test may also skip when that host/run does not reproduce J1), BK-246, BK-241, BK-236, S171.
- `py_compile` OK; no trailing whitespace.
- **No platform skips** in this suite.

## Limits

- One host, local NTFS, only the spawn start method. POSIX, where concurrent `rename` never fails, network filesystems and fork were not tested.
- The gates replace atomic_io's module-level `os` attributes in the child; real OS scheduling without a barrier was not measured.
- BK-259 uses `Process.kill()` (TerminateProcess). Power loss and OS crash durability are not covered; see the BK-239 note that the parent directory is not fsynced.
