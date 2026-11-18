# BT-103: G-06 Roll Montage Property Readback Locked C-1155 Runner

**Task:** BT-103
**Status:** Source implementation accepted by lead; runner not executed; fresh exact-hash receipt required for any future run
**Implementer:** Antigravity
**Tech Lead:** Codex
**Date:** 2026-11-18
**Policy:** C-1155 (Read-Only Execution Boundary)
**Related Tasks:** [BT-99](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/BT_99_BK1_ROLL_RETARGET_RUNNER_ISOLATION.md), [BT-100](file:///c:/UnrealProject/OneBossFight/Documentation/TASKS.md), [BT-101](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/BT_101_GREYSTONE_ROLL_DISPLACEMENT_AUDIT.md), [BT-102](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/BT_102_G06_ROLL_MONTAGE_PROPERTY_PROBE.md)
**Runner Script:** [run_probe_g06_roll_montages_locked.ps1](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/run_probe_g06_roll_montages_locked.ps1)
**Probe Script:** [probe_g06_roll_montages.py](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/probe_g06_roll_montages.py)

---

## 1. Executive Summary & Objective

In accordance with Codex directive `[X-2644]`, task **BT-103** provides a dedicated, fail-closed, hash-bound C-1155 PowerShell runner ([run_probe_g06_roll_montages_locked.ps1](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/run_probe_g06_roll_montages_locked.ps1)) to execute the read-only inspection probe [probe_g06_roll_montages.py](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/probe_g06_roll_montages.py) inside the full Unreal Editor.

This runner establishes an immutable cryptographic envelope and strict runtime invariants ensuring that reading back the montage properties (`PlayLength`, `RateScale`, `BlendIn`, `BlendOut`, `BlendOutTriggerTime`, composite sections, slot tracks, and `FAnimSegment` bounds/play rates) and extracting root-motion displacements across the pack, `_Grey`, and candidate `_RM` quick rolls, as well as `BP_GreystoneERPlayer` defaults, produces zero asset mutations, zero config mutations, zero builds, and zero PIE executions.

This task is **strictly source and documentation only**. No Unreal Editor instance was launched, the runner was not executed, no probe was run, and no assets or configs were modified.

---

## 2. Runner Architecture & Execution Pipeline

The runner follows the exact C-1155 protocol enforced on all authoritative editor operations:

```
[Preflight Checks]
  ├── Verify UnrealEditor.exe is NOT running
  ├── Verify ENGINE_LOCK.json does NOT exist at project root or Docs/
  ├── Verify existence of project, editor binary, probe script, and editor module DLL
  ├── Require -LeadApprovalReceipt parameter
  └── Validate lead approval receipt JSON & verify exact cryptographic hash envelope
           │
           ▼
[Stage 1: Atomic Dual Locking]
  ├── Generate unique run GUID owner token
  ├── Write atomic temporary lock files with PID, owner token, UTC timestamp, and hashes
  ├── Atomically move locks to root and Docs/ paths
  └── Read back locks to guarantee owner token and policy compliance
           │
           ▼
[Stage 2: Pre-launch Snapshot & Rehash]
  ├── Snapshot all package files (including sidecars) for the 4 target packages to Saved/G06RollMontageReadback/...
  ├── Verify SHA-256 integrity of all snapshots
  └── Recompute deterministic asset hash immediately before launching editor
           │
           ▼
[Stage 3: Launch Editor Probe]
  ├── Launch UnrealEditor.exe with -ExecutePythonScript, -nosplash, -nosound, -abslog
  ├── Redirect stdout and stderr to dedicated run logs
  └── Wait with bounded 300-second timeout (fails closed if hung)
           │
           ▼
[Stage 4: Post-execution Invariant Validation]
  ├── Check 1: Zero Asset Mutations (recompute package hashes vs pre-launch snapshots)
  ├── Check 2: Parse log for exact [G06RollProbe] RESULT= line (fails on FAIL or PARTIAL, requires PASS)
  └── Check 3: Parse and validate OUTPUT_MANIFEST JSON (requires task BT-102, outcome PASS, 0 extraction errors)
           │
           ▼
[Cleanup & Receipt Generation]
  ├── Ensure owned editor PID is terminated before lock removal
  ├── Release dual locks only if clean
  └── Write atomic status.json and status.txt
```

---

## 3. Cryptographic Envelope & Lead Approval Schema

The runner strictly enforces authorization via the mandatory parameter `-LeadApprovalReceipt <path>`. The receipt must be valid JSON satisfying the following schema:

```json
{
  "task": "BT-103 G-06 roll montage property readback",
  "lead": "Codex",
  "agent": "Antigravity",
  "approved": true,
  "mode": "read_only",
  "source_hashes": {
    "runner": "479775D916340A7E277239A0F1CE50DFE15E93538D2C19A1F232314EF6A8C51D",
    "probe": "412D99A00C2D19C5800D8CBB3539DC40249004793000443AF6D5A7B478A5B190",
    "project": "B9FE452589D2E13E096DFFCD364EA4F6C541C56670F55CF5317F2BC127C35818",
    "editor_module": "EDC6CB6C81B04E1203663B5F6270C82069A49376BC0EA3E290ADAA4573192E31",
    "assets": "4CCFA3E08310B371FE4A10D052D957DD96A29743E83E742245898E1573BDB24B"
  }
}
```

### Deterministic Source Hashes Verified
- **Runner Script (`run_probe_g06_roll_montages_locked.ps1`, ordinal-sort hotfix):** `479775D916340A7E277239A0F1CE50DFE15E93538D2C19A1F232314EF6A8C51D`
- **Probe Script (`probe_g06_roll_montages.py`):** `412D99A00C2D19C5800D8CBB3539DC40249004793000443AF6D5A7B478A5B190`
- **Project File (`OneBossFight.uproject`):** `B9FE452589D2E13E096DFFCD364EA4F6C541C56670F55CF5317F2BC127C35818`
- **Editor Module (`Binaries/Win64/UnrealEditor-OneBossFightEditor.dll`):** `EDC6CB6C81B04E1203663B5F6270C82069A49376BC0EA3E290ADAA4573192E31`
- **Target Assets Combined Hash:** `4CCFA3E08310B371FE4A10D052D957DD96A29743E83E742245898E1573BDB24B`

### BT-106 deterministic-order hotfix (2026-11-18)

Lead reproduced an aggregate-hash mismatch with unchanged per-file bytes: PowerShell `Sort-Object` used culture-sensitive ordering and placed the `_Grey_RM` entry before `_Grey`, while the prior approved `4CCFA3...` envelope was generated with ordinal ordering. Updated `Compute-DeterministicAssetHash` to call `List[string].Sort(StringComparer.Ordinal)` explicitly. The current package files now deterministically hash to `4CCFA3E08310B371FE4A10D052D957DD96A29743E83E742245898E1573BDB24B` under the runner's canonical ordering. This source change modifies the runner SHA above; the previous Owner/lead source-hash envelope is stale. BT-104 remains unexecuted pending a fresh exact-hash authorization/receipt. No runner/Editor/build/test/PIE/asset operation was performed for this hotfix.

The target assets hash covers all package files for:
1. `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage`
2. `/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage_Grey`
3. `/Game/OneBossFight/Player/Greystone/RootMotion/Montages/quick/Dodge_Small_Forward_Roll_Montage_Grey_RM`
4. `/Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer`

---

## 4. Invariant Protection & Fail-Closed Guardrails

1. **Pre-flight & Post-Lock Editor Mutex:** Aborts immediately if an `UnrealEditor` process is running before lock acquisition or appears immediately after.
2. **Atomic Dual Locks & Verified JSON Replacement:** Acquires locks in both the repository root and documentation tracking directories using transactional file moves. `Write-JsonAtomic` uses a unique same-directory `.bak` backup file and verifies written JSON readback.
3. **Byte-Level Asset Immutability & Package Rehash:** Pre-launch snapshots of all package files are stored in `Saved/G06RollMontageReadback/...`. Following editor exit, every package file is hashed and compared against its pre-launch snapshot. In addition, `Compute-DeterministicAssetHash` is recomputed post-run and total package file counts are verified to guarantee zero added sidecars, modified files, or deleted assets.
4. **Strict Outcome Parsing:** The runner verifies the probe log. If the probe outputs `RESULT=FAIL` or `RESULT=PARTIAL` (e.g. if root motion extraction fails or properties are missing), the runner throws and fails closed. It requires exact `RESULT=PASS`.
5. **Output Manifest Schema & Deep Contract Validation:** Per Codex `[X-2648]` and `[X-2649]`, the generated output JSON manifest is inspected to verify that:
   - All 3 expected montages (`pack_quick`, `grey_quick`, `candidate_quick_rm`) match exact target package paths.
   - Child Blueprint (`BP_GreystoneERPlayer`) matches exact target path, timing class `RPGDodgeTiming`, non-empty `quick_montage` and `full_montage`, and positive `quick_play_rate` and `full_play_rate`.
   - Top-level montage timing (`play_length`, `sequence_length`, `rate_scale`), blend configuration (`blend_in`, `blend_out`, `blend_out_trigger_time`), and composite sections exist and are non-empty.
   - `total_segments` is recorded and is >= 3, and each montage contains non-empty tracks and segments.
   - Every `FAnimSegment` explicitly validates `anim_reference_path`, `anim_start_time`, `anim_end_time`, `anim_play_rate`, `start_pos` (non-null, no error), and `looping_count` (non-null, no error).
   - Every referenced sequence explicitly validates `path`, positive `play_length`, `enable_root_motion`, `root_motion_root_lock`, `force_root_lock`, `number_of_sampled_frames` (non-null, no error), and `raw_root_xy_displacement_cm` (non-null, no error).
   - `extraction_errors` and `property_errors` exist and are strictly empty.
6. **No Phantom Lock Releases:** In the event of process timeout or crash where an editor PID remains active, locks are retained to prevent concurrent operations from corrupting project state.

---

## 5. Execution Command Line for Future Scheduling

Once Codex issues the lead approval receipt (`receipts/BT103_lead_approval.json`), the runner can be invoked via:

```powershell
powershell -ExecutionPolicy Bypass -File c:\UnrealProject\OneBossFight\Scripts\Editor\run_probe_g06_roll_montages_locked.ps1 -LeadApprovalReceipt c:\UnrealProject\OneBossFight\receipts\BT103_lead_approval.json
```

---

## 6. Verification & Compliance Checklist

- [x] Dedicated locked runner authored: [run_probe_g06_roll_montages_locked.ps1](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/run_probe_g06_roll_montages_locked.ps1).
- [x] Syntax verified via PowerShell AST parser (`SYNTAX_OK`).
- [x] Dual locking, preflight checks, pre-launch snapshotting, and hash verification implemented.
- [x] Cryptographic receipt binding implemented with verified SHA-256 values.
- [x] Fail-closed outcome parsing (`FAIL`, `PARTIAL`, `PASS`) and manifest validation implemented.
- [x] Zero Unreal Editor launches executed during task authoring.
- [x] Zero runner executions conducted.
- [x] Zero asset or configuration modifications performed.
- [x] Zero builds, tests, or PIE runs executed.
- [x] Zero git commits or pushes executed.
