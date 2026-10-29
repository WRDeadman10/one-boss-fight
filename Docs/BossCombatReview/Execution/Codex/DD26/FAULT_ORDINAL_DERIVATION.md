# DD26 fault ordinals re-derived from frozen allocation code

Preparation.cpp:240 resets GStepCount. Allocate loops MemberIndex then PlanIndex at139/146, skips target-only, and calls InjectedFaultAfterStep after each successfully completed allocation at179. Configure loops in the same member/plan order at190/197 and calls the step hook after successful callback/checks at221. The step hook increments once at24, no preflight or bookkeeping step is counted.

With two boss-core members and twelve plans each: allocations boss1=1..12, boss2=13..24, configures boss1=25..36, boss2=37..48. Target-only contributes zero. Sample first/middle/last of EACH block, extending the original1,3,5 sample positions for a block of5 to positions1,6,12 in a block of12: {1,6,12,13,18,24,25,30,36,37,42,48}. This is re-derived by operation order, NOT multiplying the old numbers.49 is beyond all48 real steps and is the non-firing control (old21 beyond20). No production step counter code changed.

The collision fixture still blocks third component Encounter on boss2: all12 of boss1 and2 earlier boss2 components must be cleaned, blocked third remains, ALL9 later names indexes3..11 absent. Tests now loop over every later name, rather than only the former indexes3,4.

WorldInputCompilerTests old633-634 literals9 are ANIMATION lease counts from the explicit nine-entry BossAnimationPaths array, not plan/component counts. They intentionally remain9. Registry AddSet tags5/6 are encounter IDs, not counts; remain unchanged. Existing scalar0.5/1.5 etc remain unchanged.
