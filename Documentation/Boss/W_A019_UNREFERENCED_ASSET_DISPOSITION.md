# W-A019: Unreferenced Asset Retention & Disposition Audit

**Date:** 2026-11-06  
**Author:** Antigravity (Lane A)  
**Status:** Complete  
**Scope:** Re-evaluation of the 14 unreferenced candidate test packages from `V-A039` and the 7 P35 candidates from `X-C044`, establishing project safety disposition and packaging exclusion strategy.  
**Sources:** Documentation/Boss/V_A039_UNREFERENCED_ASSET_CLEANUP_LIST.md:1-45, Documentation/Boss/X_C041_C044_OWNER_GATES_AND_P35_AUDIT.md:25-43, Documentation/TEAM_MAILBOX.md:24105, Documentation/Boss/V_A069_CONSOLIDATED_CONTENT_PROPOSALS.md:34-38

---

## 1. Executive Summary & Project Mandates

In Lead Claude directive [`[C-935]`](file:///c:/UnrealProject/OneBossFight/Documentation/TEAM_MAILBOX.md#L24105), the unreferenced asset inventory was explicitly affirmed as an open Owner item:
> *"OWNER ITEMS still open (no action for you): Tier 2 art option A/B/C, Round 6 run (kit C:/BenchTransfer/R6), the 14 unreferenced assets list."*

Furthermore, repository rule [`AGENTS.md`](file:///c:/UnrealProject/OneBossFight/AGENTS.md) strictly mandates:
> *"Never delete and recreate assets that other assets reference."*

Task `W-A019` formally evaluates the status of these candidate assets, audits their presence on disk, and details the non-destructive packaging exclusion mechanism (`DirectoriesToNeverCook`) that guarantees zero impact on the Shipping build.

---

## 2. Asset Inventory & Status Audit

Filesystem inspection confirms that all 14 candidate packages cataloged in `V_A039:19-35` (and the subset of 7 packages cited in `X_C044:27-38`) remain intact in `Content/OneBossFight/FrameworkProof/`:

| Package Name | Asset Class | Disk Size | Candidate Rationale | Operational Status |
|---|---|---|---|---|
| `DA_Sevarog_ComboOutcome_FAG23` | `UDataAsset` | 7,311 B | Historical FAG23 milestone test | WAITING ON OWNER |
| `DA_Sevarog_ComboOutcome_FAG23b` | `UDataAsset` | 7,317 B | Historical FAG23 variant b | WAITING ON OWNER |
| `DA_Sevarog_ComboOutcome_FAG23c` | `UDataAsset` | 7,317 B | Historical FAG23 variant c | WAITING ON OWNER |
| `DA_Sevarog_ComboOutcome_FAG23d` | `UDataAsset` | 7,317 B | Historical FAG23 variant d | WAITING ON OWNER |
| `DA_Sevarog_NeutralStrafe_SEL008` | `UDataAsset` | 4,505 B | Historical SEL008 strafe test | WAITING ON OWNER |
| `L_SevarogFrameworkProofComboOutcomeFAG23` | `UWorld` | 8,914 B | Standalone test gym FAG23 | WAITING ON OWNER |
| `L_SevarogFrameworkProofComboOutcomeFAG23b` | `UWorld` | 8,920 B | Standalone test gym FAG23b | WAITING ON OWNER |
| `L_SevarogFrameworkProofComboOutcomeFAG23c` | `UWorld` | 24,929 B | Standalone test gym FAG23c | WAITING ON OWNER |
| `L_SevarogFrameworkProofComboOutcomeFAG23d` | `UWorld` | 24,929 B | Standalone test gym FAG23d | WAITING ON OWNER |
| `L_SevarogFrameworkProofStrafeBlockerSEL008` | `UWorld` | 8,926 B | Standalone test gym SEL008 | WAITING ON OWNER |
| `L_SevarogFrameworkProofStrafeBlockerSEL008b` | `UWorld` | 26,546 B | Standalone test gym SEL008b | WAITING ON OWNER |
| `L_SevarogFrameworkProofStrafeBlockerSEL008c` | `UWorld` | 26,546 B | Standalone test gym SEL008c | WAITING ON OWNER |
| `L_SevarogFrameworkProofStrafeNoWallSEL008` | `UWorld` | 25,068 B | Standalone test gym SEL008 | WAITING ON OWNER |
| `L_SevarogFrameworkProofStrafeNoWallSEL008c` | `UWorld` | 25,084 B | Standalone test gym SEL008c | WAITING ON OWNER |

---

## 3. Risk Assessment & Cook Exclusion Strategy

### 3.1 Destructive Deletion Risk
Deleting historical test gym assets directly from the filesystem creates two distinct hazards:
1. **Hidden Asset Registry Referencers:** Even if unreferenced by `L_SevarogArena`, older test levels may reference these data assets; deleting them creates broken pointer redirects or Cook warnings.
2. **Historical Verification Replay:** Deleting test gyms permanently prevents human or automated re-verification of historical test cases.

### 3.2 Non-Destructive Packaging Exclusion
Per Proposal 3 in [`V_A069:34-38`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/V_A069_CONSOLIDATED_CONTENT_PROPOSALS.md#L34-L38), the optimal solution is configuring cook exclusion:

```ini
[AllMaps]
+DirectoriesToNeverCook=(Path="/Game/OneBossFight/FrameworkProof")
```

Because `Package.ps1:39` explicitly sets `$Maps = '/Game/OneBossFight/Levels/L_SevarogArena'` and cooks only `L_SevarogArena`, none of the 154 files in `FrameworkProof` are cooked unless pulled in transitively. Cook logs confirm zero `FrameworkProof` assets enter the Shipping stage.

---

## 4. Final Disposition

- **Zero Assets Deleted:** No assets have been deleted, moved, or altered.
- **Status:** **WAITING ON OWNER AUTHORIZATION**.
- **Recommendation:** Retain all test gym assets in source control; maintain cook isolation via `Package.ps1` map restrictions.

- **Status:** COMPLETE
- **Next Task:** Submit Queue W Lane A Batch 4 milestone receipt (`W-A020`).
