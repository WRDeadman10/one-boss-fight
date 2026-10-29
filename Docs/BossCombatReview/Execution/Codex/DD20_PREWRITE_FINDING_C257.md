# C257 DD20 required pre-write check

Claude: DD19 scoped run acceptance and A182 offline acceptance read. Before editing DD20 I followed C257 item7 ("if ... a hidden dependency on the legacy move table ... stop and say so with the evidence"). No DD20 Source edit or engine/build action has occurred.

LowSweep has a concrete tracker-table dependency:

- RPGBossLowSweep.cpp TickComponent gets URPGAttackTracker, requires GetCurrentMove()==MoveId plus IsActiveWindow, and drives BladeAngle from GetTiming(MoveId) only if ActiveEndTime>ActiveStartTime.
- RPGAttackTracker.cpp:124 GetTiming searches the component's Attacks array by MoveId; no definition/config lookup or typed timing lease is passed here.
- RPGAttackTracker.cpp:78-89 creates the native A4 timing/clip entry with fixed0.60/0.90 active bounds. StartMove:234 onward plays table ClipPath entries or the hard-coded ability-by-move map.

Thus validating MoveId as non-None/no-whitespace proves only syntactic identity and seven/eight-field assignment, not a resolvable move, correct active timing, or a working LowSweep. A configurable nondefault id can be accepted structurally yet never drive an attack. I have not altered the tracker/table to conceal this.

Source pins (read-only):
- RPGBossLowSweep.h 48630dcb71e7569567452e514f74196a881dd09ec5524a695345d6d69e6289ba
- RPGBossLowSweep.cpp bea63c889b32af847d69a65f0b144fe4219eca7c55e15877a6695681976c0e81
- RPGBossMath.h 89ff1aa3c367da2fe84de1583da889dd623bddd11787c416d43792f15cc2ebf0
- RPGAttackTracker.cpp f2d2615f1b938aa8bf1f4ad9d7574b1876446823d83b87cd69521ca9d1153f0c

Geometry findings for your scope/domain decision:

- SweepTouches compares Distance +/- PlayerRadius against Reach/InnerRadius, then raw PlayerAngle against Min/Max of the crossed angles expanded by capsule tolerance. Equal angles therefore produce a stationary angular band; reversed endpoints work through Min/Max; values beyond360 are raw interval bounds, NOT automatic multi-turn/wrapped coverage.
- Tick interpolates the two authored angles with FMath::Lerp. A generic finite-only endpoint check is not proof that subtraction/interpolation stays finite for opposing float extremes. No arbitrary360 cap should be presented as a derived native rule.
- Reach>=1 and BladeHeight>=1 are editor metadata. The implementation contains no such runtime floor. Height zero/signed height changes the feet-plane test; zero reach can still overlap a capsule. InnerRadius>Reach is not rejected natively, and a capsule can span both bounds; an ordering restriction would be an explicit authored semantic contract, not an existing native guard.

Shockwave fallback also consumes Tracker->GetCurrentMove()==MoveId/IsActiveWindow (RPGBossShockwave.cpp:152-155), so it does not eliminate the move-identity dependency, although its radial advancement does not call GetTiming for every step.

Decision requested from you as lead: confirm DD20 proceeds as an explicitly UNWIRED structural profile with unresolved tracker/move-table capability and state the intended radius/height/angle capability contract, or issue a different exact fallback. I recommend retaining LowSweep with those limitations rather than silently promising move resolution or introducing tracker/schema work. Your item7 currently requires this stop before write; no owner confirmation or broader permission is being inferred.
