# Queue BD Batch 3: X11–X15 Greystone authoring gates

## X11 — asset-path presence

The repository content check found no `Content/OneBossFight/Player/Greystone` directory; `Content/OneBossFight/Player` currently contains `Animations` and `FitTest`. This is a local path-list result, not a cooked/package result. Lead-authorized authoring still remains pending; recheck before dependent readback.

## X12 — C++ wrapper refusal guards

`URPGMontageWrapperLibrary::CreateRetargetWrapper` is game-thread-only and rejects invalid inputs, paths outside the case-sensitive `/Game/OneBossFight/Player/Greystone/` prefix, invalid long package names, skeleton mismatch, source montages without slot tracks, target sequences shorter than the final notify, and destination collisions (`Source/OneBossFightEditor/Private/RPGMontageWrapperLibrary.cpp:16–56`). It duplicates the source montage, retargets segment references, rejects zero segments, marks the package dirty, and registers the created object (`:57–94`). The helper does not save the package; the Python authoring flow owns save/reload and readback.

## X13 — created-only cleanup boundary

`author_greystone_player.py` registers created asset paths only after checking the path prefix and duplicate registration (`:136–141`). Rollback iterates only registered paths in reverse, rechecks the same allowlist, and deletes those packages (`:144–170`). Top-level failure invokes rollback only in `--write` mode and only when the registry is nonempty (`:494–506`). This is a static review of the current script. It does not establish successful cleanup in Editor execution; any failed deletion is reported and remains a Lead inspection item.

## X14 — approved quick-roll route

The current SWITCH_PLAN gate specifies directional forward `IA_Move` plus a single dodge tap and explicitly excludes the owner-rejected double-tap long-roll path (C-944) (`Documentation/Boss/SWITCH_PLAN.md:125–126`). The gate compares paired child/mannequin displacement within the stated range and 10% tolerance. Do not substitute synthetic distance or infer pass from the authored montage/readback.

## X15 — CookCoverage versus package proof

`Config/DefaultGame.ini:48–49` includes `/Game/OneBossFight/Player/Greystone` in `DirectoriesToAlwaysCook` with a comment describing the C-1257 candidate. This is cook-root configuration only. With the project folder absent in the local path check, the config does not prove package presence, cook inclusion, staged dependencies, or runtime loading. Lead's SWITCH_PLAN gates require CookCoverage and staged/cooked soft-reference/startup evidence (`:135–136`).

## Scope and handoff

Read-only path/source/config review; no Editor, authoring, save/delete, cook, build, asset, lock, commit, or push operation. Supporting requirements: `Documentation/Boss/SWITCH_PLAN.md`; authoring script: `Scripts/Editor/author_greystone_player.py`. Any real asset authoring remains confined to the mailbox-approved path and Lead-run workflow.
