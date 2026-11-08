# AR-C16–C20 — KI-197 configuration-specific stage roots

Status: source/config fix and offline contracts complete. Lead dual-package verification is still required; Codex did not build, cook, package, or inspect a new staged output. No evidence of existing stage contamination was found or asserted.

## Source change

`Scripts/Package.ps1` previously passed `Saved\StagedBuilds` to UAT for both configurations. It now defaults Development to `Saved\StagedBuilds` and Shipping to `Saved\StagedBuilds_Shipping`, so their Windows stages land at the roots already documented by `Scripts/MakeBenchKit.ps1`. The optional `-StageDir` parameter accepts an explicit relative (project-root-relative) or absolute UAT staging root. Configuration is still restricted to Development/Shipping; required-tool, G044 pair-input, and normalized-path setup checks occur before UAT invocation. Build stamps remain under `$StageDir\Windows\OneBossFight\Saved`, the same Build ID format remains, and `-G044RequiredFile` / `-G044CookManifest` continue to be passed to the same checker with the selected configuration.

Updated consumers:

- `Scripts/ShippingSmoke.ps1` now plans and runs its package, benchmark, and feature-symbol scan against `Saved\StagedBuilds_Shipping\Windows`, explicitly passing its parent to `Package.ps1 -StageDir`.
- `Scripts/PackagedSmoke.ps1` chooses the Shipping or Development default launcher based on `-Configuration`; an explicitly supplied `-ExePath` remains authoritative.
- `Scripts/CheckShippingBinary.py` defaults to the Shipping stage.
- `Scripts/MakeBenchKit.ps1` no longer silently substitutes the shared Development root when the default Shipping stage is missing. It now fails its existing required-Shipping-stage check, preserving correct configuration identity.

No cleanup, `-clean`, or deletion was added. Explicit caller-supplied stage roots remain caller-controlled; use separate roots and run the identity preflight before a dual configuration package/kit operation.

## Offline contract coverage

`Scripts/Tools/test_package_stage_roots.py` checks default separation and agreement with bench-kit roots; missing-Shipping fallback removal; preservation of `-ShippingStage` and `-DevelopmentStage` overrides; ShippingSmoke and packaged-smoke default routing; explicit path override support; required validation before UAT; and preservation of build-stamp/cook-check arguments. Seven static source contracts pass. They do not run PowerShell, UAT, cook, build, or package.

## Lead verification request (AR-C20)

After the package bench is available, run clean Development and Shipping packages in separate sessions with no Editor already open. For each, record the exact command, UAT log, configuration, emitted Build ID, stage root, `BuildStamp.txt` path/value, and SHA-256 of both manifests and the inner executable. Confirm Shipping files exist only under `Saved\StagedBuilds_Shipping\Windows` and Development files under `Saved\StagedBuilds\Windows`; run `Scripts/Tools/check_stage_identity.py` with both roots. Then create the bench kit from those exact roots and verify BUILD_INFO IDs/configuration and executable hashes. Any stale-output cleanup policy is a separate decision: no deletion was introduced by this fix.

## Scope limits

Existing audit notes and previously retained stage receipts predate this source change. The fix does not prove a new package's contents, stale-output cleanliness, runtime behavior, cook closure, or no-contamination. Until Lead returns same-run artifacts, KI-197 stays open at source-fix-authored / package-verification-pending.
