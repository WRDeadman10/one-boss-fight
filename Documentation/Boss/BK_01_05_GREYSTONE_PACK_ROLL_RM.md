# BK-01–05 — Greystone pack roll root-motion retarget

## Source-derived inventory

The current Greystone player readback and `C1259_GREYSTONE_SOURCE_INVENTORY.md` identify exactly two pack roll montage/sequence pairs used by `URPGDodgeTiming`:

| Route | Mannequin source sequence | Current Greystone sequence | Current Greystone montage | Consumer |
|---|---|---|---|---|
| Quick roll | `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll` | `/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Grey` | `/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage_Grey` | `URPGDodgeTiming.QuickMontage`, `GA_Player_Dodge.DodgeMontage` quick entry |
| Full/recovery | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle` | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Grey` | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Montage_Grey` | `URPGDodgeTiming.FullMontage`, `GA_Player_Dodge.DodgeMontage` full entry |

The current child readback names the two `_Grey` montages. The exported `GA_Player_Dodge` CDO snapshot only exposes the full/recovery map entry; the quick route is confirmed by the live child readback and `URPGDodgeTiming` substitution path. C1259 separately inventories weapon ability montage arrays for attacks, guard, flask, hit, death, equip and sheath; those are not consumers of these two roll sequences and are excluded from this roll-only selection. No broader weapon array is retargeted.

## Tool and safety behavior

`Scripts/Editor/retarget_greystone_pack_rolls_rm.py` is read-only by default. `--write` is required for changes. It:

- accepts only the two inventory rows above;
- refuses if any output asset path already exists;
- uses a duplicated target IK rig and a new retargeter with the `Root -> Root` FK mode `GLOBALLY_SCALED`;
- writes new `_RM` sequences and montage wrappers under `/Game/OneBossFight/Player/Greystone/RootMotion/`;
- creates montage copies through `URPGMontageWrapperLibrary`, preserving montage structure/notifies and replacing the copied segment references;
- proves each source/output root XY displacement and ratio, requires root motion enabled and a nonzero output displacement, and writes a JSON manifest in `Saved/`;
- never edits the existing `_Grey` sequences/montages, pack assets, child properties, or deletes assets. If a write fails partway, it reports partial outputs for inspection and does not automatically delete them.

## Verification and remaining gate

### BT-100 attempt 1 and source hotfix (2026-11-18)

Codex took over BT-100 after Antigravity was reported offline. The C-1155 dry-run passed, but write stopped after creating only the isolated target IK rig. In UE 5.5.4, `IKRetargeterController.set_ik_rig` and `set_preview_mesh` are void UFUNCTIONs; the Python driver incorrectly required truthy return values and reported `could not assign source rig`. The runner then masked that result while writing `step_results.json`, because `File.Replace` received a null backup path. The newly created IK rig package was moved intact to `Saved/GreystonePackRollRM/Run_20261118_000530_178d74bf/partial_outputs/` (SHA256 `915448F492245BD4F9183E6749EE7942B1483DD301FA16133FF207E85FEB9C2B`); no existing asset was overwritten or deleted. All 10 source package hashes matched their snapshots; Editor exited and both locks were released. The driver now checks setter state through the paired getters, and the runner uses a valid same-directory replacement backup. These source changes require a fresh hash-bound C-1155 receipt before retry. G-06 remains open.

### BT-100 authoring retry accepted (2026-11-18)

Fresh Codex-bound C-1155 retry `Saved/GreystonePackRollRM/Run_20261118_001105_65628550` passed both dry and write stages. UE getter readback completed; manifest `Saved/GreystonePackRollRM_20261118_054212.json` reports `Root -> Root`, `GLOBALLY_SCALED`, root motion enabled, quick displacement 501.917 cm (1.15346x source), full displacement 589.084 cm (1.15346x source), and montage notify/segment rows retained. All six isolated `_RM` assets exist. All 10 source package snapshots match, the Editor exited, and both locks were released. BT-100 authoring is accepted; G-06 remains open for a paired PIE movement check and any owner visual inspection. No build, tests, PIE, package or cook ran.

Offline contract: `python Scripts/Tools/test_bk1_greystone_roll_rm_contract.py` — **5/5 passed**. Python compilation passed for the new Editor tool and contract.

No Unreal Editor execution, asset creation, save, build, PIE, or root-motion measurement was performed in this batch because Claude owns the engine for X26. Therefore BK-01 inventory and BK-05 offline contract are complete; BK-02–04 tool source is authored but awaiting Lead's editor window and asset readback. The existing `_Grey` montage routes remain untouched, and the player default remains the mannequin pending the separate gate/owner switch.

## BT-99 Isolated C-1155 Runner Implementation

To decouple the BK-1 roll root-motion retarget from the legacy bundled runner `run_B_GREYSTONE_FIX_locked.ps1` (which coupled layer repair, roll retarget, and child repoint under a Codex-only runner parameter), BT-99 implemented a dedicated, narrowly scoped C-1155 runner:

- **Runner Script (content-input binding hotfix)**: [run_greystone_pack_rolls_rm_locked.ps1](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/run_greystone_pack_rolls_rm_locked.ps1) (SHA256: `AEBD774A098333CE22A6A504A4D719B95F76ED4E2FE89DDF062884E8729C7C16`)
- **Driver Script**: [retarget_greystone_pack_rolls_rm.py](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/retarget_greystone_pack_rolls_rm.py) (SHA256: `F77449810BA557E601E2A9E16D8AE087439847A713398F1E45EEA4B31B50C876`)
- **Wrapper C++ Library**:
  - [RPGMontageWrapperLibrary.cpp](file:///c:/UnrealProject/OneBossFight/Source/OneBossFightEditor/Private/RPGMontageWrapperLibrary.cpp) (SHA256: `DC206360556759B26FC6CB6AA2D945C0FA8A36295B45BE4E6ACCFCF742115997`)
  - [RPGMontageWrapperLibrary.h](file:///c:/UnrealProject/OneBossFight/Source/OneBossFightEditor/Public/RPGMontageWrapperLibrary.h) (SHA256: `E4A39EB449F3C685565D9CB34706528C79CF33FE574BEDA905325A6580B4A2BA`)

### Runner Safety Contracts & Invariants

1. **Strict Stage Isolation**: Executes ONLY `retarget_greystone_pack_rolls_rm.py`. Zero invocation of `repair_grey_layer_parents.py` or `repoint_greystone_rolls_rm.py`.
2. **Agent and Approval Binding**: Restricts agent to `Antigravity`, `Codex`, or `Claude`; requires Codex lead approval to bind the exact task, agent, mode, explicit `approved_for_write`, and SHA-256 hashes of runner, driver, wrapper C++, project, editor module DLL, and every input UE asset package. This is procedural lead approval with source-hash binding; the runner does not implement cryptographic signature verification. `approved: true` alone never authorizes a write.
3. **Atomic Dual Locking**: Acquires and verifies both `ENGINE_LOCK.json` roots (`ENGINE_LOCK.json` and `Docs/BossCombatReview/Execution/ENGINE_LOCK.json`) with GUID-bound `owner_token`.
4. **Editor Preflight & Postflight Fences**: Aborts preflight if UnrealEditor is active; rechecks source and approval hashes immediately before each Editor invocation; retains locks if any Editor process remains alive post-execution.
5. **Non-Destructive Invariant**: Operates in dry-run mode by default (`RESULT=PASS dry_run=1 saves=0`); write execution requires explicit `-Write` switch and exact approval envelope authorization (`RESULT=PASS outputs=4 saves=isolated_only`). Pre-snapshots all source package files and verifies post-write that zero source assets were mutated.
6. **Isolated Destination**: Outputs only to `/Game/OneBossFight/Player/Greystone/RootMotion/`. Existing `_Grey` sequences/montages, pack assets, and child properties remain untouched.
7. **Default Pawn Invariant**: Player default remains the mannequin per C-1257.

**Lead review hotfixes (BT-99):** Initial review found `approved: true` could bypass explicit write authorization and source-hash checks. Codex hardened the runner to check current code/project/module/input-asset hashes, exact agent/mode/task binding, complete lock provenance readback, and all 10 input package snapshots before the Editor stage. A second review closed the gap where UE asset inputs were not bound to the approval. Receipts and locks record the relevant hashes. The replacement runner has not been executed.

## Precise Next Actions for Gate G-06

1. **Lead Approval Envelope**: Codex issued replacement JSON approval at `Saved/GreystonePackRollRM/lead_approval_BT100.json` (SHA-256 `BFF2F6423CB01D5AD9203C3EB8D2136650C64B2DB87504D30860C110A942962C`), bound to current code, project, editor module, all 10 input asset packages, `Antigravity`, and write mode under Owner H-17's authorization. The earlier receipt is superseded. BT-100 is active for the isolated authoring run; no assets have been written yet.
2. **Authorized Live C-1155 Execution**: Execute `run_greystone_pack_rolls_rm_locked.ps1 -LeadApprovalReceipt <path> -Write` in full Unreal Editor window to generate isolated root-motion roll assets.
3. **Readback & Root Motion Measurement**: Inspect generated manifest `Saved/GreystonePackRollRM_<timestamp>.json` and confirm nonzero XY displacement ratio on both quick and full rolls.
4. **Subsequent Paired PIE Verification**: Execute dedicated visual smoke / PIE roll test to confirm character roll displacement in-game prior to closing gate G-06.
