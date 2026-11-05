# Driver evidence copy-failure audit (D88)

Date: 2026-11-03. Static review of benchmark collection/variant wrappers and the maintained evidence-pack CLI. No benchmark, copy, or archive operation was run.

## False-success risk: BenchKit collection

`Scripts/BenchKit_Collect.ps1` sets `$ErrorActionPreference = 'Continue'` (line 16). It copies every discovered run folder with `Copy-Item`, then increments `$n` unconditionally (lines 49–58); a non-terminating copy error can therefore leave a partial/missing folder while the `runs_count.txt` value still counts the attempted copy. Log, GPU-sampler CSV, and experiment-table copies also have no explicit post-copy existence/size/hash verification (lines 68–82). The summary-table subprocess output is saved to text, but `$LASTEXITCODE` is not checked (lines 60–66). Finally `Compress-Archive` is called and “Results written to” is printed without verifying the archive exists or contains required entries (lines 84–87). Under the script's continue-on-error policy, collection failure can thus still produce a success-like zip path and copied-run count.

The script also accepts zero run directories (`$n` begins at zero) and still reaches the archive/result message; that output describes archive creation, not a minimum evidence-set acceptance rule. Logs are optional by design (“when there is one”), so their absence alone is not a collection failure unless a consumer requires them.

## Contrasting failure contracts

- `Scripts/RunVariants.ps1` sets `$ErrorActionPreference = 'Stop'`, calls `RunBenchmark.ps1` before reading a summary, then copies the summary. A missing summary or failed `Copy-Item` terminates the loop/script rather than printing a successful variant row for that copy (lines 20–42). It does not add a hash or re-open the copy for byte comparison.
- `Scripts/Tools/evidence_pack.py` validates required input files, creates payloads using same-directory atomic no-overwrite copies, records copied byte counts and SHA-256, writes the hash list, and publishes the JSON manifest last (lines 37–70; `atomic_io.py:57–74`). A copy/publication exception prevents the success print and normal return, so an incomplete pack is not reported as success by this CLI. Previously published payloads can remain if a later step fails; the manifest-last marker is absent in that case. Pack-wide rollback is not claimed (covered in D68/D71).

## Disposition

D88 acceptance is not met for `BenchKit_Collect.ps1`: a missing or failed retained copy can be counted as copied and followed by an unconditional success-like result message. `RunVariants.ps1` and `evidence_pack.py` fail more conservatively but do not provide copy hash verification in the former or whole-bundle rollback in the latter. This is source-only; filesystem permission, archive contents, and actual copy failure behavior were not exercised. No script was changed.
