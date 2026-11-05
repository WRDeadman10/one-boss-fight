# Queue F-C batch: tasks 6–10, Validate Boss action

## Task 6 — compile and preflight API audit

The UE 5.5 Python API documents `BlueprintEditorLibrary.compile_blueprint(blueprint) -> None`; the call does not return a compiler report. The tool reads `BlueprintEditorLibrary.generated_class()` after compile and captures newly appended `[Compiler]` lines from the Editor log as diagnostics. It does not read `Blueprint.status`, which is protected in the live UE 5.5.4 Python session. It resolves the log in this order: `C2_EDITOR_LOG_PATH`, the current process `-abslog` argument from `SystemLibrary.get_command_line()`, then `Paths.project_log_dir()`. It refuses verification if the file cannot be read before compile, predates the current Editor process session, or does not grow during compile. On Windows it obtains process creation time from the current process; wrappers may set `C2_EDITOR_SESSION_START_EPOCH` explicitly. Set `C2_EDITOR_LOG_PATH` explicitly if the wrapper's command line is unavailable or uses an unusual argument form. A compiler line is marked `asset_match` only when it textually contains the selected asset name/path; this is best-effort attribution, not a compiler-provided object reference.

## Task 7 — selection and map preconditions

Run inside the open Editor with exactly one boss `AnimBlueprint` selected in the Content Browser. Zero/multiple selection and a wrong asset class return a structured refusal. This action is asset-scoped: it reads no world/map, does not require an open proof level, does not start PIE, and does not write/save the Blueprint or any map. Its purpose is AnimBlueprint compile health; it does not claim to validate the profile's skeleton, socket, or FullBody slot contract.

## Task 8 — editor-only action

`validate_selected_anim_blueprint.py` is the editor-only action. From the Editor Python console, run:

```python
exec(open('C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/C2/validate_selected_anim_blueprint.py', encoding='utf-8').read())
```

It is read-only with respect to saved assets: it compiles the selected Blueprint in memory, reports compile-attempt/generated-class/compiler-log evidence, and never saves. It logs one `[C2_VALIDATE]` JSON receipt and shows a short modal summary. It works without a selected map.

## Task 9 — structured diagnostics

The receipt has stable diagnostic `code`, `severity`, `asset_path`, `field`, and `message` keys. It includes selection failures, API exceptions, failed/error status, missing generated class, and new compiler log lines. UE's Python compile wrapper does not return individual compiler diagnostics, so raw new `[Compiler]` log lines are retained verbatim; this path cannot guarantee asset attribution for lines that omit an asset name. If the Editor uses a nonstandard log destination, set `C2_EDITOR_LOG_PATH` in the Editor process environment before launch.

## Task 10 — asset and field context

The modal summary prints the asset path, each status/generated-class field, and any diagnostic field/code/message. The complete JSON record goes to the Editor log for copying or a later report tool. No source profile/config field is guessed from an AnimBlueprint.

## Verification boundary

API references: [UE 5.5 BlueprintEditorLibrary](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/BlueprintEditorLibrary?application_version=5.5) documents the void compile call; [UE 5.5 EditorUtilityLibrary](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorUtilityLibrary?application_version=5.5) documents Content Browser selection; [UE 5.0 EditorDialog](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/EditorDialog?application_version=5.0) provides the modal message API; [UE 5.5 Paths](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/Paths?application_version=5.5) exposes the project log directory; and [UE 5.5 EBlueprintStatus](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/Engine/EBlueprintStatus?application_version=5.5) defines compile-state values, including error, up-to-date, and up-to-date-with-warnings.

No Editor/PIE/build/test run was performed. Runtime API exposure and compiler-log tail behavior still require Lead validation in the configured UE 5.5.4 Editor.
