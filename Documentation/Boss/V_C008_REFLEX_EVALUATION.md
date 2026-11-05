# V-C008 — Reflex latency and Shipping evaluation plan

## Decision scope

This is a measurement and packaging plan, not an integration approval. NVIDIA describes Reflex Low Latency as synchronizing CPU and GPU pipelines for just-in-time rendering and eliminating queued work in GPU-bound cases; its Streamline guide lists GeForce 900-series and newer with driver 456.38+ as supported, which covers the project's RTX 2060 Super target and RTX 3060 proxy on the tested driver. Reflex is intended to reduce click-to-photon latency; it does not make the GPU render the frame faster. The Round 4 result is GPU-bound (roughly 42 ms GPU p99), so FPS/p99 alone cannot establish a Reflex benefit.

Sources: [NVIDIA Reflex overview and latency metrics](https://developer.nvidia.com/performance-rendering-tools/reflex), [Streamline Reflex integration guide](https://github.com/NVIDIA-RTX/Streamline/blob/main/docs/ProgrammingGuideReflex.md).

## Current-project evidence

- The enabled engine-level `DLSS.uplugin` is version 8.9.0 and describes DLSS Super Resolution/Ray Reconstruction/DLAA. Its modules include `DLSS`, `DLSSBlueprint`, `NGXRHI`, and `StreamlineNGXCommon`; the project has not separately enabled a `Streamline` Reflex plugin. The installed `StreamlineNGXCommon` source mentions Reflex in a comment but the local project/plugin inspection did not establish a callable Reflex control or its Shipping runtime closure.
- NVIDIA's current DLSS product page describes Reflex as among the plugin's available features, so the local descriptor/module list alone does not prove the feature is unavailable. First inspect the installed plugin's public Blueprint/C++ API and packaged DLL set; do not add another plugin until this is resolved.
- No input-to-photon or input-to-simulation baseline has been measured for this project. The benchmark's frame-time counters are insufficient for a latency claim.

## Proposed proof sequence

1. On the current UE 5.5.4 plugin installation, document the exact supported control/API, enable/disable path, availability query, and plugin/runtime files from installed first-party source and descriptors. If no supported control is exposed, stop and request an owner decision before adding or replacing a plugin.
2. Add a Development-only, optional toggle only after the API is confirmed; default must preserve today's behavior. No Shipping control or default changes in this evaluation step.
3. Establish an input-latency measurement method before comparing modes. Prefer a hardware Reflex Analyzer/LDAT capture for click-to-photon; otherwise instrument input receipt through simulation/render submission and label it as software pipeline latency, not click-to-photon. V-C041's press-to-montage-start driver is not a substitute for display latency.
4. On the same build, GPU, driver, console session, selected route, resolution, frame cap, and graphics settings, alternate Reflex Off/On for at least 20 valid samples per state. Record input-to-photon distribution (median, p95, p99), frame p99, GPU p99, CPU/GPU utilization, and measurement-device/setup details. Repeat on the RTX 2060 Super before any target-hardware claim.
5. Test support unavailable, plugin/runtime missing, and initialization failure. Off/fallback must stay safe; no Shipping launch failure or silent settings change is acceptable.
6. Compare a Development and Shipping package manifest. Record every Reflex/Streamline/NVAPI DLL or other runtime file actually required, architecture, source plugin version, license/redistribution terms, and whether the files are already supplied by the installed engine/plugin. Run the existing Shipping binary guard and packaged smoke only after Lead review/build.

## Decision gate

Recommend integration only if the supported UE 5.5.4 API is confirmed, the Shipping runtime closure and redistribution terms are documented, the measured latency distribution improves repeatably on the target GPU, and frame p99 does not regress beyond the project's 5% experiment guard. The owner decides whether the measured latency change is worth a visible setting. Until then, Reflex remains unintegrated and no low-latency default is selected.
