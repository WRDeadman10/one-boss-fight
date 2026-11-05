# PIE driver failure propagation review (S185)

Static review of `Scripts/RunDrivers.ps1` and its PowerShell parse. The driver was not executed; the script requires an open Unreal Editor and bridge, which remain Lead-owned.

## Failure paths

- **Timeout:** when no final result/summary line arrives by the deadline, the script appends a `TIMEOUT` row and breaks the driver loop (`RunDrivers.ps1:136-140`). The final `$bad` filter includes every non-`PASS` result and exits 1 (`:181-183`). Full-mode timeout also enters that table (`:177`).
- **Zero or too few checks:** parsed result counts are compared against each driver's configured `Min`; `$total -ge $d.Min` is required even when the reported failure count is zero (`:148`). A `RESULT 0/0` or any below-minimum result therefore becomes `FAIL`, then exits 1 through the final table.
- **Failed checks:** result/summary parsing derives a positive `$failed` count (`:142-146`); `$failed -eq 0` is required for `$ok` (`:148`). Failed rows flow to the final nonzero exit.
- **Bridge unavailable:** startup failure exits 2 with the bridge URL and recovery instruction (`:94-96`).

`Invoke-Editor` does not directly propagate Python's exit code (`:84-86`), but the driver path waits for its expected final log record; absence becomes a timeout, which is nonzero. For this audit's three required cases, source control flow reaches a nonzero script exit. PowerShell AST parsing reported no syntax errors. No code changes were needed; acceptance is supported by source tracing, not by executing timeout/zero/failure scenarios in PIE.
