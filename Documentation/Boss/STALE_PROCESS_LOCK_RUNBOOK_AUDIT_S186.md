# Stale process and lock runbook audit (S186)

Reviewed editor/staging lock guidance and narrowed the cleanup helpers to process ownership, then documented safe recovery steps in `Documentation/GATE4_RUNBOOK.md#editor-and-staging-locks`. No process was stopped, and no packaging/editor command was run.

## Findings and changes

- `Scripts/Rebuild.ps1` previously closed and force-stopped every `UnrealEditor.exe` by image name. It now reads command lines and selects only editor processes containing this checkout's full `.uproject` path. If process inspection fails, it stops before closing or building. A hung matching editor is terminated by confirmed PID with `/T /F`, limited to that process tree.
- `Scripts/PackagedSmoke.ps1` already started cleanup from the staged launcher's PID. Its extra wildcard game-process sweep could include a separately launched game. It now snapshots process descendants through parent-PID relationships and creation time, stops the launcher tree by PID, and only targets a surviving snapshotted child when a fresh CIM query confirms its creation timestamp and parent PID still match. It uses no image-name sweep.
- The Gate 4 runbook now gives a read-only process inventory command, says to close normally first, and documents PID-tree termination only after confirming the correct root PID. It warns against image-name, wildcard, and command-line-pattern termination and against deleting/renaming staged files to clear active handles.

Both changed PowerShell scripts pass the PowerShell AST parser; `git diff --check` reports no whitespace errors (only the repository's LF-to-CRLF working-copy notices). Acceptance is met at source/runbook level. Live process ownership, Windows access behavior, and staging lock release were not exercised.
