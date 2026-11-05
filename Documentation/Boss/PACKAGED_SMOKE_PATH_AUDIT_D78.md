# Packaged smoke path audit (D78)

Date: 2026-11-03. Read-only source review of `Scripts/PackagedSmoke.ps1` and `Scripts/CheckPackagedLog.ps1`; no packaged game was launched.

- Default executable resolves from the script directory to `Saved/StagedBuilds/Windows/OneBossFight.exe`; `-ExePath` allows an explicit staged launcher. The path must resolve to a leaf file. The adjacent `CheckPackagedLog.ps1` is required.
- Launch args are `-nosound -log`; the wrapper waits the requested bounded duration and records whether the launcher PID remains alive.
- Cleanup is scoped to that launcher PID tree, not an image-name sweep. It snapshots descendants and rechecks creation time/parent identity before stopping them. If process inventory fails, it warns and still attempts root PID-tree cleanup; `taskkill` child status is not independently checked.
- Runtime-log lookup searches at most five ancestor levels for `OneBossFight/Saved/Logs/OneBossFight.log` and `Saved/Logs/OneBossFight.log`. It requires modification time at/after launch to avoid accepting a stale log, then invokes the packaged-log checker and passes only when both process liveness and checker exit are good.
- If no fresh runtime log exists but the staged Shipping binary is found under the launcher's sibling `OneBossFight/Binaries/Win64`, it skips log checking and runs `CheckShippingBinary.py`; this is a binary debug-symbol-name check plus launcher liveness, not runtime-log or packaged-content proof.
- Failures for missing executable/checker throw; absent fresh log, checker failure, failed binary check, or early process exit return nonzero. Temporary output/artifact cleanup is not done by this wrapper.

Path discovery is bounded by five ancestors and relies on launch time/mtime rather than a per-run log identity marker. No staged assets, logs, processes, or build artifacts were touched.
