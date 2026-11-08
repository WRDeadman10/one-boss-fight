# AR-C41–C45 — camera default migration dry run

## Current state and decision boundary

`Source/OneBossFight/Player/RPGCameraRig.cpp:24–31` declares three default-off console experiments inside `#if !UE_BUILD_SHIPPING`; the behavior reads are also Development-guarded. The project has no camera production-settings class or selected camera default. `Config/DefaultGame.ini` currently contains no camera choice. The owner has made no selection.

The current decision brief C-1088 requests B, C, or B+C; its table records that A performed worse in the tested orbit and recommends dropping A. C-1051 contains an earlier A/B/C wording. This plan follows the latest C-1088 brief and accepts only B, C, or BC. If the owner reopens A or changes the menu, update the decision source and planner mapping before preparing any implementation plan. C-1090 is one bounded B+C attack-mode case on both routes; it does not establish broad acceptance, visual readability, or package behavior.

`Scripts/Tools/plan_camera_default.py` emits a JSON plan to stdout. Missing choice or missing decision reference returns `WAITING_FOR_OWNER`; a choice outside the current menu returns `INVALID_CHOICE`. A nonempty reference is only carried into the plan: the tool does not verify that a real owner decision exists or authenticate approval. Even a `READY_FOR_REVIEW` result has `apply_available=false`, `save_available=false`, and makes no filesystem changes. No Source or config apply/save code exists in this planner.

## Proposed migration after a matching owner decision

| Area | Dry-run proposal | Acceptance needed before any implementation |
|---|---|---|
| Config source | Introduce a production settings type (proposed `URPGCameraSettings`, `Config=Game`, `DefaultConfig`) and a single `SelectedBehavior` enum: `None`, `HideBossInside`, `LockOnFraming`, or `HideBossInsideAndLockOnFraming`. Put the explicit selection in `Config/DefaultGame.ini` under the proposed class section. The common default config applies to Development and Shipping; do not invent a Shipping-only override without a separate decision. | Confirm final type/section/property name against Unreal config conventions in the implementation review. Effective readback must be checked in Development and Shipping. |
| Missing/invalid setting | Treat missing, unrecognized, or `None` as all behaviors disabled. Keep each experiment's current zero/off default until the approved setting is loaded. | Native tests prove absent, invalid, and `None` settings stay off. |
| Runtime availability | Make only the owner-selected behavior callable in Shipping. Keep diagnostic logging, probes, and test-only input/CVars under `!UE_BUILD_SHIPPING`. Existing CVar experiments remain Development test controls and cannot be required for production activation. | Source contract checks the exact selected behavior/config mapping and confirms diagnostic-only APIs remain guarded. |
| Rollback | Set `SelectedBehavior=None`, rebuild/repackage both configurations, then repeat route smoke checks. Keep the experimental CVar paths for Development comparison where practical. | Staged config and behavior readback show the disabled fallback; preserve both package identities and logs. |
| Verification | Native config/source suite; Development and Shipping config readback; both routes in packaged builds; representative selected-option camera matrix; inspect stage symbols/logs for Development diagnostics. | Lead owns build, package, route runtime, and matrix execution. Owner reviews player-visible framing and aura/telegraph readability. |

The candidate config section and enum above are design proposals, not existing project APIs. Before adding a settings class, implementation must verify the engine's config behavior for the exact class/property and prove both packaged configurations load the intended value. The plan does not assert that an arbitrary console-variable entry in an ini file can activate a CVar that is compiled out of Shipping.

## Option map

| Current brief choice | Proposed `SelectedBehavior` | Existing experiment |
|---|---|---|
| B | `HideBossInside` | `rpg.Camera.HideBossInside` |
| C | `LockOnFraming` | `rpg.Camera.LockOnFraming` |
| B+C | `HideBossInsideAndLockOnFraming` | Both Development experiments enabled together |

The planner intentionally rejects A because the current C-1088 brief recommends dropping it after the tested orbit result. No behavior is selected by Codex.

## Dry-run and no-write contract

```powershell
python Scripts/Tools/plan_camera_default.py
python Scripts/Tools/plan_camera_default.py --choice invalid --owner-decision-ref TEST-ONLY
python Scripts/Tools/plan_camera_default.py --choice BC --owner-decision-ref TEST-ONLY
```

The first command returns `WAITING_FOR_OWNER`; the second returns `INVALID_CHOICE`; the third prints a proposed migration plan only. The test suite verifies no Source/config mutation, apply/save entry point, output-file argument, or authenticated-owner claim is present. The `TEST-ONLY` reference is not evidence of an owner decision.

## Checks and open gates

- `Scripts/Tools/test_camera_default_plan_contract.py` covers missing/invalid choice, missing decision reference, current option mapping, explicit non-authentication, and the no-write API boundary.
- The plan cannot close KI-037/KI-066 camera cases or prove Shipping behavior. C-1090's limited B+C result remains separate from the required broader matrix.
- Do not edit `RPGCameraRig`, add the proposed settings type, change `DefaultGame.ini`, build, package, or choose an option until an owner decision is recorded and the implementation is separately claimed/reviewed.
