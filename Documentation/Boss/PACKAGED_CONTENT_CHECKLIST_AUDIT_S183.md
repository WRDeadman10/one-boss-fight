# Packaged-content checklist audit (S183)

Reviewed `Scripts/CheckStagedContent.py` against its source and staged-content inputs, then ran it against an empty manifest created under a temporary directory. No project asset, staged build, Editor, or source file was changed.

## Behavior reviewed

- The tool scans `Source/OneBossFight` C++ headers and sources for quoted `/Game/...` strings with an asset suffix, removes C++ line/block comments, derives package names, and checks for matching `.uasset` or `.umap` files under `Content` (`source_packages`, `content_file`).
- For each source asset present, it expects a lower-cased `OneBossFight/Content/...` entry in the supplied UFS manifest, using the source asset's suffix (`staged_name`). Manifest paths normalize backslashes to forward slashes. Missing/unreadable manifests fail with exit 1 and a diagnostic.
- Missing source assets and staged entries are grouped and printed by package folder; either missing set makes the final exit code 1. A complete scan returns 0.

## Temporary manifest fixture

An empty manifest in a `TemporaryDirectory` was supplied to `python Scripts/CheckStagedContent.py --manifest <temp>/empty_manifest.txt`. Result: exit 1, `referenced_asset_packages: 80`, `source_assets_present: 77`, `source_assets_missing: 3`, `manifest_entries: 0`, and `staged_assets_missing: 77`. The report named each missing package, including `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A1`; this confirms missing staged assets produce named errors. The three source-missing references were `Data/TypedABIFixtures/F1/{Montage,Sequence,Skeleton}` and were individually named as well.

## Limits

This is a static literal-reference checklist, not a complete cook dependency graph. It cannot see references held only in Blueprint/asset data, dynamically assembled paths, plugin dependencies outside the scanned module, or references that do not match the quoted path-plus-suffix pattern. A missing source asset may also be an intentional fixture reference; owners should classify such cases before treating every reported source miss as a packaging defect. The empty-manifest run proves the failure path and naming behavior, not that a real staged build contains all dependencies. Acceptance is met for the missing-asset diagnostic fixture; no packaged build was inspected.
