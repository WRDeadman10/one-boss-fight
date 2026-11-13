# BK-151..155: environment, child-process, output-path and exit-handling census of C-1155 runners

Assigned by X-2030 (lead Codex) to C (implementer), 2026-11-11. New files only: `Scripts/Tools/test_bk151_155_c1155_runner_io_census.py` and this report.

**Text-only.** The 34 `.ps1` files under `Scripts/` that contain `owner_token` are read as source. No runner or child process is executed, and no lock, temp file, log or asset is touched.

`classify_io()` is checked on synthetic runner text. Its per-runner results are then compared with explicit tables frozen on 2026-11-11.

**Counts describe the source, not runtime behavior. Audit only, with no production edit. X-1991 is still open.**

## BK-151: environment and working-directory assumptions

| Class | Count | Runners / note |
|---|---|---|
| Project root hardcoded (`'C:\UnrealProject\OneBossFight'`) | 32 | all except the two below |
| Project root as a param, resolved with `Resolve-Path` | 2 | `run_bk56_60_deferred_selection`, `run_bk7_shipping_pipeline` |
| UE 5.5 install path hardcoded, as a literal or param default | **34** | `C:\Program Files\Epic Games\UE_5.5` |
| `Set-Location` to the project root, **never restored** | **9** | `be_x26_x30`, `be_x31_x35`, `be_x36_x40`, `bf_x01_x05`, `bf_x11_x15`, `bf_x16_x20`, `bk2_x26`, `bk56_60`, `c1280_x26` |
| Env vars changed, prior value saved and restored | 4 | `be_x26_x30`, `bk2_x26`, `bk56_60`, `c1280_x26` |
| Env vars set, then **removed in `finally` without saving** (a caller's pre-set value is erased) | **7** | `c1252a`, `c1253a`, `c1254a`, `c1256a_live_self_test`, `c1258a_live_self_test`, `c1262a_live_diagnostic`, `c1265b_clip_trace` |
| No env change | 23 | — |
| Tool resolved from `PATH` (`Get-Command python`) | 2 | `bk56_60`, `bk7` |

Assumptions:
- Every runner assumes the `C:` layout and UE 5.5 at the default path.
- The 9 `Set-Location` runners change the caller's location when run in an existing session, for example dot-sourced or from an interactive shell. When run with `-File`, the change ends with the process.

## BK-152: child-process construction

- **Launch styles:**
  - 27 runners use the call operator `&`, which passes arguments per token, so there is no joining ambiguity.
  - 12 use `Start-Process`.
  - 5 use both.
- **Quoting (9 runners):** `bk2_x26`, `bk56_60`, `c1256a_live`, `c1257a_author`, `c1257a_dry_run`, `c1258a_live`, `c1262a_live`, `c1265b`, `c1275a`.
  - Each passes an `-ExecCmds="py <path> …"` element with embedded double quotes inside a `Start-Process -ArgumentList @(...)` array.
  - Windows PowerShell joins array elements with spaces and does not quote them. Correctness therefore depends on those embedded quotes and on lowercased short (8.3) script paths, which have no spaces. A path or extra argument containing a space or a quote would split or merge arguments.
- **Caller-controlled inputs:**
  - Only the 2 param runners accept caller input: `EngineRoot` and `ProjectRoot`, plus `BuildId` and others in `bk7`. These flow into executable and output paths.
  - No runner reads an environment variable as an input; env reads only save prior values.
- **`$args` assignment:** `run_c1274_s6_locked_dryrun` assigns PowerShell's **automatic `$args`** variable as its argument list (`$args = @(...)`). It works at script scope but shadows the script's own arguments; this is fragile.

## BK-153: output path uniqueness and overwrite

| Class | Count | Note |
|---|---|---|
| Per-run evidence folder (timestamp `yyyyMMdd_HHmmss`, or `$run`, `$runName`, `$stamp` built from it) | 16 | `be_*`, `bf_*`, `bk2_x26`, `bk56_60`, `bk7` (`BuildId` + timestamp), `c1275a`, `c1280_x26` |
| **Fixed evidence folder reused by every run**: same-named files (`build.log`, `status.txt`, editor logs) are overwritten | **18** | all `c1252a`..`c1274_*` runners except `c1275a` and `c1280` |
| Fixed folder **shared by two different runners** | 3 folders | `C1256A_SPAWN_BRIDGE` (`c1256a_live_self_test` + `c1256a_spawn_bridge_build_suite`), `C1258A_RANGE_RETRY` (`c1258a_live_self_test` + `c1258a_locked_build`), `C1262A_SEVAROG_DIAG` (`c1262a_live_diagnostic` + `c1262a_locked_build`) |
| Abort if the evidence folder already exists | 3 | `bk56_60`, `bk7`, `c1275a` |
| Folder created with `New-Item -Force` (merges into an existing folder) | 33 | — |
| Per-run folder with **no existence check** (relies on a 1-second timestamp alone) | 13 | — |

## BK-154: timeout, cancellation, exit codes

| Class | Count | Note |
|---|---|---|
| Poll the launched editor against a deadline (`AddMinutes`), kill on timeout or marker | 9 | `bk2_x26`, `bk56_60`, `c1256a_live`, `c1257a_author`, `c1257a_dry_run`, `c1258a_live`, `c1262a_live`, `c1265b`, `c1275a` |
| `Start-Process -Wait` with **no timeout** | **3** | `be_x26_x30`, `c1274_s6`, `c1280_x26` |
| Call-operator `&` steps (build, suite, python) with a timeout | **0** | Every `&` step can block without limit. |
| `$LASTEXITCODE` read after `&` | 27 | Tied to the launched process. |
| `$proc.ExitCode` read | 5 | `be_x26_x30`, `bk56_60`, `c1257a_author`, `c1274_s6`, `c1280_x26` |
| **Stale-log marker risk:** polls a log in a fixed folder and never deletes the old log before launch | **6** | `c1256a_live`, `c1257a_author`, `c1257a_dry_run`, `c1258a_live`, `c1262a_live`, `c1265b`. The poll starts 2 s after launch, so a **previous run's log containing the success marker can end the wait**. The editor is then killed and the status is built from that text. The result is tied to a log path, not to the launched process. |
| Log deleted before launch | 0 | — |

## BK-155: tests and results

From `Scripts/Tools`: `python -I -m unittest discover -s . -p "test_bk151_155_c1155_runner_io_census.py" -v` → **`Ran 14 tests ... OK`**. All 14 are ordinary tests; there are no expected failures, because this is a census of current state.

| Class | Tests |
|---|---|
| `ClassifierSelfCheck` (1) | Synthetic runners check each detection: per-run vs fixed evidence, root kind, env classes, embedded-quote `ExecCmds`, unbounded `-Wait`, poll with and without log removal, `$args` assignment, exists-abort. |
| `Census` (1) | 34 runners, deterministic. |
| `Bk151EnvironmentAndCwd` (4) | Roots and engine; `Set-Location` with no restore; env 4 / 7 / 23; tools from `PATH`. |
| `Bk152ChildProcess` (2) | Launch styles 27 / 12; quoting 9, params 2, `$args` 1. |
| `Bk153OutputPaths` (3) | Fixed 18 / per-run 16; exists-abort 3, `-Force` 33, unchecked per-run 13; shared folders 3. |
| `Bk154TimeoutAndExit` (3) | Poll 9, unbounded wait 3; exit-code reads 27 / 5; stale-log risk 6, log removal 0. |

Also checked:
- `py_compile` → OK; no trailing whitespace.
- A first draft of the frozen env table listed 4 runners as clearing without saving. The classifier found 7 (`c1252a`, `c1253a` and `c1254a` also do), and the table was corrected to match the source.

## Limits

- Regex classification of source text. Unusual constructs could be misclassified; the frozen tables flag any change for manual review.
- **No runtime claims.** The stale-log risk, the unbounded waits and the quoting ambiguity are possible behaviors read from the source, not observed. For example, whether the editor truncates the log before the first poll depends on startup timing.
- "No `&` timeout" means no explicit timeout in the script. External tools such as UBT may still have their own limits.
