# Queue BF Batch 7 — Greystone authoring and motion gates (X31–X35)

Date: 2026-11-11  
Status: source/docs audit complete. No Editor, build, asset, package, or runtime operation was performed.

## X31 — wrapper readback and identity refusal

`Scripts/Editor/author_greystone_player.py` defaults to dry-run and requires explicit `--write` for authoring. Its exact write allowlist is `/Game/OneBossFight/Player/Greystone/`; it refuses existing output paths before construction, checks source montage and fitted sequence types/skeleton, compares root-motion settings, notify classes/tracks/times/segments, and after saving reloads wrapper/child assets for identity and property readback. The C++ wrapper must be available for write mode. This is source behavior; no current authored asset readback is asserted here.

## X32 — cleanup ownership

The montage author records created paths in `CREATED_ASSETS` only after creation, requires each recorded path to be inside the allowlist, and rollback iterates only those tracked paths. The C-1285 retarget script records retarget output paths in `CREATED` and its exception cleanup deletes only those outputs. Existing outputs are refused before authoring. The C-1285 script also saves rig/retargeter changes before generating clips, and does not roll those saved changes back; a failure may leave those settings saved. A tool failure between asset creation and registration could also leave an untracked partial output. No existing/referenced asset deletion path was found in these reviewed cleanup loops.

## X33 — root-motion diagnosis and proposed flags

`fix_greystone_fit_root_motion.py` documents the root-motion diagnosis: add/map a `root -> root` chain on both mannequin and fit rigs, map the retargeter Root chain, and set FK translation mode to `GloballyScaled` with alpha `1.0`. It then retargets four ER sources to `_Fit_GreystoneRM`, checks root/pelvis XY displacement, requires the backstep output root displacement to exceed half the source displacement, and emits a per-run manifest. The authoring wrapper separately copies `enable_root_motion` and `root_motion_root_lock` from the source sequence and refuses mismatch. These are the configured repair steps and checks; no C-1285 write/paired acceptance result is inferred from them.

## X34 — paired capture schema

For a meaningful mannequin/Greystone comparison, record both arms under the same map/build, world origin, initial actor transform, montage/action, input time, frame rate, warm-up, camera and measurement interval. Capture per arm: actor identity and generation; montage/source sequence and retarget-output identity; root and pelvis XY displacement; start/end transform and total actor displacement; movement mode and root-motion extraction settings; attack/trace contact outcome and damage; timestamps for takeoff/landing or action end; and any warning/error. Keep source/retarget settings readback separate from the observed in-PIE motion. The exact table is included in the Lead checklist below; no live pair is claimed.

## X35 — package/default-player gate

The Greystone child authoring script explicitly logs `DEFAULT_PLAYER_UNCHANGED=1`; the current reports retain the mannequin as the default. The Greystone candidate is an isolated child under the project allowlist and does not itself switch the project GameMode/default pawn. A saved wrapper, Development build, or cook-root entry alone does not establish the Shipping package route. Lead/Owner acceptance still needs an identity-bound package/cook record and explicit default-player decision before any default-route change.

## Disposition

BF-X31–X35 are complete as a static audit and documentation update. No test or engine command was run. Saved-asset readback, root-motion PIE pair, Shipping/package proof, and default-player decision remain open. Continue with BF-X36–X40.
