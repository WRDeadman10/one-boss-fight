# BN-36..40: manual check of the heuristic-O KIs (lane BN, batch 8 of 10, per X-2213)

C (implementer), 2026-11-12. X-2229 is carried forward: the running count entering this batch is 2 O out of 34.

**Not done:** no code, asset, engine, build, PIE or test work. No KNOWN_ISSUES status changes and no commits.

| Task | KI | Row | Evidence checked | Manual class | Offline follow-up? |
|---|---|---|---|---|---|
| BN-36 | KI-106 | `KNOWN_ISSUES.md:167`: `pie_close_attacks` C7 hits in only 1-2 of 5 trials, while `pie_close_reach.py` hits 100 percent. The row attributes the difference to the driver setup: "Not a product bug as far as measured" | A driver/PIE timing difference; any change needs PIE reruns | **E** (PIE driver) + L | No |
| BN-37 | KI-101 | `:171`: `pie_attack_rules` R5 stalls in about half the runs with the build selector registered. The cause is not in the project montage-stop code; R5 was relaxed to 1 or more tracked attacks, with a WARN | An intermittent PIE stall with a mitigation already applied | **E** (PIE) + L (mitigated) | No |
| BN-38 | KI-092 | `:174`: the Gate 3 items for M13 are not done (F6/F7/F8, shrine selector, dex chain stages, boss defeat per build). The action is "Balance run M14" | Needs PIE and a balance run | **E** (PIE/balance) | No |
| BN-39 | KI-110 | `:177`: phase two buffs are not reversible for `DamageScale` below 1, because remove subtracts only `if (AppliedAttack > 0)`. "NOT reproduced in an engine run"; the typed adapter refuses factors below 1 | **Re-verified in current source:** `Source/OneBossFight/Player/RPGBossPhases.cpp:368` applies `Attack*(DamageScale-1)`, and `:390` still gates on `AppliedAttack > 0.0`. The row and source match. `DECISIONS.md:648` records X-245's accepted capability limit: the adapter refuses factors below 1, with no native fix/clamp/tuning | **L** (current capability limit is explicitly retained) + E (not reproduced in engine) | **No:** X-245 says the native fix is not scheduled; a later rescope would be needed before implementation. No source edit or test in this lane |
| BN-40 | KI-128 | `:203`: arithmetic residual (DD19 threshold-growth intermediate overflow; external-input risks). "Open residual; no lasting nonfinite threshold claimed" | BM-26..30 already pinned this as transient (`RPGBleedThresholdOverflowTests.cpp`, not compiled) | **L** (accepted residual) + E (the BM native test is uncompiled) | No new one (the BM test exists) |

**Batch 8 result:** 0 new O. Running total: 2 O (KI-026, KI-067) out of 39.

**Limits:** row reads plus one grep of the current source for KI-110. The KI-110 fix was not written or compiled.
