# Supplemental primary-source notes for U-C01p — DLSS 4.5 (UE 5.5)

Scope: extra primary-source and UE 5.5 compatibility notes supplementing the canonical `U-C01P_DLSS_MODE_REFERENCE.md`. Documentation only; no render settings or project configuration changed.

Sources read from `C:\UnrealProject\2026.10.16_UE5.5_DLSS4.5Plugin_v8.9.0`:

- `Documentation/DLSS_Super_Resolution_UE_Plugin_Guide.pdf` (plugin guide, v8.9.0 package).
- `Getting Started with NVIDIA DLSS 4 for Unreal Engine.pdf` (package primer, v8.7.0; PDF cover says UE 5.5 is deprecated, page 1).

## Supported app paths and exact controls

| Intent | Documented API/control | Source |
|---|---|---|
| Enable SR/DLAA at runtime | `r.NGX.DLSS.Enable 1`; `r.NGX.Enable` is read-only (default 1), command-line overrides are `-ngxenable` / `-ngxdisable` | Plugin guide, p. 7, “Enabling DLSS-SR/DLAA (Plugin Side)” |
| Select an explicit SR quality mode | Query `Get Supported DLSS-SR Modes` / `Is DLSS-SR Mode Supported`; call `Get DLSS-SR Mode Information` for the selected mode, set `r.ScreenPercentage` to its returned optimal value, then call `Enable DLSS-SR` | Plugin guide, p. 7, “Enabling DLSS-SR/DLAA (Plugin Side)” |
| Select DLAA | Use the DLSS blueprint library's DLAA support and set screen percentage to 100; the quickstart also requires `r.NGX.Enable 1`, `r.NGX.DLSS.Enable 1`, `r.ScreenPercentage 100` | Plugin guide, pp. 3, 7, 12, 16 |
| Select Off/Auto | For Auto, call `Get DLSS-SR Mode Information` with the documented fake `Auto` mode and the screen resolution; set `r.ScreenPercentage` only if returned nonzero, then call `Enable DLSS-SR`. Off disables DLSS-SR. | Plugin guide, p. 7; p. 16 |
| Verify it is active | Inspect Output Log for `LogDLSS: NVIDIA NGX DLSS supported 1`; unsupported GPU/driver configurations do not activate DLSS | Plugin guide, pp. 3, 4, 15 |

The plugin guide explicitly recommends the `UDLSSLibrary` Blueprint/C++ functions over directly setting console variables (p. 12). The legacy `SetDLSSMode` and `EnableDLAA` Blueprint functions are deprecated; use `EnableDLSS` plus the appropriate `r.ScreenPercentage` (pp. 15–16).

## Quality mode names and scale values

Expose only modes returned by `Get Supported DLSS-SR Modes` and supported by `Is DLSS-SR Mode Supported`. The guide's workflow obtains the current plugin's optimal screen percentage from `Get DLSS-SR Mode Information`; it does not prescribe one fixed percentage per named mode. Do not hard-code a guessed scale table. DLAA is the documented exception: 100% screen percentage. The quickstart recommends 50–67% for DLSS and 100% for DLAA (p. 2), but this range is not a mode-to-percentage mapping.

The Round 5 experiment should log the mode enum/name and returned optimal percentage for every run, then verify activation using the `LogDLSS` line. A run without the activation evidence is invalid, even if its requested mode was configured.

## UE 5.5 compatibility caveat

The Getting Started PDF cover identifies v8.7.0 as supporting UE 5.6, 5.7, and 5.8, with UE 5.5 deprecated (p. 1). The installed package is v8.9.0 and the project/engine BUILD-223 is the compatibility gate; the primer does not establish v8.9.0's UE 5.5 support. Do not infer compatibility from this reference. The plugin guide has a “UE 5.5 and older” API appendix; use that appendix when reviewing any C++ API proposal.
