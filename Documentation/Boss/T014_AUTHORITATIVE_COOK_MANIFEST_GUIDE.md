# Collecting authoritative package cook evidence

This is a Lead-run package step. `Scripts/Package.ps1` wraps UAT `BuildCookRun`; it stages to `Saved/StagedBuilds/Windows` (or the equivalent configured stage). Do not treat a source dependency census or the old BUILD-222 cook as evidence for a later package.

For each configuration, retain together:

1. The exact `Scripts/Package.ps1 -Configuration Shipping` or `Development` command, console transcript, UAT log path, exit code, and build identifier.
2. The staged UFS file inventory at `Saved/StagedBuilds/Windows/Manifest_UFSFiles_Win64.txt` (or the configured staging root). This proves which files UAT placed in the stage; by itself it does not prove `/Game` package identities.
3. The cooked Asset Registry at `Saved/Cooked/Windows/OneBossFight/Metadata/DevelopmentAssetRegistry.bin` and package-store manifest at `Saved/Cooked/Windows/OneBossFight/Metadata/packagestore.manifest`. Preserve each raw file and SHA-256. They are binary artifacts; do not pass them directly to the text-log comparator.
4. An authoritative plain-text UAT cook log containing the retained `/Game/...` package entries, or a normalized JSON export derived from the package's cooked inventory. For JSON, use `Scripts/Tools/g044_cook_manifest.schema.json`; record the source artifact's SHA-256 in `source_manifest_sha256`, exact `build_id`, `configuration`, and the three role-keyed roots (`selection`, `boss`, `player`). The export's `packages` list must contain the root packages and all packages being claimed as cooked.
5. The H2 required closure list and the exact, reviewed editor-only folder roots, if any. Keep every exclusion visible in the output.

Run the offline check from the project root:

```powershell
python -I Scripts/Tools/check_g044_cook_manifest.py --required <h2-required.txt> --manifest <retained-uat-cook-log.txt> --json
```

For a normalized inventory export:

```powershell
python -I Scripts/Tools/check_g044_cook_manifest.py --required <h2-required.txt> --normalized-manifest <cook-manifest.json> --json
```

Add `--editor-only-folder /Game/Reviewed/Folder` only for a separately reviewed, explicit allowlist. A zero-missing result is a comparison of the supplied inputs; it does not itself prove which build produced the source manifest or that the game launched. Link the raw UAT/cook artifacts and their hashes beside the comparison summary.
