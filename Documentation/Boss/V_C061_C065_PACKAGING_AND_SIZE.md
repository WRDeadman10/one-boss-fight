# Queue V C061–C065 — package evidence and size review

Status: C061 and C064 need fresh Lead package evidence; C062 procedure is ready; C063 opt-in check is implemented and fixture-verified; C065 is proposal-only. No package build or game launch was performed by Codex.

## C061 — Shipping smoke receipt (Lead-run)

`Scripts/PackagedSmoke.ps1` launches the staged executable with `-nosound -log`, checks that the process stays alive for the requested interval, then uses `CheckShippingBinary.py` when Shipping correctly emits no runtime log. Preserve the exact command, package/build identity, executable SHA-256, full console output, exit code, and Shipping binary-check output together. Validate the captured stdout with:

```powershell
python -I Scripts/Tools/check_packaged_smoke_receipt.py <captured-stdout.txt> --configuration Shipping --exit-code <script-exit-code>
```

Run the smoke explicitly as Shipping, for example `Scripts/PackagedSmoke.ps1 -Configuration Shipping -ExePath <Shipping-stage>\OneBossFight.exe`, with stdout redirected to the retained receipt file.

The existing receipt fixtures cover missing, duplicate, contradictory, and wrong-configuration tokens. A real Shipping run and receipt are still pending. The current local staged directory is not accepted as Shipping evidence because its target configuration/build identity has not been established here.

## C062 — Development recovery smoke procedure

First create a fresh Development package with `Scripts/Package.ps1 -Configuration Development`. Launch the arena directly, with a separate output log for each arm:

```text
OneBossFight.exe /Game/OneBossFight/Levels/L_SevarogArena -nosound -log -RPGBenchmark -H019EncounterDefinition=/Game/OneBossFight/Data/DoesNotExist_C062
OneBossFight.exe /Game/OneBossFight/Levels/L_SevarogArena -nosound -log -RPGBenchmark -H019EncounterDefinition=/Game/OneBossFight/VFX/NS_Boss_ShockwaveRing.NS_Boss_ShockwaveRing
```

The first arm requests an absent asset. The second supplies an existing, always-cooked Niagara asset where an encounter-definition object is required, exercising the wrong-class path without altering assets. Capture executable hash, Development package identity, exact command, runtime log, process exit/timeout, screenshot of the arena state, and the activation diagnostic. Expected source contract: the request is treated as selected startup, emits `EncounterSelection.AssetLoad`, destroys any partial binding, disables the selected boss/removes owned legacy components, and leaves player-side additions available. This is a recovery/fail-closed check, not a successful encounter. Lead must verify the precise runtime log and visual state; Codex did not launch the package.

## C063 — Package script G044 + VFX check

`Scripts/Package.ps1` now has an opt-in post-UAT check. Supplying both `-G044RequiredFile` (reviewed H2 closure list) and `-G044CookManifest` (normalized export) runs `Scripts/Tools/check_packaged_g044_cook.py`; supplying only one is rejected. The checker validates manifest schema/roots and requested configuration, then requires every H2 closure path and every `.uasset`/`.umap` under `Content/OneBossFight/VFX` to appear in the cooked package list. Missing closure/VFX paths fail the package command. No implicit editor-only exclusions are applied.

The comparison report hashes the supplied closure and manifest, and carries the manifest build ID/configuration. The package operator still owns the provenance link between that manifest and the just-completed UAT package; matching configuration alone does not establish build identity. Focused offline fixtures: 5/5 pass, including nested VFX, missing closure, missing VFX, configuration mismatch, and Package.ps1 wiring. PowerShell parser check passes. No package was built.

## C064 — staged size inventory (partial; not an asset top-50)

Read-only inventory of `Saved/StagedBuilds/Windows` at this review: 60 files, 4,351,585,036 bytes total. The largest file is `OneBossFight/Content/Paks/OneBossFight-Windows.ucas` at 3,249,584,880 bytes; next are the 405,319,680-byte PDB and 305,538,048-byte game executable. The staged root has UFS/non-UFS/debug manifests dated 2026-11-05 18:40 local time. The target configuration and a build ID tied to this stage are not established by those filenames/timestamps.

The container format keeps individual cooked asset sizes inside the IoStore container; the stage inventory cannot support an honest top-50 per-asset ranking. Therefore this report records the largest 50 stage files as file-level inventory below, not as a top-50 asset list. C064 remains partial until Lead exports per-package cooked sizes from the matching build and records the configuration/build identity.

| Rank | Bytes | Staged file |
|---:|---:|---|

| 1 | 3249584880 | `OneBossFight/Content/Paks/OneBossFight-Windows.ucas` |
| 2 | 405319680 | `OneBossFight/Binaries/Win64/OneBossFight.pdb` |
| 3 | 305538048 | `OneBossFight/Binaries/Win64/OneBossFight.exe` |
| 4 | 93504624 | `Engine/Plugins/Marketplace/DLSS/Binaries/ThirdParty/Win64/Development/nvngx_dlssd.dll` |
| 5 | 59383920 | `Engine/Plugins/Marketplace/DLSS/Binaries/ThirdParty/Win64/Development/nvngx_dlss.dll` |
| 6 | 58956912 | `Engine/Plugins/Marketplace/DLSS/Binaries/ThirdParty/Win64/nvngx_dlss.dll` |
| 7 | 48343664 | `Engine/Plugins/Marketplace/DLSS/Binaries/ThirdParty/Win64/nvngx_dlssd.dll` |
| 8 | 18287840 | `Engine/Binaries/Win64/EOSSDK-Win64-Shipping.dll` |
| 9 | 17444920 | `Engine/Binaries/ThirdParty/Vulkan/Win64/VkLayer_khronos_validation.dll` |
| 10 | 14042432 | `OneBossFight/Binaries/Win64/DML/DirectML.dll` |
| 11 | 13573448 | `Engine/Plugins/NNE/NNERuntimeORT/Binaries/ThirdParty/Onnxruntime/Win64/onnxruntime.dll` |
| 12 | 10759813 | `OneBossFight/Content/Paks/OneBossFight-Windows.pak` |
| 13 | 10192952 | `Engine/Binaries/ThirdParty/Vulkan/Win64/VkLayer_api_dump.dll` |
| 14 | 5794624 | `OneBossFight/Binaries/Win64/D3D12/d3d12SDKLayers.dll` |
| 15 | 5453160 | `Engine/Binaries/ThirdParty/NVIDIA/NVaftermath/Win64/GFSDK_Aftermath_Lib.x64.dll` |
| 16 | 5395052 | `Engine/Content/SlateDebug/Fonts/LastResort.ttf` |
| 17 | 3975736 | `Engine/Binaries/ThirdParty/Vulkan/Win64/VkLayer_gfxreconstruct.dll` |
| 18 | 3355456 | `OneBossFight/Binaries/Win64/D3D12/D3D12Core.dll` |
| 19 | 3010560 | `OneBossFight/Binaries/Win64/tbb.pdb` |
| 20 | 2557648 | `Engine/Binaries/ThirdParty/MsQuic/v220/win64/msquic.dll` |
| 21 | 2478176 | `OneBossFight/Content/Paks/global.ucas` |
| 22 | 2243256 | `Engine/Binaries/ThirdParty/DbgHelp/dbghelp.dll` |
| 23 | 1735448 | `Engine/Binaries/ThirdParty/Vorbis/Win64/VS2015/libvorbis_64.dll` |
| 24 | 1723031 | `OneBossFight/Content/Paks/OneBossFight-Windows.utoc` |
| 25 | 1544248 | `Engine/Binaries/ThirdParty/Vulkan/Win64/VkLayer_khronos_profiles.dll` |
| 26 | 1427428 | `Manifest_UFSFiles_Win64.txt` |
| 27 | 1126400 | `OneBossFight/Binaries/Win64/tbbmalloc.pdb` |
| 28 | 868720 | `Engine/Binaries/ThirdParty/Windows/XAudio2_9/x64/xaudio2_9redist.dll` |
| 29 | 799254 | `OneBossFight/Content/Splash/Splash.bmp` |
| 30 | 372504 | `OneBossFight/Binaries/Win64/boost_program_options-mt-x64.dll` |
| 31 | 346624 | `OneBossFight.exe` |
| 32 | 335928 | `Engine/Binaries/ThirdParty/Vulkan/Win64/VkLayer_khronos_synchronization2.dll` |
| 33 | 259568 | `Engine/Content/Renderer/TessellationTable.bin` |
| 34 | 255768 | `OneBossFight/Binaries/Win64/boost_regex-mt-x64.dll` |
| 35 | 234768 | `OneBossFight/Binaries/Win64/tbb.dll` |
| 36 | 213784 | `OneBossFight/Binaries/Win64/boost_python311-mt-x64.dll` |
| 37 | 187346 | `Engine/Extras/GPUDumpViewer/GPUDumpViewer.html` |
| 38 | 161560 | `OneBossFight/Binaries/Win64/boost_filesystem-mt-x64.dll` |
| 39 | 97711 | `Engine/Binaries/ThirdParty/Vulkan/Win64/VkLayer_khronos_validation.json` |
| 40 | 95512 | `OneBossFight/Binaries/Win64/boost_thread-mt-x64.dll` |
| 41 | 79376 | `Engine/Binaries/ThirdParty/Windows/WinPixEventRuntime/x64/WinPixEventRuntime.dll` |
| 42 | 76560 | `OneBossFight/Binaries/Win64/tbbmalloc.dll` |
| 43 | 70424 | `Engine/Binaries/ThirdParty/Ogg/Win64/VS2015/libogg_64.dll` |
| 44 | 69912 | `OneBossFight/Binaries/Win64/boost_iostreams-mt-x64.dll` |
| 45 | 69719 | `Engine/Binaries/ThirdParty/Vulkan/Win64/VkLayer_khronos_profiles.json` |
| 46 | 59160 | `Engine/Binaries/ThirdParty/Vorbis/Win64/VS2015/libvorbisfile_64.dll` |
| 47 | 56600 | `OneBossFight/Binaries/Win64/boost_chrono-mt-x64.dll` |
| 48 | 38680 | `OneBossFight/Binaries/Win64/boost_atomic-mt-x64.dll` |
| 49 | 30992 | `OneBossFight/Binaries/Win64/boost_system-mt-x64.dll` |
| 50 | 27194 | `Engine/Binaries/ThirdParty/Vulkan/Win64/VkLayer_gfxreconstruct.json` |

## C065 — package-size proposals (list only)

- Request a per-package cooked-size export for the current matching build before targeting specific assets; one `.ucas` total cannot identify which assets dominate.
- Review the shipping cook graph for unused content, then remove or exclude only after reference proof and owner approval. The staged UFS list is not itself an unused-asset proof.
- Evaluate texture resolution/mip policy and audio compression using asset-level size and visual/audio acceptance checks; avoid broad quality reductions based on container size alone.
- Compare plugin/runtime payloads across Development and Shipping manifests. The current staged tree includes a 405 MB PDB and Development-labeled DLSS binaries; verify configuration-specific staging rules and archive required symbols separately before proposing a distribution change.
- Keep gameplay and visual settings unchanged until a comparable package measurement and required owner approval exist.

No cleanup, config change, asset mutation, or package-size optimization was applied.
