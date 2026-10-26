# Tracker seam — staged, not applied

Prerequisite: step1 accepted, draft promotion reviewed, preimages and hashes taken immediately before modifying the existing tracker. This seam adds **observational metadata only**. It is not G4 Montage_Stop caller instrumentation or G5 forced pack-move instrumentation.

1. In `Player/RPGAttackTracker.h`, BEFORE `RPGAttackTracker.generated.h`, add `#include "Boss/RPGShadowCompare.h"`. The generated include remains last.
2. In the tracker class public section, add:

```cpp
#if !UE_BUILD_SHIPPING
RPGTimeline::FAfterTracker OnAfterObservation;
#endif
```

3. In `RPGAttackTracker.cpp` add `#include "Misc/ScopeExit.h"`. Immediately after its existing `Super::TickComponent(...)` call, BEFORE the first actor/anim lookup, insert:

```cpp
#if !UE_BUILD_SHIPPING
ON_SCOPE_EXIT
{
    if (OnAfterObservation.IsBound())
    {
        const RPGTimeline::FPassiveSnapshot Sample = RPGTimeline::CaptureAfterTracker(*this);
        OnAfterObservation.Broadcast(Sample);
    }
};
#endif
```

This covers the current disabled/no-anim, dead, INDEX_NONE/untracked, denied montage, priority-veto and branch-denial returns as well as the normal end. It copies after the tracker in the SAME tick; no second tick prerequisite or animation evaluation. It cannot identify the caller/cause of a stop. Listener must not mutate gameplay or destroy the tracker from its callback. Current only listener is the staged read-only shadow component.

4. During reviewed hydration, configure shadow with precompiled per-variant artifacts/content lease before registration; then BindTracker on the actual associated actor once the full batch is ready. Unsubscribe in EndPlay (implemented). No anonymous process-global bus. Do not call StartMove/PlayMoveMontageForTest to manufacture natural coverage. Passive adapter handles untracked active montage metadata without inventing a native move/action identity.

This snippet depends on promoting BOTH step2 and step3 headers; the shadow cpp intentionally depends on the tracker member introduced here. The live module must NOT see only half this change. No preimage is needed yet because existing files remain untouched.
