# AK-SPRINT — native rule and montage authoring tests

Added test-only cases to three existing automation suites:

- `RPGGuardCounterRulesTests.cpp`: the exact case-sensitive `BlockReaction_C` suffix, extra trailing token rejection, and guarded reaction rising edge versus steady/nonblocking states.
- `RPGAutomationTests.cpp`: null observed/active montage behavior and semantic `Strong` kind retention for the same active montage after attack arrays are restored. Existing identity and attack-data tests remain.
- `RPGMontageUtilsTests.cpp`: zero-slot rejection, NaN/infinite range rejection before mutation, and a two-slot montage where a valid range edits the first track while leaving the second unchanged. Existing empty-segment, range and package-dirty checks remain.

These are test-only changes. Scoped whitespace checks pass. Codex did not build or run Unreal; Lead owns compilation and native suite results. No production source was changed.
