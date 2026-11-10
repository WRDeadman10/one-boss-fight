# BC-A01..A02: `URPGMontageWrapperLibrary::CreateRetargetWrapper` Contract Verification

**Queue Lane:** `QUEUE_BC_AG` Tasks `BC-A01`, `BC-A02` (Antigravity)  
**Unblocked By:** `[X-1821]` (`C-1269a` READY, locked `503/503` suite PASS)  
**Sources Reviewed:**
- `Source/OneBossFightEditor/Public/RPGMontageWrapperLibrary.h:1-22`
- `Source/OneBossFightEditor/Private/RPGMontageWrapperLibrary.cpp:1-99`
- `Source/OneBossFightEditor/Private/Tests/RPGMontageWrapperLibraryTests.cpp:1-83`
- `Documentation/Boss/SWITCH_PLAN.md:108-114`
- `Docs/BossCombatReview/Execution/Codex/C1269_GREYSTONE_WRAPPER/build_status.txt`

---

## 1. Security, Allowlist & Validation Guard Matrix

| Requirement (`[C-1269]`) | Source Line (`RPGMontageWrapperLibrary.cpp`) | Error Token | Verified Behavior |
|---|---|---|---|
| **GameThread guard** | `:20-24` | `MontageWrapper.NotGameThread` | Fails closed off GameThread before touching any UObject |
| **Non-null UObjects** | `:25-29` | `MontageWrapper.RequiredObject` | Rejects invalid/null `Source`, `TargetSequence`, or `TargetSkeleton` |
| **Strict Greystone allowlist** | `:13, :30-35` | `MontageWrapper.PackagePathOutsideGreystoneAllowlist` | Enforces case-sensitive prefix `/Game/OneBossFight/Player/Greystone/` + `FPackageName::IsValidLongPackageName` |
| **Target skeleton match** | `:36-40` | `MontageWrapper.TargetSkeletonMismatch` | Requires `TargetSequence->GetSkeleton() == TargetSkeleton` |
| **Source slot presence** | `:41-45` | `MontageWrapper.SourceHasNoSlotTracks` | Refuses empty `SlotAnimTracks` |
| **Last-notify end containment** | `:46-57` | `MontageWrapper.TargetShorterThanLastNotify` | Checks `TargetSequence->GetPlayLength() + KINDA_SMALL_NUMBER >= LastNotifyEnd` over both point notifies (`GetTriggerTime()`) and states (`GetEndTriggerTime()`) |
| **No silent overwrite** | `:58-62` | `MontageWrapper.DestinationAlreadyExists` | Refuses if `FindPackage` or `DoesPackageExist` finds an existing destination |
| **Segment replacement & metadata copy** | `:70-98` | `MontageWrapper.SourceHasNoSegments` | `DuplicateObject<UAnimMontage>(Source, Package, AssetName)` copies `CompositeSections`, `Notifies`, `RateScale`, blend settings, and root-motion flags verbatim, re-binds `TargetSkeleton`, replaces every segment via `SetAnimReference(TargetSequence, false)`, recalculates length, and dirties the new package without touching source/pack assets |

---

## 2. Source-Timing Alignment (`SWITCH_PLAN.md` Check)

Per `[C-1269]` + `[X-1821]`, `SWITCH_PLAN.md:110` now records the exact source readback for Backstep (`ANS_iFrames` `0.091–0.414 s`, duration `0.323 s`; `ANS_InputBuffer` `0.198–0.567 s`, duration `0.369 s`), superseding the earlier `0.075–0.268 s` summary table. `DuplicateObject<UAnimMontage>` preserves every notify time/duration without Python manipulation.

---

## 3. Native & Offline Verification

- **Codex Locked Editor Suite (`[X-1821]`):** `OneBossFight.Editor.MontageWrapper.SyntheticCopyAndGuards` PASS (`suite.log:6235`), full suite `503/503` PASS (`DD27J=cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec`, `NO_ASSETS=1`).
- **Antigravity Offline Contract Test:** [`test_bc_a01_montage_wrapper_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bc_a01_montage_wrapper_contract.py) asserts the Editor-only module placement, exact `GreystoneRoot` allowlist, all 7 refusal error tokens, `DuplicateObject` notify/section preservation, `SWITCH_PLAN.md:110` corrected backstep `0.091–0.414 s` window, and `0` pack edits.
