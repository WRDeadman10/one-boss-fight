# Queue V C066–C069 — build identity, symbols, logs, and kit readiness

Status: C066 plan complete; C067/C068 implementation is authored and awaits Lead Development build/run; C069 automated checklist is authored and fixture-tested. No Unreal build or packaged game run was performed by Codex.

## C066 — owner crash and symbol retention plan

- Keep each owner build's exact executable, build ID, configuration, source revision, compiler/toolchain identity, and matching PDBs in a restricted build archive. Record SHA-256 for the executable and each PDB; preserve the archive as an immutable build pair.
- For an owner-approved crash report, retain the minidump, matching binary/PDB hashes, module list, OS/GPU/driver facts, and the per-run `game.log`. A dump without its exact PDB is not symbolication-ready.
- Exclude PDBs from the transferable performance kit; `MakeBenchKit.ps1` already copies stages with `/XF *.pdb`. Keep symbols in the owner archive, never delete them as a size optimization.
- Limit dump/log access to the owner and assigned reviewers; do not add an automatic upload or reporter dependency without an owner decision. Set a retention period only after the owner chooses the storage location and policy.

## C067 — Development build stamp

After a successful package, `Scripts/Package.ps1` writes a unique `OBF-DEVELOPMENT-<UTC>-<nonce>` or `OBF-SHIPPING-<UTC>-<nonce>` ID to the staged project's `Saved/BuildStamp.txt`. `RPGDevelopmentBuildStamp` reads it at the first packaged game world and displays Development IDs for 30 seconds. Unstamped Development launches visibly identify themselves as `UNSTAMPED`; Shipping compiles to a no-op. This is a package-side sidecar, not an embedded binary identity: retain the emitted `[PACKAGE_BUILD_ID]` line with the binary hash and do not infer source revision from the ID.

Lead still needs to build Development, confirm the overlay and packaged Saved path, and confirm a Shipping build shows no stamp. No asset or config was changed for this feature.

## C068 — one log per packaged play/smoke run

`PackagedRunLog.psm1` allocates `Saved/PackagedRuns/<build-id>/<label>-<UTC>-<nonce>/game.log`. `PlayDevBuild.ps1` and `PackagedSmoke.ps1` pass that exact path through `-abslog`; smoke validates the new run's own log. Shipping log-free behavior stays on the binary scan path. `MakeBenchKit.ps1` stages the module used by the two scripts. Existing benchmark logs remain in their benchmark folders.

Lead should make two Development launches, confirm distinct paths and retained content for each, then run Shipping smoke and confirm it reports the binary check while leaving no empty file claimed as a game log.

## C069 — bench kit rebuild checklist

`Scripts/Tools/check_bench_kit.py` checks required scripts/readme/build info, Shipping-stage executable and UFS manifests, optional Development-stage files, nonempty required artifacts, package build ID, executable SHA-256, and absence of PDBs before zipping. `MakeBenchKit.ps1` copies the checker and invokes it after writing `BUILD_INFO.txt`; failure stops before archive creation. It reports file count and total bytes as a JSON receipt. Five offline fixtures cover a passing kit, missing dependency, leaked PDB, missing requested Development stage, and MakeBenchKit wiring.

The checklist validates structure, not package freshness, binary compatibility, GPU drivers, or runtime behavior. Lead still owns a real kit rebuild and target-PC smoke.
