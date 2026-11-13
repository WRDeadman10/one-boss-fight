# BK-196..200: Python files that mention ENGINE_LOCK, and the two Python lock mutators

Assigned by X-2045 (lead Codex) to C (implementer), 2026-11-12. This is batch 6 of 20. New files only:
- `Scripts/Tools/test_bk196_200_python_lock_mutators.py`
- this report

**Source-only.** Neither mutator was run, imported or edited, and no lock, asset, editor or subprocess was touched. **The facts below are read from the source; the risks are labelled as risks. No live event is claimed.** X-1991 is still open.

## BK-196: inventory and query boundary

**Query:** every `Scripts/**/*.py` whose text contains `ENGINE_LOCK` (case-sensitive), excluding `__pycache__` and audit files named `test_bk<N>_` with **N ≥ 186**, which were written after A-847 and A-849. **Result: 32 files**, reproducing A-847's count of non-`.ps1` files. All of them are `.py`.

| Class | Count | What it is |
|---|---|---|
| **Lock mutator** (writes or deletes a lock file) | **2** | `Scripts/Editor/retarget_mixamo_backstep.py`, `Scripts/Editor/run_c1003_under_lock.py` |
| Editor precondition doc | 12 | Editor scripts whose docstring says "run under ENGINE_LOCK"; they never touch the file. |
| Test reference | 12 | Contract tests that assert runner text, plus earlier audit tests (BK-141, BK-181). |
| Tool constant or validator | 6 | Proposal and validator modules that name the lock paths. |

## BK-197: `Scripts/Editor/retarget_mixamo_backstep.py`

**Source facts:**
- **Execution lock only** (`:48`); the root lock is never taken.
- **Takes over any lock owned by "AG"** (`:98`): an existing lock is refused only if its owner is not `AG`, so another live AG run's lock is overwritten.
- **Non-exclusive write**, `open(full_lock, "w")` (`:108`), after a separate existence check (`:94`).
- **No run token**: the record holds owner, purpose and time only.
- **Unconditional release:** `os.remove` (`:117`) with no owner or token check. A failed release is only logged (`:120`).
- **Placement:** acquire happens at `:350`; the cleanup `try` opens at `:351`, with `finally` / release at `:408-409`. The write happens inside `acquire_engine_lock()`, so a failure after `:108` leaves the lock behind.
- **Runs inside the editor:** `execute_pipeline()` runs only `IN_ENGINE`, under `import unreal`. Outside the editor, `main()` only performs a dry check.

**Risks:**
- The lock is taken **after Unreal is already running**, the reverse of the C-1155 order.
- It can take over another AG holder's live lock.
- It can delete a lock it does not own.

## BK-198: `Scripts/Editor/run_c1003_under_lock.py`

**Source facts:**
- **Execution lock only** (`:8`).
- **Check, then a non-exclusive write:** the existence check is at `:13-15`, then `open(LOCK_PATH, "w")` at `:18`.
- **The write is before the `try`** (`:25`).
- **Unconditional release** in `finally` (`:46-49`), with no owner check.
- **No running-editor check** and **no token**.
- **Subprocess boundary:** list-form argv (no shell), with `-run=pythonscript`, `-nullrhi` and `-nosound`, and a **120 s timeout** (`subprocess.run` kills the child on timeout, and `finally` still releases).
- **The child's return code is printed but never becomes the script's exit status**, so a failed editor run still exits 0.

**Risks:**
- A race between the check and the write can overwrite a lock.
- A write or serialization failure before `:25` leaves the lock behind.
- It can delete a lock it does not own.
- A failed child is not reported as a failure.

## BK-199: comparison with the C-1155 PowerShell protocol

| C-1155 property | retarget_mixamo_backstep | run_c1003_under_lock |
|---|---|---|
| Both locks (root and execution) | no | no |
| No Unreal process before the lock | **no** (runs inside the editor) | no (never checks) |
| Exclusive create (fails if present) | no | no |
| Unique run token in the record | no | no |
| Ownership-checked release | no | no |
| Lock written inside the cleanup try | no (in the acquire function, before `:351`) | no (`:18` before `:25`) |
| Release in `finally` | yes | yes |

Both scripts are older, owner-string-based ("AG") lock handlers that predate the token-based C-1155 runners. `test_table_matches_source` computes the table from the source.

## BK-200: tests and results

From `Scripts/Tools`: `python -I -m unittest discover -s . -p "test_bk196_200_python_lock_mutators.py" -v` → **`Ran 8 tests ... OK`**.

| Class | Tests |
|---|---|
| `Bk196Inventory` (3) | Exactly 32 files, deterministic, all `.py`; the boundary excludes later audit files (including this one) and caches; class counts 2 / 12 / 12 / 6. |
| `Bk197RetargetMixamoBackstep` (2) | The line anchors above; no root lock; no token; runs inside the editor. |
| `Bk198RunC1003UnderLock` (2) | The line anchors above; no running-editor check and no token; the subprocess boundary (list argv, timeout, return code not propagated). |
| `Bk199ProtocolComparison` (1) | The comparison table, computed from the source. |

Also checked:
- `py_compile` → OK; no trailing whitespace.
- My first expected class counts and one table cell were guesses that did not match the source. They were corrected to the computed values: 12 / 6 classes, and retarget "written inside the cleanup try" = no.

## Limits

- Only `ENGINE_LOCK` text in `.py` files is in scope. Other languages and files outside `Scripts/` are not.
- Whether either script has ever been run, or overlapped with another run, cannot be known from the source. Both are now documented as active lock mutators outside the PowerShell census. **Neither was edited**; changing them would be a separate lead assignment.
