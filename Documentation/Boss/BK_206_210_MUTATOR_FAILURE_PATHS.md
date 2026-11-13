# BK-206..210: invocation routes, failure paths and a remediation decision table for the two legacy Python lock mutators

Assigned by X-2054 (lead Codex) to C (implementer), 2026-11-12. This is batch 8 of 20. New files only:
- `Scripts/Tools/test_bk206_210_mutator_failure_paths.py` (`Ran 9 tests ... OK`; every line anchor below is asserted)
- this report

**Scope:**
- `Scripts/Editor/retarget_mixamo_backstep.py` (R)
- `Scripts/Editor/run_c1003_under_lock.py` (C)
- its child `Scripts/Editor/set_strong_attack_data_c1003.py`

**Source-only.** Nothing was imported, run or edited, and no lock, log, temp file, asset, editor or subprocess was touched. Each item is marked **[fact]** (read directly from the source) or **[risk]** (a possible consequence). No live event is claimed. X-1991 is still open.

## BK-206: invocation routes

| Route | R | C |
|---|---|---|
| Launcher code (`.ps1`/`.bat`/`.cmd`/subprocess) | **none** [fact, BK-202] | **none** [fact, BK-202] |
| Tests | the untracked `scratch/` test, which cannot load the real module [fact] | none |
| Docs | KNOWN_ISSUES, TASKS, the mailbox, BK reports | same |
| Manual only | `python` (dry check only: outside the editor `:413` → `dry_check`) or in-editor `-ExecutePythonScript` (`:417` → `execute_pipeline`) [fact] | `python run_c1003_under_lock.py`. There is **no `__main__` guard**: module-level code from `:13` means even an **import** takes the lock [fact]. |
| Child launched directly | — | `set_strong_attack_data_c1003.py` is a standalone editor script with **no lock code** [fact]. A direct launch writes assets unlocked [risk]. |

## BK-207: the C-1003 wrapper's child process, step by step

1. `:13-15` An existing lock leads to printing an error and `sys.exit(1)` [fact].
2. `:18` The lock is written with `open(…, "w")`, **before** the `try` at `:25` [fact]. A write or serialization failure leaves the lock behind [risk].
3. `:37` `subprocess.run(cmd, capture_output=True, text=True, timeout=120)` runs a list-form argv with no shell [fact].
4. **Propagation** [fact]: there is no `except` anywhere. `TimeoutExpired` (after `subprocess.run` kills the child), `FileNotFoundError` (editor missing) and a failing `os.remove` all propagate after `finally` and end the script non-zero. **A child's non-zero return code is only printed (`:38`) and never propagated**, so the script exits 0. Only one `sys.exit` exists, at `:15`.
5. `:46-49` In `finally`, the lock is removed if present, with no owner check [fact]. `:50` prints "Lock released." even when `:49` was skipped because the file was missing [fact], which is misleading evidence [risk].
6. **Ordering:** the release runs after the child exits, or after it is killed on timeout [fact]. `kill()` ends only the direct child, so any processes the editor started could outlive the release [risk; not verifiable from source].

## BK-208: retarget acquisition and cleanup failure paths

1. `:94-101` An existing lock is read. A non-`AG` owner, or unreadable JSON, is re-raised as "Cannot acquire engine lock" (`:100-101`), so the run is refused [fact].
2. `:107-109` `makedirs`, then `open(…, "w")` and `json.dump`. A failure after `:108` has created the file leaves a **partial lock**: acquire happens at `:350`, **before** the `try` at `:351`, so no `finally` runs [fact / risk].
3. `:371` and `:384` raise `RuntimeError` inside the `try`, and `finally` (`:408-409`) releases [fact].
4. **Release** (`:115-120`): if the file exists it is removed with `os.remove`, with no owner check [fact]. Any exception is **only logged** (`:119-120`, no re-raise), so the pipeline can return `True` (`:407`) while the lock stays behind [fact / risk].

## BK-209: comparison with the C-1155 runner invariants (exact mismatches, all [fact])

| C-1155 invariant | R | C |
|---|---|---|
| Both locks | Execution lock only | Execution lock only |
| No Unreal before the lock | **violated** (runs inside the editor) | not checked |
| Exclusive create | no (`open "w"`) | no (`open "w"`) |
| Run token | none | none |
| Ownership-checked release | no | no |
| Lock written inside the cleanup try | no (`:350` before `:351`) | no (`:18` before `:25`) |
| Failed release surfaced | logged only | raises (non-zero exit) |
| Child failure surfaced | n/a | **no** (return code not propagated) |

## BK-210: remediation decision table (options only; the choice belongs to the lead or owner)

| Option | Removes | Keeps | Needs | Open unknowns |
|---|---|---|---|---|
| R1. Retire or archive both, plus a refuse guard in the child | 2 unconditional deleters; the unlocked-child path | nothing; the outputs already exist (R) and the data step is done (C) | a lead assignment (edits or moves files) | manual or external users of either script |
| R2. Outer C-1155 runner for R, with an in-editor check that only reads the locks | the in-editor lock creation; restores launch order | the in-editor retarget flow | a new runner plus a small Python guard (keep `-nosound`, per A-853) | whether a retarget rerun is ever needed |
| R3. Standard C-1155 runner for the C-1003 child, plus a child guard | the wrapper's unsafe protocol; the unlocked direct path | the C-1003 data step | edits the child | whether the C-1003 step is ever rerun |
| R0. Do nothing (document only, as now) | — | everything | — | the risks in BK-207/208 stay |

**Unknowns** that apply to every option:
- manual launches;
- callers outside this repository;
- launchers with unusual file extensions, which the search did not cover;
- runtime process trees (grandchild processes).

## Tests

`python -I -m unittest discover -s . -p "test_bk206_210_mutator_failure_paths.py" -v` (from `Scripts/Tools`) → **`Ran 9 tests ... OK`**.

| Class | Tests |
|---|---|
| `Bk206InvocationRoutes` (3) | Entry points; C has no `__main__` guard; the child is standalone with no lock code. |
| `Bk207C1003ChildProcessTrace` (2) | Anchors `:13-15`, `:18`, `:25`, `:37-38`, `:46-50`; no `except`, no propagation of the return code, a single `sys.exit`. |
| `Bk208RetargetFailurePaths` (3) | Anchors `:94-109`, `:115-120`, `:350-351`, `:371`, `:384`, `:407-409`. |
| `Bk209InvariantComparison` (1) | Every lock path is the Execution lock; no exclusive create, token or ownership check; R imports `unreal`; C never checks for a running editor. |

Also checked: `py_compile` OK; no trailing whitespace.
