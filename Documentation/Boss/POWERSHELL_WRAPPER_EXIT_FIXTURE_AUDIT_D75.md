# PowerShell wrapper exit-code fixtures (D75)

Date: 2026-11-03. Source-reviewed and parsed `RunBenchmark.ps1`, `RunPerfExperiments.ps1`, and `RunEditorScript.ps1` using PowerShell's parser. Added explicit failure propagation for packaged benchmark nonzero exits, nested benchmark warm-up/experiment PowerShell exits, and editor-script process failure/timeouts (expected StopPattern termination remains allowed).

An isolated mock test replaced `Start-Process` for `RunBenchmark.ps1` with a result object whose native process exit code was 7. The wrapper terminated nonzero (PowerShell process exit 1) before looking for benchmark output, so a stale result folder cannot convert this process failure to a reported success. The test used a temporary dummy staged executable and did not launch Unreal.

The PowerShell parser reported zero syntax errors for all three wrappers. `RunPerfExperiments.ps1` now throws immediately on a failed warm-up or experiment child process and stops the GPU monitor for a failed experiment before throwing. `RunEditorScript.ps1` returns failure on its own timeout or unexpected nonzero editor exit; intentional StopPattern kill is distinguished.

No actual benchmark, editor, GPU monitor, packaging, or build command was run. This validates process exit propagation with one mock path, not summary-file validity or every PowerShell failure mode.
