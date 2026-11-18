# BT-98: Reconciliation of Greystone Fit-Gate Status

Date: 2026-11-18 (Asia/Kolkata)
Author: Antigravity (Implementer)
Reviewer: Codex (Tech Lead)
Task ID: BT-98
Status: Complete (Ready for Review)

---

## 1. Executive Summary

Per Lead directive [X-2626], this report reconciles the technical and operational status of the **C-1257 / C-1268 Greystone player-fit gates** across project documentation ([TASKS.md](file:///c:/UnrealProject/OneBossFight/Documentation/TASKS.md), [TEST_PLAN.md](file:///c:/UnrealProject/OneBossFight/Documentation/TEST_PLAN.md), [PROJECT_STATE.md](file:///c:/UnrealProject/OneBossFight/Documentation/PROJECT_STATE.md), and [KNOWN_ISSUES.md](file:///c:/UnrealProject/OneBossFight/Documentation/KNOWN_ISSUES.md)) against empirical evidence through 2026-11-18.

### Core Policy Alignment:
1. **Evidence-Gated Claims**: Only milestones backed by direct, verified receipts on disk are recorded as passed/closed.
2. **Preservation of Open Gates**: Where empirical verification has not occurred, gates remain strictly open.
3. **C-1257 Intentional Mannequin Default**: The mannequin pawn remains the default player character in Shipping builds. Switching the production default to Greystone is intentionally held until all fit gates close and the Owner approves the transition.

---

## 2. Comprehensive Fit-Gate Status Matrix

| Gate ID | Description | Current Status | Supporting Evidence & Receipts | Open Deficiencies / Next Actions |
| :--- | :--- | :--- | :--- | :--- |
| **G-01: Character Asset Authoring** | Author `BP_GreystoneERPlayer` child and four `AM_ER_*` attack montage wrappers via C++ helper `URPGMontageWrapperLibrary` | **CLOSED (PASS)** | `C-1282` / `BUILD-297`; `Content/OneBossFight/Player/Greystone/` (`BP_GreystoneERPlayer.uasset`, `AM_ER_*.uasset`); `replace_write pass=True`, readback=0 | None. Assets serialized cleanly on disk. |
| **G-02: Runtime Retarget Wiring** | Author `ABP_Greystone_RuntimeRetarget` and attach `GreystoneRuntimeVisual` to `CharacterMesh0` | **CLOSED (PASS)** | `C-1622` / [author_greystone_runtime_retarget.py](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/author_greystone_runtime_retarget.py); hard references verified in uasset binaries | None. Verified in PIE visual smoke. |
| **G-03: PIE Opt-In Visual Smoke** | Automated no-save PIE smoke verifying exact possession, source mesh hiding, visible retarget mesh, continuous logging, zero `GetMainAnimBP` errors, and clean CVar readback | **CLOSED (PASS)** | `BT-83 Run 4` ([BT_83_GREYSTONE_SMOKE_RUN_4.md](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/BT_83_GREYSTONE_SMOKE_RUN_4.md)); receipt `accepted=true`, `result=PASS`, token `15380a4c48de47638c29bc7aacafe7a5` | Visual art/deformation evaluation separated (G-07). |
| **G-04: KI-052 Log Flood Resolution** | Eliminate `GetMainAnimBP` Accessed None error flood observed in earlier layer tests | **CLOSED (PASS)** | `BT-83 Run 4` receipt: `get_main_anim_bp_errors = 0` across 184,542 bytes of monitored Editor log | Runtime retarget architecture bypasses defective unarmed layer. |
| **G-05: Backstep Paired Root Motion** | Verify Greystone backstep distance within <= 10% normalized pairing against Mannequin | **CLOSED (PASS)** | `[C-1289]` Run 4 (`P_C1282_GREYSTONE_RM4_*`): Mannequin mean `83.83 cm`, Greystone mean `99.35 cm`; scaled ratio `1.15346` -> normalized `86.13 cm` (**+2.75%**, within 10% band) | None for backstep. |
| **G-06: Quick Roll Paired Root Motion** | Verify Greystone dodge roll distance within verified 248–334 cm scaled / 215–290 cm normalized band | **OPEN** | `[C-1289]` Run 4: 4/5 trials at `0.00 cm` displacement due to pelvis-baked pack sequence `Dodge_Small_Forward_Roll_Montage_Grey` | Requires re-retarget of pack roll sequences without pelvis baking (`BK-1`). |
| **G-07: Owner Visual / Aesthetic Review** | Owner video evaluation of 8 core animation states (Idle, Run, Light, Heavy, Roll, Backstep, Guard Counter, Plunge) using 0–2 rubric | **OPEN** | [C1257C_GREYSTONE_OWNER_REVIEW_CHECKLIST.md](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/C1257C_GREYSTONE_OWNER_REVIEW_CHECKLIST.md); Run 4 receipt records `visual_art_judgment.status = PENDING_OWNER_INSPECTION` | Video reel capture in `D:/FightVideo/greystone_review/` and Owner sign-off pending. |
| **G-08: Combat Trace & Parry Fidelity** | Live combat interaction and weapon trace alignment during melee exchange with Sevarog | **OPEN** | `C-1268` clip trace failed ("requires boss SkeletalMeshComponent and player CapsuleComponent"); 0 trace frames | Requires live combat trace capture during interactive duel. |
| **G-09: Packaged Cook Readiness** | Audit of package map scope, startup defaults, and transitive cook coverage for Greystone | **CLOSED (AUDIT PASS)** | `BT-97` ([BT_97_PACKAGED_STARTUP_AND_COOK_READINESS_AUDIT.md](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/BT_97_PACKAGED_STARTUP_AND_COOK_READINESS_AUDIT.md)); confirmed `L_SevarogArena` startup, cook roots, and hard imports | Actual packaged build execution remains unverified (G-10). |
| **G-10: Packaged Build Runtime Verification** | Execute packaged Development build with `-Cvar "rpg.GreystonePlayerTestPawn 1"` to verify standalone client execution | **OPEN** | No packaged build has been run or staged for Greystone runtime retargeting | Requires packaging under `Development` and running [PlayDevBuild.ps1](file:///c:/UnrealProject/OneBossFight/Scripts/PlayDevBuild.ps1). |
| **G-11: Shipping Default Pawn Switch** | Repoint GameMode default pawn or encounter definition to permanently switch Shipping builds to Greystone | **OPEN (GATED)** | [DefaultEngine.ini](file:///c:/UnrealProject/OneBossFight/Config/DefaultEngine.ini) retains `BP_AdvancedGameMode` with mannequin default; CVar switch compiled out of Shipping (`#if !UE_BUILD_SHIPPING`) | Intentionally held fail-closed per C-1257 until G-06, G-07, G-08, and G-10 pass. |

---

## 3. Discrepancy Reconciliation Across Core Documentation

### 3.1 [TASKS.md](file:///c:/UnrealProject/OneBossFight/Documentation/TASKS.md)
- **Current Text**: Outdated references stating `C-1257a` is blocked because UE 5.5 Python lacks montage track structs and saves 0 assets.
- **Reconciliation**:
  - Note that `C-1257a`'s Python struct limitation was bypassed by `C-1275a` / `C-1282` via the native C++ library `URPGMontageWrapperLibrary`, which authored `BP_GreystoneERPlayer` and all four wrappers.
  - Record `BT-83 Run 4` PASS (`accepted=true`) for the PIE visual smoke.
  - Retain `C-1257b` Quick Roll as **OPEN** (pending `BK-1`).
  - Retain `C-1257c` Owner video review as **OPEN**.

### 3.2 [TEST_PLAN.md](file:///c:/UnrealProject/OneBossFight/Documentation/TEST_PLAN.md)
- **Current Text**: Lists `C-1257a/b` Greystone switch preparation as `NOT READY` with 0 saved assets.
- **Reconciliation**:
  - Update status to show asset authoring is complete (`BP_GreystoneERPlayer.uasset` and `ABP_Greystone_RuntimeRetarget.uasset` present).
  - Add `BT-83 Run 4` receipt evidence (`Saved/GreystoneVisualSmoke/Run_20261117_221027_15380a4c/receipt.json`).
  - Reiterate that Quick Roll root-motion (G-06) and Owner visual evaluation (G-07) remain open.

### 3.3 [PROJECT_STATE.md](file:///c:/UnrealProject/OneBossFight/Documentation/PROJECT_STATE.md)
- **Current Text**: States C-1257 is in progress with C-1257a blocked on track structs and paired root-motion unrun.
- **Reconciliation**:
  - Update Greystone section: C-1282 authored the child pawn and wrappers; C-1622 wired runtime retargeting; BT-83 Run 4 verified possession and retarget visual in PIE with 0 `GetMainAnimBP` errors.
  - Clarify that in Development builds Greystone is opt-in via `rpg.GreystonePlayerTestPawn=1`, while Shipping compiles out the replacement.
  - State clearly that the production default pawn switch is gated by remaining open items (roll root motion, live combat trace, Owner review).

### 3.4 [KNOWN_ISSUES.md](file:///c:/UnrealProject/OneBossFight/Documentation/KNOWN_ISSUES.md)
- **Current Text**: `KI-052` tracks the `GetMainAnimBP` Accessed None error flood from the earlier layer-retarget route.
- **Reconciliation**:
  - Primary Table Row ([KNOWN_ISSUES.md#L120](file:///c:/UnrealProject/OneBossFight/Documentation/KNOWN_ISSUES.md#L120)): Reconciled to preserve the historical 2026-10-19 record (revert to mannequin) while appending the 2026-11-18 runtime retarget resolution: `ABP_Greystone_RuntimeRetarget` verified 0 errors across 184 KB logs in `BT-83 Run 4`.
  - Detailed Note ([KNOWN_ISSUES.md#L415](file:///c:/UnrealProject/OneBossFight/Documentation/KNOWN_ISSUES.md#L415)): Updated to clarify that while `KI-052` was a blocker on the direct layer-retarget route, it is resolved under the C-1622 runtime retarget architecture.

---

## 4. Verification

- **Static Docs Reconciliation**: 0 builds executed, 0 Unreal Editor launches, 0 PIE runs, 0 asset/config mutations, 0 git commits/pushes.
- **Doc Links Verification**:
  ```bash
  python c:\UnrealProject\OneBossFight\Scripts\Tools\check_doc_links.py
  # Result: broken_links=0
  ```
