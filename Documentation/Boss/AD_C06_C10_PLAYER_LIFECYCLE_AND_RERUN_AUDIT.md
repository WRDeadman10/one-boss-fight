# Queue AD-C06–C10 — player lifecycle and rerun audit

Date: 2026-11-07. Static source/evidence audit only. No Unreal, PIE, build, or tests run by Codex.

## AD-C06 — active player montage cleanup

| Event | Project source evidence | Finding / boundary |
|---|---|---|
| Player death | `RPGDodgeTiming::EndPlay` restores its temporary guard-counter ability-array override and clears its guard timer (`Source/OneBossFight/Player/RPGDodgeTiming.cpp:40-47`). It does not stop a player montage. The component has no death-state callback in the reviewed code. | If player death tears down the component, `EndPlay` runs; whether pack death does so, and whether a replacement pawn is possessed, is runtime/pack behavior not established here. |
| Encounter reset | `URPGSevarogDirector::ResetEncounter` calls unqualified `Montage_Stop(0.1f)` on the owner boss character mesh (`Source/OneBossFight/Boss/RPGSevarogDirector.cpp:372-403`). `URPGBossEncounter::ResetEncounter` likewise stops on its boss owner (`Source/OneBossFight/Player/RPGBossEncounter.cpp:328-402`). | Those calls identify boss meshes, not the player's mesh. The player subsystem receives reset and may rebind; no reviewed reset call explicitly stops an active player attack montage. This is a source boundary, not proof of a live failure. |
| Pawn replacement/rebind | `URPGPlayerMovesSubsystem::OnRebindPoll` waits for possession, and reset handling performs the rebind path (`RPGPlayerMovesSubsystem.cpp:368-382, 430+`). `AttachPlayerComponents` adds `URPGDodgeTiming` to eligible pack players (`:884-888`). | Tests assert component setup on respawns/replacements, including `RPGBossStartupActivationTests.cpp:629-630`; they do not run an attack montage through replacement and assert the old/new mesh state. |
| Explicit interruption | `URPGBossStagger::StartRiposteClips` can stop a player montage during the riposte flow (`RPGBossStagger.cpp:597`), with a later specific riposte-montage stop (`:745`). | This is a targeted riposte interruption path, not general player death/reset cleanup. |

No reviewed native/offline case couples active player montage playback to death, encounter reset, replacement pawn, or component teardown. Existing attach/rebind tests cover component ownership/presence; they must not be described as montage lifecycle coverage. Whether the pack independently cancels such montages remains unknown.

## AD-C07 — temporary ability-array override

`ApplyMontageArrayOverride` first restores any prior snapshot, locates `CreatedAbilities`, exports each eligible montage array before replacing it, and records the weak ability pointer/property name/serialized array (`RPGDodgeTiming.cpp:540-629`). No valid target/array restores and returns false. `RestoreGuardCounterMontageOverride` imports each still-live ability's saved array and clears snapshots (`:633-647`). Tick restoration checks whether the montage is playing and restores while it is playing or once the one-second fallback expires (`:649-678`). `EndPlay` restores regardless of teardown reason (`:40-47`).

The source covers repeated override, no-target failure, playing montage, expiry, and component teardown. No test was found that asserts an actual before/after pack ability-array value for death/reset interruption. Reset alone does not imply this player component gets `EndPlay`; the surviving-pawn case remains a Lead runtime check, not an inferred defect.

## AD-C08 — C-975 / C-978 route evidence

| Receipt | Route | What retained logs show | What it does not show |
|---|---|---|---|
| C-975 / BUILD-247 (483/483 accepted); `P_C975_AIRFIELDS/probe_*_lines.txt` and matching logs | 2026-11-07; legacy (`H019_ENCOUNTER_DEFINITION` unset) and selected data (`DA_Sevarog_G044_Encounter`) | Both routes assigned the AirLight/AirHeavy optional montages and logged those montage starts; the same run logged the grounded R1/R2 comparison. | The earlier scripts did not exercise active movement for the moving-tap case. Those observations are invalidated by C-980/KI-196; they do not establish a moving dodge. |
| C-978 / BUILD-248 (484/484, Shipping compile accepted); `P_C978_AIRRESTORE/probe_*_lines.txt` and matching logs | 2026-11-07; legacy and selected data | Both routes show AirLight and AirHeavy montage starts, then after grounded state, both ground `Attack_PrimaryA_Montage` (R1) and `Ability_E_Anim_Montage` (R2). Logged starts: legacy 79.01/182.27 ms; data 77.35/181.00 ms. | These are specific route/action observations. They do not cover player death, encounter reset during montage, pawn replacement, or all ability-array teardown paths. |

The C-978 probe waits for the airborne montage to finish and for landing before sending grounded follow-ups, checking `is_falling()` and the prior montage. These receipts support only that tested post-air restoration sequence on their recorded routes/builds.

## AD-C09 — KI-196 corrected moving-input probes (static check)

Both current drivers (`Scripts/Editor/pie_er_air_restore.py` and `pie_er_control_latency.py`) use `pawn.add_movement_input(pawn.get_actor_forward_vector(), 1.0, True)` during the moving case before the 0.30 s dodge press. At the press they log `speed_cm_s` and `get_last_movement_input_vector()` (`air_restore.py:199-229`; `control_latency.py:193-204`). Thus the source now has actual CharacterMovement input before press plus speed/vector evidence, rather than synthetic `IA_Move` injection. The retained C-975/C-978 logs predate this correction and contain no `moving_press` receipt. KI-196's corrected two-route rerun is still required; no live movement acceptance is claimed.

## AD-C10 — Lead rerun receipt template

For each test row, capture:

| Field | Required value |
|---|---|
| Build identity | Exact BUILD ID, executable/source identity, and build date; attach the gate output. |
| Route | `legacy` or selected `data`; for data include selected definition path/hash. One route per receipt row. |
| Case/action | Explicit action and lifecycle trigger; include player death, reset, replacement/rebind, and moving dodge as separate cases. |
| Actor/component identity | Old/new pawn IDs, possession/rebind timestamps or generation, `RPGDodgeTiming` presence, and mesh/AnimInstance identity. |
| Montage evidence | Name, active state and position immediately before trigger and after cleanup/rebind; note input context and relevant ability-array snapshot/restore. |
| Moving input | At dodge press: speed in cm/s and last movement-input vector, plus proof the per-tick movement ran before the press. |
| Raw evidence | Unedited log path/hash, exact relevant log lines, driver/script revision, and route selector state. |
| Verdict | PASS / FAIL / INCONCLUSIVE with criterion and observed value; distinguish source/static result from live result. |
| Invalidation | Mark prior C-975 moving taps invalid under C-980/KI-196; identify missing route, stale build, absent movement vector/speed, or missing actor/montage evidence. |

This receipt template is preparation only. Lead owns the build and PIE reruns. Current conclusion: C-978 closes post-air ground R1/R2 restoration on both tested routes; KI-196 moving-dodge reruns and player active-montage death/reset/rebind checks remain open.
