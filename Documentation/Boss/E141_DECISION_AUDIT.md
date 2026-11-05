# E141 — selector reset immutable config

**Decision:** None is needed; Reset intentionally preserves the initialized candidate/config set. **Authority:** project owner if a future API is proposed to replace candidates during an encounter.

`FRPGBossMoveSelector::Reset` clears cooldown timestamps, repeat history, tie offset, and cone memory while retaining immutable config/candidates and `bInitialized` (`RPGBossMoveSelector.cpp:91-96`, state fields in `.h:67-75`). Double reset is idempotent by assignment. Existing tests cover cooldown/history reset and cone memory (`RPGBossMoveSelectorTests.cpp:78-83,219-224`); repeated seeded reset replay is now directly asserted by `FBossMoveSelectorRepeatedResetTieReplay`. No mutable state requiring a new reset policy was found.

Static source/doc audit only; no build/tests run by Codex.
