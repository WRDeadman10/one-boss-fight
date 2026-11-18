# BT-102: Read-Only G-06 Roll Montage Property Probe Implementation

## 1. Executive Summary

- **Task**: `BT-102` (assigned by Codex in `[X-2641]`, accepted as source deliverable in `[X-2650]`).
- **Status**: Source implementation accepted by lead; probe not executed; G-06 remains open.
- **Implementer**: Antigravity.
- **Objective**: Advance BT-101's identified unknowns regarding quick roll montage internal properties by implementing a dedicated, read-only Unreal Editor Python probe ([probe_g06_roll_montages.py](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/probe_g06_roll_montages.py)).
- **Deliverables**:
  1. Read-only Editor Python probe: [probe_g06_roll_montages.py](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/probe_g06_roll_montages.py) (SHA256: `412D99A00C2D19C5800D8CBB3539DC40249004793000443AF6D5A7B478A5B190`).
  2. Comprehensive deliverable report: [BT_102_G06_ROLL_MONTAGE_PROPERTY_PROBE.md](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/BT_102_G06_ROLL_MONTAGE_PROPERTY_PROBE.md).
- **Execution Constraints**: Strictly source/docs only. Zero Unreal Editor launches, zero probe executions, zero builds, zero PIE runs, zero asset or config mutations, zero git commits or pushes. Prohibited test operations avoided (contract test file removed).

---

## 2. Target Assets Inspected

The probe enumerates and inspects four specific assets:

| Asset Role | Target Package Path | Type |
|---|---|---|
| **Pack Mannequin Quick Roll** | `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage` | `AnimMontage` |
| **Greystone Pack Quick Roll** | `/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage_Grey` | `AnimMontage` |
| **Greystone Candidate Quick Roll** | `/Game/OneBossFight/Player/Greystone/RootMotion/Montages/quick/Dodge_Small_Forward_Roll_Montage_Grey_RM` | `AnimMontage` |
| **Greystone Player Child BP** | `/Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer` | `BlueprintGeneratedClass` (`RPGDodgeTiming`) |

---

## 3. Inspected Property Matrix & Fail-Closed Model

### 3.1 AnimMontage Properties
For each of the three quick roll montages:
- **Core Timing**:
  - `play_length` via `montage.get_play_length()`.
  - `sequence_length` via `get_prop("sequence_length", "SequenceLength")` (fails closed if missing).
  - `rate_scale` via `get_prop("rate_scale", "RateScale")` (fails closed if missing).
- **Blend Configuration**:
  - `blend_in`: `blend_time` and `blend_option` (fails closed if struct or properties missing).
  - `blend_out`: `blend_time` and `blend_option` (fails closed if struct or properties missing).
  - `blend_out_trigger_time` via `get_prop("blend_out_trigger_time", "BlendOutTriggerTime")` (fails closed if missing).
- **Composite Sections**:
  - Full enumeration of `composite_sections` (`section_name`, `time`).
- **Slot Tracks & FAnimSegment Structs**:
  - Traversal of `slot_anim_tracks` -> `anim_track` -> `anim_segments`.
  - For each `FAnimSegment`:
    * `anim_reference`: referenced `AnimSequence` package path.
    * `anim_start_time`: segment start time offset (fails closed if missing).
    * `anim_end_time`: segment end time offset (fails closed if missing).
    * `anim_play_rate`: playback rate multiplier for the segment (fails closed if missing).
    * `start_pos`: position in montage timeline (records exact value or `null` with explicit error; never fabricates `0.0`).
    * `looping_count`: loop count (records exact value or `null` with explicit error; never fabricates `1`).
- **Referenced Sequence Metadata**:
  - `enable_root_motion`: boolean (fails closed if missing).
  - `root_motion_root_lock`: root lock mode (fails closed if missing).
  - `force_root_lock`: boolean (fails closed if missing).
  - `number_of_sampled_frames`: frame count (records exact value or `null` with error; never fabricates `0`).
  - `raw_root_xy_displacement_cm`: extracted root XY travel via `extract_root_motion`. If extraction raises an exception, records `null` and populates `extraction_error: repr(exc)`; never records `0.0 cm` on error.

### 3.2 Child Blueprint (`BP_GreystoneERPlayer`) Component Defaults
- Traversal via `SubobjectDataSubsystem` (`k2_gather_subobject_data_for_blueprint`) with fallback to CDO `get_component_by_class(unreal.RPGDodgeTiming)`.
- Fails closed if the `RPGDodgeTiming` component cannot be located.
- Reads:
  - `QuickMontage`: assigned montage package path (fails closed if missing).
  - `QuickPlayRate`: assigned quick roll play rate (fails closed if missing).
  - `FullMontage`: assigned full roll montage package path (fails closed if missing).
  - `FullPlayRate`: assigned full roll play rate (fails closed if missing).
  - `BackstepMontage`: assigned backstep montage package path (fails closed if missing).
  - `BackstepPlayRate`: assigned backstep play rate (fails closed if missing).
- **Boundary Boundary Note**: Values represent saved Blueprint component defaults; they do not claim observation of C++ constructor defaults or runtime `ApplyClip` ability map rewrites.

---

## 4. Cryptographic Provenance & Source Hashes

| Artifact | File Path | SHA-256 Hash |
|---|---|---|
| Editor Probe Script | [probe_g06_roll_montages.py](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/probe_g06_roll_montages.py) | `412D99A00C2D19C5800D8CBB3539DC40249004793000443AF6D5A7B478A5B190` |

---

## 5. Safety Invariants & Execution Boundary

### 5.1 Safety Invariants
1. **Asset & Config Mutation Invariant**: Performs zero asset creations, zero asset saves, zero asset deletions, and zero config modifications. It writes strictly an evidence JSON file to the `Saved/` directory.
2. **Fail-Closed & Outcome Discrimination**:
   - If any of the 4 assets or required properties are missing, raises an exception and logs `[G06RollProbe] RESULT=FAIL error=...`.
   - Prevents vacuous pass: verifies `total_segments > 0` and that each of the 3 inspected montages has at least one slot track and at least one anim segment. If any montage has zero segments, logs `property_errors` and downgrades outcome to `PARTIAL`.
   - Child Blueprint Validation: Validates that `BP_GreystoneERPlayer` has valid non-empty `QuickMontage` and `FullMontage`, positive play rates (`QuickPlayRate`, `FullPlayRate`), and component class `RPGDodgeTiming`.
   - If any required `FAnimSegment` property (`StartPos`, `LoopingCount`) or sampled frame count fails reflection or returns an error, or if `extract_root_motion` fails or is unavailable on any referenced sequence, the probe records `null` and populates the respective error, sets `"outcome": "PARTIAL"`, and logs `[G06RollProbe] RESULT=PARTIAL total_errors=... extraction_errors=... property_errors=...`.
   - Only when 100% of inspected segments yield valid required property reads AND valid root-motion measurements does the probe log `[G06RollProbe] RESULT=PASS ...`.
3. **Structured Evidence**: Emits a timestamped JSON manifest to `Saved/G06RollMontageProbe_<timestamp>.json` recording all inspected properties, segment fields, property errors, extraction errors, and outcome.
4. **Clean Shutdown**: `finally` block executes `unreal.SystemLibrary.execute_console_command(None, "Quit")` to guarantee Editor termination.

### 5.2 Compliant C-1155 Locked Execution Boundary
No direct shell or Editor command is available or executed within BT-102. Under project rule `AGENTS.md`, live execution is prohibited until a dedicated, task-specific C-1155 dual-lock runner is implemented.

Implementation of that hash-bound C-1155 read-only runner is the immediate separate follow-up task (**`BT-103`**), which will enforce:
1. `Get-Process UnrealEditor*` absence check at preflight.
2. Atomic dual C-1155 locks (`ENGINE_LOCK.json` roots) with GUID-bound `owner_token`.
3. Fresh Codex lead receipt binding to runner, probe (`412D99A00C2D19C5800D8CBB3539DC40249004793000443AF6D5A7B478A5B190`), `.uproject`, editor module DLL, and all 4 inspected package sidecars.
4. Pre-launch rehash and post-execution lock release only after owned Editor exit.
