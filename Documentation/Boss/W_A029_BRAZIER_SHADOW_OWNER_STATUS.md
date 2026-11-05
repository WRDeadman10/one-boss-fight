# W-A029: Brazier Shadow Profile Owner Decision Status

**Date:** 2026-11-06  
**Author:** Antigravity (Lane A)  
**Status:** WAITING ON OWNER  
**Scope:** Status reconciliation of Owner review for arena brazier shadow profiles (L1 vs L2) in `L_SevarogArena`, including spatial depth trade-offs and performance impact.  
**Sources:** Documentation/Boss/V_A021_LIGHTING_CVAR_PROFILES.md:1-55, Documentation/Boss/V_A023_BRAZIER_SHADOW_SELECTION.md:1-67, Documentation/PERFORMANCE_LOG.md:55-56, Documentation/TEAM_MAILBOX.md:24105

---

## 1. Context & Operational Status

In `L_SevarogArena`, 12 perimeter braziers currently cast dynamic Virtual Shadow Maps (VSMs). In Round 2 telemetry ([`Documentation/PERFORMANCE_LOG.md:55-56`](file:///c:/UnrealProject/OneBossFight/Documentation/PERFORMANCE_LOG.md#L55-L56)), virtual shadow maps account for **8.2 ms** of GPU frame time.

Lane A formulated two optimization profiles in `V-A021` and detailed the spatial coordinate map in `V-A023`. This item is submitted to the Owner for decision:

| Profile | Shadow Casters | Total GPU Savings | Visual / Gameplay Trade-Off | Operational Status |
|---|---|---|---|---|
| **L1 (Zero Shadows)** | 0 of 12 braziers | [PROPOSAL] **12.0 - 14.0 ms** | Flat lighting; loses character grounding shadows; unviable for Soulslike duel | Available for fallback |
| **L2 (4 Cardinal)** | 4 of 12 (`00, 03, 06, 09`) | [PROPOSAL] **8.5 - 11.0 ms** | **Recommended:** Preserves North/South/East/West depth perception and combat readability | **Recommended Candidate** |
| **L3 (Baseline)** | 12 of 12 braziers | 0 ms (Current) | High VSM page table churn; GPU bound at 28.6 FPS | Baseline (Bottleneck) |

---

## 2. Mailbox & Decision State

A review of the mailbox tail through `[A-563]` and `[X-1335]` indicates:
1. No Owner directive has been posted regarding the L1 vs L2 selection.
2. In accordance with rule `AGENTS.md` ("Never delete and recreate assets that other assets reference" and Look-Changing restrictions), no level files (`L_SevarogArena.umap`) or lighting components have been altered.
3. This decision remains tracked in `OWNER_DECISIONS_PENDING.md`.

---

## 3. Recommended Path Forward

Upon Owner review:
- If Owner selects **Profile L2**: Apply via level script or `DefaultGame.ini` actor parameters, activating shadow casting exclusively on cardinal braziers `00, 03, 06, 09`.
- If Owner defers: Maintain current baseline and rely on DLSS Balanced mode pending Round 6 transfer kit validation.

---

## 4. Disposition

- **Task Status:** **WAITING ON OWNER DECISION**
- **Next Task:** Submit Queue W Lane A Batch 6 milestone receipt (`W-A030`).
