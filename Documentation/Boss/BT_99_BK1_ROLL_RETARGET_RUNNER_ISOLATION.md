# BT-99: BK-1 Greystone Pack Roll Root-Motion Retarget Runner Isolation

## 1. Executive Summary

- **Task**: `BT-99` (assigned by Codex in `[X-2629]`).
- **Implementer**: Antigravity.
- **Objective**: Isolate the BK-1 Greystone quick/full roll root-motion retarget into a narrowly scoped C-1155 authoring runner ([run_greystone_pack_rolls_rm_locked.ps1](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/run_greystone_pack_rolls_rm_locked.ps1)), avoiding the bundled layer repairs and child repointing stages of legacy `run_B_GREYSTONE_FIX_locked.ps1` and removing its agent-restricted gate.
- **Deliverables**:
  1. Dedicated, standalone C-1155 runner: [run_greystone_pack_rolls_rm_locked.ps1](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/run_greystone_pack_rolls_rm_locked.ps1).
  2. Updated [BK_01_05_GREYSTONE_PACK_ROLL_RM.md](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/BK_01_05_GREYSTONE_PACK_ROLL_RM.md) with isolated runner documentation, source hashes, and exact next actions.
  3. Comprehensive deliverable report: [BT_99_BK1_ROLL_RETARGET_RUNNER_ISOLATION.md](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/BT_99_BK1_ROLL_RETARGET_RUNNER_ISOLATION.md).
- **Execution Constraints**: Strictly source/docs only. Zero Unreal Editor launches, zero builds, zero PIE runs, zero asset or config mutations, zero git commits or pushes. Lead review identified and corrected an approval fail-open before any run.
- **Gate Status**: Gate `G-06` (Quick Roll Root Motion) remains strictly **OPEN** until an authorized C-1155 write execution and subsequent paired PIE evidence are completed.

---

## 2. Decoupling Rationale

### 2.1 Problem with Legacy `run_B_GREYSTONE_FIX_locked.ps1`
The previous C-1155 authoring path for Greystone fixes (`run_B_GREYSTONE_FIX_locked.ps1`) bundled three distinct operations together:
1. `repair_grey_layer_parents.py` (reparenting layer AnimBPs to `ABP_CombatAnimLayersBase_Grey`).
2. `retarget_greystone_pack_rolls_rm.py` (authoring isolated `_RM` sequences and montages).
3. `repoint_greystone_rolls_rm.py` (mutating child class properties to reference new montages).

Furthermore, the legacy runner enforced a rigid `[ValidateSet('Codex')][string]$Agent = 'Codex'` constraint and required a multi-stage adapter script (`greystone_fix_stage.py`). This bundled approach posed unnecessary blast radius risks and prevented executing the non-destructive asset retarget independently.

### 2.2 Narrow Scope of Isolated Runner
The new runner [run_greystone_pack_rolls_rm_locked.ps1](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/run_greystone_pack_rolls_rm_locked.ps1) executes **only** [retarget_greystone_pack_rolls_rm.py](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/retarget_greystone_pack_rolls_rm.py).
- Zero calls to `repair_grey_layer_parents.py`.
- Zero calls to `repoint_greystone_rolls_rm.py`.
- Zero child property mutations.
- Direct invocation of the driver script via `-ExecutePythonScript` without indirection adapters.
- Accepts only the enumerated agent names and checks a Codex lead-authored approval JSON against the exact requesting agent, mode, task, and hashes of the runner, driver, and wrapper C++ files. This is procedural lead approval with source-hash binding; the runner does not implement cryptographic signature verification.

---

## 3. Cryptographic Provenance & Source Hashes

| Artifact | Path | SHA-256 Hash |
|---|---|---|
| Isolated C-1155 Runner (content-input binding hotfix) | [run_greystone_pack_rolls_rm_locked.ps1](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/run_greystone_pack_rolls_rm_locked.ps1) | `B55CDBA966F0CBC54E5800E730051351AE46D43C3E0492A9B9776484E83F7D14` |
| Driver Script | [retarget_greystone_pack_rolls_rm.py](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/retarget_greystone_pack_rolls_rm.py) | `C4666C1FB0358F507348C299F2987D54CF9E101348E63E0ED136F1037AEC7741` |
| C++ Montage Wrapper Impl | [RPGMontageWrapperLibrary.cpp](file:///c:/UnrealProject/OneBossFight/Source/OneBossFightEditor/Private/RPGMontageWrapperLibrary.cpp) | `DC206360556759B26FC6CB6AA2D945C0FA8A36295B45BE4E6ACCFCF742115997` |
| C++ Montage Wrapper Header | [RPGMontageWrapperLibrary.h](file:///c:/UnrealProject/OneBossFight/Source/OneBossFightEditor/Public/RPGMontageWrapperLibrary.h) | `E4A39EB449F3C685565D9CB34706528C79CF33FE574BEDA905325A6580B4A2BA` |

---

## 4. Runner Architecture & Safety Model

### 4.1 Interface & Parameters
```powershell
param(
    [Parameter(Mandatory=$true)][string]$LeadApprovalReceipt,
    [ValidateSet('Antigravity','Codex','Claude')][string]$Agent = 'Antigravity',
    [switch]$Write
)
```
- `$LeadApprovalReceipt`: Mandatory path to lead approval JSON. It must set `task` to `BK-1 Greystone pack roll root-motion retarget`, `lead` to `Codex`, `agent` to the exact invoking agent, `approved: true`, `mode` to the invoked mode (`dry_run` or `write`), `approved_for_write` to match that mode, and `source_hashes.runner`, `.driver`, `.wrapper_cpp`, and `.wrapper_header` to the exact current SHA-256 values. `approved: true` alone never authorizes writes.
- `$Agent`: Identifies invoking agent (defaults to `Antigravity`; accepts `Codex` or `Claude`).
- `$Write`: Switch required to perform actual asset creation. Without `-Write`, the runner executes in read-only dry-run mode.

### 4.2 C-1155 Invariant Enforcement
1. **Preflight Mutual Exclusion**:
   - `Get-Process UnrealEditor*` check fails closed if any Unreal Editor instance is running.
   - Dual C-1155 lock existence check fails closed if either `ENGINE_LOCK.json` or `Docs/BossCombatReview/Execution/ENGINE_LOCK.json` is already present.
2. **Atomic Dual Locking**:
   - Creates GUID-bound lock payloads with metadata (agent, task, PID, start time, policy C-1155, driver hash, C++ hashes, lead receipt hash).
   - Uses `[System.IO.FileMode]::CreateNew` and `[System.IO.FileShare]::None` into `.tmp` before atomic move to final lock path.
   - Reads back both locks to confirm `owner_token` match before proceeding.
   - Re-verifies editor absence post-lock acquisition.
3. **Rollback & Non-Destructive Snapshotting**:
   - Pre-snapshots the 6 source roll packages (`Dodge_Small_Forward_Roll`, `Dodge_To_Idle`, and their corresponding `_Grey` sequences and montages) into `Saved/GreystonePackRollRM/Run_<timestamp>_<token>/rollback_files/`.
   - Enumerates the 6 isolated output assets under `/Game/OneBossFight/Player/Greystone/RootMotion/`.
   - Writes `rollback_manifest.json` before any editor execution.
   - After write execution, verifies that zero source package hashes were modified.
4. **Execution Protocol**:
   - Stage 1: Dry run (`01_rolls_dry`) with `-nosplash -nosound -abslog`. Expects `RESULT=PASS dry_run=1`.
   - Stage 2 (if `-Write` passed): Write run (`02_rolls_write`) with `--write`. Expects `RESULT=PASS outputs=4 saves=isolated_only`.
   - 15-minute process timeout with process handle tracking.
   - Fail-closed log inspection requiring exact expected `RESULT=` match and zero `RESULT=FAIL` occurrences.
5. **Clean Exit & Receipt Generation**:
   - `finally` block guarantees cleanup of `.tmp` files.
   - Retains locks if any Editor process remains alive.
   - Releases only locks created by this runner matching `owner_token`.
   - Emits structured `status.json` and human-readable `status.txt` recording all results, invariants (`no_build=1`, `no_pie=1`, `no_package=1`, `no_map_save=1`), and token hashes.

---

## 5. Output Asset Inventory (Isolated Scope)

When executed under `-Write`, the runner creates strictly isolated assets in a dedicated folder without touching existing assets:

| Asset Name | Target Asset Path | Description |
|---|---|---|
| `IK_Greystone_RM` | `/Game/OneBossFight/Player/Greystone/RootMotion/IK_Greystone_RM` | Isolated copy of target IK rig with ensured root chain |
| `RTG_CombatMannequin_To_Greystone_RM` | `/Game/OneBossFight/Player/Greystone/RootMotion/RTG_CombatMannequin_To_Greystone_RM` | Isolated retargeter with `Root -> Root` FK mode `GLOBALLY_SCALED` |
| `Dodge_Small_Forward_Roll_RM` | `/Game/OneBossFight/Player/Greystone/RootMotion/Sequences/quick/Dodge_Small_Forward_Roll_RM` | Retargeted quick roll animation with enabled root motion |
| `Dodge_To_Idle_RM` | `/Game/OneBossFight/Player/Greystone/RootMotion/Sequences/full/Dodge_To_Idle_RM` | Retargeted full roll animation with enabled root motion |
| `Dodge_Small_Forward_Roll_Montage_Grey_RM` | `/Game/OneBossFight/Player/Greystone/RootMotion/Montages/quick/Dodge_Small_Forward_Roll_Montage_Grey_RM` | C++ montage wrapper preserving notifies and timing |
| `Dodge_To_Idle_Montage_Grey_RM` | `/Game/OneBossFight/Player/Greystone/RootMotion/Montages/full/Dodge_To_Idle_Montage_Grey_RM` | C++ montage wrapper preserving notifies and timing |

Existing assets under `/Game/OneBossFight/GreystonePack/` and `/Game/AdvancedARPGCombat/` remain completely untouched.

---

## 6. Gate G-06 Status & Precise Next Actions

### BT-100 attempt 1 / corrective source update (2026-11-18)

Codex took over from offline Antigravity. The C-1155 dry stage passed; the write stage created only `IK_Greystone_RM` before the Python driver failed. UE 5.5.4 declares `SetIKRig` and `SetPreviewMesh` as void; Python returns `None`, so their calls now require paired getter readback instead of boolean return checks. The runner's atomic JSON update now supplies a same-directory replacement backup instead of null, so it can preserve and report the actual Editor failure. The partial `.uasset` is preserved in the attempt's `partial_outputs` directory with its hash recorded in `Documentation/TASKS.md`; no source package hash changed, Editor exited, locks released, and no build, tests, PIE, config, package, or cook ran. A fresh receipt bound to the corrected runner/driver hashes is required before the next write attempt.

### BT-100 retry accepted (2026-11-18)

The retry passed (`Saved/GreystonePackRollRM/Run_20261118_001105_65628550/status.txt`, both Editor exit codes 0, locks 2/2 released). Receipt `Saved/GreystonePackRollRM/lead_approval_BT100_Codex_retry.json` bound runner SHA256 `B55CDBA966F0CBC54E5800E730051351AE46D43C3E0492A9B9776484E83F7D14` and driver SHA256 `C4666C1FB0358F507348C299F2987D54CF9E101348E63E0ED136F1037AEC7741`. The output manifest is `Saved/GreystonePackRollRM_20261118_054212.json`; it records two root-motion sequences with nonzero displacement, ratios and preserved montage segment/notify rows. All six isolated assets were created and the ten source-package snapshot hashes match. BT-100 authoring is accepted. G-06 remains open pending paired PIE movement verification; no PIE/build/tests/package/cook occurred.

### 6.1 Gate Status
- **Gate G-06 (Quick Roll Root Motion)** remains **OPEN**.
- The authoring runner and tool are ready, isolated, and statically verified, but actual execution and root-motion displacement verification require an authorized live write run and subsequent paired PIE evidence.

### 6.2 Precise Next Actions
1. **Lead Approval Receipt**: Codex lead issued a replacement source-hash-bound write approval for Antigravity at `Saved/GreystonePackRollRM/lead_approval_BT100.json` (SHA-256 `BFF2F6423CB01D5AD9203C3EB8D2136650C64B2DB87504D30860C110A942962C`). It binds the runner, driver, wrapper C++, project, editor module, and aggregate hashes of all 10 input asset packages. It supersedes the earlier receipt, which did not bind UE input assets. Owner H-17 provides the authorization basis; this authorizes only the isolated C-1155 write described by BT-100.
2. **Authorized C-1155 Write Run**: Execute:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\Editor\run_greystone_pack_rolls_rm_locked.ps1 -LeadApprovalReceipt Saved\GreystonePackRollRM\lead_approval.json -Write
   ```
3. **Manifest & Displacement Verification**: Verify that `Saved/GreystonePackRollRM_<timestamp>.json` reports nonzero root XY displacement for both quick and full roll retargeted outputs.
4. **Paired PIE Evidence**: Conduct a dedicated visual smoke / PIE session with character roll input to record displacement in-game prior to closing gate `G-06`.
