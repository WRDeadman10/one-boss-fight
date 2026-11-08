# AQ-C11–C15 — combined B+C validation matrix

## Purpose and limits

Lead has passed B (HideBossInside) and C (LockOnFraming) individually. C-1090 has since supplied one B+C attack-mode PIE case on both routes; those measured rows are filled below. This matrix compares baseline/off, B, C, and B+C on both routes using the maintained `Scripts/Editor/pie_camera_engage.py`. It is not a general acceptance claim: only the exact C-1090 cases are complete; all other cells remain pending.

## Run matrix

Use independent clean Editor processes for every row and route. Each run is 30 seconds of sampled scenario time after setup. For the C input check, set `CAM_LOOK_TEST=1` to inject the pack look action for one second at scenario time 10–11 s. Use the default Move list `A4,A6` for attack rows; it calls `RPGAttackTracker.start_move` while the boss is held awake and the player is in the 80–150 cm band.

| Case | `CAM_MODE` | Camera CVars (all others 0) | `CAM_SPEED` | Additional inputs | Primary comparison |
|---|---|---|---:|---|---|
| R0 | `retreat` | all off | 1.0 | existing repeated 70 cm retreat setup | baseline intrusion/hide count |
| R1 | `retreat` | HideBossInside=1 | 1.0 | same as R0 | B hide count, distance, duration, false triggers |
| R2 | `orbit` | all off | 0.35 | no look injection | walking baseline view-to-boss |
| R3 | `orbit` | LockOnFraming=1 | 0.35 | look injection | C walk framing and grace/reacquisition |
| R4 | `orbit` | all off | 1.0 | no look injection | sprint baseline view-to-boss |
| R5 | `orbit` | LockOnFraming=1 | 1.0 | look injection | C sprint framing and grace/reacquisition |
| R6 | `attack` | all off | 0.35 | `CAM_ATTACK_MOVES=A4,A6` | attack overlap baseline |
| R7 | `attack` | HideBossInside=1 | 0.35 | `CAM_ATTACK_MOVES=A4,A6` | B during tracker-started attacks |
| R8 | `attack` | HideBossInside=1; LockOnFraming=1 | 0.35 | `CAM_ATTACK_MOVES=A4,A6`, look injection | combined B+C walking attack behavior |
| R9 | `attack` | all off | 1.0 | `CAM_ATTACK_MOVES=A4,A6` | sprint attack overlap baseline |
| R10 | `attack` | HideBossInside=1 | 1.0 | `CAM_ATTACK_MOVES=A4,A6` | B during sprint attack overlap |
| R11 | `attack` | HideBossInside=1; LockOnFraming=1 | 1.0 | `CAM_ATTACK_MOVES=A4,A6`, look injection | combined B+C sprint attack behavior |

### C-1090 completed cases

The following six rows are the exact attack-mode cases from `P_C1090_ATTACKCAM/`.
The runner did not set `CAM_SPEED`, so the maintained probe default 1.0 applies;
it did not inject IA_Look. All six cases completed with nine A4/A6 tracker
starts and zero refusals. These are one 30 s scenario per route, not repetitions
or a package/default verdict.

| Matrix row | Route | Result |
|---|---|---|
| R9 off | legacy | 10 mesh-AABB / 9 boss-capsule inside samples; arm shorter than 300 cm: 0 |
| R9 off | data | 11 mesh-AABB / 10 capsule inside samples; arm shorter than 300 cm: 5 |
| R10 B | legacy and data | 4 hide entries per run, entering at 96–104 cm (Lead C-1090 report) |
| R11 B+C | legacy and data | 0 mesh-AABB and capsule intrusion samples; view-to-boss median 36–37° (Lead C-1090 report) |

R0–R8 remain pending. R9–R11 at speed 0.35, look-injected R11, additional
repetitions, and any unrepresented attack/terrain/input cases remain pending.
The tracker starts do not prove lunge contact or damage.

The original matrix comprises 24 PIE runs. C-1090 completed R9–R11 on both
routes; the other 18 runs remain pending. For every remaining run, use a fresh
process per case and route. Camera CVar values must be fully explicit. Preserve
mode, route, speed, move list, look injection, build ID, start/end, and terminal
status in a per-run log and video. If any run lacks a SUMMARY, count it as a
setup/driver failure; do not treat partial rows as a pass.

## Measurements and acceptance fields

1. **Hide behavior:** transition enters/exits, hides per 30 s, hide duration distribution, distance to boss center at transition, any hide outside the intended close overlap, and visible mesh primitive count. For B+B+C, report each transition with the contemporaneous view-to-boss angle and tracker move/phase.
2. **Framing:** sampled view-to-boss absolute yaw median and p90, split by walking/sprinting and route. Report off and option-on using the same driver and speed. Treat camera-point-in-bounds/capsule values as geometry proxies, not rendered occlusion or visibility verdicts.
3. **Look grace:** injected action start/end, control yaw delta during the 1 s input, post-input initial angular error, and time to reacquire; confirm the probe did not drive an attack solely to force a pass.
4. **Attack overlap:** requested/accepted move IDs, tracker start count/refusals, in-band sample count/min/max, per-sample current move and phase, hides overlapping each active move, and whether the player or boss left the 80–150 cm band. A tracker start alone does not prove a hit or a lunge.
5. **Safety/readability:** video observations for boss silhouette, player silhouette, telegraph/aura, dodge and attack readability, target loss, wall/floor contact, abrupt camera changes, and cleanup/CVars reset. Record observations; do not infer unobserved cases.

The combined B+C attack-mode result is limited to these route/speed/move cases.
It does not establish other attack timings, lunge contact, aura readability,
broader terrain/input cases, or packaged behavior. Owner selection and package
validation remain separate gates.

## Fresh-process procedure

- Verify no stale Unreal process or engine lock; only Claude runs the engine.
- Start each row in a new process with `-nosound`; select route before `BeginPlay`; set all three CVars explicitly.
- Confirm driver registration, route and CVar logs; confirm boss/player components exist and encounter setup completed.
- After each run, capture `[CamEngage] SUMMARY`, camera transition logs, `LogRPGAttack` lines, process exit, and the matching short video. Store with an immutable run label/build ID and file hashes.
- Confirm PIE ended and all CVar environment variables were cleared before the next row.
- Keep all 24 cells individually PENDING until exact artifacts and results are logged. Do not combine repetitions or routes into a single pass claim.
