# BT-84: C-1155 Source-Hash Preflight Packet for Greystone Visual Smoke

**Author:** Antigravity (Implementer)
**Date:** 2026-11-17
**Scope:** Source-only preflight packet for BT-83 (`rpg.GreystonePlayerTestPawn=1` in `L_SevarogArena`), incorporating forensic evidence from accepted BT-88 diagnosis.
**Constraint:** Strict source-only preflight; 0 builds, 0 Unreal Editor launches, 0 PIE runs, 0 asset/config mutations, 0 git commits/pushes. No approval receipt is created or inferred.

---

## 1. Canonical Four-Way Source Hashes (SHA256)

The following four files form the complete locked source set verified by `Scripts/Editor/run_greystone_visual_smoke.ps1`:

| Identifier | Source Path | Canonical SHA256 Hash |
| :--- | :--- | :--- |
| `runner` | `Scripts/Editor/run_greystone_visual_smoke.ps1` | `FAB7A89AC4710F9F955F8A3E9DDA18C97F0882BC973132E210213B070B14DB1F` |
| `driver` | `Scripts/Editor/pie_greystone_visual_smoke.py` | `68CF485F54858B943A5D7B1DE2D209768898E0F143B79E550D06B35836EB4AF1` |
| `retarget_cpp` | `Source/OneBossFightEditor/Private/RPGGreystoneRuntimeRetargetLibrary.cpp` | `22A04C1A5B12AAC1A045EC33AB2E346064D55FBABA83FA5E25FA2E749C5778AF` |
| `moves_cpp` | `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp` | `60097589BA1FAF3C12827ECDF6AC0FD32651EA3AA292EF25C17AB1878D7FB838` |

All four hashes have been re-verified directly against current repository files.

---

## 2. Runner Preflight & Locking Disciplines

1. **Preflight File Existence Checks:**
   - Unreal Editor binary verified present at `C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor.exe`.
   - Project file verified present at `C:\UnrealProject\OneBossFight\OneBossFight.uproject`.
   - Baseline configuration verified present at `C:\UnrealProject\OneBossFight\Config\DefaultGame.ini`.
   - All four bound source files verified present.

2. **Concurrency & Lock Acquisition Guards:**
   - Pre-lock check enforces zero running `UnrealEditor` / `UnrealEditor-Cmd` processes via `Test-EditorRunning`.
   - Pre-check enforces that neither root `ENGINE_LOCK.json` nor `Docs\BossCombatReview\Execution\ENGINE_LOCK.json` exists.
   - Dual-lock acquisition runs atomically inside a dedicated `try/finally` block.
   - `Acquire-Lock` creates a temporary lock file (`<path>.<token>.tmp`) using `FileMode::CreateNew`, writes the formatted C-1155 record, flushes, and moves to target path.
   - Full readback verification strictly checks:
     * `owner_token == $token`
     * `policy == 'C-1155'`
     * `party == 'X'`
     * `agent == 'Antigravity'`
     * `task == 'BT-79 Greystone visual smoke PIE'`
     * `command_id == 'run_greystone_visual_smoke'`
   - Post-lock recheck verifies that no Editor appeared during lock acquisition.
   - Post-lock source hash verification re-confirms all four source hashes match `$lockedHashes` before any Editor launch.

3. **Teardown & Recovery Guarantees:**
   - `DefaultGame.ini` SHA256 is checked before lock release; any read error or hash mismatch retains owned locks and reports `RECOVERY_NEEDED` without automatic overwriting.
   - If Editor is still running, owned locks are retained and `RECOVERY_NEEDED` is reported.
   - If Editor has exited cleanly and config hash is verified, only exact owner-token locks (`owner_token == $token`) are removed.
   - Environment variables (`GREYSTONE_SMOKE_RUN_TOKEN`, `GREYSTONE_SMOKE_RECEIPT`, `GREYSTONE_SMOKE_LOG`, `GREYSTONE_SMOKE_SOURCE_HASHES`) are cleared unconditionally on all execution branches.

---

## 3. Exact Required Lead Approval Receipt Schema

For `run_greystone_visual_smoke.ps1` to accept the lead approval receipt (`-LeadApprovalReceipt <Path>`), the JSON envelope must satisfy:

```json
{
  "status": "APPROVED",
  "result": "PASS",
  "accepted": true,
  "map": "/Game/OneBossFight/Maps/L_SevarogArena",
  "run_token": "<UNIQUE_RUN_TOKEN>",
  "source_hashes": {
    "runner": "FAB7A89AC4710F9F955F8A3E9DDA18C97F0882BC973132E210213B070B14DB1F",
    "driver": "68CF485F54858B943A5D7B1DE2D209768898E0F143B79E550D06B35836EB4AF1",
    "retarget_cpp": "22A04C1A5B12AAC1A045EC33AB2E346064D55FBABA83FA5E25FA2E749C5778AF",
    "moves_cpp": "60097589BA1FAF3C12827ECDF6AC0FD32651EA3AA292EF25C17AB1878D7FB838"
  }
}
```

### Specific Validation Rules in Runner:
1. `status` must match `'APPROVED'` exactly (case-sensitive).
2. `result` must match `'PASS'` exactly (case-sensitive).
3. `accepted` must be boolean `true`.
4. `map` must match `'/Game/OneBossFight/Maps/L_SevarogArena'` exactly.
5. `run_token` must be a non-empty string.
6. `source_hashes` block must be present, with all four keys matching the canonical hashes byte-for-byte.

---

## 4. Cold-Start Timeout Architecture & Evidence-Based Rationale

### 4.1 Empirical Observations from Run 1 (`Run_20261117_161913_a87434f6`)
- **Observed Startup Timing:**
  * Process launch: `16:19:13.852Z`.
  * Python script entry: `16:20:13.852Z` (elapsed: 60.0s).
  * Level loaded and PIE requested: `16:20:14.121Z`.
  * PIE world started and observed by driver: `16:20:20.247Z` (elapsed: 66.4s).
- **Observed Teardown Timing:**
  * Runner 60s timeout expired at `16:20:13.852Z`, queuing `CloseMainWindow()`.
  * Slate processed window closure during Frame [ 3] (`16:20:29.636Z`), resulting in `PIE game world lost while waiting for possession` at `16:20:29.852Z`.
- **Observed Frame Deltas:**
  * Frame [ 2]: 6.57s delta warning (`FAutomationControllerManager::Tick()`).
  * Frame [ 3]: 9.61s delta warning (`FAutomationControllerManager::Tick()`).
- **Unobserved Lifecycle Events:**
  * Neither initial pawn spawn nor pawn possession was observed before teardown; the final snapshot recorded `POSSESSED_PAWN class=None path=None`.
  * Whether pawn spawn occurred in the engine before teardown is unknown from the log.

### 4.2 Separation of Facts from Working Hypotheses
1. **Cause of Cold Start Delays:**
   - *Fact:* The log records concurrent package streaming skips (Lines 1812-1827) and material compilation warnings (Lines 1828-1835).
   - *Inference/Hypothesis:* Attributing the cold-start duration or the 9.61s delta solely to asset/shader compilation is an unproven inference; general engine initialization, asset registry gathering, and background Slate processing also ran concurrently.
2. **Possession and Replacement Duration:**
   - *Hypothesis:* Based on static code inspection (`URPGPlayerMovesSubsystem::OnPackPawnSpawned`), replacement is scheduled on next tick.
   - *Distinction:* Any estimate that pawn possession and animation verification will complete within a sub-5s budget is an unverified hypothesis, not measured empirical data.
3. **180s Timeout Effectiveness:**
   - *Hypothesis:* Setting `$TimeoutSeconds = 180` provides a ~113s margin over the observed 66.4s world start.
   - *Distinction:* The 180s timeout setting has **not been runtime-verified** in a complete PIE execution.

### 4.3 Rationale for Bounded Process-Anchored Deadline
- Anchoring the deadline firmly at process launch (`$deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)`) prevents indefinite hangs if the engine freezes during early bootstrap.
- The 180s default provides substantial headroom over the observed 66.4s world initialization while capping execution deterministically within the allowed range (`[ValidateRange(1, 300)]`).

---

## 5. Compatibility, Blocker & Approval Gate Assessment

- **Runner / Driver / C++ Compatibility:** CLEAN (0 syntax errors, 0 link breakages, exact path bindings verified).
- **Process & Environment Readiness:** CLEAN (No lingering editor processes, no stale lock files).
- **Execution Gate:** **LOCKED (BT-83 GATED)**.
  * As mandated by C-1155, execution is strictly blocked until a fresh, authentic Owner approval receipt is issued.
  * Because the runner was updated in BT-86, the approval envelope must be explicitly bound to the updated runner hash:
    `FAB7A89AC4710F9F955F8A3E9DDA18C97F0882BC973132E210213B070B14DB1F`.
  * Zero tests, builds, Unreal Editor launches, PIE runs, config/asset changes, or git operations will be executed without that specific approval.
