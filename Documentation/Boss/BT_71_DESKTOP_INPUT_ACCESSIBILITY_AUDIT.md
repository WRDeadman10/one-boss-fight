# BT-71: Full-Mode Desktop Input Accessibility Audit & Safe Gate Disposition

**Task:** BT-71
**Status:** Diagnosed & Blocked on Desktop Input Access / Ready for Owner RDC Playtest
**Implementer:** Antigravity
**Tech Lead:** Codex
**Date:** 2026-11-18
**Policy:** C-1155 / C-1619 Route Protocol
**Related Tasks:** [BT-62](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/BT_70_FRESH_SMOKE_AFTER_BT68.md), [BT-69](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/BT_69_C1155_REFRESH_AFTER_BT68.md), [BT-71 Abort](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/BT_71_FULL_MODE_PLAYTEST_ABORT.md), [BT-72](file:///c:/UnrealProject/OneBossFight/Documentation/TASKS.md), [BT-73](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/BT_73_OWNER_RDC_PLAYTEST_CHECKLIST.md), [BT-91](file:///c:/UnrealProject/OneBossFight/Documentation/TASKS.md), [BT-92](file:///c:/UnrealProject/OneBossFight/Documentation/TASKS.md)

---

## 1. Executive Summary & Directive Context

Pursuant to Owner directive `[H-19]` and Codex delegation `[X-2652]`, Antigravity evaluated execution of **BT-71** ("Full-mode Sevarog boss-death lifecycle playtest") within Antigravity's active Windows execution session.

The objective of BT-71 is to execute the C-1619 Full-mode route under the refreshed lead approval receipt (`Saved/C1619RouteBuild/BT71_LeadApprovalRefresh_20261117_1830/route_lead_approval.json`), enter combat in `L_SevarogArena`, defeat Sevarog, and capture `[FrameworkProof] RESULT outcome=BossDefeated` to complete the boss-death lifecycle test.

Card instructions and Codex directive `[X-2652]` explicitly establish the fail-safe boundary:
> *"If desktop input is unavailable, do not leave Editor/locks/config altered: stop safely, verify cleanup, record evidence and return blocker for Owner RDC play."*

---

## 2. Empirical Desktop Input Subsystem Diagnostics

Before invoking the Full-mode runner or launching Unreal Editor, Antigravity conducted preflight Win32 API diagnostics on the active execution environment:

1. **`OpenInputDesktop` Probing**:
   - Call: `user32.OpenInputDesktop(0, False, 0x01FF)`
   - Returned Handle: `0` (NULL)
   - `GetLastError()`: `5` (`ERROR_ACCESS_DENIED`)
2. **`GetCursorPos` Probing**:
   - Call: `user32.GetCursorPos(byref(POINT))`
   - Return Code: `0` (Failure)
   - Coordinate Result: `(0, 0)`
3. **Session & WindowStation Identification**:
   - Process Session ID: `21`
   - Window Station Handle: `416`
   - Desktop Handle: `420`

### Diagnostic Finding
The agent process operates in an unattended, non-interactive Windows service session (Session 21). In this context, Windows restricts access to the interactive user input desktop with `ERROR_ACCESS_DENIED` (0x00000005). Neither synthetic mouse cursor movement, mouse clicks, nor keyboard inputs can be dispatched to an active rendering viewport.

Attempting to launch the Full-mode runner under these conditions would reproduce the known failure mode of Run 1 (where the Editor launched, waited indefinitely for combat input, and had to be aborted, holding dual locks and patching `DefaultGame.ini`).

---

## 3. Invariant Verification & Project State Safety

In strict accordance with the task specification, Antigravity maintained all project invariants:

- **Zero Editor Launches**: Unreal Editor was not launched.
- **Zero Config Modifications**: `DefaultGame.ini` was not patched or modified.
- **Zero Lock Collisions**: Neither project root `ENGINE_LOCK.json` nor `Docs/BossCombatReview/Execution/ENGINE_LOCK.json` was created or acquired.
- **Zero Asset Mutations**: No assets or packages were created, modified, or saved.
- **Zero Builds / Tests**: No compilation or PIE automation was executed.

---

## 4. Playtest Disposition & Recommended Owner Action

Because automated agent sessions cannot inject interactive combat inputs:

1. **Lead Approval Receipt Status**: Fresh lead approval receipt `Saved/C1619RouteBuild/BT71_LeadApprovalRefresh_20261117_1830/route_lead_approval.json` remains valid, binding all 9 canonical hashes to the BT-69 verified build/suite.
2. **Actionable Step for Owner**: The Owner should conduct the interactive playtest directly via Remote Desktop Connection (RDC), adhering to the exact steps detailed in [BT_73_OWNER_RDC_PLAYTEST_CHECKLIST.md](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/BT_73_OWNER_RDC_PLAYTEST_CHECKLIST.md):
   ```powershell
   powershell -ExecutionPolicy Bypass -File c:\UnrealProject\OneBossFight\Scripts\Editor\run_sevarog_arena_route_acceptance.ps1 -Mode Full -LeadApprovalReceipt c:\UnrealProject\OneBossFight\Saved\C1619RouteBuild\BT71_LeadApprovalRefresh_20261117_1830\route_lead_approval.json
   ```
3. **Observability Note**: As established in [BT_66_RAW_BT_TICK_OBSERVABILITY_AUDIT.md](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/BT_66_RAW_BT_TICK_OBSERVABILITY_AUDIT.md) and [BT_78_BT_TICK_FEASIBILITY_RECOMMENDATION.md](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/BT_78_BT_TICK_FEASIBILITY_RECOMMENDATION.md), completing BT-71 will provide empirical boss-death lifecycle evidence, but overall acceptance of BT-62 will remain blocked until the raw BehaviorTree attack-tick observability criterion is formally resolved or waived by the Owner.
