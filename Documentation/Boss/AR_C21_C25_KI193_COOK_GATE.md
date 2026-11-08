# AR-C21–C25 — KI-193 ER/Tier 2 cook gate

Status: read-only checker and offline contracts complete. The tool has not been run against a current package. KI-193 remains PARTIAL: owner-approved Source defaults and Lead default-wired PIE evidence exist, but same-build cooked asset presence and packaged runtime remain unverified.

## Exact required paths

`Scripts/Tools/er_tier2_required_cook_assets.txt` is the canonical eight-package list: four approved ER player montages, boss parry recoil, phase-two aura, parry distortion material, and combat-feedback MPC. The checker requires exactly eight unique entries and does exact normalized package-path comparison. It does not infer required assets from `DirectoriesToAlwaysCook` or from file names outside the list.

## Checker contract

`Scripts/Tools/ar_er_cook_manifest.py` reads a normalized `onebossfight.g044-cook-manifest/v1` JSON manifest. It reuses the existing schema validator, requires explicit CLI Build ID and configuration, and verifies they exactly match manifest metadata. It computes hashes of both the canonical required list and normalized manifest bytes, retains the manifest's source cook-manifest hash, rejects duplicate/malformed package rows and empty/missing identity, and reports missing required package paths.

Example for a Lead-returned Shipping manifest:

```powershell
python Scripts/Tools/ar_er_cook_manifest.py `
  --manifest <normalized-manifest.json> `
  --build-id <exact-package-build-id> `
  --configuration Shipping
```

Repeat with `--configuration Development` and that package's exact Build ID. `PASS` means only that all eight named packages occur in the supplied, identity-matched normalized manifest. `FAIL` means one or more are absent. `INVALID`/exit 2 means malformed schema/list or identity mismatch. The report explicitly marks the check route-independent and does not claim stage identity, file loadability, package launch, or visual/runtime behavior.

## Offline verification

`Scripts/Tools/test_ar_er_cook_manifest.py` covers all required paths present, one missing path, duplicate manifest path, wrong-root substitution, empty manifest, missing identity, mismatched Build ID/configuration, and a malformed one-entry required list. These are temporary synthetic fixtures and do not represent a package. See the current AR batch mailbox receipt for test count and syntax/link results.

## Lead package and runtime return (AR-C25)

For each of Development and Shipping, using the AR-C16 configuration-specific stage roots:

1. Run the selected package command and retain command text, full UAT log, emitted Build ID, configuration, stage root, stage `BuildStamp.txt`, UFS/non-UFS manifest paths/hashes, and inner executable SHA-256.
2. Export the authoritative package inventory from that exact run, normalize it with the captured source-manifest hash, and run the checker above with the exact Build ID/configuration. Return raw source manifest, normalized JSON, and output JSON for both configurations. Do not reuse historical R6/C-878 or prior build manifests.
3. Run `Scripts/Tools/check_stage_identity.py` on both stage roots; the check must identify distinct roots and matching configuration-specific stamp identities.
4. Separately run packaged input/attack validation on both legacy and selected-data routes where supported. Return route/build identity, required default-wired observations, process/log status, and a gameplay capture if visual behavior is being claimed. Cook presence alone never closes packaged runtime.

Stop on absent/mismatched build ID, configuration, source manifest hash, or route identity; preserve the failing output and report missing rows instead of substituting another build. No assets, manifests, staged files, or raw evidence were changed by Codex.
