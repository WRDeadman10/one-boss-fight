# Boss hit-stop stacking audit — D107

**Scope:** overlapping hit-stop requests, timing precedence, and existing pure-scope tests. Source review only; no time dilation exercised in Unreal.

The shared `FRPGDilationScope` is an extend-only single effect. The first `Begin` captures the original value and applies the requested dilation/deadline; later calls retain both `Saved` and `Applied`, and move `DeadlineReal` to `max(oldDeadline, Now + Seconds)`. A later shorter request cannot shorten the active pause or replace its dilation (`RPGLegend.h:22-44`). `End` clears active state and returns the first saved value (`:46-51`). This is extension, not a stack, minimum-dilation arbitration, or nesting.

`RequestHitStop` uses a constant target dilation of 1.0 as the scope's restoration baseline and applies `HitStop.Applied` to each distinct actor, saving each actor's own pre-request custom dilation exactly once. Overlapping requests therefore extend the common deadline without compounding actor dilation. Restore writes each original per-actor value and clears the tracked set (`RPGLegend.cpp:102-127`, `154-169`). The subsystem ticker uses real time, then restores on expiry (`:93-99`, `235-237`). Invalid/stale encounter requests are refused before scope mutation (`:77-90`, `102-108`).

`OneBossFight.Legend.DilationScope` tests first-start, second-request extension, keeping the later deadline, and a short request that cannot move it earlier (`RPGAutomationTests.cpp:685-704`). It does not test unequal requested dilation, actor-specific saved values, duplicate actors, exact expiry equality, or competing hit-stop and slow-motion scopes. The helper test does not prove the subsystem actor-application/restore path.

**Acceptance result:** source behavior is explicit: extend the deadline, preserve the initial applied dilation, restore each actor's initial value. Core deadline extension is directly tested; actor integration and mixed-effect precedence remain unproved. No separate precedence contract is documented for overlapping hit-stop and slow motion.
