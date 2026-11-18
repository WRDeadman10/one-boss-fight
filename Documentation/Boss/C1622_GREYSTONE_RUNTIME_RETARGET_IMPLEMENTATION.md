# C-1622 Greystone runtime-retarget authoring packet

## Implementation

- Added `URPGGreystoneRuntimeRetargetLibrary` to the editor-only module. It creates or updates an AnimBP at `/Game/OneBossFight/Player/Greystone/ABP_Greystone_RuntimeRetarget` for the Greystone skeleton, with exactly one `UAnimGraphNode_RetargetPoseFromMesh`, attached-parent source mode, and the allowlisted mannequin-to-Greystone IK Retargeter.
- The BP configurator works only on `BP_GreystoneERPlayer`. It copies the canonical `SKM_CombatMannequin` and `ABP_CombatCharacter` pair from the Advanced ARPG pack player's CDO into this child BP's inherited character mesh override, hides that source while keeping it ticking, and adds/updates visible `GreystoneRuntimeVisual` as a child with the new AnimBP. Collision remains disabled on the visual mesh; the existing character capsule and source gameplay setup remain authoritative.
- `author_greystone_runtime_retarget.py` is dry-run by default. Explicit `--write` saves only the two allowlisted assets, reloads templates, checks source/visible mesh and AnimBP readback, and inventories component parent/socket attachments for review. C-1628 hotfix routes this inventory/readback through an editor C++ reflection helper because UE 5.5 Python does not expose `Blueprint.simple_construction_script`. No map save or PIE.
- Added a Python stage adapter and C-1155 dual-lock runner that requires a Claude `C-1622` approval receipt, builds the Editor target first, then launches the full Editor with `-nosound` to author the assets. Runner was not executed.
- Added a static contract for source constraints, dry-run default, attachment audit, exact source/target paths, approval receipt, build-before-author order, and lock safety.

## C-1633 locked build and authoring result

- Claude's run `Saved/GreystoneRuntimeRetarget/Run_20261113_135043_f5867b5d` returned `RESULT=PASS saved=2`: `ABP_Greystone_RuntimeRetarget` and `BP_GreystoneERPlayer` were saved and read back. The inherited `CharacterMesh0` is `SKM_CombatMannequin_Simple` + `ABP_CombatCharacter`, hidden with `ALWAYS_TICK_POSE_AND_REFRESH_BONES`; visible `GreystoneRuntimeVisual` uses the runtime-retarget AnimBP. Engine locks are released.
- Lead hotfixes retained in source: runner points to the `.cpp` under `Private/`; corrected editor includes; `RowMeshPath` avoids shadowing; `AnimClass.Get()` reads the const component template; allowlist compares the package name via `GetOutermost()->GetName()`; Python bool/out handling treats false as `None` and true as output tuple; `FLogErrorOnExit` surfaces out-parameter errors; native `CharacterMesh0` CDO subobject is edited when no inherited-component key exists; canonical pack mesh/AnimBP names and tick enum readback are normalized.
- Updated static contract records the C-1633 lead-fix history and passes 8/8. Build and asset authoring passed; no PIE is claimed. Owner play-test remains pending: enable `rpg.GreystonePlayerTestPawn 1` and verify zero `GetMainAnimBP` errors, visible Greystone animation, capsule travel on rolls, and about 100 cm Mixamo backstep.

## Verification so far

- `test_c1622_greystone_runtime_retarget_contract.py`: 8/8 after C-1633.
- `test_sevarog_o1_source_contract.py`: 5/5 (C-1623 hotfix).
- Python syntax checks: pass.
- PowerShell parser: no syntax errors.
- Scoped `git diff --check`: pass.
- Local UE 5.5 source confirms the retarget editor node/factory APIs and the `UInheritableComponentHandler` template iterator. Claude's earlier C-1155 attempt built C++ but authoring stopped before writes because Python lacked the SCS property. C-1633's locked rerun then built and authored/read back both approved assets successfully.

## Known validation gate

The assets are authored and read back, but are not yet playable acceptance. The owner must run the Greystone test pawn in PIE and confirm animation, capsule root-motion travel, visibility, and combat behavior. No claim is made that this work alone makes Sevarog playable.
