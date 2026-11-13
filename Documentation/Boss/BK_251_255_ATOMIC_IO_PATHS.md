# BK-251..255: atomic_io.py path entries (links), parent/target-type failures, concurrent replace

Assigned by X-2105 (lead Codex) to C (implementer), 2026-11-12. This is batch 17 of 20. Test/report are new; J1 prompted a narrowly scoped source hotfix:
- `Scripts/Tools/test_bk251_255_atomic_io_paths.py`
- this report

The J1 hotfix changed only `Scripts/Tools/atomic_io.py`; tests use throwaway OS temp directories. No production caller, project output, lock, pack, Unreal, build or PIE was involved.

## Host

Windows 11, NTFS, Python 3.10. **True symlinks are unavailable**: `os.symlink` raises `OSError(22, 'A required privilege is not held by the client')` (WinError 1314). The three symlink tests skip with that exact reason. Directory junctions need no privilege and were used for the linked-parent case.

## BK-251: linked parent

- `_temporary_path` places the temp as a **lexical sibling of the target entry** (`target.parent`), not of the resolved file. Tested.
- Symlinked parent: written through the link, the bytes would land in the referent directory. **Skipped** on this host (no symlinks).
- **Junction parent — hazard J1 (new, confirmed on this host):**
  - On a path through an NTFS junction, `os.open(O_CREAT|O_EXCL)` of a new name raises `FileExistsError`, while a plain `O_CREAT` succeeds. Reproduced with `_winapi.CreateJunction` and with PowerShell `New-Item -ItemType Junction`, on both short (8.3) and long temp paths.
  - `tempfile.mkstemp` treats that as a name collision and retries up to `TMP_MAX` (2**31-1 on Windows) times. So **every `atomic_write_*` / `atomic_create_*` under a junction parent effectively hangs**. The first suite run hung until it was stopped; a faulthandler trace places it in `tempfile._mkstemp_inner` called from `atomic_io.py:23`.
  - **Pre-hotfix:** the gap was pinned as `expectedFailure` with `TMP_MAX` patched to 3, so it failed fast with `FileExistsError: No usable temporary file name found`.
  - **Lead decision and resolution:** use a bounded exclusive-create loop, switching to `os.path.realpath(parent)` only when `FileExistsError` names a path that does not exist. Preserve the lexical destination path for publication.
  - Not checked: whether any project output folder actually sits under a junction.

## BK-252: symlink destination

Both tests are **skipped on this host**. The intended contract they assert, for hosts with symlinks:
- The replace API replaces the **link entry**, which becomes a regular file, and leaves the referent unchanged.
- The create API raises `FileExistsError` and changes neither the link nor the referent.

## BK-253: parent and target-type failures

All checked by a before/after snapshot of the whole temp dir: no publication, no collateral change, no temp.

| Case | API | Result |
|---|---|---|
| A parent component is an existing **file** | write, create, copy | `FileExistsError` or `NotADirectoryError` from `mkdir`; the file is unchanged. |
| `mkdir` fails (injected `PermissionError`) | write | The **same exception object** propagates (`assertIs`); nothing is created. |
| The target is an existing **directory** with content | write, create | `OSError`; the directory and its contents are unchanged and the temp is removed. |

## BK-254: concurrent replace

- 6 threads call `atomic_write_bytes` with distinct 4 MiB payloads. A barrier placed just before `os.replace` makes every replace contend.
- **Final file:** always exactly one complete payload, never mixed or truncated. No temp residue, including the losers' temps.
- **Observation R1:** on Windows, most contending writers **fail** with `PermissionError` (WinError 5): 3-4 of 6 per run across 5 inspected runs. A replace caller doing a concurrent write may therefore get a failure even though another writer's complete file is in place. The test accepts `ok` or `PermissionError` per writer and asserts at least one `ok`.

## BK-255: pre-hotfix tests and results

- From the repo root: `python -m unittest discover -s Scripts/Tools -p test_bk251_255_atomic_io_paths.py -v` → **`Ran 10 tests ... OK (skipped=3, expected failures=1)`**.
- Repeated 20 times: 20/20 with the same result.
- `py_compile` OK; no trailing whitespace.
- Neighbor suites still OK: BK-241, BK-236, BK-246, S171.

## Limits

- The symlink tests (3) are unverified on this host.
- The concurrency tests use threads in one process. Multiple processes and network filesystems were not tested.
- J1 is observed on this host; the underlying OS or driver cause was not investigated.

## J1 hotfix (X-2109; C, 2026-11-12)

**SOURCE CHANGED:** `Scripts/Tools/atomic_io.py` `_temporary_path`. The backup taken before the change is in my scratchpad (not tracked).

- `tempfile.mkstemp` is replaced by a **bounded loop** (`_TEMP_ATTEMPTS = 100`) using `os.open(O_RDWR|O_CREAT|O_EXCL|O_NOINHERIT|O_BINARY, 0o600)`. The name stays a hidden sibling `.<name>.<12 hex>.tmp`; before, mkstemp used 8 random characters.
- **Junction signature:** a `FileExistsError` for a name that does **not** exist switches temp creation to `os.path.realpath(parent)`, once. That is the same filesystem. `os.link` and `os.replace` still publish to the **unchanged lexical target entry**; both were probed to work through a junction.
- A genuine collision repeated for every attempt raises `FileExistsError("could not create a temporary file ... after 100 attempts")`. It no longer hangs.
- **Final lead-hotfixed behavior:** a `PermissionError` from temporary creation is immediately re-raised unchanged; it is not treated as a name collision.
- Ordinary directories keep the lexical sibling. The public API, the replace/create semantics, and the T1-T4 contract are unchanged.

**Tests:** the J1 `expectedFailure` is replaced.

| Test | Covers |
|---|---|
| Junction regression | write, create and copy through a real junction finish within a 30 s watchdog; bytes land in the referent; create still refuses an existing name; no temps on either path. |
| `J1BoundedTempCreation` (4) | A persistent real collision gives up after exactly 100 attempts. A phantom collision retries in `realpath(parent)`. Name/placement and original `PermissionError` preservation. |

**Results:**
- Pre-lead-hotfix suite: **`Ran 13 tests ... OK (skipped=3)`**; Claude reports 20/20 repeats.
- **Before and after:** on the pre-fix copy, the junction test fails its no-hang watchdog after 30 s, the phantom and naming tests fail, and the bounded test hangs (killed by timeout).
- Reruns: BK-241, BK-236, BK-246, S171, BK-231, BK-226 (1 skip), evidence-manifest family 25 (1 skip), `test_verify_evidence_manifest` OK (1 skip), `evidence_pack_hashes`, path normalization, Queue C (1 skip): all OK.
- `py_compile` OK; no trailing whitespace.

**Limit:** the junction fallback was tested on this host only. A non-junction filesystem that returns phantom EEXIST would take the same realpath path.

**Final lead review:** `PermissionError` from temporary-file creation was being retried and eventually translated to `FileExistsError`. The lead hotfix now propagates the original `PermissionError`; an added regression asserts exception identity.

**Lead verification after that hotfix:** `Ran 14 tests ... OK (3 symlink-specific skips)`; repeated 20 times (20/20); `py_compile` passes for source and test. The separate junction `O_EXCL` observation test may also skip on a host/run where the J1 signature does not reproduce; AG observed that additional skip. The J1 write/create/copy regression remains active on Windows.
