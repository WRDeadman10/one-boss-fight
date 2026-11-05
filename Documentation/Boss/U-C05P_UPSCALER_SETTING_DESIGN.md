# U-C05p — Player-facing upscaler setting design

Status: design and test plan only. No Shipping UI, default, or runtime behavior is changed here. The selected default stays undecided until Round 5 results and image-quality review are available.

## Proposed options

| UI option | Runtime behavior | Availability |
|---|---|---|
| Off (TSR) | Disable DLSS-SR and retain the existing UE TSR path | Always |
| DLAA | Enable DLSS-SR at native resolution | Only when `IsDLSSModeSupported(DLAA)` is true |
| Quality | Enable DLSS-SR using the queried Quality screen percentage | Only when supported |
| Balanced | Enable DLSS-SR using the queried Balanced screen percentage | Only when supported |
| Performance | Enable DLSS-SR using the queried Performance screen percentage | Only when supported |

Use `UDLSSLibrary::QueryDLSSSupport`, `IsDLSSModeSupported`, `GetSupportedDLSSModes`, `GetDLSSModeInformation`, `EnableDLSS`, and `IsDLSSEnabled`. Query the preferred percentage for the active output resolution; do not hard-code screen percentages in a user-facing setting. The plugin guide recommends this API route over setting CVars directly (pp. 7, 12, 16); source declarations are in the installed plugin `DLSSLibrary.h`.

On a non-NVIDIA or unsupported GPU/driver/platform, hide or disable DLSS choices and automatically use the current TSR path. If a saved DLSS option becomes unsupported after a hardware/driver change, fall back to TSR for that session and leave the user's saved choice intact so reconnecting supported hardware restores it.

## Default selection rule after Round 5

Keep the UI default unassigned until the owner/Lead reviews Phase 1 measurements and image-quality notes. Choose the highest-performing DLSS mode that passes the runtime-mode witness on all three runs, stays within the agreed p99 guard against TSR, and has no unacceptable ghosting/shimmer/temporal artifact note. If no DLSS option qualifies, use Off (TSR). DLAA is evaluated for image quality even if it is slower; it should not be described as the performance default without measurements.

## Acceptance tests for a later implementation task

1. NVIDIA RTX with supported driver: each option maps to the exact `UDLSSMode`, queries the current resolution, applies the returned percentage and verifies `IsDLSSEnabled`.
2. DLAA uses native resolution; the active-feature log reports the DLAA quality token and `DenoiseMode=Off`.
3. Unsupported GPU/driver/platform: DLSS options are unavailable and TSR remains active without a startup error.
4. Persisted DLSS choice with newly unsupported hardware: the live session falls back to TSR, and the stored choice is not overwritten.
5. Resolution change: query mode information again and apply the new optimal percentage.
6. Reopening graphics settings reflects the active option and support state without toggling render settings during gameplay.

Implementation is a later C-895 task and requires Lead go, build/package validation, and visual review. This document makes no product default selection.
