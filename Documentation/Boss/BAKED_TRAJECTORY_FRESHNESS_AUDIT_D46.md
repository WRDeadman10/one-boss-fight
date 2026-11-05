# Baked trajectory freshness proof audit (Queue D D46)

## Finding

The maintained card schema does not carry a fingerprint, revision, or other persistent identity for the animation bytes/pose used to create `BakedSamples`. `FRPGBossMoveWindow` stores only sample times and component-space `BaseCS`/`TipCS` vectors (`RPGBossMoveCard.h:69`); `RPGBossMoveCards::Validate` checks sample count, finite values, ordering, clip/window bounds, and complete window coverage (`RPGBossMoveCard.cpp:140-153`). These checks establish structural validity, not freshness against the current animation.

`RPGBossBakeFreshness::IsFresh` is a pure, unwired equality rule: both caller-supplied 64-bit fingerprints must be nonzero and equal (`RPGBossBakeFreshnessRules.h:5-12`). Its tests cover equal nonzero, unequal, missing current, and missing baked values (`RPGBossBakeFreshnessRulesTests.cpp:6-11`). Nothing in the inspected card spec, card validator, baker, or verifier computes those values, persists one beside the samples, or calls `IsFresh`; the rule tests therefore prove comparison semantics only.

## Existing bake and drift checks

The C1 baker requires a selected sequence path, refuses a requested/declared sequence-path mismatch and a window beyond clip length, then evaluates pose samples and returns copied sample data (`Docs/BossCombatReview/Execution/Antigravity/MoveCards/bake_blade_path.py:223-282, 320-333`). Sequence-path agreement prevents an explicitly different path from being baked through that call; it does not detect that the same path's animation content changed after an earlier bake.

The C1 verifier reloads the declared sequence and compares stored samples to evaluated pose/socket values at Start, Mid, Apex, and End, using a default 2 cm tolerance; `--require-baked` also rejects required windows with no samples (`verify_baked_cards.py:168-205, 282-360`). This is a point-sampled pose-drift check when the verifier is actually run. It is not a stored source identity and does not attest unsampled frames or that a prior successful check remains valid after the sequence changes. `Scripts/Tools/validate_baked_cards.py` only checks JSON sample shape/finiteness/order/window placement, not animation identity.

## Evidence boundary and handoff

| Mechanism | What it supports | What it does not support |
|---|---|---|
| MoveCard structural validation | Samples are finite, ordered, and cover the declared window/clip constraints. | That the samples match the current animation pose. |
| `IsFresh` plus unit test | Equality semantics for two supplied nonzero fingerprints. | Fingerprint generation, storage, source coverage, or runtime enforcement. |
| Baker sequence-path guard | The requested path agrees with declared `Sequence` for that operation. | Same-path content-change detection or permanent provenance. |
| C1 verifier | Current sampled pose points agree within configured tolerance at the checked timestamps, if run. | Continuous whole-clip freshness or future freshness after asset edits. |
| Offline JSON validator | Numeric and temporal sample structure. | Any Unreal asset readback or animation comparison. |

No stale-sample defect is claimed from this audit alone: the pipeline has a manual/re-run verifier path. A future persistent mechanism would need a defined fingerprint input (asset identity plus content/revision scope), serialization beside the bake, and a consumer that refuses stale/unknown samples; none is present in the inspected maintained code. Source/docs review only; no scripts, tests, Unreal, or build were run.
