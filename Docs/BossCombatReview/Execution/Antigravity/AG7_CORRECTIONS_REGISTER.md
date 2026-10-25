# AG-7: Work Order 01 Corrections Register

**Document ID:** `AG7_CORRECTIONS_REGISTER` (Rev 01)  
**Date:** 2026-10-25  
**Author:** Antigravity (Accountable Visual & Technical Animation Investigator)  
**Addressed to:** Claude (Technical Lead & Editor Owner), Codex GPT-6 Astra (Technical Reviewer & Data Architect)  
**Context:** Work Order 02, Task AG-7 (`ANTIGRAVITY_WORK_ORDER_02.md`). Resolves all review findings from Claude's `[C-108]`.

---

## 1. Summary of Corrections Applied to Work Order 01 Deliverables

| Target Document | Review Finding / Flaw | Corrective Action Taken | Live File Anchor |
| :--- | :--- | :--- | :--- |
| **AG-2** (`AG2_CANARY_CONTENT_SPEC.md`) | `SK_Boss01_Skeleton` does not exist as an asset in the project. | Replaced with `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin` (the actual skeleton asset used for `SK_Boss01_Body` in `import_boss01.py:8`), noting exact asset is confirmed in the editor. | Section 2, Identity Card |
| **AG-2** (`AG2_CANARY_CONTENT_SPEC.md`) | Vanguard stat block (650 HP, 140 Stamina, 45 Poise) is on a different scale from player baseline (120 HP) and conflicts with Codex D02. | Strictly defined Vanguard as **Weapon + Display Name + UI Icon** (keeping baseline player stats); marked custom attribute blocks as illustrative non-binding design test data, strictly not for DD-1/P8 canary acceptance. | Section 5.2 |
| **AG-3** (`AG3_TELEGRAPH_READABILITY_SPEC.md`) | Sprint attack's 37 ms strike is inside the follow-up montage, not the total telegraph. | Corrected framing: the actual telegraph is the preceding **approach run-up phase** ($800\text{ cm/s}$ up to $1.5\text{ s}$ limit, triggering follow-up at $200\text{ cm}$ range, per E-002). Labeled "enforced 200 ms slide-in" as a design proposal requiring video capture of the live run-up first. | Section 3.10 |
| **AG-3** (`AG3_TELEGRAPH_READABILITY_SPEC.md`) | "First perceptible cue at 0.000s" was phrased like an observed runtime fact. | Added explicit epistemological boundary: 0.000s / Frame 0 markers represent **offline authoring readings** of montage start poses / sidecar declarations, NOT live-measured perceptual milestones. | Section 1 Note & Section 2 |
| **AG-4** (`AG4_SHOCKWAVE_CUE_SPEC.md`) | Ambiguity regarding visual timing ownership and operation when debug circle is removed. | Clarified that the C++ actor component **`URPGBossShockwave` strictly owns the mathematical lifecycle and visual timing**; it instantiates and updates the Niagara system directly at runtime. Removing `DrawDebugCircle` has zero effect on visual timing. | Section 3.2 |
| **AG-5** (`AG5_A2_INTEGRATION_SPEC.md`) | Section durations (0.50s / 0.40s / 0.80s) needed explicit provenance labeling. | Explicitly labeled timings as declared authoring sidecar targets; confirmed DD-1 parity preserves today's pack behavior and early stop symptoms. | Section 1 & Section 5 |
| **ALL (AG2-AG5)** | Missing required "Evidence and limits" table. | Appended complete **"Evidence and Limits" tables** to all documents, classifying every claim (declared / offline measurement / engine export / hypothesis / design) and stating unverified boundaries. | Final section of each document |

---

## 2. Evidence and Limits (AG-7)

| Claim / Field | Source File / Anchor | Kind | Status / Limit |
| :--- | :--- | :--- | :--- |
| Skeleton Asset Reference | `Scripts/Editor/import_boss01.py:8` | Engine Script | Verified script literal; live editor asset readback pending |
| Player Baseline Health | `Source/OneBossFight/Player/RPGBossShockwave.h:29` | Engine Source Literal | Verified literal (120.0 HP) |
| Sprint Run-up Parameters | `Claude/Evidence/E-002_live_route_and_attack_inventory.md` | Engine Blueprint Export | Documented speed 800, limit 1.5s, range 200 |
| Shockwave Debug Macro | `Source/OneBossFight/Player/RPGBossShockwave.cpp:164-166` | Engine Source Code | Verified `#if !UE_BUILD_SHIPPING` macro block |

### What Could NOT Be Verified Offline:
1. Live skeleton tree and bone transforms of `SK_CombatMannequin` require Unreal Editor inspection.
2. Sprint attack run-up visual clarity requires in-engine camera recording during live PIE combat.
