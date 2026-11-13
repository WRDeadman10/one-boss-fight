# BK-236..240: atomic_io.py and its direct callers: failure paths and published-target states

Assigned by X-2086 (lead Codex) to C (implementer), 2026-11-12; precheck items from X-2090 and X-2091. This is batch 14 of 20. New files only:
- `Scripts/Tools/test_bk236_240_atomic_io_audit.py`
- this report

**`Scripts/Tools/atomic_io.py` was not modified** (no working-tree diff). No production caller was run; callers are classified by import text only.

Faults were injected by patching `os` and `pathlib` calls, in throwaway OS temp directories. No real output, lock, evidence pack, Unreal, build or PIE was involved.

## BK-236: direct callers (static, by AST)

| API semantics | Callers |
|---|---|
| **Replace** (`atomic_write_text` → `os.replace`) | `evidence_summary.py`, `make_source_manifest.py`, `summarize_encounter_cost.py`, `summarize_packaged_metrics.py`, `token_coverage.py` |
| **Create / no-overwrite** (`atomic_create_text`, `atomic_create_copy` → `os.link`) | `audit_editor_save_safety.py`, `evidence_pack.py`, `inventory_editor_asset_writers.py`, `new_rule_scaffold.py` |

No caller mixes the two. This matches the lead's X-2090 precheck.

## BK-237: temp sibling, paths, filesystem

- `_temporary_path` (`:10-13`) creates a hidden sibling `.<name>.<random>.tmp` **in the target's own directory**. Same-directory placement means the same filesystem, which `os.link` and `os.replace` need for atomicity.
- It also runs `mkdir(parents=True, exist_ok=True)` on the parent, so missing parent directories are created as a side effect, even if the write later fails.
- A crashed run can leave a `.tmp` sibling behind. A caller that globs its output folder (for example strict evidence membership) would see it.

## BK-238: failure cleanup and published-target states

| Injected fault | API | Target afterwards | Temp afterwards | Exception |
|---|---|---|---|---|
| `fsync` fails | write | **old content kept** | removed | raised |
| `os.replace` fails | write | absent (was absent) | removed | raised |
| `os.link` fails | create text / copy | **not published** | removed | raised |
| `shutil.copy2` fails | create copy | not published | removed | raised |
| destination exists | create text / copy | **unchanged** (`FileExistsError`) | removed | raised |
| temp `unlink` fails **after** `os.link` (`:54`, `:74`) | create | **published** | **remains** (a second hard link) | raised (**T1**) |
| cleanup `unlink` fails with a non-FileNotFoundError | all | create/absent target: not published; existing target: unchanged (including prior content for replace API) | remains | **the cleanup error replaces the original** (**T2**) |
| `os.close` fails (`:62`) | create copy | not published | **leaked** | raised (**T3**) |

## BK-239: cross-platform and no-overwrite semantics

- `os.link` never overwrites: an existing destination raises `FileExistsError`. `os.replace` atomically replaces an existing file.
- A filesystem without hard links makes `os.link` raise, so creation fails closed.
- **Durability limit:** only the file is fsynced (3 `os.fsync` calls, no directory fsync). Visibility is atomic, but on some filesystems a crash right after publishing may lose the new directory entry.

## Confirmed hazards (pinned as `expectedFailure`; each fails as stated)

| Id | Where | Hazard | Fix rule |
|---|---|---|---|
| **T1** | `:54`, `:74` | After a successful `os.link` the destination is committed, but a failing temp unlink still raises. A caller that retries then hits `FileExistsError` for its own file. | After the link succeeds, treat the temp unlink as best-effort: suppress `OSError` and optionally warn. |
| **T2** | `:27-30`, `:49-52`, `:69-72` | Cleanup suppresses only `FileNotFoundError`, so a `PermissionError` from cleanup **replaces** the real cause. The test injects the original error as a `ValueError` and sees the `PermissionError`. | Suppress, or log, every `OSError` from cleanup and re-raise the original. |
| **T3** | `:61-63` | `os.close(fd)` runs before the `try`, so a close failure leaks the empty temp sibling. | Move the close inside the `try`, or into its own `try/finally`. |

## BK-240: tests and results

From `Scripts/Tools`: `python -I -m unittest discover -s . -p "test_bk236_240_atomic_io_audit.py" -v` → **`Ran 15 tests ... OK (expected failures=3)`**. Lead review added explicit injected `write` and `flush` failures after noticing the original failure matrix covered `fsync`, `copy2`, `link` and `replace` only; both new cases preserve the old target and remove the temp.

| Class | Tests |
|---|---|
| `Bk236Callers` (1) | The exact caller inventory and the replace/create split. |
| `Bk237TempSibling` (2) | Hidden same-directory sibling; parent directories created. |
| `Bk238FailureCleanup` (5) | write and flush (added during lead review), fsync, replace, link (text and copy), and copy failures: target state, temp removed. |
| `Bk239NoOverwrite` (3) | Create never overwrites and leaves no temp; write replaces; no directory fsync. |
| `Bk239PostPublicationHazards` (4) | The X-2090 post-publication state (target published, temp left, exception raised); **T1**, **T2**, **T3**. |

Also checked: `py_compile` OK; no trailing whitespace.

## Limits

- Faults are simulated by patching. The real conditions are not reproduced: Windows sharing violations, network filesystems without hard links, and crash timing.
- Callers are classified statically, by their imports. Whether a caller handles T1 or T2 correctly was not traced per caller.

## BK-241..245: T1-T4 fixed (X-2094/X-2096; C, 2026-11-12)

**SOURCE CHANGED:** `Scripts/Tools/atomic_io.py`. Public signatures, replace (`os.replace`) and create (`os.link`) semantics are unchanged.

| Hazard | Fix |
|---|---|
| T1 | After `os.link` publishes, `_discard_after_publish` removes the temp best-effort; an `OSError` becomes a `RuntimeWarning` naming the target and the orphan. The call succeeds. |
| T2 | `_discard_after_failure` swallows every `OSError`, so the original exception always propagates. |
| T3 | `atomic_create_copy` closes the mkstemp fd inside the guarded block. |
| T4 | `_open_owned` closes the fd if `os.fdopen` fails, removes the temp and re-raises. |

**Tests:**
- New `Scripts/Tools/test_bk241_245_atomic_io_hotfix.py`, **9/9 after lead review**: T1 (create text and copy, including warnings-as-errors), T2 (5 api/step cases, `assertIs` on the original exception, target state kept), T3, T4 (write and create; fd closed exactly once), replace-vs-create preserved, public API.
- **Before and after:** against the copy saved before the fix, all T1-T4 cases fail (10 subtest failures/errors); the two semantics tests pass on both.
- Lead review found that promoting `RuntimeWarning` to an error could still make an already-published create appear to fail. `_discard_after_publish` now catches that promoted warning; the orphan remains reported by the ordinary warning path. This regression is included in the 9/9 result.
- BK-236 suite: the three `expectedFailure` markers are removed and the X-2090 state test now asserts the warning: **15/15**.
- Reruns: s171 4/4; BK-226 13 (1 symlink skip); BK-231 9/9; evidence-manifest suites 20 + `Scripts.Tools.test_verify_evidence_manifest` OK (1 skip); `evidence_pack_hashes` 2/2; path normalization 1/1; Queue C 31 (1 skip).

**Limit:** warning filters and file-system unlink behavior vary across hosts; the synthetic warning-as-error regression confirms the published-target success contract, while actual Windows sharing violations and orphan cleanup remain host-dependent.
