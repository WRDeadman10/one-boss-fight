# Queue BC Batch 4: X16–X20 Greystone readiness

## X16 — asset presence receipt

Read-only filesystem check on 2026-11-10: `Content/OneBossFight/Player/Greystone/` does not exist. The four retargeted fit sequences under `Content/OneBossFight/Player/FitTest/Greystone/` do exist, but none of the four wrappers or `BP_GreystoneERPlayer` exist in the new allowlist folder. This confirms the BB-X32–X35 prerequisites remain blocked. This is a workspace path check, not an Unreal asset registry readback.

## X17 — wrapper driver boundary

`Scripts/Editor/verify_greystone_wrapper_readback.py` iterates only `author.MONTAGES`; constructs each exact target from `ALLOWLIST + spec["name"]`; requires the saved package to exist; checks exact object path and `AnimMontage` class; and delegates comparison to `readback_montage`. It has no create/save/delete call. `author_greystone_player.py` also rejects target paths outside the allowlist and refuses to overwrite existing outputs before write mode. Its failure cleanup deletes only assets registered as created by that invocation and whose paths remain under the same allowlist. The readback script's unconditional editor `Quit` in `finally` is a session-control effect, but no content mutation.

## X18 — notify observability boundary

The existing comparison checks class/state/time/duration rows, ordered notify-track names, slot, skeleton, first referenced sequence, root-motion fields, and montage sections. UE Python's source helper derives sections from a textual montage helper string; event comparison through `AnimationLibrary` cross-checks event rows. It does not establish notify track membership per event, montage composite segment layout beyond the first sequence, runtime notify firing, or visual sword-contact geometry. Keep those as Editor readback/PIE acceptance boundaries rather than inferred from the offline wrapper contract.

## X19 — startup switch reset and fallback

`rpg.GreystonePlayerTestPawn` is `#if !UE_BUILD_SHIPPING`, defaults to 0, and only schedules replacement for a game-world pack player when nonzero. Replacement rechecks world, possession, loaded class and pack-player inheritance; on failure the mannequin remains. Successful replacement uses the same transform and possesses before destroying the old pawn, restoring it on possession failure. `pie_greystone_root_motion.py::finish` resets the CVar to 0 on all driver completion/error paths. This is source evidence only; no PIE outcome is claimed.

## X20 — CookCoverage/config mapping

`DefaultGame.ini` currently has explicit always-cook roots for `/Game/OneBossFight/Player/Animations` and `/Game/OneBossFight/Player/Greystone`. The native CookCoverage test scans literal `/Game/...` strings in Source files and checks each against configured directory prefixes, while intentionally excluding selected fixture/Editor-proof paths. Therefore the Greystone root covers the switch's child class literal at source-check time, but CookCoverage does not prove that packages currently exist or were included in a particular cooked/staged build. `FitTest/Greystone` is not separately rooted; its current editor authoring/readback use does not itself make it a runtime Shipping dependency. No cook/build was run.

## Outcome and limits

All five items are static source/config/filesystem audits. The child and wrappers remain absent, so the asset-level readback and route tests stay blocked for Lead. No source production changes, test additions/execution, Unreal, build, cook, PIE, packaging, or asset operation were performed. `git diff --check` reported no whitespace errors (line-ending notices only).
