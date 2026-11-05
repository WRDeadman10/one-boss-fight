# U-C01p — DLSS SR mode reference (UE 5.5)

Scope: the installed NVIDIA DLSS Super Resolution plugin v8.9.0. This covers DLSS-SR and DLAA only; Ray Reconstruction, Frame Generation, Reflex, NIS and Dynamic Vibrance are outside this experiment.

## Supported modes and control

The plugin's `UDLSSMode` enum declares `Off`, `Auto`, `DLAA`, `UltraQuality`, `Quality`, `Balanced`, `Performance`, and `UltraPerformance` (`DLSSBlueprint/Public/DLSSLibrary.h:46-56`). `Auto` is explicitly a query mode, not a fixed quality preset.

| Experiment mode | Plugin mode / setting | Required Round 5 CVar arguments | Source-backed control |
|---|---|---|---|
| TSR baseline | Native UE upscaler; DLSS disabled by default | no override | Existing packaged default; preserve the clean baseline config |
| DLAA | `DLAA`, native-resolution reconstruction | `r.NGX.DLSS.Enable=1;r.ScreenPercentage=100` | UE DLSS guide p.3 gives these values; p.16 confirms 100% for DLAA |
| Quality | `Quality` | `r.NGX.DLSS.Enable=1;r.ScreenPercentage=66.7` | UE DLSS guide pp.2, 7, 16 recommends querying the mode's optimal percentage; NVIDIA's UE plugin article lists 66% as the Quality default |
| Balanced | `Balanced` | `r.NGX.DLSS.Enable=1;r.ScreenPercentage=58` | NVIDIA's UE plugin article lists 58%; the active-feature log is the runtime mode check |
| Performance | `Performance` | `r.NGX.DLSS.Enable=1;r.ScreenPercentage=50` | UE DLSS guide p.2 recommends 50–67% for DLSS; NVIDIA's UE plugin article lists 50% |

The plugin's documented controls are `r.NGX.Enable` (read-only; default 1 and command-line overrides are documented), `r.NGX.DLSS.Enable` (default 0; enables DLSS-SR/RR), and `r.ScreenPercentage`. Do not set a made-up mode CVar. In UE 5.1+, mode is selected by screen percentage; `GetDLSSModeInformation` returns the optimal value for a given `UDLSSMode` and output resolution. A future player setting should query this function rather than treat the nominal percentages above as universal. (NVIDIA, *DLSS Super Resolution UE Plugin Guide*, pp. 3, 7, 12, 16.)

The plugin guide p.3 documents the `LogDLSS: NVIDIA NGX DLSS supported 1` line and the optional DLSS on-screen indicator. The support line proves capability, not activation. The plugin's active feature creation log is the mode-bearing evidence: `NGXRHI.cpp` logs `Creating   NGX DLSS Feature %s` when registering a live feature; `NGXRHI.h` formats the descriptor with `NGXPerfQuality=<mode>` and `DenoiseMode=<mode>` (`NGXRHI.cpp:653`, `NGXRHI.h:102-177`). Require that line in every DLSS receipt and match `NGXPerfQuality` to the planned mode; require `DenoiseMode=Off` for SR/DLAA. `stat DLSS` (guide p.8) is supplementary evidence that a DLSS feature is allocated, but it does not name the quality mode.

## References

- NVIDIA, *DLSS Super Resolution UE Plugin Guide*, installed v8.9.0 copy: `C:\UnrealProject\2026.10.16_UE5.5_DLSS4.5Plugin_v8.9.0\Documentation\DLSS_Super_Resolution_UE_Plugin_Guide.pdf`, pp. 2–3, 7–8, 12, 16–17.
- NVIDIA, *Getting Started with NVIDIA DLSS 4 for Unreal Engine*, installed plugin bundle, p. 2 (SR and DLAA behavior; frame generation hardware constraints).
- NVIDIA, [Tips: Getting the Most out of the DLSS Unreal Engine Plugin](https://developer.nvidia.com/blog/tips-getting-the-most-out-of-the-dlss-unreal-engine-4-plugin/) (nominal default input resolutions: Quality 66%, Balanced 58%, Performance 50%). This older article supplies starting percentages only; the installed plugin's active log and queried mode determine whether a run actually used the intended mode.
- Installed plugin source: `C:\Program Files\Epic Games\UE_5.5\Engine\Plugins\Marketplace\DLSS\Source\DLSSBlueprint\Public\DLSSLibrary.h`; `...\NGXRHI\Public\NGXRHI.h`; `...\NGXRHI\Private\NGXRHI.cpp`.

No benchmark or runtime session was performed by Codex. These values form an experiment plan, not a selected product default.
