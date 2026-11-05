# Queue C proof limits, authoring parity, and evidence map (S16–S20)

Read-only evidence review, with one documentation correction in KI-157. No assets, runtime code, ledger classifications, or owner decisions were changed.

## S16: W3 / neutral-strafe proof status

The R3c run is not a stuck-recovery witness: `Docs/BossCombatReview/Execution/Claude/B_STRAFE_STUCK/pie_r3c_run1/editor_raw.log` records normal strafe steps and a direction flip, but no `strafe_stuck` token. This agrees with `KNOWN_ISSUES.md` KI-149 and `OPEN_ISSUES_DIGEST.md`: neutral strafe itself is implemented and live-proven; the stuck detection/recovery branch is unit proven, live not proven. The failed R3/R3b cage attempts and their assets remain retained; the current expected sheet asks for a real `strafe_stuck flipped=1` witness. No fresh geometry or live authoring attempt is proposed.

## S17: proof-hook compile boundary

KI-157's previous phrase that the hook “fields are compiled only” for non-shipping was too broad. The behavior is shipping-guarded: `ProofGStart` and `ProofIF*` are read/armed in `RPGFrameworkBossCharacter.cpp:264–319` and `:523–537` under `#if !UE_BUILD_SHIPPING`. The members themselves are plainly declared in `RPGFrameworkBossCharacter.h:80–81`, outside a header compile guard. Updated KI-157 to distinguish the guarded behavior from the unguarded member storage. The accepted limitation is confined to a non-shipping interrupted proof session; no production gameplay path is involved.

## S18: cooldown proof-setup parity

The three profile generators set each candidate `cooldown_seconds` to `0.0` and validate the saved readback:

| Generator | Attack count | Expected sheet | Cross-check |
|---|---:|---|---|
| `make_parry_recovery_gating_profile.py` | 4 | `PARRY_RECOVERY_EXPECTED.md` | Script checks every saved candidate; expected sheet says zero cooldown permits the two-card pool under `PhasePoolCannotStarve`. |
| `make_yaw_cone_long_profile.py` | 8 | `YAW_CONE_EXPECTED.md` | Script checks every saved candidate; expected sheet says zero cooldown for the two-card pool. |
| `make_fatigue_profile.py` | 6 | `FATIGUE_EXPECTED.md` | Script checks every saved candidate; expected sheet documents zero cooldown and its gating purpose. |

This is source/readback-guard inspection only; the scripts were not executed. These three generators do not write Boolean profile fields, so the Python Boolean property-name rule is not exercised in this slice.

## S19: current owner-action inventory

| Owner action / decision | Source | Current request |
|---|---|---|
| Decide whether to apply calibrated R2 ranges to legacy proof cards. | `KNOWN_ISSUES.md` KI-145 | Existing R2 cards are proven; legacy card values remain unchanged until a choice and readback/proof plan. |
| Run the connected-session runtime overlay screenshot recipe. | `PARTIAL_UPGRADE_PLAN.md` line 12; `Claude/B_QA001/OWNER_RUN_THIS.md` | Capture the real viewport PNG; headless screenshots were black. |
| Perform the close-telegraph feel check. | `KNOWN_ISSUES.md` KI-102; `DECISIONS.md` line 575 | Current default is 0.4 s; the owner-selected setting still awaits feel confirmation. |
| Hand-test key release during synchronized riposte. | `KNOWN_ISSUES.md` KI-085 | Release sprint/guard while input is disabled and verify the action is not latched after execution. |
| Run packaged performance on target RTX 2060 Super. | `KNOWN_ISSUES.md` KI-051 and `PARTIAL_UPGRADE_PLAN.md` line 13 | Record 1080p/60 FPS p99 against 16.67 ms; editor/proxy measurements do not replace it. |

No action is inferred from a stale owner request in the historical mailbox. KI-155 is a proof-profile setup note and has no owner action; use zero cooldown and attack count 4 for the recovery gate proof.

## S20: retained proof / control / failure map

| Lane | Latest retained pass or positive evidence | Control | Retained failure / limitation |
|---|---|---|---|
| Warp ease | `Claude/B_WARP_EASE` linear/eased PIE runs and result metadata. | Linear control map/run in the same evidence folder. | No known failed final run; the room-distance limitation is recorded in BUILD-165. |
| Guard chip | `Claude/B_GUARD_CHIP` enabled run with `guard_chip` telemetry. | Same folder's zero-fraction control has no `guard_chip` line. | Initial proof setup/review caveats are preserved with the run. |
| Parry recovery | `Claude/B_PARRY_RECOVERY` A4 gate runs. | PARRY control run. | Initial starvation failures retained; C-711 established cooldown must be 0, since 0.1 is still refused. |
| Telegraph scale/restore | `Claude/B_TELEGRAPH/pie_enabled_run2_restore`. | `pie_control`. | Earlier enabled run without restore observation retained beside the later restore run. |
| Cone hysteresis / start parity | `Claude/B_YAW_CONE/pie_long_hysteresis_run2_fixed` and `Claude/B_CONE_START_FIX`. | `B_YAW_CONE/pie_control`. | `pie_long_hysteresis_run1_FAIL_MoveModel.Cone_at_start_with_slack` retained; this is the bug that prompted the Lead's runtime fix. |
| Strafe stuck recovery | No live pass yet. | R3c arena-edge run is a negative setup: normal strafe, no stuck token. | Failed R3/R3b authoring attempts and R3c no-token run remain under `Claude/B_STRAFE_STUCK`. |
| Full suite after R136–R180 | `Claude/B_CODEX_R141_180/build_raw.log` and `tests_raw.log`; BUILD-174 327/327. | Not applicable. | Prior accepted compile/test failures are retained in their earlier batch evidence folders. |
| Restart counters | `Claude/F8/ki150b/restart1..3/editor_raw.log`. | Three repeat restart runs provide repeatability. | They show cumulative result totals; no generation-local RESULT counter pass exists. |

Paths above are repository-relative. A missing “pass” is stated explicitly rather than inferred from code or compilation.
