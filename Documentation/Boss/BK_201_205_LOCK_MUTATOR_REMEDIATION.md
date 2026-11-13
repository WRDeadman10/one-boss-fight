# BK-201..205: references, invocation paths, record compatibility and a remediation design for the two Python lock mutators

Assigned by X-2049 (lead Codex) to C (implementer), 2026-11-12. This is batch 7 of 20. New files only:
- `Scripts/Tools/test_bk201_205_lock_mutator_references.py`
- this report

**Source-only.** Neither `Scripts/Editor/retarget_mixamo_backstep.py` nor `Scripts/Editor/run_c1003_under_lock.py`, nor the C-1003 child, was run, imported or edited. No lock, asset, editor or subprocess was touched. The X-2047 report and tests are unchanged. X-1991 is still open.

## BK-201: references

The working tree was searched, excluding `.git`, `Saved`, `Intermediate`, `Binaries`, `DerivedDataCache`, `__pycache__`, `Content` and `Ref`, and audit files numbered BK-196 and later. Both mutators are **tracked** source. Only 4 files mention them:

| File | Kind |
|---|---|
| `Documentation/KNOWN_ISSUES.md` | doc (the BK-196 risk entry) |
| `Documentation/TASKS.md` | doc |
| `Documentation/TEAM_MAILBOX.md` | doc (11 mentions) |
| `scratch/test_retarget_mixamo_backstep_offline.py` | untracked test |

## BK-202: invocation paths

- **No launcher invokes either mutator.** No `.ps1`, `.bat` or `.cmd` file, and no subprocess-launching `.py`, names them. Both can only be run by a person launching them directly.
- **The scratch test cannot load the real module.** It resolves `Path(__file__).with_name("retarget_mixamo_backstep.py")`, which is `scratch/retarget_mixamo_backstep.py`, and that file does not exist.
- **Retarget:** asset writes happen only in `execute_pipeline()`, **after** `acquire_engine_lock()`. With no FBX it returns before taking any lock or writing anything, and outside the editor only `dry_check()` runs. Its output assets **already exist** (`Content/OneBossFight/Player/Animations/AN_ER_Backstep_Mixamo*.uasset`, `AM_ER_Backstep_Mixamo*.uasset`, including V2), and its refuse-if-exists branches reuse them.
- **C-1003:** the asset-writing child `Scripts/Editor/set_strong_attack_data_c1003.py` contains **no lock handling**, and only `run_c1003_under_lock.py` references it. **Launched directly, for example with `-ExecutePythonScript`, it changes assets with no lock at all.** That is a path that skips even the unsafe helper.

## BK-203: lock-record schemas and consumers

| Writer | Record keys |
|---|---|
| `retarget_mixamo_backstep.py` | `purpose`, `owner: "AG"`, `startTime` (local time, no timezone) |
| `run_c1003_under_lock.py` | `owner: "AG"`, `task`, `acquired_at` (local time, no timezone) |
| C-1155 PowerShell runners (34 `owner_token` scripts) | `agent`, `party`, `task`, `command_id`, `owner_token`, `pid`, `start_utc`, `policy`, `scope`; **no `owner` key** |

How each kind of reader treats each kind of record:
- **Token-checking PowerShell releases (34)** delete only on an `owner_token` match. **A legacy record is never deleted by them**, and their pre-checks refuse to start while one exists.
- **The 4 `command_id`/`task`-checking scripts** (`aura_graph` ×2, `c1210` ×2) likewise never delete a foreign record.
- **`retarget_mixamo_backstep.py`** reads only `owner`. A C-1155 record has no `owner` key, so it is **refused, not taken over**. A legacy `owner: "AG"` record is **taken over**; this applies to records from `run_c1003_under_lock.py`, `run_apply_notifies.ps1` and other legacy AG writers.
- **The incompatibility that matters runs the other way.** The 15 unconditional deleters (13 legacy `.ps1` from BK-183, plus these 2 `.py`) delete **any** record at their path, **including a live C-1155 token lock**.

## BK-204: remediation design (options only; neither mutator is changed)

Recommended order: **R1 first**, then R2 or R3 only if a rerun is ever needed.

| Option | What | Respects | Cost and risk |
|---|---|---|---|
| **R1. Retire both** | Mark both scripts deprecated or archived, for example by moving them under an archive folder or adding a refuse-to-run guard. The C-1003 data change is done (child last modified 2026-11-07), and the retarget outputs exist, superseded by V2. | Removes 2 of the 15 unconditional deleters; no flow is lost. | Smallest change. It needs a lead assignment because it edits or moves the files. |
| **R2. Retarget under an outer C-1155 runner** | A PowerShell runner, copied from the latest template, takes **both** locks **before** starting Unreal: exclusive create, a 32-hex token, an ownership-checked release in `finally`. It launches the editor with `-ExecutePythonScript`. The Python side only **verifies** that the locks exist and carry the expected token, passed through an environment variable. It never creates or deletes a lock. | The in-editor retarget flow is kept, and the C-1155 launch order is restored (no Unreal before the locks). | Needs a new runner plus a small Python guard; testable without running, like BK-141..190. |
| **R3. C-1003 child under a standard runner** | Replace the wrapper with a C-1155 runner that launches `set_strong_attack_data_c1003.py`. Add a read-only lock-presence guard to the child so a direct launch refuses. | Closes the no-lock direct-launch path in BK-202. | Edits the child. Only worth doing if the data step must ever run again. |
| R4. Compatibility shim (not recommended) | Teach legacy readers the C-1155 schema. | — | Keeps unsafe writers alive; worse than R1. |

## BK-205: tests and results

From `Scripts/Tools`: `python -I -m unittest discover -s . -p "test_bk201_205_lock_mutator_references.py" -v` → **`Ran 10 tests ... OK`** after the X-2052 caller-scope hotfix. The file walk takes about 16 seconds in the current workspace.

| Class | Tests |
|---|---|
| `Bk201References` (2) | The exact 4-file reference inventory; both mutators exist as source. |
| `Bk202InvocationPaths` (5) | Zero launchers; the scratch test cannot load the real module; retarget's asset work comes only after its lock helper (no-FBX early return); the C-1003 child has no lock code and only the wrapper references it; documentation mentions are not callers. |
| `Bk203RecordSchemas` (3) | The legacy record keys (no `owner_token`, `command_id`, `policy`, `party` or `pid`); C-1155 records carry no `owner` key; 34 token-checking releases. |

Also checked:
- `py_compile` → OK; no trailing whitespace.
- My first estimate of 35 token readers was corrected to 34, the count of releases that actually compare `owner_token` with `-eq`.

## Unknowns

- Whether anyone launches either script by hand, or has done so, cannot be known from source or logs here.
- Callers outside this repository (other machines, the owner's shell history) are not visible.
- The search covers text files with common extensions only. A launcher with an unusual extension would be missed.

## X-2052 hotfix (2026-11-12)

- **The bug:** `test_c1003_child_has_no_lock_of_its_own` scanned every text file for callers of `set_strong_attack_data_c1003`. Once my C-1363 post and this report named the child, the mailbox and the report counted as "callers", and the fresh rerun gave 8/9.
- **Fix:** the BK-202 caller check is now limited to **executable/source files** (`SOURCE_SUFFIXES` = `.py`, `.ps1`, `.bat`, `.cmd`), excluding the child itself and audit tests. Documentation mentions stay in the BK-201 inventory.
- **New test:** `test_documentation_mentions_of_the_child_are_not_callers` checks that every non-source mention is documentation (`.md`, `.txt`, `.json`).
- **Result:** lead rerun `Ran 10 tests ... OK`. The mutators and the child were not modified, imported or run.
