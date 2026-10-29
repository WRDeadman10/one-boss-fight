# C231 DD14 real-asset fixture source acceptance

ACCEPT SOURCE ONLY. Claude may perform fresh safety/editor build, isolated focused ProductionPreflight tests, then full suite only after focused passes cleanly. This source acceptance establishes no loaded asset compatibility yet.

Independent check JSON `C231_DD14_INDEPENDENT_SOURCE_CHECKS_2026-10-28.json`:11 receipts,178 live Source hashes,24 dependencies,14 candidate package hashes, Review/live equality and2 existing binary pins verified. Pre177 manifest matches accepted DD13; exactly1 new test file and all177 prior Source files unchanged. Test SHA256 `a418076bee99b76553fd61f3346917d499d7685ce8c26463b85752c35897e170`; diff `3c260f6e7e3d5566f76132652efd4f9423f03951b2fb5bfb7ee0cf749bfb7cfa`. Read all673 test lines and actual compiler/preflight contracts. Local UE Set.h confirms the TArrayView Append overload used for required-field union; no confirmed compile defect found. Only actual compilation certifies that result.

## Decisions on the fixture

- Observed CDO mesh approach accepted: LoadClass/ACharacter CDO reads, native ACharacter-only deferred spawn, no pack Blueprint actor spawn. The native spawn handler recognizes pack class names, so native characters avoid the legacy bundle branch. Test world never begins play; no managed consumer callback runs. Normal native character component registration during fixture construction is not gameplay hydration.
- Nine boss animation refs include dormant/wake/roar, three real pack montages, fall/down/reaction; one player riposte sequence. Including all chosen montages is deliberate: a skeleton mismatch must fail with identities, not be removed or replaced. Source equality/type hypotheses are not runtime results.
- A165 says SKM_CombatMannequin; offline package-name scan suggests SKM_CombatMannequin_Simple. The latter candidate file is independently present and pinned, but only the test's actual loaded CDO output establishes the observed mesh. Do not revise gameplay, select a preferred mesh or retroactively certify either association from a byte-name scan. AG quickstart should keep this association unverified until actual report.
- Genuine production CompileParticipant is called for both transient definitions; bSyntheticFixture is checked false. Caller Legacy epoch, SHA-shaped manifest and fixture parity rows do not establish GI/source provenance. No asset saves, CDO writes, level loads, actor BeginPlay/ticks/playback or runtime binding calls are present.
- Negative clones manually retain values/leases and have an accepted unmodified control. Null/missing/mismatched leases and no-mesh actor preserve earlier valid output clearing and world/context invariance. Transient mismatched skeleton/animation are negative controls only.
- Dirty snapshots begin AFTER class loads/spawn/production compilation, covering preflight/negative cases only. CDO check covers retained mesh pointers, not every CDO property. Disk package hashes before/after and no-save policy remain important; do not broaden this witness into a complete no-mutation proof.
- The two prior review edits have no preserved intermediate snapshots, as C231 explicitly says. Record that provenance limitation; final source/diff and the pending execution are pinned, not reconstructed imaginary iterations.

## Claude execution release

Fresh operator safety, preserve any active job/unsafe editor state rather than interfering. Freeze178 Source hashes, accepted test pin,24 dependencies,14 candidate package pins and DLL/EXE before execution. Reviewed editor Rebuild/NoRelaunch workflow; record actual UHT status, compiler diagnostics, raw logs/job exits, source and resulting binary hashes. No compiler fixes or source changes authorized during this run.

ONLY focused `OneBossFight.Binding.ProductionPreflight` (PositiveBatch, DependencyRejections;2 expected, actual discovery required). The tests may load the named class assets/CDOs and animations and construct their isolated native fixtures, exactly as reviewed; no additional assets/scenes/PIE/bridge. Require both unique Success, no fatal/ensure/unsupported fixture/observer failure or Error-severity failure. Missing chosen assets, load failures or identity mismatches are findings: stop full-suite progression and preserve exact errors, observed paths/classes/mesh/skeleton pairs and source/binary/input hashes. No retarget, omitted montage, replacement skeleton, synthetic-positive substitute, expected-error suppression or repeated run to chase a pass.

ONLY IF focused clean, full `OneBossFight` on unchanged source/binary. Expected110 is not assumed: actual prior108+exact2, no duplicate/missing/failing paths, CookCoverage Success. Report exact warning/error categories, new load-related warnings compared with prior baseline, actual package preloading and identity AddInfo output. Existing60-warning baseline is not a required forced number or permission to filter new messages. No cold-load claim.

Final full-source/dependency/candidate package hashes must match the frozen inputs; EXE unchanged unless actual workflow unexpectedly touches it (report drift). Include raw build/focused/full logs and SHA256, job exits, manifests and receipt index. Any failure/drift stops for exact reviewed delta before edits/retry. Do not save dirty loaded assets on exit; ambiguous editor prompts mean preserve/report, not blind acceptance.

## Limits and parallel work

Even a pass proves only this real-asset/native-character compiler/preflight fixture in the pinned editor binary. It does not prove actual arena/Blueprint actor behavior, ability/effect class suitability, playback/root motion/timings, packaged dependency closure, authored/serialized boss Data Assets or Details workflow, actual GI epoch/manifest authority, runtime coordinator/Ready/startup/target-reset wiring, networking, full driver gate, Shipping/noneditor or all83 completion. No activation/git release.

AG-CONTENT02 remains active under direct-owner X269: offline authoring quickstart/examples only, no engine/source/content/git overlap. All83/networking required,A5 parked. DD10 failures and all earlier evidence/provenance limits remain preserved.
