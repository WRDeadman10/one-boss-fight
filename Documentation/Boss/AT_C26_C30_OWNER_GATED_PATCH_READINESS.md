# AT-C26–C30: owner-gated patch readiness

**State:** offline readiness only; no camera selection or aura approval is implied.

## Camera B+C default

The existing camera component is `URPGCameraRig`; the proposed `RPGCameraSettings` class in the earlier planner did not exist in Source. The owner brief still offers B, C, or B+C and records no selection. Keep `RPGCameraRig` and `DefaultGame.ini` unchanged until the owner decision is recorded.

After a recorded choice, the proposed config shape is `Config=Game` on the camera component and two `UPROPERTY(Config)` booleans in `[/Script/OneBossFight.RPGCameraRig]`: `bDefaultHideBossInside` and `bDefaultLockOnFraming`. Missing keys default to `false/false`; this avoids string parsing and fails closed with both behaviors off. B maps to `true/false`, C to `false/true`, and B+C to `true/true`. The no-write planner prints that proposal and never authenticates an owner reference or writes files.

Implementation sequence after owner authorization:

1. Add the two config properties with C++ defaults `false`; make the component class read Game config.
2. Compute each effective feature as its selected config bit OR its Development-only test CVar. Keep CVar declarations and diagnostics under `!UE_BUILD_SHIPPING`.
3. Move only the B/C runtime behavior bodies and required state handling out of `!UE_BUILD_SHIPPING`; retain B/C off when the config choice is `None`. Keep A's collision experiment and all diagnostics Development-only.
4. Add native contracts for default `None`, exact B/C/BC parsing, invalid-value fail-closed behavior, and per-feature effective selection. Run the full native suite after owner authorization.
5. Lead verifies effective config in Development and Shipping, absence of diagnostic-only symbols in Shipping, then performs the DATA-default package smoke with a same-run activation witness. No true-legacy parity rerun is required.

Rollback: set both config properties to `false`, restore any guard movement from the reviewed patch, rebuild both configurations, and repeat the DATA-default packaged smoke. B+C remains bounded evidence only (C-1090 attack case and C-1105 look case); KI-037/KI-066 and package acceptance remain open.

## Aura candidate creation readiness

`create_phase_two_aura_boost.py` is a candidate-asset authoring script, not a runtime apply switch. It duplicates the source Niagara asset, changes fixed bounds, saves and verifies the candidate. The checked-in target path already exists in this workspace, so the script's current behavior is a readback-only no-op when the target exists. Do not run it or overwrite/delete the candidate as part of this readiness task.

The PowerShell launcher checked for an engine process and an existing lock but acquired the lock with a non-exclusive `Set-Content`, leaving a check-then-write race. The launcher now creates the lock file exclusively and removes it only after this process acquired it. This is static script hardening; no Editor, asset, or `ENGINE_LOCK.json` was touched.

Before any future authoring run, require explicit owner approval, closed Editor, no existing engine lock, and a fresh owner-approved destination path. The existing candidate's presence does not imply approval or selection.
