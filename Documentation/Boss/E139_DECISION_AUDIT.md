# E139 — zero-weight refusal token stability

**Decision:** No separate compatibility promise is needed; the current named refusal is `Selector.Domain`. **Authority:** project owner if external tools or serialized content begin depending on token-specific compatibility.

Selector initialization rejects candidate weight `<= 0` and invalid multipliers with `Selector.Domain` (`RPGBossMoveSelector.cpp:19-28`). `FBossMoveSelectorInit` asserts that token for zero weight (`RPGBossMoveSelectorTests.cpp:40-48`). Thus zero-weight exclusion is a current behavior contract, not a supported “eligible but never selected” mode. No evidence shows an external consumer relying on this token across versions; avoid claiming cross-version stability beyond current tests.

Static source/doc audit only; no build/tests run by Codex.
