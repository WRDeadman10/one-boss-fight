# BK-26–30 — Selector diagnostics and owned-tag generation fence

Implemented a lock-protected selection diagnostic getter/writer and routed early binding/selection refusal paths through the writer. The diagnostic records the current stable refusal token, including off-thread, world-state, generation/reset, definition, census, actor-state, spawn, and profile failures; a successful binding clears it. The test `OneBossFight.Binding.EncounterSelection.ThreadAndWorldStateRefuseBeforeResolution` seeds a stale value and verifies that off-thread and foreign-world refusals replace it.

Added participant-generation lookup for owned-tag cleanup retries. I-frame and parry components capture the generation when they acquire an owned tag; delayed retry callbacks compare actor identity and current participant generation before issuing removal, and carry that token across retries. A stale callback logs `cancelled_stale` and exits without removing the new generation's tag. Unbound legacy actors remain generation zero; ambiguous duplicate binding ownership fails closed.

The focused native regression `OneBossFight.Player.OwnedTagCleanup.PriorGenerationCannotRemoveCurrentTag` covers matching generation, the same actor with a newer generation, and actor identity mismatch. Native build/automation execution is pending a Lead editor/build release; no engine or asset operation was run.

Offline source contract: `python Scripts/Tools/test_bk4_bk5_cleanup_source_contract.py` — **5/5 passed**. `git diff --check` on scoped BK-26–30 files passed (only line-ending conversion notices). Source guards check that the retry lambda captures the generation token. No native compilation or runtime acceptance is claimed.
