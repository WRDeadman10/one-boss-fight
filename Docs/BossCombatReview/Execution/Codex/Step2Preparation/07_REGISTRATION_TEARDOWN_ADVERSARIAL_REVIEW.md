# Registration and teardown: abstract-model correction

Codex lead, 2026-10-26. Offline design refinement only. No live Source, Config, Scripts, assets, build, editor or gameplay changes. Step2b and later integration remain held under the existing approvals.

## Reproduced gap

The original 31-check coordinator model did not cover unbinding from inside a registration callback. Independent reproduction called `unbind('boss')` from `register('E', callback)`. Registration returned false, but `route('boss')` returned `Legacy`: deleting actor records lost the explicit-binding rejection. Poisoning the detached encounter object did not repair that routing decision. This is a defect in our abstract model and an incomplete design contract, not a reproduced Unreal runtime defect. The earlier 31/31 result remains historical and did not test this case.

A related identity hazard is reusing an encounter ID and slot at the same generation with different actors: a copied old key could then resolve into the replacement encounter. Actor-only retirement checks would miss it. A per-encounter busy flag also allowed a callback to begin registration in another encounter in the same world.

## Revised proposed contract

- Unbinding invalidates the whole encounter, removes active target resolution and retains rejection for every previously claimed participant. A surviving partner must not fall through to legacy attachment. Ordinary actors never claimed by a binding still use legacy.
- A fresh explicit whole-batch reservation may release participant quarantine only after complete validation and with a generation greater than the actor's retired generation and the reused encounter ID's retired generation. Same-generation retries cannot revive old keys. This is a necessary identity condition, not permission to rehydrate an actor whose components already registered: the real adapter must independently validate lifecycle state, owned-component cleanup and preexisting consumers. Existing no-begun-actor rules still apply.
- Registration uses a world-scoped transaction guard. While callbacks run, reservation, preparation, another registration and generation advancement are refused, including operations against another encounter. Invalidation, unbinding and world teardown remain permitted safety operations. After each callback the current transaction checks invalidation and stops remaining registrations. A rejected nested operation caught by its caller need not poison that caller's otherwise valid transaction; uncaught callback failures poison it.
- Teardown releases model maps and the transaction guard; disposed-world routing remains Reject. Unbinding one encounter does not invalidate another encounter's current keys.

Production representation is still open: use weak actor identity with serial-safe keys, not strong actor references or names that can be reused. Keep encounter generation high-water marks for the world session, or require non-reused encounter identities with equivalent stale-key guarantees. Define retirement cleanup when an actor is conclusively destroyed; do not clear a surviving participant's fence merely because another participant ended. These are implementation review requirements, not an instruction to copy JavaScript Maps into UE or to add an approved reset authority.

## Verification

`node Docs/BossCombatReview/Execution/Codex/Step2Preparation/coordinator_contract_model.mjs` exits zero: **41/41 abstract checks**, preserving the original 31 and adding ten checks for mid-registration unbind, retired-generation refusal, atomic failed rebind, newer-generation rebind with old-key rejection, reused encounter identity with replacement actors, cross-encounter registration/preparation/reservation/advance refusal, callback disposal, and idempotent isolated unbind. No generated source snapshot or evidence baseline was overwritten.

Required future UE evidence remains real OnRegister invalidation/EndPlay/reentrancy fixtures, weak-reference destruction and GC behavior, both attach triggers after unbind, supported reset/replacement generation authority, and complete consumer cleanup/activation ordering. Node assertions establish none of those runtime facts and provide no performance result. No Claude wake-up or owner decision is needed for this offline correction.
