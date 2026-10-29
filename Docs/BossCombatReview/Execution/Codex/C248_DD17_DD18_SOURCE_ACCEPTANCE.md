# DD17/DD18 source acceptance and one serialized verification release

Codex reviewed C245/C247 and C246/C248 against the actual source and preserved deltas. C248's original weak binding, immutable encounter GUID and complete attempted actor identities now survive the facade boundary without a raw Binding dereference afterward. The final gate resolves the retained binding, validates lifecycle/world/GUID, and the final-drift quarantine retains original plus prepared-plan actors even when admission already failed. The failed-facade quarantine retains the original attempted identities. No callback or registration was introduced.

Source acceptance is for the explicit world-input compiler, unregistered preparation facade and explicitly owned per-world reservation registry. Registry GUID plus serial plus encounter validation prevents stale tokens from releasing a replacement; clean abort frees entries, violating cleanup quarantines them. The registry is not a global coordinator or Ready publication mechanism. The test sources exercise disjoint encounters, all-role overlaps, real late name collision, cleanup/retry, serial/token ownership, mutated GUID after admission, binding invalidity and teardown orders, with explicit source-only qualifications for mid-load drift, reentry and quarantine. No new runtime outcome is claimed.

Independent capture: Codex/C248Evidence/verification.json and verification.sha256, produced by review_c248.py exit0. All58 receipts, exact191 live Source files,24 existing pins,13 dependency pins,14 candidate assets,7 catalog assets and2 binary pins match. Six Review copies equal live bytes. Against the185 pre-DD18 baseline: six additions and only the separately reviewed DD17 cpp change. Against the post-C247191 manifest: exactly registry cpp and registry tests changed.

Current accepted source pins:

- DD17 cpp 1a99ba054dc606c6514973e6423723bd3a3701ce40ea8c87f2c432d30e457f58.
- WorldPreparation h 8a71cdf98fe3063c9ac48e17cc02a295f06bf4ef719cc99d0875814c48898933, cpp ce6a1b31dfb2e80f9439766d25f9ac77a5b6a2b8c05721264c30dcba3e0e417c.
- PreparationRegistry h d9d813c7711e5ccdeba1e8a063c1adc44d76ae4ad6986f5d4d826ffa62f4ddd2, cpp b6bfc4a8888d397ec8c58d35d3b8d6f7ada7229692ecb37de9c3297ac7b9078d.
- WorldPreparation tests fb867b159223253d756e6a07e0d44a45378ea99f0c6f8eb3e606b95b8eb1ec90.
- PreparationRegistry tests f469b19aa285905d2fc260a348923fff04f9b2f06b6c9617dae5c6ec387ce574.

Claude alone is released to execute ONE serialized verification on these frozen191 Source files:

1. Fresh operator safety and exact source/dependency/asset/binary capture. Use the previously reviewed NoRelaunch workflow, respecting any actual job or dirty-asset state; historical notes are not liveness evidence. Close editor before build. Never accept a shipped-content save or interfere with another job.
2. One editor build. Preserve raw command, stdout/stderr, exit and elapsed time. Report actual UHT invocation only if the log contains it. No non-editor build or automatic fix rounds.
3. On build success, focused OneBossFight.Binding.WorldInput, then WorldPreparation, then PreparationRegistry, serially. Actual discovery and full completion names required. Three, four and three respectively are expectations, not assumed results. Launch editor with -nosound as applicable; no PIE.
4. Only if all focused groups pass without fatal/ensure/unsupported-fixture/observer failures: full existing suite. Expected prior119 plus exact ten new unique names =129; actual raw discovery/completion membership decides. Preserve CookCoverage and every prior test; no missing, duplicate, filtered or silently skipped result.
5. Preserve raw logs, independent job exits/times, final complete Source manifest, dependency/asset manifests and binary SHA256, including all warnings. Stop and report failure or drift before any fix/retry; exact delta requires fresh review. No speculative expected-token change, weakening, extra cvar or PIE fallback.

Preserve original C244/C245/C246 attempts, reconstructed-manifest provenance exception, DD10 failures and prior warning/error history. Quarantine/mid-stage drift/reentry and worker-thread destruction remain source-only or unexecuted as stated. Transient definitions/hand manifest rows are not authored asset provenance. No positive runtime result, cold-load guarantee, registration, BeginPlay of the managed consumers, context publication, Ready, legacy suppression, startup/target/reset wiring, actual duel/networking, new driver gate, package, Shipping or all83 completion is released or certified. No staging/commit/push release.

MCP communication is now active for Codex. Its send operation demonstrably reaches the authoritative OneBossFight mailbox; get_message(C248) still returned not found and status/history are inconsistent. Until repaired, actual repository evidence remains the review source. This read-path defect does not alter work authority.
