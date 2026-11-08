# AA-A08: montage notify templates and scaled timelines

Status (C-1060/C-1061): Lead BUILD-260 passed 485/485 with owner-approved `AM_ER_Backstep_Mixamo_V2` as BackstepMontage default. C-1061 no-assignment PIE shows reps 2/3 moving; first post-R2-draw press fails 2/2 and is tracked by KI-199. C-1047 Guard Counter proof and A-633 timings remain as recorded. Other ER montage package gates are separate.

## Timeline mapping

Times are montage seconds. For sliced air clips, map `Attack_PrimaryB_Montage` through the proposed source interval by subtracting slice start and clipping intervals. Table values are millisecond-rounded targets; actual helper output and Lead asset verification remain separate evidence.

**C-1003 AttackData rule (supersedes C-992 for strong overrides):** `AttackData=StrongMeleeAttackData` is set on the `ANS_CollisionTrace_C` instances in `AM_ER_Attack_Air_Heavy_Plunge` and `AM_ER_Attack_GuardCounter`; AirLight remains unset so its ability supplies DefaultMeleeAttackData. A-607's raw T3D exports under `Saved/C1003_t3d/` show those properties inside the corresponding notify subobjects. This follows Lead's finding that pack boss health damage is determined by CollisionTrace notify data, while Codex's hit-record normalization controls table classification/posture. C-1004 Lead PIE r5 closed the post-edit two-route air-hit rerun (-16.0 / -22.4 HP as above); C-1021 later supplied owner reel approval and Source defaults. **C-994 approved blend-in:** 0.100 s on all four ER montages; leave ParryRecoil outside this rule.

| New montage / length | Template and mapping | Real notify class | Template start / duration (s) | Proposed start / duration (s) | Basis / note |
|---|---|---|---:|---:|---|
| `AM_ER_Attack_GuardCounter` / 0.800 s | `Attack_PrimaryA_Montage` / 1.6667 s, scale 0.48 | `ANS_DisableMovement_C` state | 0.000 / 1.667 | 0.000 / 0.800 | scaled |
| same | same | `ANS_SetDesiredRotation_C` state | 0.000 / 0.257 | 0.000 / 0.123 | scaled |
| same | same | `ANS_CancelFrames_C` state | 0.000 / 0.286 | 0.000 / 0.137 | scaled |
| same | same | `ANS_InputBuffer_C` state | 0.315 / 0.250 | 0.120 / 0.150 | A-633: shifted to 0.120+0.150 s |
| same | same | `ANS_CollisionTrace_C` state | 0.350 / 0.186 | 0.000 / 0.180 | A-633: moved to 0.000+0.180 s (StrongMeleeAttackData; covers 83 cm strike pass) |
| same | same | `AnimNotify_PlaySound` instant | 0.351 / — | 0.050 / — | A-633: moved to 0.050 s |
| same | same | `ANS_MovementCancel_C` state | 0.731 / 0.936 | 0.300 / 0.500 | A-633: starts at 0.300 s (>=0.300 s) through montage end |
| same | same | `FootStep` instant | 0.827 / — | 0.397 / — | scaled |
| `AM_ER_Attack_Air_Light` / 0.600 s | `Attack_PrimaryB_Montage` / 1.400 s; slice 0.200–0.800 s; subtract 0.200 | `ANS_DisableMovement_C` state | 0.000 / 1.400 | 0.000 / 0.600 | A-599 Lead readback; source slice retains reported forward strike/lunge |
| same | same | `ANS_CollisionTrace_C` state | 0.350 / 0.186 | 0.150 / 0.186 | A-607 T3D confirms AttackData unset; ability supplies DefaultMeleeAttackData |
| `AM_ER_Attack_Air_Heavy_Plunge` / 0.867 s | `Attack_PrimaryB_Montage` / 1.400 s; slice 0.200–1.067 s; subtract 0.200 | `ANS_DisableMovement_C` state | 0.000 / 1.400 | 0.000 / 0.867 | A-599 Lead readback; source slice retains reported forward strike/lunge |
| same | same | `ANS_InputBuffer_C` state | 0.350 / 0.214 | 0.150 / 0.214 | PrimaryB template; A-599 Lead readback |
| same | same | `ANS_CollisionTrace_C` state | 0.350 / 0.186 | 0.150 / 0.186 | A-607 T3D confirms StrongMeleeAttackData on notify; Lead damage PIE pending |
| `AM_ER_Backstep_Mixamo_V2` / 0.567 s | Mixamo retarget and trimmed clip; no pack-montage slice | `ANS_iFrames_C` state | — | 0.091 / 0.323 | A-640 saved montage readback; C-1059 Lead movement proof |
| same | same | `ANS_InputBuffer_C` state | — | 0.198 / 0.369 | A-640 saved montage readback |
| `AM_Boss01_ParryRecoil` / 0.600 s | `HitReact_Back_Montage` / 0.800 s; scale 0.75 | `ANS_InputBuffer_C` state | 0.000 / 0.395 | 0.000 / 0.296 | scaled; template has no hit or i-frame states |

### Deliberate omissions and constraints

- Do not add `ANS_SetDesiredRotation_C` to the V2 Backstep: A-640 reports zero yaw notifies; it keeps facing. `Dodge_Small_Forward_Roll_Montage` has no cancel-frames state; do not invent one. Its `ANS_InputBuffer_C` is the exit window. C-987's old hand-built montage values below are historical and superseded by the owner-rejected `AM_ER_Backstep_Back`.
- C-995 superseded the earlier air slices/contact windows; A-599 now supplies matching montage timing/property readback for the PrimaryB slices above. The source-motion claim is reported by Antigravity, but numeric hand_r travel-over-window evidence is not in `C995_HOTFIX_EVIDENCE.txt`. No active `ANS_MovementCancel_C` is listed on either air montage. Owner review, revised visual evidence and runtime verification remain pending.
- A-596's completion claim is superseded by C-988's Lead readback of the saved assets. Do not cite A-596 as evidence of matching montage contents. Lead's five saved-asset lines in `P_C985_ASSETCHECK/check_lines.txt` are the current evidence; a new readback is required after Antigravity's four corrections. No runtime/PIE behavior is established here.

### C-988 saved-asset readback findings — historical 1 of 5 match (C-989)

| Montage | Lead readback from saved assets | Current disposition |
|---|---|
| GuardCounter | CollisionTrace 0.168+0.089 matches; saved readback omits the table's FootStep row | C-988 says OK for this asset's hotfix criterion |
| Historical hand-built Backstep_Back (owner rejected C-1060) | C-988 readback found `ANS_SetDesiredRotation_C` 0.000+0.199 in addition to iFrames 0.075+0.268 and InputBuffer 0.164+0.187 | Superseded; current owner-approved V2 values are in the timeline above (A-640/C-1059). |
| AirLight | CollisionTrace 0.119+0.063, plus SetDesiredRotation, CancelFrames, InputBuffer and MovementCancel | Re-author to table only; hit window target 0.200+0.133 on contact frames F6–F10 |
| AirHeavyPlunge | CollisionTrace 0.296+0.127, plus SetDesiredRotation, `AnimNotifyState_Trail`, sound, InputBuffer and MovementCancel | Re-author to table only; hit window target 0.367+0.166 on contact frames F11–F16 |
| ParryRecoil | zero notifies | Add `ANS_InputBuffer_C` at 0.000+0.296; recheck |

The raw five-line output is the cited saved-asset snapshot; C-988 says Antigravity must run the read-only Lead check again and paste the new five montage lines before claiming correction complete.

### A-597 / C-992 follow-up — accepted Lead readback and live fail

**Historical snapshot as of C-995; superseded for the air-hit runtime result by C-1004:** the five-line Lead readback was accepted by C-992; C-995 accepted A-598's AttackData/blend/cancel readback; C-993 called the missing GuardCounter FootStep cosmetic. At that time post-hotfix PIE still found zero air damage and C-995 ordered new source slices. C-1004 later reports both-route air hits: AirLight -16.0 HP and AirHeavy -22.4 HP. This historical paragraph is not the current runtime status; current status is at the top of this file.

Sources: C-986 and C-987 mailbox posts; `P_C985_ASSETCHECK/check_lines.txt`; `P_C987_TEMPLATES/TEMPLATE_NOTIFIES.txt`; `ER_ANIM/Attack_Air_Light/Attack_Air_Light.txt`; `ER_ANIM/Attack_Air_Heavy_Plunge/Attack_Air_Heavy_Plunge.txt`; `Evidence/exports/PR2_Dodge_Small_Forward_Roll_Montage.t3d`; `Evidence/exports/PR5_GA_Sword_Melee.txt`.
