# AK-SPRINT — Lead PIE runner

`Scripts/RunLeadPie.ps1` replaces per-probe hand-written runner copies for future Lead runs. It takes `-Script`, `-Routes legacy,data`, `-Env NAME=value`, and `-OutputDir`. It owns the shared `ENGINE_LOCK.json` for a live run, refuses an existing editor or lock, launches each route with `-nosound` and a separate `-abslog`, waits for the probe's `[Prefix] SUMMARY` marker (or `-StopMarker`), writes route-specific `_lines.txt` files and a `status.txt`, kills only its own editor process after completion/timeout, and restores process environment variables. The data route uses the existing G044 encounter definition path; legacy clears the route variable.

`-DryRun` prints the route environment, editor command, stop marker, and lines path without launching Unreal or changing the lock/output folder. `Scripts/Tests/TestRunLeadPieDryRun.ps1` checks both routes, environment, `-nosound`, `-abslog`, marker, lines paths, and no lock/output side effects. The dry-run test passed. Lead live validation remains open.

AK-C11–C15 hardening added invalid-argument refusal cases, absolute path coverage, an explicit failure exit when a live route has no stop marker, a final marker read after early process exit, and fail-fast handling when a spaced Python script path has no usable Windows 8.3 ShortPath. Dry-run tests pass; live timeout/env restoration still await Lead smoke.

Example:

```powershell
./Scripts/RunLeadPie.ps1 -Script Scripts/Editor/pie_er_guard_counter.py -Routes legacy,data -Env ER_GC_SYNTHETIC=1,ER_GC_ASSIGN=1 -OutputDir Docs/BossCombatReview/Execution/Claude/P_C1006_GUARDCOUNTER -DryRun
```

No Unreal, PIE, build, or commit by Codex.
