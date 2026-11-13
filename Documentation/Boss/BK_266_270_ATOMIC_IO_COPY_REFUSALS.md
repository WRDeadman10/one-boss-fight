# BK-266..270: atomic_create_copy refusal paths and read-only source failure paths

Assigned by X-2116 (lead Codex) to C (implementer), 2026-11-12. This is the final batch, 20 of 20. New files only:
- `Scripts/Tools/test_bk266_270_atomic_io_copy_refusals.py`
- this report
- the lane closeout, `Documentation/Boss/BK_171_270_LANE_CLOSEOUT.md`

**No source change.** No defect was demonstrated under a real condition. O5 below needs an injected fault, and it is left to the lead.

Synthetic OS temp directories only. No production caller, project output, lock, pack, Unreal, build or PIE.

**Host:** Windows 11, NTFS, Python 3.10. Hard links work here, so BK-268 ran with **no skip**.

## Results

| Task | Case | Result |
|---|---|---|
| BK-266 | Source and destination are the same path; writable and read-only sources | Exactly `FileExistsError`, from `os.link` because the destination exists. The source bytes, mode and mtime are unchanged; no temp. |
| BK-267 | A pre-existing **different** destination; writable and read-only sources | `FileExistsError`. Bytes, mode and mtime are unchanged for both files; no temp. |
| BK-268 | The destination is a **hard link** to the source (`samefile`, `st_nlink == 2`); writable and read-only, which is a shared inode | `FileExistsError`. Both entries' bytes, mode and mtime are unchanged, the link relationship is intact (still `samefile`, `nlink` 2), and no temp. |
| BK-269a | Read-only source; injected `fsync` or `os.link` fault after the M1 temp write-enable | The **original exception object** propagates (`assertIs`). The source is unchanged, nothing is published, and the writable temp is removed. |
| BK-269b | Read-only source; existing destination, writable and read-only | `FileExistsError`. Both files' metadata is unchanged, **only the temp** is ever chmodded (every `chmod` call is recorded), and no temp is left. |
| BK-269c | Read-only source; the M1 write-enable `chmod` itself fails (injected) | The original exception propagates and the source is unchanged. **Observation O5:** the temp is still read-only, so the best-effort cleanup unlink cannot remove it on Windows, leaving **1 orphan read-only temp**. On POSIX the test asserts no orphan; that branch is unverified here. |

**O5 (non-blocking; lead decision):** it happens only when `chmod` on our own freshly created temp fails, a fault that was only injected here. A possible hardening is for `_discard_after_failure` to try `os.chmod(temp, S_IWRITE)` before its unlink. Nothing was changed, per X-2116's no-runtime-change rule.

## BK-270: commands and results

- From the repo root: `python -m unittest discover -s Scripts/Tools -p test_bk266_270_atomic_io_copy_refusals.py -v` → **`Ran 6 tests ... OK`**. Repeated 20 times: **20/20**.
- `py_compile` OK; no trailing whitespace.
- **Full regression sweep (this session, after the batch):**

| Suite | Result |
|---|---|
| BK-261 | 11 (1 skip) |
| BK-256 | 4 |
| BK-251 | 14 tests; 3 symlink-specific skips, plus a possible junction-observation skip if the host does not reproduce J1 |
| BK-246 | 7 |
| BK-241 | 9 |
| BK-236 | 15 |
| S171 | 4 |
| BK-231 | 9 |
| BK-226 | 13 (1 skip) |
| BK-221 | 6 |
| BK-216 | 14 |
| `evidence_pack_hashes` | 2 |
| Queue C | 31 (1 skip) |
| `test_verify_evidence_manifest` | OK (1 skip) |

## Limits

- POSIX was not run. O5's POSIX branch and BK-268 on filesystems without hard links are unverified.
- Faults are injected by patching. No real `chmod`, `fsync` or `link` failure was produced.
