# Subprocess and editor-wrapper exit audit (S169)

Static review of process and editor-task wrappers under `Scripts`. No child process, Unreal Editor, or Blender process was launched for this audit.

## Findings

| File:line | Behavior | Risk / acceptance note |
|---|---|---|
| `Scripts/blender_exec.py:67-72,79-83,86-89` | Headless fallback writes an `executed` boolean into a temporary JSON response; when the file exists, the wrapper returns it without checking `proc.returncode`. It checks the return code only when no response file was produced. | Error state is represented in the response, but it is not a nonzero CLI exit. A static inventory found 80 scripts calling `execute_blender` and no caller explicitly checks `res['executed']` / `res.get('executed')`; many only print or consume `result`, so a failed Blender operation can look like a successful command to automation. Validate the response in callers or make the wrapper signal failure consistently, while retaining the diagnostic JSON. |
| `Scripts/run_in_editor.py:28-35` | Polls the editor task until `completed` or `failed`, then prints status/output; it does not set a failing process exit status when `st == "failed"`. | Automation calling this wrapper can receive exit 0 for a failed editor task. Return a nonzero code for failed/timeout/error status. |
| `Scripts/switch_character.py:47-52` | Outside Unreal, invokes `run_in_editor.py` with `subprocess.run(cmd)` and discards the `CompletedProcess`. | Child failure is not propagated; check `returncode` and return/exit with it (or explicitly treat invocation as a fire-and-forget operation, which this authoring command does not document).
| `Scripts/Tools/audit_tool_index.py:37-49,66` | Runs each `--help` child with timeout; records launch/timeout/nonzero issues and returns 1 if any issue exists. | Exit handling is explicit for this read-only audit tool. |

## Disposition

S169 acceptance is **not met**: the primary Blender and editor-task wrappers expose failures in payloads/log text but do not reliably propagate them as process failure, and one caller discards a child return code. The CLI-help audit tool handles its child status correctly. Exact callers and inventory detail are available in `Scripts/blender_exec.py`, `Scripts/run_in_editor.py`, `Scripts/switch_character.py`, and `Scripts/Tools/audit_tool_index.py`. Static source review only; no scripts, tests, build, Editor, runtime, or subprocesses were run.
