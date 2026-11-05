# Staged content manifest coverage audit (D79)

Date: 2026-11-03. Read-only review of `Scripts/CheckStagedContent.py`, package cook configuration, and the staged UFS manifest contract; no cook/package was run.

## What the checker covers

- Scans only `Source/OneBossFight/**/*.cpp` and `*.h` for literal quoted `/Game/...` strings after regex-based comment stripping.
- Treats a string as a package only when its final path segment contains a dot; strips the object suffix to get the package name. The checker does not resolve dynamic asset paths, macros, Blueprint references, config references, data assets, or arbitrary plugin references.
- Looks for the package in project `Content/` as `.uasset` or `.umap`; it does not inspect project/plugin asset registries or generated content.
- Compares existing project assets against `Manifest_UFSFiles_Win64.txt` by expected lowercased path `OneBossFight/Content/<relative package>.<uasset|umap extension>`.
- Returns 1 for missing manifest, unreadable/changing manifest, source asset missing from project Content, or a source asset missing from the staged UFS path; success 0 otherwise.

## Coverage blind spots

- Plugin assets, including the many `DirectoriesToAlwaysCook` entries in `Config/DefaultGame.ini`, are not discovered from source or verified against their plugin mount points by this checker. The cook configuration includes `/Game/AdvancedARPGCombat/...`, `/Game/ParagonSevarog`, and other mounted roots beyond this project's `Content/` tree; those are separate cook inputs and need their own staged manifest evidence.
- Generated content is not enumerated from source. Generated assets only appear in the check if they have a literal source reference whose cooked package is represented at the assumed project Content UFS path. Generated Blueprint/data-asset dependencies without such literals are outside scope.
- The tool checks package-file presence, not all package sidecars, dependency closure, loadability, or runtime use. It does not prove that every cooked asset is referenced, and unreferenced cooked content is not reported.
- Only `/Game/` literals are matched; plugin mount paths and dynamically composed object paths are absent by construction. Regex scanning is not a C++ parser, despite stripping comments first.

The checker is a source-literal spot check for project Content packages, not a complete staged-content inventory. Shipping content coverage remains dependent on cook output/manifest inspection and packaged runtime evidence.
