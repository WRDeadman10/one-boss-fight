# AQ-C01–C05 — maintained camera engagement probe

## Scope

The maintained copy is `Scripts/Editor/pie_camera_engage.py`; Claude's original `Docs/BossCombatReview/Execution/Claude/P_C1079_BOSSBLOCKS/pie_camera_engage.py` was treated as read-only. The maintained driver retains the Lead's `pie_lead_common` helpers and four existing camera modes: `orbit`, `away`, `retreat`, and `fixed`. `CAM_SPEED` remains configurable (finite range 0–1), and `CAM_LOOK_TEST` controls the one-second injected pack `IA_Look` sample.

The environment parser whitelists the three independent camera CVars and only accepts binary values. Unspecified options are explicitly initialized to zero on each run, and the summary records the effective settings. Therefore B+C is expressible as `rpg.Camera.HideBossInside 1;rpg.Camera.LockOnFraming 1`; this is a run setup only, not evidence that the combination works in PIE. Invalid mode, speed, look flag or CVar input raises before the driver registers or requests PIE.

The probe uses actor placement/control rotation, movement input, and the test input injector as the existing Lead driver does. It does not call `set_editor_property`, save assets, change component properties, or run PIE itself. Only Claude's external runner starts the Editor/PIE process. Attack/lunge mode is outside this batch and is specified in AQ-C06–C10.

## Validation

- Test-first red phase: `python -m unittest Scripts.Editor.test_pie_camera_engage_contract` failed because the maintained probe did not exist yet (0 tests executed; `FileNotFoundError` at probe load).
- After port/hardening: the same command passes 5/5 offline contracts.
- `python -m py_compile Scripts/Editor/pie_camera_engage.py Scripts/Editor/test_pie_camera_engage_contract.py`: pass.
- Python AST parse of the maintained probe: pass.
- `python Scripts/Tools/check_doc_links.py .`: `broken_links=0`.
- `git diff --check`: exit 0; output contains the workspace's existing LF/CRLF notices.
- No Unreal Editor, build, PIE, package, native test, asset save, commit, or push was run by Codex.

## Lead handoff

The runner should point its `py` command at the maintained script and retain the existing per-route clean-process/timeout handling. The modes, speed, look injection and B+C CVar setup have offline contracts only; run-time compatibility still requires Lead's BUILD-270/PIE pass. AQ-C06–C10 adds a real lunge-overlap mode before that run matrix is final.
