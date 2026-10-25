# Critical gaps and ranked findings

“Confirmed” below means supported by the inspected implementation, not newly reproduced in gameplay. A potential symptom stays conditional until the stated test runs. The project is not declared unplayable.

## G01 — Critical: A6's damaging ring lacks its own shipping cue

Evidence: [Wave:162](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.cpp:162) advances/resolves the damaging band; its only ring drawing is inside !UE_BUILD_SHIPPING. [Issues:69](C:/UnrealProject/OneBossFight/Documentation/KNOWN_ISSUES.md:69) independently records no wave visual. Legend handles slam feedback, not the expanding ring ([Legend:456](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGLegend.cpp:456)).

Confirmed cause: gameplay geometry and production presentation are disconnected. The pack may show the central landing, but that does not show an expanding200–1100cm band.

Impact: the48HP outward threat can be invisible in the packaged presentation. Validate immediately in a debug-off Shipping capture; an independently wired current VFX would reduce this finding, but none was established in the inspected path.

Recommendation: P1 bind a production cue to the actual wave origin/radius/lifetime; keep it readable at reduced effects. Do not increase AI sophistication before this.

## G02 — High: hitch-dependent special execution and ring contact

Evidence: [Tracker:465](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:465), [Heal:255](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHealPunish.cpp:255), [Sweep:175](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossLowSweep.cpp:175), [Wave:153](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.cpp:153), [Wave:73](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.cpp:73).

Confirmed cause: sampled-state polling rather than event/interval crossing; ring has no previous-radius sweep. A5's50ms release interval is particularly narrow. A4/A6 can also be skipped if a sufficiently large step crosses their whole active span.

Impact: a visible throw/attack can have no corresponding projectile/volume, or a grounded player can be skipped by a ring. No new runtime reproduction was performed.

Recommendation: P1 explicit crossed-boundary handling with instance/reset/interrupt validation and swept annulus. Do not indiscriminately replay damage after an abort.

## G03 — High: pack fallback does not restore pack timing

Evidence: [Tracker:61](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:61), [Tracker:105](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:105), [Tracker:285](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:285), [Swap:69](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp:69).

Confirmed cause: authored and fallback montage names share a single timing row. The swap preserves pack assets when replacements cannot load, but native commitment/recovery uses authored numbers.

Impact: fallback blade notifies may damage before the declared native commit; telegraph scaling can use the wrong active time. Missing-asset/fallback runtime test is pending.

Recommendation: P2 separate effective timing by resolved montage, validate before start, preserve pack fallback assets.

## G04 — High: damage paths lack shared defense/outcome provenance

Evidence: [DamageH:25](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGDamageResolver.h:25), [DamageH:104](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGDamageResolver.h:104), [Wave:106](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.cpp:106), [LeapTest:103](C:/UnrealProject/OneBossFight/Scripts/Editor/pie_leap_wave.py:103).

Confirmed cause: pack blade/central damage and native special HP writes are separate. Own specials do not resolve guard/parry/knockdown. A6 central priority is inferred from any HP decrease, not an attributed accepted contact.

Impact: defense differs by attack path; unrelated loss/healing can corrupt direct/splash precedence. Whether a given move should be unblockable is a design decision, not an excuse for an undocumented bypass.

Recommendation: P3 preserve pack damage but expose an authoritative resolved outcome and shared move/instance/victim key; define per-move defense policy.

## G05 — High: execution identity and guaranteed recovery are incomplete

Evidence: [Tracker:234](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:234), [Tracker:389](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:389), [Tracker:251](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:251), [Tracker:411](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:411).

Confirmed native gap: ID arrives after montage start; branch veto happens after successor starts; RecoveryEndTime is not an enforced lock; no generic attack watchdog in tracker. Pack ability safeguards may cover parts and require U03.

Impact: early/stale-event attribution and real punish opportunity are uncertain. Do not claim a current softlock or universal fake recovery from this alone.

Recommendation: P2 narrow start/finalize adapter, then P6 measured branch/recovery policy.

## G06 — High: A4 exists but is not established in natural selection

Evidence: [Sweep:25](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossLowSweep.cpp:25), [Tracker:234](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:234), [Issues:71](C:/UnrealProject/OneBossFight/Documentation/KNOWN_ISSUES.md:71). Native autonomous call-site search found A5 scheduling, not A4; existing issue explicitly says BT never picks A4.

Cause: selection integration, not missing animation or damage code. Forced A4 tests cannot prove the player encounters its jump lesson.

Recommendation: P0 inspect actual BT gate and P5 connect the existing move with bounded frequency. Do not add a rival tick selector.

## G07 — High validation risk: visible sword versus hidden trace

Evidence: [Look:76](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossLook.cpp:76), [Log:3271](C:/UnrealProject/OneBossFight/Saved/Logs/OneBossFight.log:3271), [Issues:90](C:/UnrealProject/OneBossFight/Documentation/KNOWN_ISSUES.md:90). The split is confirmed; magnitude and player-visible unfairness are not measured here.

Recommendation: P4 overlay/capture actual visible blade and production samples. Do not retune radius or replace animation based on filenames or KI-106's superseded diagnosis.

## G08 — High release gate: performance and quality acceptance remain open

[Perf:23](C:/UnrealProject/OneBossFight/Documentation/PERFORMANCE_LOG.md:23) records Shipping28–29FPS/p99~40ms on accepted3060 proxy. [Perf:39](C:/UnrealProject/OneBossFight/Documentation/PERFORMANCE_LOG.md:39) records promising Development fire-light/shadow experiments but inconsistent baseline blocks. Do not claim those experiments pass the final Shipping gate.

Claude owns performance work. Preserve60FPS/p99<=16.67ms target, validate repeated packaged full fights and current visuals. Human telegraph/punish/camera tests remain separate from automation totals.

## Not findings of absence

Utility weights, adaptive pattern memory, full BT movement policy, Motion Warping and fair boss defensive reactions are U02/U03/U04 inspection gaps. They are not proven missing. The reference's grab and multiplayer are out of scope. No architecture replacement follows from these unknowns.

