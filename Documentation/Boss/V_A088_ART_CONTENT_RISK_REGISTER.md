# V-A088: Art & Content Production Risk Register

**Date:** 2026-11-06  
**Author:** Antigravity (Lane A)  
**Status:** Complete  
**Scope:** Exhaustive risk evaluation covering art assets, content organization, GPU budgets, lifetime leaks, and platform memory constraints.
**Sources:** Documentation/KNOWN_ISSUES.md:298-302, Documentation/Boss/V_A066_PACKAGE_SIZE_PROPOSALS_REVIEW.md

---

## 1. Risk Register Matrix

| ID | Risk Description | Severity | Probability | Impact Area | Mitigation Strategy & Verification | Owner / Task Anchor |
|---|---|---|---|---|---|---|
| **RSK-ART-001** | **Unreferenced Asset Deletion Breaking Cooks:** Deleting the 14 unreferenced legacy assets ([`V_A039`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/V_A039_UNREFERENCED_ASSET_CLEANUP_LIST.md)) could break soft object references or unmapped level actors, echoing [`KI-188`](file:///c:/UnrealProject/OneBossFight/Documentation/KNOWN_ISSUES.md#L301). | High | Low | Cooking & Packaging | Held in `WAITING ON OWNER` status. No deletion occurs without explicit owner approval and passing `Package.ps1 -G044CookManifest`. | `V-A039`, `W-A019` |
| **RSK-ART-002** | **Audio SoundMix Push/Pop Imbalance:** If `Mix_ParrySlowMo` is pushed during parry dilation but encounter resets or player dies before the 0.500 s timer expires, bus remains ducked -10 dB. | High | Medium | Gameplay Audio | Lifetimes anchored to encounter reset broadcasts: `URPGPlayerParry` and `URPGSevarogDirector::ResetEncounter` explicitly execute pop on reset. | `V-A052`, `W-A007` |
| **RSK-ART-003** | **Texture VRAM Over-Allocation at 1080p:** Environment textures in staged build occupy > 1.8 GB disk ([`V_A066:28`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/V_A066_PACKAGE_SIZE_PROPOSALS_REVIEW.md#L28)). On 8 GB baseline (RTX 2060 Super), 4K textures risk VRAM thrashing with Lumen. | Medium | High | Frame Pacing & Hitching | Clamp `TEXTUREGROUP_World` max LOD resolution to 2048 in `DefaultEngine.ini`. Saves `~1.2 GB` disk and `~600 MB` VRAM with 0 loss at 1080p. | `V-A066`, `W-A018` |
| **RSK-ART-004** | **Translucent Fog Card Overdraw Hitching:** Multiple overlapping `M_FogCard` planes create 3.2x overdraw at arena perimeter ([`V_A026:24`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/V_A026_MATERIAL_COST_AUDIT.md#L24)), causing 1.5–2.0 ms frame spikes at grazing camera angles. | Medium | Medium | GPU Frame Time | Implement distance-based pixel-depth fade and clamp emitter bounds in Niagara. | `V-A026`, `V-A028` |
| **RSK-ART-005** | **Nanite Lightmap UV Artifacts:** Attempting static lighting baking on Nanite meshes creates seam tearing and invalidates dynamic cloud shadows ([`V_A024:18`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/V_A024_LIGHT_BAKING_FEASIBILITY.md#L18)). | High | Low | Visual Quality & Memory | Formally rejected static baking. Project is locked to dynamic Lumen with CVar profile gating (L1/L2) yielding 4.5–6.5 ms relief. | `V-A024`, `DECISIONS.md` |
| **RSK-ART-006** | **Asset Path Case Sensitivity Discrepancies:** Test assertions or script matchers expecting exact case matches fail against UE's case-insensitive `FString` / `FName` system ([`Documentation/TEAM_MAILBOX.md:23985`](file:///c:/UnrealProject/OneBossFight/Documentation/TEAM_MAILBOX.md#L23985), `[C-933]`). | Medium | Low | Test Determinism | Enforced standard `FString::operator==` across all presentation rules, test fixtures, and verification scripts. | `RPGPresentationRulesTests.cpp:30` |

---

## 2. Risk Tracking & Review Protocol

All identified risks are integrated into the automated test gate:
1. Zero unreferenced asset deletion occurs without pre-flight Asset Registry verification (`test_content_script_safety.py`).
2. Texture LOD clamping proposals will be verified via `Package.ps1` cook receipts before repository merge.
3. Lifetime symmetry for audio and presentation hooks is formally audited under Queue W task `W-A007`.
