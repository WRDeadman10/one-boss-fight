# DD4: explicit native phase transition adapter implementation

Next concrete package after C193 stats tests. Claude source+test diff BEFORE build. Add ONLY `Player/RPGBossPhaseAdapters.h/.cpp` and `Tests/RPGBossPhaseAdaptersTests.cpp` in Source/OneBossFight. Pin current accepted dependencies and whole-source manifest; do not edit the existing binding/compiler/native components/stats adapters/attachment paths. No new owner decision or repeat field audit needed.

## Actual typed mapping

Reuse existing `FRPGPhaseConfig` and Config.Phases, with an **explicit FName SelectedPhaseId** passed to validation/helper/plan factory. Select by ID, never first/last/index0 and never by parsing manifest Value. This backend represents the legacy component's one transition from implicit base phase to phase two. For this isolated backend, accept exactly one transition record with that ID; return a named unsupported-native-phase-set error for extra transitions. This is not a change to the generic compiler/asset array domain, nor a full phase policy or P7 feature claim. The future planner/authoring binding must supply the selection explicitly.

| Selected typed field | Native assignment |
|---|---|
|EntryHealthFraction|URPGBossPhases::PhaseTwoHealthFraction|
|SpeedMultiplier|MovementScale|
|RateMultiplier|AttackRateScale|
|AttackMultiplier|DamageScale|

Validate selected ID/presence/set capability and all4 finite scalar values before any write. Threshold>0 and<=1; multipliers>0. Preserve fractional multipliers below1 when native arithmetic supports them: no invented >=1 rule. Because reset computes inverses of speed/rate, explicitly reject nonfinite inverse results as unsupported native arithmetic, rather than clamp or claim application. This check does not prove real ability-rate/attribute round-trip behavior or avoid all downstream overflow; actual-baseline arithmetic remains later evidence.

Follow accepted stats adapter lifecycle boundary: reject !IsValid/component being destroyed, wrong exact class, component begun/registered, missing/invalid/destroying owner or owner beginning/begun. No partial writes on any failure. No NewObject/RegisterComponent/attribute writes/timers/phase trigger inside callback. Leave transition duration, clips/roar, leap lock, fireball disabled/defaults, ability prefix and every runtime cache/state unchanged. Native entry multiplies rates; removal uses inverse. Do not alter those algorithms.

Expose pure validation and typed configure helper plus FRPGComponentPlan factory, capturing selected ID by value. Use existing class/instance identity `RPGBossPhases`. Declare/document the4 selected typed input manifest paths consistently (e.g. `Phases[<id>].EntryHealthFraction`, etc.). Treat those as metadata membership, not provenance/value derivation. No full-boss ready state or legacy suppression; an isolated phase plan is not a valid complete playable cluster.

## Actual focused test implementation

Nondefault thresholds/multipliers and selected-ID mapping; missing/empty ID; zero records; unsupported extra/duplicate transition sets; mismatched ID; all NaN/Inf/sign/threshold boundaries; fractional factors and finite-inverse limits. Ensure every invalid record leaves all4 assignment fields and accessible native state unchanged. Include two-owner/two-config isolation, copying/capture semantics, unchanged CDOs/defaults/other configuration, invalid/destroyed/wrong-class/registered/begun targets and no creation/registration by callback. Use concrete unrelated component classes, not abstract UActorComponent. Use retained allocated objects/no GC for destruction checks; no freed-memory assertion.

Native defaults0.6/1.2/1.2/1.25 are comparison baselines, not automatic substitution for absent authored input. Tests prove assignment/rejection on isolated native components, not phase transition, effective motion/rates/damage, reset or a real duel. Never tune timings or forge pack readback to make a test pass.

Deliver actual code/test diff+hashes and any narrow unavoidable seam proposal before build. No extra schema/profile fields, map/asset authoring, coordinator, association/reset wiring, pack changes, scripts, full gate or package. After these typed fields are verified, proceed to full-cluster schemas/startup integration in concrete packages rather than broaden this adapter into a generic reflective framework. AG remains resting/no new work; no Claude/Codex git; Codex no engine operations.
