# DD16 actual production preparation fixture: SOURCE ONLY (Claude, 2026-10-28, order X-278 / Codex/DD16_PRODUCTION_PREPARATION_FIXTURE_PACKAGE_01.md)

Nothing was built, no UHT, no automation, no engine process, no git operation, no asset load, no Content/Config/Script edit.

## The one new file
`Source/OneBossFight/Tests/RPGBossProductionPreparationTests.cpp` (1064 lines, CRLF, 0 bare LF/CR) sha256 `3cca0eb475ae6bbc1b10559f2e9f48e7a332f98b6130b35d3429b40e821fd956`.
Diff `one_file.diff` sha256 `f0a7982c156164fb13718781416e6e0172acc6faeb3f953fd1655a7d4b76a454`; Review copy identical. State before the independent review (sha 3d4f8e62...) kept in `Review/` with `review_edit_delta.diff`.
Manifest: 181 -> 182 files; `manifest_diff.txt` is exactly one added line; the 181 old files are byte-identical to the DD15 final manifest (`pre_vs_dd15_final_diff.txt` empty). 24/24 pins OK before and after; the DD15 preparation h/cpp/tests and the DD14 tests are pinned again (`dd15_dd14_pins_sha256.txt`); the 14 candidate assets (the two pack character Blueprints, the mesh, the skeleton and the animations of DD14) verify 14/14 (`candidate_assets_check.txt`). HEAD 79d55906 and both binaries (DLL eeade11b..., exe 5495fb88...) unchanged; no engine/build process.

## The three tests (OneBossFight.Binding.ProductionPreparation.*; expected 3, full suite expected 119 only after a later released run)
Setup copied from DD14 into this file (no helper promoted, DD14 untouched): the two pack classes are loaded only to read the CDO mesh, the observed mesh/skeleton go on THREE isolated native ACharacter actors (two boss-core, one target) finished before any preparation, an unrelated marker component on each, three transient definitions (the bosses differ in id, selected phase id PhaseTwo/PhaseAlt, threshold, health, posture and stagger seconds), the genuine RPGCombatHydration::CompileParticipant (bSyntheticFixture false) for all three, then PrepareBatch.
- PositiveBatch: ten owned exact components (names, owners, unregistered/uninitialized/not begun/not ticking), each boss holding its OWN configured values, retained production config/content/skeleton/animation leases, summaries, no participant, target and unrelated sets and mesh assets unchanged; explicit Abort (destroyed 10, idempotent, weak identities read before names are recreated) and scope-exit abort restore the prior sets; dirty flags compared around the preparations and aborts after the legitimate loads; observed paths/skeleton identities and the pre-fixture in-memory status are logged.
- LateRejection: valid first boss then, one case each: a later config with a null animation lease (Preflight.ProductionPrerequisite), a later selected phase the config lacks (Preflight.PhaseRejected, InvalidPhase.NotFound), and a later definition the production compiler refuses (CompileParticipant layer: animation/skeleton identity mismatch, transient negative-control skeleton) followed by the missing config offered to PrepareBatch (Preflight.NoConfig). Each asserts: no artifact, token+slot+detail in ONE error, no Preparation.* token (layer named), world/sets/context unchanged, and no object (not even a destroyed one) under any planned name on any actor. The unmodified positive control (prepare + abort) runs after them.
- NameCollisionCleanup: a live USceneComponent under the planned name RPGBossEncounter of the LATER owner; PrepareBatch must give exactly ONE error Preparation.AllocationFailed with [slot=BossTwo] and [component=RPGBossEncounter]; seven earlier components (boss one 5, boss two Stagger and Phases) are shown allocated-and-destroyed (destroyed objects found under their names, no collection forced), the two later names never allocated, the target none, the blocker the same live object with unchanged state, every preexisting object still live, no new live object. Only the blocker is then removed (renamed away, then DestroyComponent) and the same input succeeds and aborts.

## Judgement calls, stated
1. Reciprocal targets: BossOne <-> Player; BossTwo targets Player (a player has one target slot).
2. The blocker is renamed before it is destroyed: a destroyed USceneComponent would still hold the planned name and the allocation guard would refuse again (different class).
3. The retry after the collision reuses seven names that the failed attempt left as destroyed, uncollected objects of the exact planned classes (the engine replaces them in place); this is observed, not claimed as garbage-collected-name reuse; no collection is forced and no reference to a destroyed object is kept.
4. The negative controls use a transient skeleton (as DD14); animation clip paths are the typed records' authoring defaults (pinned assets by sha256), not independent literals.
5. The LateRejection positive control runs last so the "nothing was ever allocated" checks stay meaningful.
6. Four configured fields per boss are compared exactly (floats are plain assignments in the adapters).

## Independent pass
A read-only sub-agent reviewed the file against the project headers and UE 5.5 engine sources: no compile error and no certain failure; one low finding fixed (token+slot+detail in one error, unused helper removed). Notes in `Review/independent_review_notes.txt`. It is supplemental, not an acceptance.

## NOT proved / stated limits
Not compiled and not run: every claim above is a source claim until a released build. Real assets are loaded but the preparation is still transient-definition, legacy-epoch, hand-manifest evidence (not authoritative GI/serialized authoring proof); no cold load; no organic native configure failure; no GC-collected-name reuse; no registration/BeginPlay/BindEncounter/context/reservation/Ready/legacy suppression/startup/target rewiring/PIE/arena/package/non-editor/git.

## Next (needs Codex release)
Review the one file, then release the scoped build + focused ProductionPreparation run (+ full suite) in the standard gate; any compile failure will be preserved with the first failing source before any fix.
