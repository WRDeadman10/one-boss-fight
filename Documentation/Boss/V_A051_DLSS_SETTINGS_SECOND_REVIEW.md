# V-A051: Second Review of V-C006 / V-C007 (DLSS Settings & GameUserSettings Persistence)

**Author:** Antigravity (Lane A)  
**Date:** 2026-11-06  
**Reference Tasks:** `V-C006` (DLSS player setting), `V-C007` (Settings persistence), `U-C05p` design, `[X-1289]`, `[C-926]`, `[C-928]`

---

## 1. Executive Summary & Review Verdict

Codex's disposition on `V-C006` and `V-C007` in `[X-1289]`—holding both tasks as `WAITING ON OWNER/LEAD` pending Round 6 mode selection and owner image-quality review—was **accepted by Lead Claude in `[C-926]`**.

This second review audits the architectural foundation established in [`U-C05P_UPSCALER_SETTING_DESIGN.md`](./U-C05P_UPSCALER_SETTING_DESIGN.md) against production Shipping requirements, engine plugin boundaries (`DLSS.uplugin` v8.9.0), fallback semantics, and `GameUserSettings` serialization rules. The proposed design is technically sound and adheres strictly to the project's zero-regression and default-parity mandates.

---

## 2. API & Architecture Verification

### 2.1 Plugin API vs Raw CVar Control
`U-C05p` correctly mandates calling the official `UDLSSLibrary` API functions rather than mutating console variables directly during gameplay:
- `UDLSSLibrary::QueryDLSSSupport()`: Queries hardware, driver, and platform capability.
- `UDLSSLibrary::IsDLSSModeSupported(UDLSSMode Mode)`: Validates support for individual quality modes (`DLAA`, `Quality`, `Balanced`, `Performance`).
- `UDLSSLibrary::GetDLSSModeInformation(...)`: Retrieves recommended screen percentages dynamically for the current display resolution.
- `UDLSSLibrary::EnableDLSS(bool bEnabled)`: Handles viewport attachment and primary screen percentage clamp.

> [!IMPORTANT]
> **No Hardcoded Screen Percentages:** Hardcoding percentage factors (e.g. 66.7% for Quality) violates dynamic resolution and window resizing conventions. The official DLSS SDK adjusts optimal fractions depending on whether the target output is 1080p, 1440p, or 4K. Relying exclusively on `GetDLSSModeInformation` guarantees vendor-certified image reconstruction.

### 2.2 Decoupling from Reflex / Streamline
`V-C008` noted that NVIDIA Reflex / Streamline integration should remain strictly orthogonal to DLSS-SR. Reflex operates in `StreamlineReflex`, whereas DLSS-SR operates in `DLSS`. Keeping `V-C006` focused exclusively on Super Resolution avoids introducing external DLL dependencies (`sl.interposer.dll`, `sl.reflex.dll`) into Shipping package verification before owner consent.

---

## 3. Fallback & Hardware Heterogeneity Rules

| Scenario | Persisted Config Value | Live Runtime Setting | Active Upscaler | Fallback Behavior |
|---|---|---|---|---|
| **Supported RTX GPU (Default Case)** | `Quality` | `Quality` | `DLSS` | DLSS-SR enabled at queried screen percentage. |
| **Non-NVIDIA GPU (AMD/Intel)** | `Quality` (preserved) | `Off` | `TSR` | DLSS options disabled in UI; falls back cleanly to TSR 100% without corrupting saved user preference. |
| **Unsupported Driver / Outdated RTX** | `Quality` (preserved) | `Off` | `TSR` | Gracefully falls back to TSR; logs informational notice once at startup (`LogRPGPerf`). |
| **GPU Swap / Portability** | `Quality` (saved on desktop) | Evaluated on boot | Auto | If launched on laptop with unsupported iGPU, runs TSR. If swapped back to RTX, DLSS automatically resumes without requiring manual re-selection. |

---

## 4. `GameUserSettings` Persistence Contract

1. **Storage Section:** Settings must serialize under `[/Script/OneBossFight.RPGGameUserSettings]` in `Saved/Config/Windows/GameUserSettings.ini`.
2. **Failure Robustness:** If `GameUserSettings.ini` is corrupted, missing, or read-only, deserialization must default to `Off (TSR)`, preserving complete D5 baseline parity.
3. **Application Timing:** Upscaler mode must be applied during `PostInitProperties` or explicit `ApplySettings()` calls, never ticking per-frame or re-initializing the viewport during active combat encounters.

---

## 5. Decision Gates for Implementation

Implementation (`V-C006` / `V-C007`) may proceed only when the following owner and measurement gates are cleared:
1. **Round 6 Performance Data:** Confirmation that DLSS Quality or Balanced achieves p99 <= 16.67 ms (60 FPS) on the reference RTX 2060 Super test rig.
2. **Owner Visual Acceptance:** Confirmation that temporal stability on Sevarog's cloth sim, foliage wind, and weapon trail particles is visually acceptable under DLSS compared to native TSR.
3. **Packaging Cleanliness:** Zero link-time or staging errors in Shipping configuration (`-G044RequiredFile` gate verified).
