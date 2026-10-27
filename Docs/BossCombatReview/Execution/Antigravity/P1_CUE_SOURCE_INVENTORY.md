# P1 Non-Debug Cue & Source Inventory (REV3)

**Document ID:** `P1_CUE_SOURCE_INVENTORY_REV3`  
**Date:** 2026-10-26  
**Author:** Antigravity (Visual & Technical Animation Investigator)  
**Work Order:** `Docs/BossCombatReview/Execution/ANTIGRAVITY_WORK_ORDER_05.md` (Task **AG05-2 Rev 3**)  
**Companion Machine-Readable Artifact:** [`P1_CUE_SOURCE_INVENTORY.json`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/P1_CUE_SOURCE_INVENTORY.json)  
**Zero-Dependency Offline Semantic Validator:** [`audit_cue_source_inventory.py`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/audit_cue_source_inventory.py) (Validated: 12/12 negative probe checks PASS, 14/14 inventory route records PASS, 1:1 Markdown-to-JSON ID parity verified, Code 0)  
**Primary Engine Evidence & Export Anchors:**  
- Requirements Baseline: [`06_REFERENCE_REQUIREMENTS.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Reference/06_REFERENCE_REQUIREMENTS.md) (SHA256: `33087a54fcd823c7213c09c5afebaea10155232dcb79d3762e6ec0ff8ae37746`)
- Engine Fingerprint: [`E-001_fingerprint.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/Evidence/E-001_fingerprint.md) (SHA256: `86abb6fab65eedb9299999efa3b8c35c90bc0590ce7b8bf55c8ee8dd3d95b0e5`)
- Live Attack Inventory: [`E-002_live_route_and_attack_inventory.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/Evidence/E-002_live_route_and_attack_inventory.md) (SHA256: `383f83cc0cce29c7035958ed0a04c88ad691d9b146987a9a63a3d84af6efdf3e`)
- A5 Release Timing: [`E-007_CAP01_A5_release_timing.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/Evidence/E-007_CAP01_A5_release_timing.md) (SHA256: `31568577b52f398ca00085533eb5e3d43b00f6b9e6ebb44cd6eb5dc8bda751b2`)
- A4 Geometry Probe: [`E-008_CAP02_A4_query_vs_visible_blade.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/Evidence/E-008_CAP02_A4_query_vs_visible_blade.md) (SHA256: `30c29078bca2bbaaf0f00b0f7178e96c2bb87032fb0f11bf1ef1a7bdd7d3d31e`)
- Pack Reuse Exports: [`E-009_pack_reuse_exports.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/Evidence/E-009_pack_reuse_exports.md) (SHA256: `b57eb82a6b592aa1243f52a88ffa95066fce75d018695451a8647c3c164bb048`)
- Pack Typed Exports: [`E-011_pack_typed_exports.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/Evidence/E-011_pack_typed_exports.md) (SHA256: `1f48254eb6f9e37f817a2287c05d2a1fecfd8048aa2056a3e1175bf1a32164af`)
- Montage Notifies Dump: [`montage_notifies_2026-10-25.txt`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/Evidence/exports/montage_notifies_2026-10-25.txt) (SHA256: `950c611ee5eae7bcdd7abca1ea56c051c3b42d988b427cf64452829142ab0b31`)

---

## 1. Executive Summary & Revised Counting Rule

This inventory provides the **definitive offline catalog of all candidate non-debug audiovisual and pose cues** across the live combat encounter in `L_SevarogArena`.

### Documented Counting Rule & Denominator
- **Denominator Definition:** The denominator is strictly established as the **14 named, evidenced attack route variants** across the live encounter, cleanly separating pack-authored montages and project-swapped replacement montages into independent records with unmixed clock domains.
- **Variant Breakdown (Total: 14):**
  * **9 Pack-Authored Route Variants:**
    1. Move A1 Pack Variant (`INV-ROUTE-A1-PACK`) &mdash; `GS_Attack01_Montage`
    2. Move A1b Pack Branch (`INV-ROUTE-A1B-PACK`) &mdash; `GS_Attack01_Montage` (Follow-up branch)
    3. Move A2 Heavy Slam (`INV-ROUTE-A2-PACK`) &mdash; `GS_ChargedAttack_Montage`
    4. Move A3a Pack Horizontal (`INV-ROUTE-A3A-PACK`) &mdash; `GS_Attack02_Montage`
    5. Move A3b Pack Back-Sweep (`INV-ROUTE-A3B-PACK`) &mdash; `GS_Attack03_Montage`
    6. Move A6 Leap Attack (`INV-ROUTE-A6-PACK`) &mdash; `GS_LeapAttack_Montage`
    7. Mid01 Mid-Range Slash (`INV-ROUTE-MID01`) &mdash; `Mid01_Anim_Montage`
    8. Sprint Attack Follow-Up (`INV-ROUTE-SPRINT`) &mdash; `GS_SprintAttackFollowUp_Montage`
    9. Retaliation Attack (`INV-ROUTE-RETAL`) &mdash; `RetaliationAttack_Montage`
  * **3 Project-Swapped Route Variants:**
    10. Move A1 Project Variant (`INV-ROUTE-A1-PROJECT`) &mdash; `AM_Boss01_A1`
    11. Move A3a Project Variant (`INV-ROUTE-A3A-PROJECT`) &mdash; `AM_Boss01_A3a`
    12. Move A3b Project Variant (`INV-ROUTE-A3B-PROJECT`) &mdash; `AM_Boss01_A3b`
  * **2 Native Project Special Routes:**
    13. Move A4 Low Sweep (`INV-ROUTE-A4`) &mdash; `RPGBossLowSweep` planar geometry query
    14. Move A5 Javelin Throw (`INV-ROUTE-A5`) &mdash; `RPGBossHealPunish` native projectile spawn
- **Exclusion Rule:** Non-damaging utility and system abilities granted to the boss (`GA_GS_Boss_TurnInPlace`, `HitStun`, `EnterCombat`, `ExitCombat`, `GA_EnemyRagdollDeath`) are tracked in structural documentation but excluded from the attack denominator.

> [!IMPORTANT]
> **Candidate Cue Caveat & Timing Precision:**
> 1. The static presence of an `AnimNotify_PlaySound` or `AnimNotifyState_Trail` in an exported notify table constitutes a **candidate cue**. It does *not* prove runtime audibility under combat mixing, luminance contrast against dark arena geometry, correct cooking, or Shipping visibility.
> 2. Pack-authored montages (e.g. `GS_Attack01_Montage` with contact at $0.166\text{ s}$) and project-swapped montages (e.g. `AM_Boss01_A1` with contact at $0.350\text{ s}$) have different timing structures and are strictly kept in separate records.
> 3. Static notify time markers (e.g. $0.037\text{ s}$, $0.627\text{ s}$, $0.637\text{ s}$, $0.444\text{ s}$, $0.446\text{ s}$) are structural observations subject to export decimal formatting ($0.001\text{ s}$ precision) and source authoring frame rates. Three-decimal offsets do not automatically imply runtime $60\text{ fps}$ frame-boundary quantization or meaningful $2\text{ ms}$ microsecond player-reaction precision.

---

## 2. Master Attack Route Traceability Matrix (REV3)

| Audit ID | Move / Variant Name | Executor Owner | Ability Class & Behavior Gate | Canonical Montage / Clip Asset Path | Active Damage Window | First Gameplay Contact Source | Candidate Non-Debug Cues | Runtime Observation Status |
|---|---|---|---|---|---|---|---|---|
| **INV-ROUTE-A1-PACK** | Move A1 Pack Variant | Pack-Derived (Tracked) | `GA_GS_Boss_CloseAttack` | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_Attack01_Montage` | $0.166\text{ s} - 0.469\text{ s}$ | `ANS_CollisionTrace_C` (0.166s) | Blade hoist, Sound at 0.164s | Live PIE bot combat (E-002:43) |
| **INV-ROUTE-A1-PROJECT** | Move A1 Project Variant | Pack-Derived (Tracked) | `GA_GS_Boss_CloseAttack` | `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A1` | $0.350\text{ s} - 0.500\text{ s}$ | `ANS_CollisionTrace_C` (0.350s) | Blade hoist, Sound at 0.330s | Swapped in PIE (E-002:43) |
| **INV-ROUTE-A1B-PACK** | Move A1b Pack Branch | Pack-Derived (Tracked) | `GA_GS_Boss_CloseAttack` | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_Attack01_Montage` | Follow-up section | `ANS_CollisionTrace_C` (Follow-up) | Follow-through pose, swing sound | Branch gate at 0.544s (E-002:43) |
| **INV-ROUTE-A2-PACK** | Move A2 Heavy Slam | Pack-Derived (Tracked) | `GA_GS_Boss_CloseRare` (25% roll) | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_ChargedAttack_Montage` | $1.567\text{ s} - 1.760\text{ s}$, $1.925\text{ s} - 2.104\text{ s}$ | `ANS_CollisionTrace_C` (1.567s, 1.925s) | Two-handed raise, Sounds at 1.593s/1.817s | PIE & CAP-06 image audit |
| **INV-ROUTE-A3A-PACK** | Move A3a Pack Horizontal | Pack-Derived (Tracked) | `GA_GS_Boss_CloseAttack` | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_Attack02_Montage` | $0.166\text{ s} - 0.469\text{ s}$ | `ANS_CollisionTrace_C` (0.166s) | Lateral draw, Sound at 0.164s | Live PIE combat (E-002:43) |
| **INV-ROUTE-A3A-PROJECT** | Move A3a Project Variant | Pack-Derived (Tracked) | `GA_GS_Boss_CloseAttack` | `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3a` | $0.400\text{ s} - 0.600\text{ s}$ | `ANS_CollisionTrace_C` (0.400s) | Lateral draw, Sound at 0.380s | Swapped in PIE (E-002:43) |
| **INV-ROUTE-A3B-PACK** | Move A3b Pack Back-Sweep | Pack-Derived (Tracked) | `GA_GS_Boss_CloseAttack` | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_Attack03_Montage` | $0.166\text{ s} - 0.469\text{ s}$ | `ANS_CollisionTrace_C` (0.166s) | Reversal stroke, Sound at 0.164s | Live PIE combo (E-002:43) |
| **INV-ROUTE-A3B-PROJECT** | Move A3b Project Variant | Pack-Derived (Tracked) | `GA_GS_Boss_CloseAttack` | `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3b` | $0.150\text{ s} - 0.400\text{ s}$ | `ANS_CollisionTrace_C` (0.150s) | Reversal stroke, Sound at 0.130s | Swapped in PIE (E-002:43) |
| **INV-ROUTE-A6-PACK** | Move A6 Leap Attack | Pack-Derived (Tracked) | `GA_GS_Boss_LeapAttack` (Far < 800cm, P2) | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_LeapAttack_Montage` | $0.754\text{ s} - 1.175\text{ s}$ | `ANS_CollisionTrace_C` (0.754s) | Aerial leap trajectory, landing impact | Live PIE combat (E-002:46) |
| **INV-ROUTE-MID01** | Mid-Range Slash | Pack-Owned (Untracked) | `GA_GS_Boss_MidRangeAttack` | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/ExampleSwordMob/Mid01_Anim_Montage` | $0.637\text{ s} - 0.884\text{ s}$ | `ANS_CollisionTrace_C` (0.637s) | Step forward, Sound at 0.627s | Historical bot: 1 hit / 108 dmg |
| **INV-ROUTE-SPRINT** | Sprint Follow-Up | Pack-Owned (Untracked) | `GA_GS_Boss_SprintAttack` | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_SprintAttackFollowUp_Montage` | $0.037\text{ s} - 0.230\text{ s}$, $0.364\text{ s} - 0.551\text{ s}$ | `ANS_CollisionTrace_C` (0.037s, 0.364s) | Sprint into strike, Sound at 0.037s | Class defaults (E-002:47) |
| **INV-ROUTE-RETAL** | Retaliation Attack | Pack-Owned (Untracked) | `GA_GS_Boss_RetaliationAttack` | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/ExampleSwordMob/RetaliationAttack_Montage` | $0.444\text{ s} - 0.630\text{ s}$ | `ANS_CollisionTrace_C` (0.444s) | Spin counter, Sound/trail at 0.446s | Trigger confirmed (E-002:82) |
| **INV-ROUTE-A4** | Move A4 Low Sweep | Native Project Attack | `URPGAttackTracker::PlayClip` (Forced) | `UNKNOWN_NOT_EXPORTED` (Clip: `/Game/OneBossFight/Boss01/Animations/AN_Boss01_A4_LowSweep`) | $0.609\text{ s} - 0.879\text{ s}$ | `RPGBossLowSweep` planar query | Low crouch, blade pull back | Forced test hook probe (E-008:5) |
| **INV-ROUTE-A5** | Move A5 Javelin Throw | Native Project Attack | `URPGBossHealPunish` (Heal reaction) | `UNKNOWN_NOT_EXPORTED` (Clip: `/Game/OneBossFight/Boss01/Animations/AN_Boss01_A5_JavelinThrow`) | Simulation: code 0.450s, spawn 0.470s | Native `ARPGBossJavelin` actor | Overhead cocking stance | Telemetry verified; visuals PARKED |

---

## 3. Detailed Route Records

### 3.1 Pack-Authored Attack Routes

#### Record 1: Move A1 Pack Variant (`INV-ROUTE-A1-PACK`)
- **Executor Owner:** Pack-Derived (Tracked by `URPGAttackTracker`).
- **Ability Class & Gate:** `GA_GS_Boss_CloseAttack` (`Ability.Melee.Close`). Gated by Behavior Tree distance $< 250\text{ cm}$.
- **Canonical Asset Paths:**
  * Montage: `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_Attack01_Montage`
  * Source Clip: `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_Attack01_Montage`
- **Timing Coordinates (Montage Clock):** Total length $1.200\text{ s}$. Movement disabled $[0.000\text{ s}, 1.200\text{ s}]$. Rotation lock $[0.000\text{ s}, 0.317\text{ s}]$. Sound notify at $0.164\text{ s}$. Damage trace $[0.166\text{ s}, 0.469\text{ s}]$ ($0.303\text{ s}$ active). Follow-up branch trigger at $0.544\text{ s}$. Ability end at $0.962\text{ s}$.
- **Gameplay Contact Source:** `ANS_CollisionTrace_C` opens at $0.166\text{ s}$.
- **Readability & Cues:** Candidate audio cue at $0.164\text{ s}$ coincides with damage trace opening at $0.166\text{ s}$ (2ms difference is within static export rounding uncertainty). Visual cue is provided by the vertical weapon hoist.
- **Requirements Mapping:** `BOSS-ANM-001`, `BOSS-ANM-002`, `BOSS-ANM-004`, `BOSS-PAC-001`.

#### Record 2: Move A1b Pack Branch (`INV-ROUTE-A1B-PACK`)
- **Executor Owner:** Pack-Derived (Tracked by `URPGAttackTracker`).
- **Ability Class & Gate:** `GA_GS_Boss_CloseAttack`. Gated by `AN_PerformFollowUp_C` notify at $0.544\text{ s}$ in Section 1.
- **Canonical Asset Paths:** `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_Attack01_Montage` (Follow-up section).
- **Gameplay Contact Source:** `ANS_CollisionTrace_C` in follow-up section.
- **Readability & Cues:** Continuous follow-through stroke transitioning into secondary swing. Branch gate opens at $0.544\text{ s}$.
- **Requirements Mapping:** `BOSS-ANM-001`, `BOSS-PAC-001`, `BOSS-PAC-004`.

#### Record 3: Move A2 Heavy Slam (`INV-ROUTE-A2-PACK`)
- **Executor Owner:** Pack-Derived (Tracked by `URPGAttackTracker`).
- **Ability Class & Gate:** `GA_GS_Boss_CloseRare` (`Ability.Melee.CloseRare`). Gated by distance $< 250\text{ cm}$, $25\%$ chance roll.
- **Canonical Asset Paths:** `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_ChargedAttack_Montage`
- **Timing Coordinates (Montage Clock):** Total length $3.400\text{ s}$. Movement disabled $[0.000\text{ s}, 4.933\text{ s}]$. First trace $[1.567\text{ s}, 1.760\text{ s}]$. Sound notifies at $1.593\text{ s}$ (downward stroke) and $1.817\text{ s}$ (ground impact). Second trace $[1.925\text{ s}, 2.104\text{ s}]$. Grounded weapon rest starts at $2.104\text{ s}$.
- **Gameplay Contact Source:** Dual `ANS_CollisionTrace_C` windows (downward slash + ground impact).
- **Readability & Cues:** High two-handed raise provides $>1.0\text{ s}$ visual preparation. Grounded rest confirmed in CAP-06 image audit.
- **Requirements Mapping:** `BOSS-ANM-002`, `BOSS-ANM-003`, `BOSS-PAC-001`, `BOSS-PAC-003`, `BOSS-QA-007`.

#### Record 4: Move A3a Pack Horizontal (`INV-ROUTE-A3A-PACK`)
- **Executor Owner:** Pack-Derived (Tracked by `URPGAttackTracker`).
- **Ability Class & Gate:** `GA_GS_Boss_CloseAttack`.
- **Canonical Asset Paths:** `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_Attack02_Montage`
- **Timing Coordinates (Montage Clock):** Total length $1.200\text{ s}$. Movement disabled $[0.000\text{ s}, 1.200\text{ s}]$. Rotation lock $[0.000\text{ s}, 0.317\text{ s}]$. Sound notify at $0.164\text{ s}$. Damage trace $[0.166\text{ s}, 0.469\text{ s}]$. Follow-up notify at $0.544\text{ s}$.
- **Gameplay Contact Source:** `ANS_CollisionTrace_C` at $0.166\text{ s}$.
- **Requirements Mapping:** `BOSS-ANM-001`, `BOSS-ANM-002`, `BOSS-ANM-004`, `BOSS-PAC-001`.

#### Record 5: Move A3b Pack Back-Sweep (`INV-ROUTE-A3B-PACK`)
- **Executor Owner:** Pack-Derived (Tracked by `URPGAttackTracker`).
- **Ability Class & Gate:** `GA_GS_Boss_CloseAttack` (Combo Follow-up).
- **Canonical Asset Paths:** `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_Attack03_Montage`
- **Timing Coordinates (Montage Clock):** Total length $1.200\text{ s}$. Movement disabled $[0.000\text{ s}, 1.200\text{ s}]$. Rotation lock $[0.000\text{ s}, 0.317\text{ s}]$. Sound notify at $0.164\text{ s}$. Damage trace $[0.166\text{ s}, 0.469\text{ s}]$.
- **Gameplay Contact Source:** `ANS_CollisionTrace_C` at $0.166\text{ s}$.
- **Requirements Mapping:** `BOSS-ANM-001`, `BOSS-ANM-002`, `BOSS-ANM-004`, `BOSS-PAC-001`.

#### Record 6: Move A6 Leap Attack (`INV-ROUTE-A6-PACK`)
- **Executor Owner:** Pack-Derived (Tracked by `URPGAttackTracker`).
- **Ability Class & Gate:** `GA_GS_Boss_LeapAttack` (`Ability.Melee.Leap`). Gated by distance $< 800\text{ cm}$, Phase 2.
- **Canonical Asset Paths:** `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_LeapAttack_Montage`
- **Timing Coordinates (Montage Clock):** Total length $2.333\text{ s}$. Movement disabled $[0.000\text{ s}, 2.333\text{ s}]$. Rotation lock $[0.000\text{ s}, 0.640\text{ s}]$. Sound notifies at $0.467\text{ s}$ (leap start) and $0.754\text{ s}$ (landing). Damage trace $[0.754\text{ s}, 1.175\text{ s}]$.
- **Gameplay Contact Source:** `ANS_CollisionTrace_C` at $0.754\text{ s}$.
- **Requirements Mapping:** `BOSS-ANM-002`, `BOSS-PAC-001`, `BOSS-PAC-003`.

#### Record 7: Mid01 Mid-Range Slash (`INV-ROUTE-MID01`)
- **Executor Owner:** Pack-Owned (Untracked by project C++).
- **Ability Class & Gate:** `GA_GS_Boss_MidRangeAttack`. Behavior Tree distance $< 800\text{ cm}$.
- **Canonical Asset Paths:** `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/ExampleSwordMob/Mid01_Anim_Montage`
- **Timing Coordinates (Montage Clock):** Total length $2.667\text{ s}$. Movement disabled $[0.000\text{ s}, 1.667\text{ s}]$. Sound notify at $0.627\text{ s}$. Damage trace $[0.637\text{ s}, 0.884\text{ s}]$.
- **Gameplay Contact Source:** `ANS_CollisionTrace_C` at $0.637\text{ s}$.
- **Readability & Cues:** Sound at $0.627\text{ s}$ precedes collision trace opening at $0.637\text{ s}$ by $10\text{ ms}$ (within export rounding window). Visual cue is diagonal step forward.
- **Requirements Mapping:** `BOSS-ANM-001`, `BOSS-ANM-002`, `BOSS-ANM-004`, `BOSS-PAC-001`.

#### Record 8: Sprint Attack Follow-Up (`INV-ROUTE-SPRINT`)
- **Executor Owner:** Pack-Owned (Untracked by project C++).
- **Ability Class & Gate:** `GA_GS_Boss_SprintAttack`. Fall-through from FarRare failure.
- **Canonical Asset Paths:** `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_SprintAttackFollowUp_Montage`
- **Timing Coordinates (Montage Clock):** Total length $1.867\text{ s}$ (1.86666667s in raw export). Movement disabled $[0.000\text{ s}, 3.400\text{ s}]$. Sound notify at $0.037\text{ s}$. First trace $[0.037\text{ s}, 0.230\text{ s}]$ ($0.193\text{ s}$ duration). Second sound notify at $0.361\text{ s}$. Second trace $[0.364\text{ s}, 0.551\text{ s}]$ ($0.187\text{ s}$ duration).
- **Gameplay Contact Source:** `ANS_CollisionTrace_C` (first window opens at $0.037\text{ s}$, second at $0.364\text{ s}$).
- **Readability & Cues:** Sound notify at $0.037\text{ s}$ exactly coincides with first trace opening. Visual telegraph belongs to the preceding sprint run-up phase of `GA_GS_Boss_SprintAttack`.
- **Requirements Mapping:** `BOSS-ANM-001`, `BOSS-ANM-002`, `BOSS-PAC-001`, `BOSS-PAC-002`.

#### Record 9: Retaliation Attack (`INV-ROUTE-RETAL`)
- **Executor Owner:** Pack-Owned (Untracked by project C++).
- **Ability Class & Gate:** `GA_GS_Boss_RetaliationAttack`. Triggered when hit count $\ge 3$ or incoming combo threshold met.
- **Canonical Asset Paths:** `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/ExampleSwordMob/RetaliationAttack_Montage`
- **Timing Coordinates (Montage Clock):** Total length $1.500\text{ s}$. Movement disabled $[0.000\text{ s}, 1.500\text{ s}]$. Trail notify $[0.446\text{ s}, 0.630\text{ s}]$. Sound notify at $0.446\text{ s}$. Damage trace $[0.444\text{ s}, 0.630\text{ s}]$.
- **Gameplay Contact Source:** `ANS_CollisionTrace_C` at $0.444\text{ s}$.
- **Readability & Cues:** Sound and trail notifies at $0.446\text{ s}$ coincide with collision trace opening at $0.444\text{ s}$ ($2\text{ ms}$ difference is within export rounding uncertainty). Spin counter rotation provides visual cue.
- **Requirements Mapping:** `BOSS-ANM-001`, `BOSS-ANM-002`, `BOSS-ANM-004`, `BOSS-PAC-001`.

---

### 3.2 Project-Swapped Attack Routes

#### Record 10: Move A1 Project Variant (`INV-ROUTE-A1-PROJECT`)
- **Executor Owner:** Pack-Derived (Tracked by `URPGAttackTracker`).
- **Ability Class & Gate:** `GA_GS_Boss_CloseAttack` (swapped by `RPGBossCloseClipSwap`).
- **Canonical Asset Paths:** `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A1`
- **Timing Coordinates (Montage Clock):** Total length $1.200\text{ s}$. Movement disabled $[0.000\text{ s}, 0.500\text{ s}]$. Rotation lock $[0.000\text{ s}, 0.330\text{ s}]$. Sound notify at $0.330\text{ s}$. Damage trace $[0.350\text{ s}, 0.500\text{ s}]$ ($0.150\text{ s}$ duration). Recovery $[0.500\text{ s}, 1.200\text{ s}]$.
- **Gameplay Contact Source:** `ANS_CollisionTrace_C` opens at $0.350\text{ s}$.
- **Readability & Cues:** Sound cue at $0.330\text{ s}$ precedes collision trace opening at $0.350\text{ s}$ by $20\text{ ms}$; visible $330\text{ ms}$ hoist provides clear preparation.
- **Requirements Mapping:** `BOSS-ANM-001`, `BOSS-ANM-002`, `BOSS-ANM-004`, `BOSS-PAC-001`, `BOSS-QA-007`.

#### Record 11: Move A3a Project Variant (`INV-ROUTE-A3A-PROJECT`)
- **Executor Owner:** Pack-Derived (Tracked by `URPGAttackTracker`).
- **Ability Class & Gate:** `GA_GS_Boss_CloseAttack` (swapped by `RPGBossCloseClipSwap`).
- **Canonical Asset Paths:** `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3a`
- **Timing Coordinates (Montage Clock):** Total length $0.800\text{ s}$. Movement disabled $[0.000\text{ s}, 0.600\text{ s}]$. Rotation lock $[0.000\text{ s}, 0.380\text{ s}]$. Sound notify at $0.380\text{ s}$. Damage trace $[0.400\text{ s}, 0.600\text{ s}]$ ($0.200\text{ s}$ duration). Follow-up gate at $0.750\text{ s}$.
- **Gameplay Contact Source:** `ANS_CollisionTrace_C` opens at $0.400\text{ s}$.
- **Readability & Cues:** Lateral blade draw provides directional cue; rotation locks $20\text{ ms}$ before damage window.
- **Requirements Mapping:** `BOSS-ANM-001`, `BOSS-ANM-002`, `BOSS-ANM-004`, `BOSS-PAC-001`.

#### Record 12: Move A3b Project Variant (`INV-ROUTE-A3B-PROJECT`)
- **Executor Owner:** Pack-Derived (Tracked by `URPGAttackTracker`).
- **Ability Class & Gate:** `GA_GS_Boss_CloseAttack` (swapped follow-up branch).
- **Canonical Asset Paths:** `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3b`
- **Timing Coordinates (Montage Clock):** Total length $1.333\text{ s}$. Movement disabled $[0.000\text{ s}, 0.600\text{ s}]$. Rotation lock $[0.000\text{ s}, 0.130\text{ s}]$. Sound notify at $0.130\text{ s}$. Damage trace $[0.150\text{ s}, 0.400\text{ s}]$ ($0.250\text{ s}$ duration). Recovery $[0.400\text{ s}, 1.333\text{ s}]$.
- **Gameplay Contact Source:** `ANS_CollisionTrace_C` opens at $0.150\text{ s}$.
- **Readability & Cues:** Fast back-sweep stroke; sound at $0.130\text{ s}$ precedes damage by $20\text{ ms}$.
- **Requirements Mapping:** `BOSS-ANM-001`, `BOSS-ANM-002`, `BOSS-ANM-004`, `BOSS-PAC-001`.

---

### 3.3 Native Project Special Attack Routes

#### Record 13: Move A4 Low Sweep (`INV-ROUTE-A4`)
- **Executor Owner:** Native Project Attack (`URPGAttackTracker::PlayClip`).
- **Ability Class & Gate:** C++ native planar sweep (`RPGBossLowSweep`). Forced in test hook probes (E-008:5).
- **Asset Paths:**
  * Montage: `UNKNOWN_NOT_EXPORTED` (Reason: dynamic montage wrapper generated transiently in memory via `Anim->PlaySlotAnimationAsDynamicMontage` in `RPGAttackTracker.cpp:169`; no static `.uasset` montage exists on disk).
  * Source Clip: `/Game/OneBossFight/Boss01/Animations/AN_Boss01_A4_LowSweep`
- **Timing Coordinates (Montage Clock):**
  * Clip Asset Duration: $1.767\text{ s}$ (`AN_Boss01_A4_LowSweep`).
  * Configured Tracker Timing (`RPGAttackTracker.cpp:84-87`): Commit time $0.400\text{ s}$, Active damage window $[0.600\text{ s}, 0.900\text{ s}]$ ($0.300\text{ s}$ duration), Recovery end $1.750\text{ s}$.
  * Sampled Geometry Probe (`E-008:5`): Active floor crossing window $[0.609\text{ s}, 0.879\text{ s}]$ ($0.270\text{ s}$ duration), peak reach at $0.855\text{ s}$.
- **Gameplay Contact Source:** `RPGBossLowSweep` planar geometry query (box shape swept along floor plane).
- **Readability & Cues:** Low crouching wind-up and blade pull-back provide an anticipation wind-up window ($0.000\text{ s} - 0.600\text{ s}$ configured / $0.609\text{ s}$ sampled). No audio notify exported in raw sequence.
- **Requirements Mapping:** `BOSS-ANM-001`, `BOSS-ANM-002`, `BOSS-HIT-001`, `BOSS-PAC-001`.

#### Record 14: Move A5 Javelin Throw (`INV-ROUTE-A5`)
- **Executor Owner:** Native Project Attack (`URPGBossHealPunish`).
- **Ability Class & Gate:** Gated by player potion/heal action. Scheduled via `URPGBossHealPunish` (`RPGBossHealPunish.cpp:179`).
- **Asset Paths:**
  * Montage: `UNKNOWN_NOT_EXPORTED` (Reason: dynamic montage wrapper generated transiently in memory via `Anim->PlaySlotAnimationAsDynamicMontage` in `RPGAttackTracker.cpp:169`; no static `.uasset` montage exists on disk).
  * Source Clip: `/Game/OneBossFight/Boss01/Animations/AN_Boss01_A5_JavelinThrow` (Clip asset duration: $1.000\text{ s}$).
- **Timing Coordinates & Provenance:**
  * Authored Sidecar Marker: $0.400\text{ s}$ (frame 12 @ 30fps).
  * Configured Tracker Timing (`RPGAttackTracker.cpp:97-100`): Commit time $0.450\text{ s}$, Active release window $[0.450\text{ s}, 0.500\text{ s}]$ ($0.050\text{ s}$ duration), Recovery end $0.950\text{ s}$, Track turn rate $240.0\text{ deg/s}$.
  * Sampled Runtime Telemetry (`E-007:5`): Projectile spawn at $0.470\text{ s}$.
  * Configured Projectile Flight Parameters (`RPGBossHealPunish.h:54-68`): `FlightTime = 1.2 s`, `MinSpeed = 450.0 cm/s`, `MaxSpeed = 2500.0 cm/s`, `JavelinRadius = 25.0 cm`, `JavelinMaxRange = 3000.0 cm`, `AimHeight = 100.0 cm`.
- **Gameplay Contact Source:** Native projectile actor (`ARPGBossJavelin::StaticClass()` spawned in `RPGBossHealPunish.cpp:179`) with spherical collision sweep.
- **Readability & Cues:** Overhead spear cocking stance represents candidate preparation pose (nominal 400ms sidecar marker); nominal 50ms (sampled 70ms in E-007) offset between sidecar marker and code spawn; visual hand departure is unverified and **strictly PARKED AS UNVERIFIED** per Owner directive.
- **Smallest Missing Measurement:** `PARKED - No execution requested (in-arena hand departure capture is parked per Owner directive)`.
- **Requirements Mapping:** `BOSS-ANM-001`, `BOSS-ANM-002`, `BOSS-PAC-001`, `BOSS-QA-006`, `BOSS-QA-007`.

---

## 4. Summary & Verification

- **Semantic Validator Check:** Executing `python Docs/BossCombatReview/Execution/Antigravity/audit_cue_source_inventory.py --self-test` verifies that:
  1. All 12 negative test cases (invented paths, invalid clocks, string NaNs, invalid requirement IDs, empty required strings, zero denominator, boolean timings, null timings, list NaNs, reversed windows, invented clips within approved roots, duplicate IDs) are properly rejected.
  2. The 14/14 inventory route records pass all domain, clock, requirement, and path validations.
  3. 1:1 ID parity between Markdown table and JSON is verified.
