# AB-C16–C20 — package gates and optional air-field proposal

Date: 2026-11-07. Configuration and offline contract authored; no cook, package, Editor, build, or PIE run.

## C16/C17 — optional ER assets and CookCoverage

Added `/Game/OneBossFight/Player/Animations` to `DirectoriesToAlwaysCook`; the pre-change contract failed on the missing root, then passed after the config edit. Existing `/VFX` and `/Boss` roots remain. The root contains the accepted/import-authorized GuardCounter AnimSequence and is intended for accepted clips and generated montages. It does not make an asset runtime-referenced or prove it survived a real cook. `OneBossFight.Content.CookCoverage` checks hard-coded `/Game` paths found in Source against configured cook roots; it does not enumerate optional soft references or inspect staged IoStore contents. Lead must run native CookCoverage and package asset-readback checks after the montage is created. Pending Lead compile/cook/package.

## C18 — data-default Shipping package manifest

Capture one row per package:

| Field | Required evidence |
|---|---|
| Build identity | BUILD_INFO/build ID, Source revision, configuration, executable SHA-256 |
| Stage identity | stage root, package creation time, staged launcher and inner game binary hashes |
| Route | explicit Development/PIE route witness and stored encounter selection; Shipping package alone cannot emit runtime log |
| Cook | UAT/cook log, CookCoverage result, expected ER/Tier 2 asset paths present in staged container |
| Smoke | exact command, seconds, exit/verdict, process alive/cleanup output, binary debug scanner result |
| Gameplay | separate captured data-route startup and player-input proof; smoke PASS is not gameplay PASS |
| Performance | omit unless owner resumes benchmark work; no inference from smoke duration |

Do not compare a smoke receipt to a different build ID or silently substitute the legacy parity control.

## C19 — packaged smoke process/timeout audit

`PackagedSmoke.ps1` bounds its wait with `ValidateRange(1,3600)`, launches `-nosound -log`, snapshots child process IDs, and stops the launcher tree in `finally`. Shipping skips runtime-log validation because logging is compiled out; it checks alive + `CheckShippingBinary.py`. Identified limits: a long 3600 s timeout can leave a package running for an hour by operator choice; a pre-existing output path does not authenticate build identity; child discovery can miss a process spawned after the snapshot or outside the parent chain; a crash before the timer still waits until the configured sleep ends. Use short smoke durations and separate build hashes; the script's PASS is intentionally narrow.

## C20 — Development data-route log gate

The existing generic `CheckPackagedLog.ps1` rejects asset-load failures, errors, LogRPG warnings, and fatal patterns; it does not require a data-route witness. A Development route check should require the same-run log to contain `[EncounterActivation] route=data reason=StoredDefinition outcome=Pending` followed by `outcome=Activated`, and reject `route=legacy`, `HardError`, missing terminal outcome, or a different selection/build ID. Require the selector definition/map and the matching run-log path. Keep this gate separate from Shipping binary scanning; do not require Shipping runtime logs.

## C972/C973 — optional air montage fields (approved and implemented)

Claude approved this test-first production change in C-973. Added empty-default `TSoftObjectPtr<UAnimMontage> AirLightMontage` and `AirHeavyMontage` to `URPGDodgeTiming`. Native pure-rule tests cover grounded fallback, assigned airborne light/heavy, and empty-field fallback; PackWiring asserts both CDO fields are null. Runtime uses the existing weapon arrays only while the player is falling: AirLight temporarily overrides `FallingAttackMontages`, AirHeavy overrides `StrongAttackMontages`; array restoration is handled after montage start, timeout, or component EndPlay. If the relevant pack array is missing/empty, the helper keeps the existing pack route. Accepted montage assets are not yet assigned; Lead build, CookCoverage, and PIE must verify the actual data route and hit attribution. No hit-window or tuning values were changed.
