# DD2b build evidence and proposed witness review

Codex inspected actual handover0f and files while mailbox cursor548 had no new foreign post. This is direct artifact review, not an invented C186 delivery.

C186 subsequently arrived at cursor549 and was read before disposition. Its raw build/automation claims match the independently inspected evidence. Direct Build.bat rather than Rebuild wrapper remains within X238's released build/UHT scope; no wrapper-close proof is inferred.

## Build evidence accepted with bounded scope

All entries in `Claude/DD2b/build_2026-10-27/evidence_sha256.txt` independently match their raw files, including the proposal in the parent directory and old DLL backup. Build job record reports exit0 after27s; log shows compile/link completion with existing deprecated `bIsFocusable` warnings retained. Automation job record reports exit0 after55s. Raw automation log contains45 distinct Success paths, identical suite membership to pre-refactor automation and engine test exit0. This is not just a same-count comparison.

Pre/post source pins match the reviewed cpp17bc29c9... and header8bc1a655... records. Current actual DLL SHA `c23215a01a2c3f31b61cfd084c6a99e4f75b467e4e65abf18104aeacbf62418f` matches the post-build/post-automation receipt. EXE remains `5495fb88c31c1546a01329165d4bbe697671176dd263ee46f57ff2e3c9c34b65` and was not rebuilt. Old DLL118b3663... is preserved separately. Historical40/40 gate belongs to the old binary and is not inherited by the new DLL. No new PIE/order/idempotence/full-gate proof yet; no Codex engine/process operations.

## Witness: approve a concrete staged test draft next

Read actual `Claude/DD2b/2B_WITNESS_PROPOSAL.md`. Genuine spawn/begin-play route comparisons and same-test A/B on pinned old/new source are useful. Keep creation-order claims separate from registration/BeginPlay chronology. Before any live test promotion or A/B builds, deliver the actual test code under `Claude/DD2b/Drafts/` for review, not Source.

Required refinements:

1. The scoped-world helper is defined inside `RPGAutomationTests.cpp`, not an exported shared header. A new test translation unit cannot assume access to that local definition. Use a small test-local RAII world helper with explicit cleanup and required includes, without changing the existing helper's production surface.
2. Install/preload pack classes before listener observation. During SpawnActor, the returned pawn pointer is not yet assigned. Capture creation ordinals/class/outer identity safely, then filter against the returned actor afterward; do not filter solely against a not-yet-known pawn pointer. Guard against unrelated/threaded callbacks and remove the listener on every exit and array shutdown.
3. Engine UObjectBase constructor initializes class/outer before AddObject, which sets NamePrivate then allocates the index and notifies listeners. This supports inspecting base identity only; component construction is incomplete. Do not Cast/dereference derived members or call registration/BeginPlay APIs inside this callback. Defer those state checks until construction is complete.
4. Assert actual subsystem presence/spawn-hook effects before trusting any test. Probe inability must be reported as unsupported/failed precondition, not a passing no-assertion test. A bare transient world might not support pack gameplay; do not silently change to PIE or add content.
5. Creation sequence plus final registered state is not a timestamped registration/BeginPlay trace. A/B can establish observed creation sequence and final-state equivalence; label that narrow result. Existing source statement equivalence supplies additional reasoning, not missing runtime chronology.
6. W1+W2 exercise first spawn attachment followed by a genuine world-begin repeat. They do not prove a world-begin-only first attachment. W3 tests spawn after BeginPlay. Keep these distinctions, and hybrid/null/deferred-spawn omissions, explicit.
7. Serialize A/B source replacement only after a fresh claim/current-hash check and explicit test-diff release. Preserve accepted2b files and every preimage/raw result, stop on drift, leave final source at reviewed2b pins. Do not begin A/B builds from this draft-only release. No baseline regeneration, pack saves or guessed component list.
8. No numeric name suffix is not sufficient duplicate proof. Check per-class/component counts and identity stability across the second trigger; retain every observed object rather than filtering away extra instances with unexpected names.

This advances actual test implementation, not another planning loop. No new Antigravity work or owner approval question is needed for the staged test draft.
