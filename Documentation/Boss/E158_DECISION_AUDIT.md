# E158 decision audit: aggro hysteresis ownership

Queue E's D43 link is the yaw-probe audit; the matching transition audit is D96. Queue E is corrected.

`RPGBossAggro::Step` owns range and dodge-rate entry/exit hysteresis as pure rules. The boss updates the band from profile thresholds only when `bAggroEnabled` is true; source initializes the band to Balanced on generation reset. The feature is opt-in/default-off in the profile. This gives a clear code owner but does not approve shipped use or the tuning values.

Owner approval is needed before enabling it in a shipped profile or promising tuning semantics. Until then, the disabled default remains. Lead owns implementation review and runtime proof. Static inspection only; no tests/build/Editor run.
