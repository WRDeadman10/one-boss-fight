# Queue_50 Batch 5 follow-up: charge notify input guards

**Date:** 2026-11-13  
**Finding source:** historical read-only audit X-1786 (task 23), recovered during BQ-61..65.  
**Files:** `Source/OneBossFight/Pack/RPGPackNotifies.cpp`.

**Review:** Accepted at source/planning level by Antigravity in A-976. Compile/runtime verification remains open.

## Change

`URPGANS_ChargeToTarget::NotifyTick` now fails closed when `StopDistance` or `MaxSpeed` is non-finite or negative. It also rejects non-finite/near-zero planar target distance before division, invalid remaining montage time, and non-finite/negative computed speed before changing movement velocity. This covers malformed serialized notify data because `ClampMin` is editor metadata only.

The guard prevents the reported zero-distance division path: a negative serialized `StopDistance` previously allowed a coincident target to pass `Distance <= StopDistance` and then evaluate `ToTarget / Distance`.

## Validation and limits

- Reviewed the changed function and the X-1786 reproducer path statically; the guard precedes speed computation and vector normalization.
- No test was added or run, and no Unreal build, PIE, or asset operation was performed. Native compile/runtime behavior remains unverified and should be checked by the Lead's next permitted C-1155 build/suite.
- The separate `RPGBuildLoadout.cpp` reflected `SetIntParam` property-type risk from X-1786 is unchanged.
