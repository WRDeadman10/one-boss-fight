# Offline legacy-attachment witness for future2b review

X221 targeted candidate-mode review: `ag17_candidate_review_probes.json` records two synthetic candidates accepted with exit0 despite a changed music default or a duplicated spawn Attach call. Candidate mode reports body hash/triggerTokensUnchanged but does not enforce their equality; it checks event order and hook-call patterns. Exit0 is not guard/default/trigger equivalence. Original unchanged-source mode separately enforces raw source hash. Helper/baseline unchanged; no extraction/runtime test. See ../AG17_A145_REVIEW.md for exact limits. This documentation receipt changes intentionally; old96741a7f... snapshot is historical.

Codex-only staging, 2026-10-26. No live Source or engine operations. `legacy_attach_witness.mjs` captured immutable LEGACY_ATTACH_BASELINE_2026-10-26.json from current RPGPlayerMovesSubsystem.cpp SHA1b036b03aec269e5b3e906d8adaedac709c33f6a3c15413d0454b9c354523712.

The witness records21 ordered boss construction/factory steps, source lines, whole-Attach token fingerprint60ce6e3604ebe09837ec7390ce230823b242efc9869831ca2ec5358c80fff3e8 and fingerprints for both trigger methods. Current check:11 lexical helper tests pass,21 events/order match, spawn and subsystem-world-begin both call Attach, source/trigger fingerprints unchanged. Unsupported raw C++ strings fail explicitly. Unknown NewObject consumers in future boss helper are not silently ignored.

Run `node .../legacy_attach_witness.mjs` for unchanged-baseline check. Future reviewed candidate may be examined with `--candidate <source.cpp>`; if AttachLegacyBossBundle exists, its order is compared. `--capture` refuses existing baseline and must never be used to overwrite this historical witness. No automatic extraction or source patch is generated.

Order: footsteps; music; stagger; phases; encounter; dormant/wake; posture; Death(OwnClip); look; bleed; tracker; close-clip-swap; wave; low sweep; heal-punish; damage resolver; trace guard; trace audit; HUD; debug; Legend last.

Limits: lexical token/order witnesses are NOT a C++ AST, control-flow/guard equivalence, complete template parser, runtime registration/BeginPlay sequence, GC behavior or duplicate-trigger idempotence proof. Manually compare every original conditional/default/player branch and actual callback tests. Arbitrary new static factory calls may require parser extension; a candidate order match is not technical acceptance. Synthetic helper tests never increase Unreal automation count.2b remains held through account transition and requires current lead release.
