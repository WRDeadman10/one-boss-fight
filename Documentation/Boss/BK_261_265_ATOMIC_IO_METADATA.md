# BK-261..265: atomic_io.py metadata (mode/mtime), copy2 parity, symlink source; M1 fix

Assigned by X-2112 (lead Codex) to C (implementer), 2026-11-12. This is batch 19 of 20.

New files:
- `Scripts/Tools/test_bk261_265_atomic_io_metadata.py`
- this report

**SOURCE CHANGED:** `Scripts/Tools/atomic_io.py` (`atomic_create_copy`, plus the new helper `_restore_mode_after_publish`), for **defect M1**, which was demonstrated before the change.

Synthetic OS temp directories only. No production caller, project output, lock, pack, Unreal, build or PIE.

**Host:** Windows 11, NTFS, Python 3.10. Here `os.chmod` only toggles the read-only attribute, so modes read `0o100444` or `0o100666`.

## Defect M1: read-only source (demonstrated, fixed)

**Before the fix:** `shutil.copy2` copies a read-only source's mode onto the temp. Then:
- `temporary.open("r+b")` for the fsync raises `PermissionError`, so **the copy is refused**;
- the cleanup unlink of the read-only temp fails silently, leaving **an orphan temp**.

Reproduced directly: the result was `PermissionError` plus `.out.txt.<hex>.tmp` left at mode `0o100444`.

**Fix (`atomic_create_copy`):**
- `copy2` still runs; after it, a temp that is not owner-writable is chmodded to `mode | S_IWRITE`.
- Then come the fsync, `os.link` and the temp unlink.
- After publication, `_restore_mode_after_publish` applies the copied source mode to the target. On failure it emits a `RuntimeWarning` (swallowed under warnings-as-errors) and never reports a failed copy, which is T1 policy.
- `chmod` does not change the copied mtime.
- For writable sources nothing changes: no extra chmod.

## BK-261: temp metadata at the pre-link gate

| Source | Temp mode at the `os.link` gate | Temp mtime | Source permissions visible before publication? |
|---|---|---|---|
| Writable | equal to the source mode | equal to the source mtime | **Yes**: copy2 applies them to the temp. |
| Read-only (after M1) | **writable** (`0o666` on Windows) | equal to the source mtime | **No** for the read-only bit; it is applied right after the link. Brief window: the published target is writable until the chmod. |

## BK-262: copy2 parity

For writable and read-only sources, the final copy's bytes, mode and mtime equal an independent `shutil.copy2` reference. The source's bytes, mode and mtime are unchanged. A clean copy emits no warning, and no temp is left.

## BK-263: symlink source

**Skipped on this host:** `os.symlink` raises `OSError(22, 'A required privilege is not held by the client')`. The test asserts copy2's default `follow_symlinks=True`: the destination is a regular file with the referent's bytes, and the link and referent are unchanged. **Unverified here.**

## BK-264: replace (`atomic_write_*`) metadata, current behavior (no preservation contract)

- **Absent target:** a fresh, owner-writable file with mtime now. On POSIX the mode would be `0o600`, because the temp is opened `0o600` and no umask default applies. That POSIX case is asserted only off Windows and is unverified here.
- **Existing writable target:** its metadata is **not preserved**. The mtime is the new file's, not the old one, and the mode is the temp's.
- **Existing read-only target (Windows):** `os.replace` is refused with `PermissionError`; the target bytes and mode are unchanged and no temp is left. This is a Windows-specific test.

## BK-265: tests and results

- From the repo root: `python -m unittest discover -s Scripts/Tools -p test_bk261_265_atomic_io_metadata.py -v` → **`Ran 10 tests ... OK (skipped=1)`**. Repeated 20 times: **20/20**. The skip is the symlink test (host privilege).
- **Before and after:** against the copy saved before the fix, all 5 M1-dependent cases fail (4 errors, 1 failure): the gate test, read-only copy2 parity, M1 success, mode-restore warning, and the failure-before-link orphan.
- Reruns: BK-256 4/4; BK-251 OK (3 symlink-specific skips, with a possible additional junction-observation skip when J1 does not reproduce); BK-246, BK-241, BK-236, S171; BK-231; BK-226 (1 skip); the evidence-manifest family and `test_verify_evidence_manifest` (1 skip); `evidence_pack_hashes`; Queue C (1 skip): all OK.
- `py_compile` OK; no trailing whitespace.

## Limits

- POSIX mode semantics (`0o600` and group/other bits) and symlink sources are not exercised on this host.
- The read-only bit is applied after publication, so another process can observe a writable target for a moment.
- Only the mode and mtime were audited; ACLs, alternate data streams and atime were not.

## Lead hotfix for AG-R115 review note

Added `test_mode_restore_warning_cannot_turn_published_copy_into_failure`, which injects the post-publication chmod error under `warnings.simplefilter("error", RuntimeWarning)`. This verifies T1's warning-as-error handling directly. Lead focused rerun: 11 tests, 1 symlink-privilege skip; 20/20 repeats; py_compile passes.
