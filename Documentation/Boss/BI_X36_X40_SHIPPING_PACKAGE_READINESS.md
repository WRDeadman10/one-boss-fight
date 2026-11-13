# Queue BI Batch 8 — Shipping and package evidence readiness

**Status:** Static source, documentation, and stage-metadata audit only. No Shipping build, UHT, package, smoke, binary scan, or test was run. The existing stage directories were not modified.

## BI-X36 — Development reflection contracts versus Shipping request

The existing source contract and Lead checklist in `BE_X21_X25_SHIPPING_REFLECTION.md` cover five reflected classes: `URPGDamageResolver`, `ARPGFrameworkBossCharacter`, `URPGDodgeTiming`, `URPGIFrameMonitor`, and `URPGPlayerParry`. The relevant test-only UFUNCTION declarations use `WITH_EDITORONLY_DATA`; production readers and player-facing APIs intentionally remain reflected. `BF_X11_X15_SHIPPING_REFLECTION.md` adds `URPGFrameworkProofFixture::RestartEncounterForTest` to its narrower inventory. Those are source-level declarations/contracts, not proof of the generated Shipping class function tables.

The existing `Scripts/CheckShippingBinary.py` is a separate binary string check for `rpg.Debug` and `LogRPGDebug`. `Scripts/CheckShippingFeatureSymbols.py` checks `rpg.Art.Tier2`, `BuildStamp.txt`, and `DEVELOPMENT BUILD`. Neither script creates the required reflection dump. The Lead evidence needs to bind one exact build: source revision/hash, UE version, target, platform/config, command and exit status; UHT log and warnings/errors; runtime/cooked reflection dump; both binary scans and their input hashes; and the packaged smoke output. Development UHT/build evidence cannot substitute for Shipping evidence.

## BI-X37 — Existing stage inventory and freshness boundary

Read-only filesystem metadata on this checkout:

| Stage | BuildStamp | launcher / config binary | UFS manifest |
|---|---|---|---|
| `Saved/StagedBuilds/Windows` | `OBF-DEVELOPMENT-20261109T064804Z-992f44a8` | `OneBossFight.exe` present (305,826,304 bytes; mtime 2026-11-09 06:46:06Z) | 1,438,001 bytes, mtime 2026-11-09 06:48:02Z |
| `Saved/StagedBuilds_Shipping/Windows` | `OBF-SHIPPING-20261106T071240Z-ac05f0da` | Stage launcher `OneBossFight.exe` present (346,624 bytes; mtime 2026-11-06 06:35:55Z); config binary `OneBossFight-Win64-Shipping.exe` present (148,851,200 bytes; mtime 2026-11-06 06:34:32Z) | 1,432,790 bytes, mtime 2026-11-06 06:36:16Z |

The Development and Shipping roots contain their expected launchers, UFS/NonUFS manifests, and in-stage BuildStamps; the Shipping root also contains its Debug manifest and `.pak`, `.ucas`, and `.utoc` payload files. A prior read-only check reported the Shipping root launcher missing; the current recheck finds it present, and the reason for the discrepancy is unknown. The roots and stamp IDs are distinct. The stamp establishes only its self-described config/time/id; it does not bind the stage to current HEAD, intended source inputs, a successful recorded UAT invocation, or accepted smoke. The older timestamps are a freshness prompt, not proof of validity. File hashes were not calculated.

`Scripts/Tools/check_stage_identity.py` checks presence/nonzero size for the launcher, UFS and NonUFS manifests, and BuildStamp; stamp format/config; distinct resolved roots; and distinct IDs. The currently inspected required files are present, but the checker was read, not run. It does not bind binary/manifest hashes to source, target, map, UAT logs, or smoke. `Scripts/Package.ps1` defaults to separate Development and Shipping roots and cooks `/Game/OneBossFight/Levels/L_SevarogArena`; `-StageDir` can override the root, so the resolved-root collision check remains necessary.

## BI-X38 — Lead package intake checklist

For a single package, preserve a read-only intake record containing:

1. Git HEAD and source-tree identity, UE version, `.uproject` identity, target, Win64 platform, configuration, exact UAT command, start/end UTC, exit code, and complete UAT log path/hash.
2. Resolved stage root; BuildStamp content; launcher and actual configuration binary paths, sizes and SHA-256; UFS, NonUFS, and Debug manifest paths, sizes and SHA-256; and exact package/manifest association.
3. Cooked map identity (`/Game/OneBossFight/Levels/L_SevarogArena`), normalized cook-manifest path/hash and any required-closure checker result. Record the route/encounter definition, command line/environment selection, and relevant config snapshot for the smoke.
4. Shipping UHT result/log hash and a reflection dump bound to the same build ID, listing absent test-only hooks and present required production APIs.
5. `CheckShippingBinary.py` and `CheckShippingFeatureSymbols.py` commands, exact input binary hashes, exit codes and captured output.
6. Packaged smoke command, resolution/map/route, start/end, process exit, benchmark/log/receipt paths and hashes, plus any failure. The benchmark executable must be from this exact Shipping stage.
7. A final cross-reference that all artifacts resolve to one build/package ID. Missing or mismatched identity is an incomplete intake, not a pass.

`Scripts/ShippingSmoke.ps1` defaults to a printed dry run; its `-Execute` path packages Shipping, runs `RunBenchmark.ps1`, then scans Development-only symbols. No execution was performed. Its current plan does not itself produce the full provenance/reflection record above.

## BI-X39 — Defaults and guard scope inspected

This was a targeted reconciliation of shared defaults and related Development diagnostics, not an exhaustive configuration audit. `Config/DefaultGame.ini` currently sets data startup on, camera hide-boss-inside off, lock-on framing on, and Tier 2 presentation on (C-1168). `RPGCameraRig.cpp` places the hide-boss and lock-on override CVar declarations behind `!UE_BUILD_SHIPPING`; their fallback behavior uses the shared config defaults. The presentation source documents that `rpg.Art.Tier2` overrides are Development-only. Framework test bridge UFUNCTION metadata is `WITH_EDITORONLY_DATA`-guarded per the reflection reports above.

No config/default edit was made. These source/config observations do not independently verify cooked config, Shipping preprocessing/UHT, or runtime behavior in the staged binary.

## BI-X40 — Disposition and Lead-owned actions

All five task scopes are complete as a static readiness audit. No source change or test was justified by this pass. Lead actions remain: establish the stage's source/UAT provenance and freshness, then capture Shipping UHT/reflection evidence; run both binary scans against the same identified executable; and run/record a smoke against that same package. The current file-presence inventory is not proof of build identity or acceptance. Owner decisions/defaults are not requested or inferred.

**Validation:** manual source/document reads and read-only `Get-Item`/BuildStamp inspection only. No tests, checkers, build, Unreal, package, smoke, binary scan, commit, or push.
