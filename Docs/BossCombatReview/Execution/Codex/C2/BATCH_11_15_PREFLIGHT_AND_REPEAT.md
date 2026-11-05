# Queue F-C batch: tasks 11–15, profile blockers and safe reruns

## Task 11 — preflight blockers

`validate_selected_boss_profile.py` requires exactly one selected `URPGBossFrameworkProfile`, resolves its mesh/class/card/sequence references for inspection, builds the existing C1 configuration shape, and calls `validate_boss_config.py`. Each validator token is returned as a stable diagnostic code with a field and message; the receipt also lists identity, band, and card-count context.

## Task 12 — successful/no-save path

On an accepted profile the action emits `ok=true`, `saved=false`, and `compiled=false`. It calls no `set_editor_property`, asset creation, save, or Blueprint compile API. Only dependency reads and the pure configuration validator run. This is an Editor-side validation receipt, not proof of a byte-for-byte package hash.

## Task 13 — invalid-profile/no-save path

Any C1 validator error token makes `ok=false`. The script reports all blockers and returns before any compile/save path; no profile or map is changed by the script. Readback exceptions become `Profile.PreflightException` with `ProfileReadback` field context.

## Task 14 — safe repeat

The profile action is deterministic for unchanged asset/config data, makes no serialized edits, and can be run repeatedly. The standalone AnimBlueprint compiler action is separately repeatable and does not save; it may recompile generated data in the current Editor session.

## Task 15 — stale selection refusal

The profile action snapshots the selected profile path, performs preflight, and rereads Content Browser selection before reporting success. If the selection is empty, multiple, or points to a different asset, it returns `Selection.Stale` and discards the result.

## Acceptance boundary

The profile checker uses the repository's pure C1 validator, which mirrors core native domains but is not a direct call to `RPGFramework::ValidateProfile`; current rule parity and soft-reference resolution need Lead's UE 5.5.4 Editor review. Static syntax/diff checks only; no Editor/PIE/build/test run by Codex.
