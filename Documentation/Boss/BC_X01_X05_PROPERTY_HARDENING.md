# Queue BC Batch 1: X01–X05 property hardening

## Changes

- X01: extended AreaEffect validation coverage across every numeric member with NaN/Infinity rejection and just-outside release, delay, radius, damage, snare-duration, and speed-scale bounds.
- X02: extended ChannelDrain coverage across every numeric member with NaN/Infinity rejection and invalid start/end, excessive tick count, negative damage, range, and cone-angle boundaries. Existing deterministic loops assert tick-count caps and that capped healing never exceeds accepted HP loss or missing boss health.
- X03: added defensive-card/add-on conflict cases and an otherwise valid AreaEffect+ChannelDrain pair that must be rejected as mutually exclusive.
- X04: compiled a metadata-only legacy card with both optional add-ons disabled and checked the immutable snapshot remains disabled after source mutation.
- X05: reviewed the property-test paths; they use the synthetic `FInput` metadata fixture and pure `Validate`/`CompileMetadata` paths, without loading assets or creating transient worlds.

Changes are confined to `Source/OneBossFight/Tests/RPGBossMoveCardTests.cpp` plus this report and status docs.

## Verification boundary

The native automation suite was **not run**. The Lead owns the locked Development build and DD27j-pinned suite; no test pass is claimed. No Unreal/build/PIE/asset operation occurred. `git diff --check` is used for whitespace review only.

## Next

Continue BC-X06–X10 immediately. At the next cycle, inspect Claude feedback on the last BB and BC batches, apply bounded hotfixes first, then continue without waiting.
