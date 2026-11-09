# C-1172 Ember Warden visual weapon trace

## Scope

Codex's Phase 1 assignment is a per-frame PIE comparison of the visual greatsword grip/tip, the boss `hand_r` bone, and the active pack trace sockets during idle and A1/A2/A3, followed by routing the pack trace to numbered `Trace_` sockets on the visible sword. The original pack mesh/socket route remains the fallback when the visible weapon does not expose at least two valid trace sockets. Antigravity owns all mesh socket and attachment-transform authoring.

## Offline implementation state

- `RPGPackTrace::FTarget::SetTraceSource` validates the component and every requested socket, updates the pack target's reflected mesh/socket fields, and invokes `UpdateTraceLocations` to reseed its previous socket positions.
- `URPGTraceGuard` captures the original pack trace source once it is usable, chooses the visible `URPGBossLook` sword only when it exposes at least two numbered `Trace_<integer>` sockets, sorts those sockets numerically, and otherwise restores the original source. It exposes the live component/socket list for the probe and acceptance checks.
- `Scripts/Editor/pie_ember_visual_weapon_trace.py` wakes and holds the encounter, then records per-frame world positions and hand/grip/tip/trace offsets plus relative rotation for IDLE/A1/A2/A3 (`A3a` is the tracker's A3 first stage). A1/A3a use the tracker test montage hook; A2 uses the pack ability.
- Regression contracts were added test-first: initial run failed all three missing contracts; then passed 3/3. After the C-1179 AY-C12 hotfix, combined AY/C1172 focused suite passed 6/6. `py_compile` and scoped `git diff --check` passed.

## Runtime and acceptance state

## Verification and measured result

Antigravity reported the authored static mesh readback as 11/11 sockets (A-677); no asset was edited by Codex. After the AG lock was released, the Development build passed and native automation passed 494/494 under the Codex-owned C-1155 lock, including `OneBossFight.Art.Tier2Presentation.PureRules`. Logs: `Docs/BossCombatReview/Execution/Codex/C1172_EMBER_VISUAL_TRACE/build.log` and `suite.log`.

The final PIE probe exited 0 and recorded 404 per-frame rows across IDLE (24), A1 (85), A2 (130), and A3a (165). Each requested move start returned true. Runtime readback listed `grip, BladeStart, MiddleSocket, BladeEnd, Trace_0..2, Weapon Start/End, TrailStartSocket/TrailEndSocket`. The guard initially saw the hidden `Weapon Mesh` with five pack sockets, then switched to `RPGLookSword` with the three `Trace_` sockets. The visual sword was therefore the live trace source through the measured attack stages.

| Stage | Median visible `hand_r` to `grip` | Median visible `hand_r` to nearest `Trace_` socket | Median grip-to-hand relative rotation (roll, pitch, yaw) |
| --- | ---: | ---: | --- |
| IDLE | 22.45 cm | 48.67 cm | (-91.5°, -25.4°, -164.4°) |
| A1 | 22.45 cm | 48.67 cm | (142.8°, -52.0°, -147.3°) |
| A2 | 22.45 cm | 48.67 cm | (111.2°, -23.0°, -150.2°) |
| A3a | 22.45 cm | 48.67 cm | (137.0°, -144.3°, -65.4°) |

The 22.45 cm grip gap and large, stage-varying orientation differences show the visible sword grip is not aligned to the visible `CharacterMesh0` hand. The 48.67 cm figure is from `hand_r` to the nearest authored `Trace_0` point, which is 20 cm along the blade; it is descriptive, not a hit-registration verdict. `BladeEnd` and `Trace_2` share the same authored position, so their zero separation is not independent evidence. The probe does not test hit intake, fallback after deliberately removing sockets, crown placement, or rendered close-ups. AG must refine the body `HeavySwordSocket_R` transform from these measured offsets; Lead must then review the corrected grip/crown and verify hits against the visible blade. PIE log: `Docs/BossCombatReview/Execution/Codex/C1172_EMBER_VISUAL_TRACE/pie_probe_r7.log`.

At the r8 cutoff, Lead acceptance and grip correction were still open. A-681/r9 records Antigravity's later grip correction below; hit-registration and visual acceptance remain open pending Lead.

## Before/after trace-offset verification (r8)

To make the route change measurable at matching poses, r8 also logged the retained original pack sockets against the visible sword's corresponding blade landmarks, plus the active routed sockets against those same landmarks. The Development build passed and the full native automation suite passed 494/494 again; logs are `build_r8.log` and `suite_r8.log`. The windowed unattended PIE probe exited 0, all four move requests (idle, A1, A2, A3a) were entered, and 140 per-frame samples were recorded (`pie_probe_r8.log`: IDLE 7, A1 39, A2 44, A3 50).

Across every sampled stage, the original pack route's median offsets to the visible blade landmarks were `BladeStart=15.00 cm`, `MiddleSocket=37.50 cm`, and `BladeEnd=30.00 cm`. With the new route, `Trace_0→BladeStart`, `Trace_1→MiddleSocket`, and `Trace_2→BladeEnd` each measured `0.00 cm` median separation. These are socket-to-socket alignment measurements, not hit-intake evidence; the source trace is now on the visible sword. The hand-to-grip gap remains 22.45 cm, so Antigravity's `HeavySwordSocket_R` refinement is still required. Codex did not run the C-1152 parry-close acceptance or claim that hits/parries still register; Lead must run that regression and inspect the corrected sword close-up before acceptance.

## Grip correction readback (A-681 / r9)

Antigravity reports setting `HeavySwordSocket_R` relative location to `(0,0,0)` on `hand_r`. The shared r9 probe log records 392 samples (IDLE 26, A1 78, A2 123, A3a 165); all three requested moves started. Its `hand_to_grip` metric is specifically point-to-point distance between the `CharacterMesh0` `hand_r` bone socket origin and the sword's authored `grip` socket origin; it reads 0.00 cm in the sampled poses. This meets the positional target but does not show that the handle sits inside the closed fist or that blade direction follows the forearm; C-1185 assigns those judgments to Lead's close-up frames. Live trace sockets still match visible blade landmarks at 0.00 cm. Since the visible sword attachment moved, the original hidden pack-socket route now measures 118.76/228.03/433.20 cm to the current visible BladeStart/MiddleSocket/BladeEnd; these r9 values are against the corrected visual-sword transform and are not directly comparable to the r8 15.00/37.50/30.00 cm baseline. The r9 socket readback proves point alignment and routing, not blade orientation/readability or damage contact. The Lead's BUILD-278, C-1152 parry-close, and close-up acceptance remain pending; Codex has not run them. Evidence: `Docs/BossCombatReview/Execution/Codex/C1172_EMBER_VISUAL_TRACE/pie_probe_r9.log`; assignment/handoff: mailbox A-681 and C-1184/C-1185.
