# BI-X26–X30 — Greystone Authoring and Motion Evidence Audit

**Status:** Static source, documentation, and mailbox-evidence audit. No Editor, asset, build, package, PIE, or test operation was performed.

## BI-X26 — C-1282 authored wrappers versus C-1285 root-motion repair

C-1282 reports five project-native assets saved under `/Game/OneBossFight/Player/Greystone/`: the isolated child BP and four ER montage wrappers. The four wrappers were saved/reloaded and their notify rows read back; all six `URPGDodgeTiming` fields were read back. The child remains unreferenced and the mannequin remains default. This is authored wrapper evidence, not root-motion movement acceptance.

C-1285 documents a different defect: root translation was in the pelvis while `ROOT_MOTION_FROM_MONTAGES_ONLY` extracts the root bone, yielding zero root XY and no capsule translation. Its corrective script proposes Root-to-Root chain mapping with FK `GLOBALLY_SCALED`, then four `_Fit_GreystoneRM` outputs and measured root/pelvis readback. The latest located Lead/Antigravity receipts report only `FIX_dryrun exit=0`; no live `--write`, `Saved/ERFitRM_*.json`, or paired `P_C1282_GREYSTONE_RM4_*` run is recorded. The C-1282 wrapper readback cannot be conflated with later `_RM` outputs or accepted motion.

## BI-X27 — Readback and rollback boundaries

`retarget_er_fit_candidate.py` ensures/maps a Root chain and sets target FK translation mode, but saves rig changes while preparing outputs. `fix_greystone_fit_root_motion.py` dry-run is read-only; `--write` saves the source/target rigs and retargeter before retargeting and saving new sequences. Its exception cleanup deletes outputs recorded in `CREATED`; saved rig/retargeter changes are not rolled back. The separate Greystone wrapper author defaults to dry-run, refuses existing output paths, reloads authored packages for readback, and rolls back only invocation-created registered assets. These are source-level boundaries; no failure-path run was reproduced here.

## BI-X28 — Paired root-motion capture identity

For each mannequin/Greystone pair, retain the same map/build, route, actor starting transform/origin, action and montage intent, play rate, frame rate, warm-up, camera, input timestamp, and measurement interval. Per arm record actor/generation; source clip, retarget output, target montage and hashes; serialized root-motion mode/root-lock and retarget Root-chain/FK setting; root/pelvis XY at start/end; capsule start/end transform and horizontal displacement; movement mode, root-motion extraction mode, contact/damage result, action timestamps, and warnings/errors. Preserve raw logs and manifest hashes. Do not call results from different setup identities a pair.

The switch plan's candidate gates remain 84–98 cm backstep and 215–290 cm quick roll, five trials per action and paired-arm displacement within 10%. Keep the measured mannequin baseline distinct from these candidate thresholds. A root-bone curve readback alone does not prove capsule displacement.

## BI-X29 — Default and package boundary

The authored candidate is an isolated child; C-1282 says mannequin remains default and assets are unreferenced. `author_greystone_player.py` logs `DEFAULT_PLAYER_UNCHANGED=1`. Cook roots or saved assets do not prove a Shipping package contains and starts the candidate. No default change is authorized by the reviewed records.

## BI-X30 — Disposition and open proof

| Gate | Status from checked records | Owner |
|---|---|---|
| Four C-1282 wrapper notify/property readbacks | Reported PASS for authored wrappers | Lead |
| C-1285 Root-chain live write and four `_RM` outputs | Not recorded; only dry-run receipt located | Lead |
| Paired mannequin/Greystone backstep and quick-roll trials | Pending; no RM4 receipt located | Lead |
| Child default selection | Explicitly unchanged; mannequin remains default | Owner/Lead decision required before switch |
| Identity-matched cook/Shipping package and startup smoke | Not established by authoring/readback or cook-root listing | Lead |

**Result:** BI-X26–X30 complete. Evidence distinctions and the C-1285 write rollback limitation are documented; no acceptance status was upgraded. Continue BI-X31–X35 and address explicit bounded review rejects.
