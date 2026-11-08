# AN-C31–C35: ER and Tier 2 Cook/Package Gate

Status: offline reference audit and checklist complete. No package, cook, Editor or runtime operation was run by Codex. Lead owns BUILD/package verification.

## Findings

- `RPGDodgeTiming.cpp:43-46` uses four exact soft paths for the current ER defaults: Mixamo V2 backstep, GuardCounter, AirLight and AirHeavy. The rejected `AM_ER_Backstep_Back` is not an active default.
- `RPGTier2BossPresentation.cpp:18-19` loads the boss recoil montage and aura Niagara system; `RPGLegend.cpp:379-380` names the parry distortion material and combat-feedback MPC.
- `Config/DefaultGame.ini` includes `/Game/OneBossFight/Player/Animations`, `/Boss01`, `/VFX`, `/Effects`, and `/Data` in `DirectoriesToAlwaysCook` (among its other roots). `RPGAutomationTests.cpp` `OneBossFight.Content.CookCoverage` checks source `/Game` literals are covered by configured directories. `test_default_route_contract.py` checks the relevant root text. These checks do not prove the built package contains each exact asset.
- `Scripts/Package.ps1` runs UAT BuildCookRun and stamps a build ID. Its optional post-cook `check_packaged_g044_cook.py` path verifies a required closure plus every project VFX asset, but the VFX census alone does not cover the ER montages outside VFX. The normalized-manifest reader and the generic `check_g044_cook_manifest.py` can verify an exact package-path list against a supplied cook manifest.
- Added `Scripts/Tools/er_tier2_required_cook_assets.txt` with eight exact UE package IDs: the four live ER montages, boss recoil, aura, PPM and MPC. A focused assertion in `test_air_attack_wiring_contract.py` keeps the asset list aligned and rejects the retired backstep name. This is a source-to-manifest coverage check only.

## Lead package checklist

1. Build the intended Development or Shipping package using `Scripts/Package.ps1`; retain its `[PACKAGE_BUILD_ID]` and UAT output. Do not treat `DirectoriesToAlwaysCook` or BUILD success as staged-asset proof.
2. Export/collect a normalized cooked-package manifest from that exact staged build. Run:

   ```powershell
   python Scripts/Tools/check_g044_cook_manifest.py `
     --required Scripts/Tools/er_tier2_required_cook_assets.txt `
     --manifest <manifest-or-UAT-cook-log> --json
   ```

   Require `missing_count=0` / `VERDICT PASS` for all eight paths and preserve the manifest hash/build identity. If using a normalized manifest, it must contain the actual package entries; an arbitrary text note is not sufficient evidence.
3. Launch the packaged build and verify the four default ER controls and Tier 2/aura/parry visual hooks in the packaged arena. Record configuration, build ID, route, logs and video separately from the cook manifest.
4. Keep raw FBX out of the required package list and source-controlled `Content`; the approved Mixamo-derived UE assets are the only runtime paths listed.

## Disposition

KI-193 remains PARTIAL: BUILD-255 Source defaults and C-1042 default-wired PIE behavior are known, but exact cooked assets and packaged runtime are still open. KI-191 also remains PARTIAL: aura lifecycle exists in PIE, A-637/C-1053 says it was not visible on camera, and its proposed look boost has no owner approval in the mailbox. These package checks do not close the separate guard-counter/contact or visual-approval decisions. Codex did not edit gameplay Source/assets or run UAT.
