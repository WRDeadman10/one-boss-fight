# DD17 revision for X-284: binding lifecycle and identity checkpoints. SOURCE ONLY (Claude, 2026-10-28)

Nothing was built, no UHT, no automation, no engine process, no git operation, no asset load. The tests file is byte-identical to the state Codex reviewed (`cmp` equal; sha256 `c606437268c80824cec95a376b999a8f903421035dd1919f4cfac4c7df8f7f02`). Only the header and the cpp changed.

## Preserved bytes
`Review/*.reviewed_by_codex_X284` are the three files exactly as Codex reviewed them (header `4c07c8c9...`, cpp `b9fff21e...`, tests `c6062437...`). The older `Review/*.before_independent_review` files (the states before my own independent pass) are kept as well.

## New bytes
- `Player/RPGBossWorldInputCompiler.h` 59 lines sha256 `343d74db59c3f8fa6f28a16fbeb7bf58fab4193580c25fea4960b77d67141c0e`
- `Player/RPGBossWorldInputCompiler.cpp` 604 lines sha256 `9451d166f24d4c49119ed2dc767dfc00c9b1e90ad1505acac71cf9696ad560e7`
- `Tests/RPGBossWorldInputCompilerTests.cpp` unchanged, 1109 lines
Exact deltas: `revision_X284_RPGBossWorldInputCompiler.h.diff` (25 lines) and `revision_X284_RPGBossWorldInputCompiler.cpp.diff` (295 lines); the full three-file diff is `three_file_revised.diff` sha256 `18a2674d9d6830b2f4fb42f75363bbb1911676179b66a47c3cb487ba16270650`. Manifest 185 files: `manifest_revision_diff.txt` shows exactly the two changed lines (.h and .cpp); against the DD16 final manifest there are 3 added lines and 0 removed; 24/24 pins, 10/10 dependency pins, 14/14 candidates, 7/7 catalog assets, HEAD 79d55906 and both binaries unchanged; no engine/build process.

## What changed (all in the anonymous namespace plus the call sites)
1. One shared `Checkpoint(...)`, run before AND after EVERY `CompileParticipant` and at publication. In order: the content identities (`StillSame`: world valid and the same, game instance the same and now also VALID, its catalog subsystem the same and now also VALID, the ForWorld epoch pointer the same) = `WorldInput.ContentDrift`; then the binding is resolved through a RETAINED weak reference (`TWeakObjectPtr<const ARPGEncounterBinding> BindingRef`) and must resolve, pass `BindingProblem` (valid, not being destroyed, in the expected world, not begun, not beginning), keep the same GUID and participant snapshot (`SameSnapshot`), and every member actor and definition must still pass the actor predicate (valid, not destroying, same world, not begun) and be valid = `WorldInput.BindingDrift`. The after-compile checkpoint runs BEFORE the candidate reuses the member's raw actor, so a mutation during the loads cannot reach the request.
2. The initial validation now uses the SAME predicates: `BindingProblem` (the four binding diagnostics keep their exact text and token `WorldInput.InvalidBinding`) and `ActorProblems` (a bit set: missing, stale, destroying, foreign, begun) whose bits map to the unchanged member diagnostics (`ParticipantActorMissing/Stale/Destroying/Foreign/Begun`). The existing foreign, begun and destroyed binding/actor tests therefore exercise the guards the checkpoints use. Initial diagnostics are unchanged; checkpoint failures use `WorldInput.ContentDrift` and `WorldInput.BindingDrift` with a where text naming the phase ("before compiling [slot=X]", "while compiling [slot=X]", "before publication").
3. `Acquire` also requires the game instance and the subsystem to be valid.
4. API comment fixed: on any failure on the GAME thread the output is cleared; an OFF-thread refusal leaves it untouched (lease safety). The drift paragraph in the header describes the new checkpoint.
5. No new test and no weakening: the existing positive and negative tests and diagnostics stay. A mutation during the production loads cannot be provoked without a callback, a cvar or an injection framework (none is added), so the checkpoint branches are source claims, not executed runtime failures, and are stated as such. `ConfigInvalid` and epoch drift stay unexercised as before.

## Self-check
Re-read the edited regions: `Checkpoint`, `BindingProblem`, `ActorProblems`, `DriftToken` are in the anonymous namespace after their dependencies; no name shadows an earlier local; `BindingRef` is declared after the validation and before its first use; the old publication-gate block was replaced as a whole. No independent sub-agent pass was run for this small revision.

## Open
Not compiled, not run. Everything in `17_DELIVERY.md` NOT-proved still applies. The reconstructed pre-change manifest slip stays on record. Nothing committed.
