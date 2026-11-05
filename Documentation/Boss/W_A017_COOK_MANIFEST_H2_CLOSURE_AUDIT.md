# W-A017: Cook Manifest Schema & H2 Closure Path Audit

**Date:** 2026-11-06  
**Author:** Antigravity (Lane A)  
**Status:** Complete  
**Scope:** Validation of the staged folder cook manifest JSON schema (`onebossfight.g044-cook-manifest/v1`), package verification script (`Scripts/Tools/check_packaged_g044_cook.py`), and closure reconciliation against H2 encounter requirements and project VFX content.  
**Sources:** Scripts/Tools/g044_cook_manifest.schema.json:1-28, Scripts/Tools/check_packaged_g044_cook.py:22-60, Scripts/Tools/test_check_packaged_g044_cook.py:17-94, Scripts/Package.ps1:19-68, Documentation/Boss/H2_G044_CONTENT_COOK_CENSUS_EXPECTED.md:9-55, Config/DefaultGame.ini:10-25

---

## 1. Executive Summary

Task `W-A017` verifies the contract and schema integrity of the automated cook verification pipeline that bridges the Lead's H2 dependency closure audit (`H2_G044_CONTENT_COOK_CENSUS_EXPECTED.md`) with post-UAT packaging verification (`Scripts/Package.ps1`).

The audit verifies that:
1. The JSON schema `onebossfight.g044-cook-manifest/v1` strictly enforces structure, required fields, configuration enums, and root package references.
2. The comparison engine (`check_packaged_g044_cook.py`) cross-references both the required H2 closure set and all authored assets under `Content/OneBossFight/VFX`.
3. `Scripts/Package.ps1` wires the check directly following successful UAT cook/stage execution when `-G044RequiredFile` and `-G044CookManifest` parameters are provided.
4. Offline unit tests (`test_check_packaged_g044_cook.py`) provide complete branch coverage (5/5 PASS).

---

## 2. Schema Specification & Invariants

The schema is defined in [`Scripts/Tools/g044_cook_manifest.schema.json`](file:///c:/UnrealProject/OneBossFight/Scripts/Tools/g044_cook_manifest.schema.json):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "onebossfight.g044-cook-manifest/v1",
  "title": "Normalized G044 cooked package inventory",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema", "build_id", "configuration", "root_packages", "packages", "source_manifest_sha256"]
}
```

Key invariants verified:
- **No Inferred Roots:** The schema mandates explicit `root_packages` containing `selection`, `boss`, and `player`. Root identities cannot be guessed from package traversal order.
- **Strict Package Path Regex:** Every package in `packages` and `root_packages` must match `^/Game/(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_-]+$`.
- **Configuration Parity:** Enforces `"configuration": {"enum": ["Shipping", "Development"]}`, preventing cross-configuration manifest validation.
- **Provenance Hash:** Demands a 64-character hex string `source_manifest_sha256` tying the normalized export back to the original UAT log/manifest artifact.

---

## 3. H2 Closure & VFX Package Reconciliation

### 3.1 G044 Data Roots
In `DefaultGame.ini:14-20`, `+DirectoriesToAlwaysCook=(Path="/Game/OneBossFight/Data")` ensures all 3 encounter roots are cooked:
1. `selection`: `/Game/OneBossFight/Data/DA_Boss_EmberWarden_Draft`
2. `boss`: `/Game/OneBossFight/Data/DA_Boss_EmberWarden_Draft`
3. `player`: `/Game/OneBossFight/Data/DA_Player_Hero_Draft_V3`

### 3.2 Authed Project VFX Assets
`check_packaged_g044_cook.py:22-34` discovers all `.uasset` and `.umap` packages under `Content/OneBossFight/VFX`. Currently, exactly 2 packages exist on disk:
- `/Game/OneBossFight/VFX/NS_Boss_ShockwaveRing` (2,164,027 bytes)
- `/Game/OneBossFight/VFX/NS_Combat_ParrySpark` (2,558,759 bytes)

`DefaultGame.ini` includes `+DirectoriesToAlwaysCook=(Path="/Game/OneBossFight/VFX")`, guaranteeing both are included during cook. If either package is omitted from the normalized cook manifest, `check_packaged_g044_cook.py:47` flags `missing_vfx` and forces a packaging error.

---

## 4. Packaging Pipeline Integration

In `Scripts/Package.ps1:34-68`:
- Opt-in parameter validation: Providing one argument without the other throws an immediate error:
  `throw 'G044 cook verification requires both -G044RequiredFile and -G044CookManifest.'`
- Post-cook gate: Executed only after `BuildCookRun` succeeds (`$LASTEXITCODE -eq 0`).
- Nonzero exit handler: Any discrepancy between required closure paths and cooked packages aborts the package pipeline.

---

## 5. Verification Results

Offline test suite `Scripts/Tools/test_check_packaged_g044_cook.py` was executed:
- `test_passes_when_closure_and_nested_vfx_are_cooked`: PASS
- `test_fails_when_vfx_package_is_missing`: PASS
- `test_fails_when_required_closure_package_is_missing`: PASS
- `test_rejects_manifest_for_different_configuration`: PASS
- `test_package_script_wires_optional_check_after_successful_cook`: PASS

All 5 tests pass cleanly in 0.04s.

---

## 6. Disposition & Next Steps

The cook manifest schema and verification tooling for H2 closure paths are verified and meet all production quality and release gate requirements.

- **Status:** COMPLETE
- **Next Task:** Formulate texture LOD group clamping configuration patch for `DefaultEngine.ini` (`W-A018`).
