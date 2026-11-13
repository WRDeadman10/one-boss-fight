# BQ-56..60: Queue BQ batch 12, Greystone layer parents, broken enemy montages, socket review

C (implementer), 2026-11-13. Queue: `QUEUE_BQ.md`.

**Static only.** Nothing was run in the Editor. No asset was written, and no build or commit. Contracts ran in-process: 9/9. Every asset path the scripts use was confirmed to exist on disk under `Content/`.

| Task | Result | Files |
|---|---|---|
| **BQ-56** (B8, KI-040) layer-ABP base | **new guarded repair, awaiting review.** Finding: the old `fix_grey_layers_1.py` and `fix_grey_layers_2.py` already target KI-040, but they are unsafe. They have no dry run, step 2 re-parents **every** AnimBlueprint under GreystonePack without checking its parent, and they delete the temporary copy. KI-040 is still Open and no temporary copy exists at `/Game`, so it is unknown whether they ever ran. **Recommendation: do not run them; this script replaces them.** `repair_grey_layer_parents.py` is a **dry run by default**. It reads each layer's `ParentClass` tag from the asset registry, with no load needed, and classifies it: stale (`/Game/ABP_CombatAnimLayersBase_Grey`), ok (the real base), or unknown (left alone). It works on a closed list of the 8 layer ABPs on disk; the base and `ABP_CombatCharacter_Grey` are excluded. Write needs `-GreyLayerRepairWrite`. Write steps: (1) create the temporary parent copy only if it is needed; (2) re-parent **only the stale layers**; (3) compile, and refuse to save on a compile error; (4) save, reload, and read the parent back from the registry; (5) delete the temporary copy only if this run created it and nothing references it, otherwise keep it and log the referencers | `Scripts/Editor/repair_grey_layer_parents.py` (new) |
| **BQ-57** (B11, KI-045) broken enemy montages | **read-only inventory, new.** Part A of `inventory_grey_broken_refs_and_sockets.py` lists every montage under GreystonePack with a dependency on a missing root-level `/Game/<name>` package (KI-045 expects 8). It also lists who still references `/Game/RMB_Cast_Grey1`, the keep-alive copy. **Lead disposition:** keep KI-045 as a recorded limitation; do not rebuild unused enemy montages or delete the montages/copy. If the inventory reveals a live referencer, pause that particular disposition for separate scope review rather than changing assets automatically | `Scripts/Editor/inventory_grey_broken_refs_and_sockets.py` (new) |
| **BQ-58** (B9, KI-035) socket transforms | **read-only review aid, new.** Part B of the same script dumps the sockets of `SK_CombatMannequin` and `Greystone_Skeleton` side by side (bone, location, rotation, scale) and flags sockets that are unadjusted copies, identical within 1e-3. That tells the reviewer which weapon sockets were never fitted to Greystone's larger body. The visual check per weapon (twin blades, claymore, dual swords, polearm, bow, quiver) and any socket edits stay ENG/owner | (same file) |
| **BQ-59** contracts | **new:** `test_bq56_60_greystone_repair_contracts.py`, **9/9 in-process**. Repair: all paths exist on disk; 8 layers, none of them the base or the character ABP; `classify` cases, with the stale and real checks provably disjoint; write ordering (dry-run return before any duplicate or reparent, compile before the error gate before save, reload readback, temporary copy removed only if this run created it and only after the referencer check); exactly one delete and one duplicate. Inventory: read-only; `is_root_level` and `same_transform` cases; its assets exist on disk | `Scripts/Editor/test_bq56_60_greystone_repair_contracts.py` (new) |
| **BQ-60** | this report | |

## Lead run (ENG, C-1155)

1. Run `inventory_grey_broken_refs_and_sockets.py`. Read `PART_A broken_montages`, the `KEEPALIVE` referencers, and the `PART_B unadjusted_copies` list.
2. Run `repair_grey_layer_parents.py` as a dry run. Expect the stale count to match the layers that fail to load.
3. If approved, run it with `-GreyLayerRepairWrite`. Expect `REPARENTED` and `READBACK` lines and `RESULT=PASS`. Then PIE every weapon style; this also checks KI-052 (the GetMainAnimBP log flood).

## Unverified until the Editor run

- The `ParentClass` registry tag format and the `status` property name after compiling. A dry run settles the first, and the second fails closed.
- The `sockets` and socket field names on `USkeleton` / `USkeletalMeshSocket` in UE Python.
- Whether KI-052's 457 warnings disappear after the re-parent. They may have a separate cause.

**Legacy scripts:** `Scripts/Editor/README.md` now marks `fix_grey_layers_1.py` and `fix_grey_layers_2.py` superseded; do not run them. The replacement is dry-run by default and remains C-1155-gated for any write.

## Lead source-review follow-up (X-2366)

Lead review found two fail-closed gaps in BQ-56: the tool ignored the return from `reload_packages()` before reading the Asset Registry, and could print `RESULT=PASS` if an unreferenced temporary copy failed deletion. The write path now checks package reload success, requires valid registry readback after reload, and refuses a pass if safe cleanup was attempted but failed. Contract assertions cover the reload-before-readback and cleanup failure paths. Lead also approved the non-destructive KI-045 disposition and documented the legacy scripts as superseded in the Editor README. AG independently accepted the hotfix in A-974. No Editor/asset operation was run.
