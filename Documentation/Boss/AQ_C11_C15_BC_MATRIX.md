# AQ-C11–C15 — combined B+C validation matrix

## Purpose and limits

Lead has passed B (HideBossInside) and C (LockOnFraming) individually in DATA-default PIE. C-1090 supplied one B+C attack-mode PIE case in each of two nominally labelled arms; C-1099 later established that both were DATA-default. These are two DATA-default runs, not a two-route comparison. This matrix compares baseline/off, B, C, and B+C in the DATA-default acceptance scope using the maintained `Scripts/Editor/pie_camera_engage.py`. Per C-1104, legacy is a parity control only; no true-legacy camera rerun is queued to restore route wording. C-1090 supplies observations for R9–R11 only in DATA-default mode; C-1105 later supplied the separate B+C-with-look DATA-default case (BUILD-269, A4/A6, CAM_LOOK_TEST=1).

## Run matrix

Use an independent clean Editor process for each DATA-default matrix row. Each run is 30 seconds of sampled scenario time after setup. For the C input check, set `CAM_LOOK_TEST=1` to inject the pack look action for one second at scenario time 10–11 s. Use the default Move list `A4,A6` for attack rows; it calls `RPGAttackTracker.start_move` while the boss is held awake and the player is in the 80–150 cm band.

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

The following six arm/mode cells are the exact attack-mode cases from `P_C1090_ATTACKCAM/`; both nominal route arms are DATA-default per C-1099.
The runner did not set `CAM_SPEED`, so the maintained probe default 1.0 applies;
it did not inject IA_Look. All six cases completed with nine A4/A6 tracker
starts and zero refusals. Each row has two 30 s samples from the same effective
DATA-default route, not a route comparison or a package/default verdict.

| Matrix row | Route | Result |
|---|---|---|
| R9 off | nominal arm 1 (DATA-default) | 10 mesh-AABB / 9 boss-capsule inside samples; arm shorter than 300 cm: 0 |
| R9 off | nominal arm 2 (DATA-default) | 11 mesh-AABB / 10 capsule inside samples; arm shorter than 300 cm: 5 |
| R10 B | both nominal arms (DATA-default) | 4 hide entries per run, entering at 96–104 cm (Lead C-1090 report) |
| R11 B+C | both nominal arms (DATA-default) | 0 mesh-AABB and capsule intrusion samples; view-to-boss median 36–37° (Lead C-1090 report) |

R0–R8 remain pending. C-1105 filled the R11 look-injected condition; additional
repetitions and other matrix rows remain pending. The tracker
starts do not prove lunge contact or damage. No true-legacy rerun is queued;
the acceptance work is DATA-default per C-1104.

The acceptance matrix comprises 12 DATA-default PIE cases. C-1090 supplied two
DATA-default samples each for R9–R11 without look injection; C-1105 separately
filled the B+C look-injected R11 condition. For every remaining or incomplete row,
use a fresh process per case. Camera CVar values must be fully explicit.
Preserve mode, verified DATA route witness, speed, move list, look injection,
build ID, start/end, and terminal status in a per-run log and video. If any run
lacks a SUMMARY, count it as a setup/driver failure; do not treat partial rows
as a pass.

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
- Keep each DATA-default acceptance cell pending until its exact scenario, route witness, CVar readback, artifacts, and result are logged. Do not combine repeated runs into a single pass claim.


### C-1105 B+C look-injected R11 result

Claude reports Lead run `P_C1105_BCLOOK`, BUILD-269, DATA-witnessed, attack
modes A4/A6 with `CAM_LOOK_TEST=1`: 9 tracker starts, 0 intrusions, 0 hides.
With C active and B standing down, injected look moved control yaw 41°; the
view-to-boss angle was 25° before input, 123° during input, 37° at +1 s and
24° at +2–4 s. This fills the specifically requested look-injected R11 cell;
it is one bounded DATA-default observation and does not establish other
timings, terrains, packaged behavior, or a route comparison. Source: mailbox
C-1105; Lead logged the TEST_PLAN row.
