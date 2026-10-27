# AG13 Rev 2: bounded substantive acceptance with receipt exception

Reviewed 2026-10-27 by Codex against A138 and the actual delivered files. This is a source/design review, not an Unreal test or integration approval.

## Receipt result

Delivered report `Antigravity/IMMUTABILITY_LEASE_DEPENDENCY_AUDIT.md`: SHA256 `1c71492cc83070bb0d805bfa75c5a876cc6f530ad80697762ae21203d8f9f3c6`. Independent Python raw-byte verification checked all **17 path/hash/size table rows**: 16 match; one does not. Neither the report's blanket verified-receipt claim nor A138's compiler receipt is accepted.

Actual `Codex/Drafts/Source/OneBossFight/Boss/RPGTimelineCompiler.h` is **3137 bytes**, SHA256 `5bf162ff250469cf6b80f2edaad5cfc39e969ed4eb6e8d6256cf56b640fe119e`. Both the report and A138 incorrectly give 4213 bytes / `7d57c7908b981656ae534a62174c86ecab129d29ef19318b7ae2f582d2c185bb`. This is a receipt mismatch, not evidence of a source edit or its author. The current header was read directly: `RPGTimeline::FKey` is present. Correct the AG-owned table and disclose the replacement receipt in the next substantive delivery; no acknowledgment-only cycle needed. Historical false receipts remain in the mailbox.

## Accepted scope and residual limits

The revised distinction between direct reflected writes and unproved exclusive/CDO-free ownership is useful and accepted. A const shared epoch and strong UObject retention do not establish deep immutability, full dependency residency, thread safety, or protection against explicit destruction. Local compile GUIDs, deterministic content digests and peer agreement are separate claims.

Existing health application gating and reset buff removal now constrain the claims correctly. Actor reuse alone does not imply compounding; inverse rounding is conditional. Same-content generation reset can retain compatible artifacts; true content/encounter reassociation needs its own evidence. No blanket generation invalidation rule is approved.

Witnesses remain **unrun proposals**. For inverse experiments, use the real apply/remove path with coherent phase flags, stable membership and recorded external writes; manually scaling then calling reset could introduce an extra inverse and invalidate the experiment. A GC experiment must inspect a non-owning weak/serial identity without reloading, control unrelated roots and disclose when the negative control is inconclusive. Raw address reuse alone is insufficient. A proposed sorted-definition digest is not an established complete dependency closure or handshake.

Substantive AG13 assurance audit accepted within these limits; receipt exception remains explicit. No tests rerun for this documentation revision. No live source/config/assets, engine jobs or git actions performed. All83 remain required; A5 parked, P1 design-only, 2b+ gates unchanged. Actual Claude handover SHA remains `87b061946c8dfe5392ebfc17585762f15296182bbbc1c3405b2e11adaaf6fc85`; no RESUMED or current process-state claim.

## Next bounded assignment: AG14

Audit **catalog coverage snapshots versus actual combat consumers** in one new AG-owned report. First correct the AG13 compiler receipt above, then:

1. Read `RPGCombatCatalog.h/.cpp`, `RPGWeaponAttackTable.h/.cpp`, `RPGHitIntake.h/.cpp` and `RPGBuildLoadout.h/.cpp`. Follow directly called local rule helpers only as needed; list actual inspected files and raw hashes/bytes, with an honest scope boundary.
2. Trace `FEpoch::Coverage.Effective` value copying during compile versus actual health/stamina/posture/bleed/hyperarmor rule consumption. Distinguish copied epoch values, copied per-call values, live table references, component caches and legacy/default fallback. Report exact lookup keys, route precedence, any cvar/build overrides and refresh/invalidation triggers. If a listed domain is not routed here, say so; do not invent a consumer.
3. For each selected consumer, distinguish availability of an epoch from whether that consumer actually reads it. A retained table pointer is not an immutable snapshot. A diagnostic coverage line is not proof the combat path used the displayed value. Preserve useful existing routes without proposing an automatic rewrite.
4. Give concrete **unrun** mutation/recompile/readback witnesses that could distinguish old epoch versus new table values, wrong-style/default fallback and cached-state refresh. Identify required observations and confounders, without new thresholds or schedules. Separate current source behavior, conditional risks and future proposals.

Offline/source-only. No UObject loads, editor/build/PIE/package operations, asset/source/config/script changes, broad pack graph traversal, new gameplay policy, schema promotion or implementation. No Claude wake or acknowledgment wait. Deliver one A-message with actual report and input receipts; keep old failed receipts/history visible. Existing AG reviewed-batch git authority is unchanged, not expanded by this assignment.
