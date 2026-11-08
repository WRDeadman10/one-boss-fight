# Queue AP-C31–C35 — camera option independence matrix

**State:** offline matrix and passive-probe telemetry complete; every runtime cell is pending.

## Three route columns

This plan separates the two existing PIE encounter modes from package coverage:

1. **Legacy PIE:** default legacy encounter path.
2. **Data PIE:** `DA_Sevarog_G044_Encounter` selected before PIE.
3. **Development package:** built Development package and its matching runtime scenario. The existing probe is Editor-only and no package camera driver exists yet, so all package cells are explicitly blocked pending a Lead-approved driver; do not count PIE as package proof.

Each row is a complete three-switch state. On every route, set the three Cvars in a fresh process/run identity, record their readback, follow the same circle/close/attack/dodge/aura/wall/floor scenario, then verify cleanup before the next state. Runs on different routes/builds are not paired unless the manifests identify the corresponding build/source and scenario. CVar order is `BossBlocks / HideBossInside / LockOnFraming`.

HideBossInside's 5 cm capsule-growth enter margin, 10 cm exit margin and 0.35 s minimum hide duration, plus LockOnFraming's 0.35 s manual-input grace and error-proportional ControlRotation yaw rate (`clamp(abs(error) * 6, 60, 360)` deg/s), are provisional Source values, not owner-approved choices; inspect their visual/feel result in the corresponding states.

| State | CVar values | Legacy PIE | Data PIE | Development package |
|---|---|---|---|---|
| S0 | `0 / 0 / 0` | Orbit partial: 0 inside; arm min 320 cm | Orbit partial: 0 inside; arm min 320 cm | Blocked: driver missing |
| S1 | `1 / 0 / 0` | Orbit partial: 30/252 inside; arm 10–108 cm; worse | Orbit partial: 28/251 inside; arm 10–108 cm; worse | Blocked: driver missing |
| S2 | `0 / 1 / 0` | Orbit partial: 0 inside; arm min 320 cm; option did not trigger | Orbit partial: 0 inside; arm min 320 cm; option did not trigger | Blocked: driver missing |
| S3 | `0 / 0 / 1` | Pending | Pending | Blocked: driver missing |
| S4 | `1 / 1 / 0` | Pending | Pending | Blocked: driver missing |
| S5 | `1 / 0 / 1` | Pending | Pending | Blocked: driver missing |
| S6 | `0 / 1 / 1` | Pending | Pending | Blocked: driver missing |
| S7 | `1 / 1 / 1` | Pending | Pending | Blocked: driver missing |

S0 must match the today's-behavior baseline. Single-switch states S1–S3 establish each option on its own. Mixed states S4–S7 check independent interaction without asserting that simultaneous options are desirable or owner-selected. Compare the relevant per-option observations in mixed states against the equivalent single-switch runs; retain failures and stop only the affected cell. Run S0 first, then S1–S3, then S4–S7 on each route so isolated behavior is established before combinations. Start each state with a clean PIE/process and an explicit CVar command for every switch; after capture, set all switches to zero, verify readback, then end PIE before the next fresh run. Keep the state manifest separate for every route/run identity. C-1081 fills only the 30-second awake-boss orbit segment for S0–S2; S1 is a regression in that segment, S2 is unproven because the hide switch did not trigger, and attack/lunge plus the remaining states are still pending. C-1082 prioritizes fresh off/B/C both-route probes after BUILD-267, with an attack/lunge overlap for B; S4–S7 mixed-state runs are lower priority and should be used for cleanup safety or if the owner chooses multiple options.

## Passive probe fields and evidence

`Scripts/Editor/probe_camera_inside_boss.py` remains passive: it reads each `rpg.Camera.*` integer once per sample using `SystemLibrary.get_console_variable_int_value`, logs `OPTIONS` with sanitized `CAMERA_PROBE_SCENARIO`, and never sets those switches. Its existing `SAMPLE` still records camera/pivot, arm target/actual, approximate sweep hit, camera-in-mesh AABB, capsule response and unreadable bounds. The approximate sweep field is not a collision proof. The Lead manually sets Cvars and drives the scene; keep logs, build/source identity, route, scenario label, cvar command sequence, video/frames and cleanup evidence together per cell.

## Offline evidence and limitations

`Scripts/Editor/test_camera_options_independence.py` enumerates all eight unique states and checks distinct default-off Development Cvars, separate per-tick apply paths, EndPlay cleanup, and passive readback for each option. `test_probe_camera_inside_boss.py` uses a mocked `SystemLibrary` to verify read-only values and marker/scenario structure. Runtime results for all 24 route/state cells remain pending; the eight Development-package cells need a separate executable driver before they can be claimed.
