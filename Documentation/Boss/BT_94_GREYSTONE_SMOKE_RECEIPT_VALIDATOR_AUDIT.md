# BT-94: Independent Audit of Greystone Smoke Receipt Validator

Date: 2026-11-18 (Asia/Kolkata)
Author: Antigravity (Implementer)
Reviewer: Codex (Tech Lead)
Task ID: BT-94
Status: Complete (Ready for Review)

---

## 1. Executive Summary

Per Lead directives [X-2615] and [X-2616], this report presents an independent, source-only audit of the Greystone visual smoke receipt and log marker validator ([validate_greystone_visual_smoke_receipt.py](file:///c:/UnrealProject/OneBossFight/Scripts/Tools/validate_greystone_visual_smoke_receipt.py)) against the current driver ([pie_greystone_visual_smoke.py](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_greystone_visual_smoke.py)) and the C-1155 runner ([run_greystone_visual_smoke.ps1](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/run_greystone_visual_smoke.ps1)).

**Audit Verdict: STRICTLY FAIL-CLOSED (CLEAN)**
The validator enforces complete fail-closed verification across all 11 required dimensions. There are **zero fail-open paths** whereby an unverified, incomplete, or spoofed receipt could be marked accepted. All criteria, bindings, log markers, and real readbacks are verified with strict type, existence, and exact value checks.

Additionally, this audit identified a critical **synchronization dependency** with ongoing task `BT-95`: both the driver and the validator currently hardcode the stale AnimBP path `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/ABP_CombatCharacter.ABP_CombatCharacter_C`. The validator's constant must be updated in lockstep with the driver hotfix to avoid false rejections.

---

## 2. Dimension-by-Dimension Audit Matrix

| Dimension | Driver Emission | Runner Assertion | Validator Rule | Audit Assessment |
| :--- | :--- | :--- | :--- | :--- |
| **1. Task & Map Binding** | Emits `BT-79: Greystone opt-in PIE visual smoke driver` and `/Game/OneBossFight/Maps/L_SevarogArena` | Requires exact match on both fields or fails script execution | Checks exact string match against `EXPECTED_TASK` and `EXPECTED_MAP`. Rejects on any mismatch | **FAIL-CLOSED** (Exact match) |
| **2. Run Token Binding** | Reads from `GREYSTONE_SMOKE_RUN_TOKEN`; fails closed if empty | Passed from Lead approval receipt; asserts `$receiptData.run_token -cne $token` | For `accepted=True`, `expected_token` is mandatory; rejects if missing, empty, or mismatched | **FAIL-CLOSED** (Mandatory token) |
| **3. Four-Way Source Hashes** | Reads and embeds `runner`, `driver`, `retarget_cpp`, `moves_cpp` from environment | Computes SHA256 pre-lock and post-lock; asserts byte-for-byte equality against receipt | For `accepted=True`, `expected_hashes` is mandatory; verifies 64-char hex regex and exact match across all 4 keys | **FAIL-CLOSED** (Cryptographic binding) |
| **4. Criteria Completeness** | Evaluates all 6 criteria booleans (`exact_pawn_possessed`, `source_mesh_hidden`, `runtime_visual_visible`, `log_monitored_continuous`, `zero_get_main_anim_bp_errors`, `cvar_restored_zero`) | Asserts each of the 6 criteria `-eq $true` | Rejects non-boolean types. Requires all 6 to be `True` when `accepted=True`. Rejects contradictory state (`accepted=False` with PASS + all True) | **FAIL-CLOSED** (No partial acceptance) |
| **5. Possessed Pawn Class/Path** | Resolves PC 0 pawn; validates exact class path `/Game/OneBossFight/Player/Greystone/BP_GreystoneERPlayer.BP_GreystoneERPlayer_C` | Logs possessed pawn class from receipt | Enforces `class == "BP_GreystoneERPlayer_C"` and `path == EXPECTED_PAWN_CLASS_PATH` in both JSON observations and log marker | **FAIL-CLOSED** (Prevents mannequin pass) |
| **6. Source Mesh Verification** | Verifies `CharacterMesh0`, `bHiddenInGame=true`, canonical mannequin mesh, and `AlwaysTickPoseAndRefreshBones` | Criteria verified via boolean flag | Enforces hidden=True, tick option contains `AlwaysTickPoseAndRefreshBones`, mesh in `ALLOWED_SOURCE_MESH_PATHS`, anim class match | **FAIL-CLOSED** (Mesh & tick verified) |
| **7. Visible Mesh Verification** | Verifies `GreystoneRuntimeVisual`, `bHiddenInGame=false`, `visible=true`, exact Greystone mesh, retarget anim class, attached to `CharacterMesh0` | Criteria verified via boolean flag | Enforces hidden=False, visible=True, exact mesh path, exact anim class path, and parent=`CharacterMesh0` in JSON & log | **FAIL-CLOSED** (Attachment & paths verified) |
| **8. Continuous Log Evidence** | Monitors Editor log tail continuously; records byte count and read count; detects `GetMainAnimBP` errors | Asserts `log_monitored_continuous` and `zero_get_main_anim_bp_errors` | For `accepted=True`, non-empty `log_text` is mandatory. Validates `total_bytes_read > 0`, `read_count > 0`, and `get_main_anim_bp_errors == 0` | **FAIL-CLOSED** (Mandatory log cross-check) |
| **9. Log Marker Anti-Spoofing** | Formats structured markers with `[GreystoneVisualSmoke] ` prefix | N/A (Validated by tool) | Rejects duplicate markers, missing markers, empty payloads, tokens without `=`, and duplicate key=value attributes | **FAIL-CLOSED** (Rejects malformed/spoofed logs) |
| **10. Real CVar Readback** | Executes `rpg.GreystonePlayerTestPawn 0` AND reads back via `get_console_variable_string_value` | Asserts `$receiptData.observations.cleanup.cvar_readback_value -cne '0'` | Enforces `cleanup.cvar_restored_to_zero is True` and `cleanup.cvar_readback_value == '0'` in JSON and log marker | **FAIL-CLOSED** (True hardware/engine readback) |
| **11. Visual Art Separation** | Populates `visual_art_judgment` with status `PENDING_OWNER_INSPECTION` | Logs visual art review status | Strictly rejects any status other than `PENDING_OWNER_INSPECTION` (explicitly prevents automated promotion to passed) | **FAIL-CLOSED** (Owner-gated visual inspection) |

---

## 3. Deep-Dive Log Marker Parsing Verification

The log marker validation in `validate_log_markers()` was audited for potential evasion vectors:

1. **Duplicate Marker Rejection**:
   - `extract_single_marker` checks `len(matching) > 1` and appends an error (`"duplicate log marker detected ..."`). An attacker or bug emitting multiple conflicting markers (e.g., both PASS and FAIL) fails closed.
2. **Strict Attribute Splitting**:
   - `parse_kv_attributes` rejects empty payloads (`tokens == []`).
   - Rejects any token lacking `=` (`"=" not in tok`).
   - Rejects tokens with empty keys (`not k`).
   - Rejects duplicate keys (`k in attrs`), preventing attribute shadowing attacks (e.g., `hidden=0 hidden=1`).
3. **Exact Outcome Matching**:
   - `RESULT=` is evaluated via exact regular expression: `^ (PASS|FAIL)(?:\s+reason=(.*))?$`.
   - Prefix matches, partial words (e.g. `PASSING`), or casing variations fail regex match and reject the receipt.
4. **Non-Empty Payload Requirements**:
   - `RUN_TOKEN=`, `MAP=`, `GET_MAIN_ANIM_BP_ERRORS count=`, and `RESULT=` all explicitly reject empty values.

---

## 4. Key Finding: Stale Source AnimBP Path Synchronization (BT-95)

During this audit and corroborated by the Run 3 empirical result ([BT_83_GREYSTONE_SMOKE_RUN_3.md](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/BT_83_GREYSTONE_SMOKE_RUN_3.md)), an exact constant divergence was identified:

- **Current Validator Definition** ([validate_greystone_visual_smoke_receipt.py#L38](file:///c:/UnrealProject/OneBossFight/Scripts/Tools/validate_greystone_visual_smoke_receipt.py#L38)):
  ```python
  EXPECTED_SOURCE_ANIM_CLASS = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/ABP_CombatCharacter.ABP_CombatCharacter_C"
  ```
- **Current Driver Definition** ([pie_greystone_visual_smoke.py#L42](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_greystone_visual_smoke.py#L42)):
  ```python
  EXPECTED_SOURCE_ANIM_CLASS_PATH = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/ABP_CombatCharacter.ABP_CombatCharacter_C"
  ```
- **Actual Content Path from Run 3 Empirical Log**:
  ```
  /Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/ABP_CombatCharacter.ABP_CombatCharacter_C
  ```

### Impact & Recommendation
1. If the driver is hotfixed under `BT-95` to use the canonical path without updating the validator, `validate_greystone_visual_smoke_receipt.py` will fail closed on any valid receipt with:
   ```
   observations.source_mesh.anim_class_path mismatch: expected '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/ABP_CombatCharacter.ABP_CombatCharacter_C', got '/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/ABP_CombatCharacter.ABP_CombatCharacter_C'
   ```
2. **Recommendation**: Synchronize `validate_greystone_visual_smoke_receipt.py` line 38 to match the canonical asset path confirmed under `BT-95`. Note that modifying the validator does not invalidate the driver's SHA256, but keeps acceptance testing aligned.

---

## 5. Verification Commands Run

Strictly read-only / static checks (0 builds, 0 Unreal Editor launches, 0 PIE runs, 0 asset/config mutations, 0 git commits/pushes):

1. **Syntax Compilation**:
   ```bash
   python -m py_compile c:\UnrealProject\OneBossFight\Scripts\Tools\validate_greystone_visual_smoke_receipt.py
   # Result: Clean (exit 0)
   ```
2. **Doc Links Verification**:
   ```bash
   python c:\UnrealProject\OneBossFight\Scripts\Tools\check_doc_links.py
   # Result: broken_links=0
   ```

---

## 6. Conclusion

The receipt validator implementation is robust, comprehensive, and guarantees fail-closed behavior across all execution paths. With the synchronization of the source AnimBP path noted above under `BT-95`, the validation toolchain is ready for end-to-end receipt verification upon successful smoke test completion.
