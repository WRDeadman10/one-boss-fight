# V-C016 — UE 5.5.4 cloud/sky CVar candidates and controlled test

## Source audit (runtime help still required)

The earlier `r.VolumetricCloud.ViewRaySampleCountScale` proposal is invalid: that name is not registered in the installed UE 5.5.4 source. The local source defines these candidate controls in `Engine/Source/Runtime/Renderer/Private/VolumetricCloudRendering.cpp`:

| Exact CVar | Default in source | What it changes | Runtime status |
|---|---:|---|---|
| `r.VolumetricCloud.ViewRaySampleMaxCount` | 768 | Maximum samples along primary view rays | Source-defined; confirm with Development `help` before use |
| `r.VolumetricCloud.Shadow.ViewRaySampleMaxCount` | 80 | Maximum samples along cloud shadow rays | Source-defined; confirm with Development `help` before use |
| `r.VolumetricCloud.ReflectionRaySampleMaxCount` | 80 | Maximum samples along reflection rays | Source-defined; confirm with Development `help` before use |
| `r.VolumetricCloud.Shadow.ReflectionRaySampleMaxCount` | 24 | Maximum samples along cloud shadow reflection rays | Source-defined; confirm with Development `help` before use |
| `r.VolumetricCloud.Shadow.SampleAtmosphericLightShadowmap` | 1 | Whether cloud shadows sample atmospheric-light shadow maps | Source-defined; confirm with Development `help` before use |
| `r.SkyLight.RealTimeReflectionCapture` | not established by this cloud source audit | Round 5 previously found it through Development preflight | Re-run `help` on the Round 6 kit; no value change proposed |

The first two exact names correct the old no-dot `ShadowViewRaySampleMaxCount` spelling in the Round 3 experiment script. The script is corrected, but Codex did not run Unreal or a console help command. This is source confirmation, not runtime registration/readback or visual approval.

## Proposed experiment

Only after the Round 6 first-run telemetry witness, Round 6 accepted mode, and Development `help` recognition: keep build, GPU/driver, route, resolution, mode, primary fraction, and camera/fight schedule fixed. Compare the baseline with one CVar at a time (view samples first; shadow samples separately), use a repeat of the baseline around the treatment, and collect at least three valid treatment runs. Record CVar readback/log, active-upscaler witness, average/p95/p99 and GPU average/p99, a steady-state ProfileGPU sample, and matched screenshots/video for cloud silhouette, banding, temporal shimmer, shadow softness and contact with the arena. Stop on UNKNOWN, missing readback, invalid GPU, or baseline drift above 5%. Do not stack both sample limits or select a default from projected milliseconds.

Source excerpts: UE 5.5.4 `VolumetricCloudRendering.cpp:52-58,84-90,161-166,218-223`; `r.DynamicRes.OperationMode` default 0 is declared in `Engine/Source/Runtime/Engine/Private/UnrealEngine.cpp:487-490`. UE source helps identify candidates; only the owner Development kit's help/readback can satisfy the queue's runtime-help acceptance.
