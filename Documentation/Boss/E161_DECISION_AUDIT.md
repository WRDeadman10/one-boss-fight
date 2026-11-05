# E161 decision audit: retreat range equality

Queue E's D47 cross-reference concerns baked sample validation, not retreat. The relevant rule is D102; Queue E is corrected.

`RPGBossRetreat::ShouldRetreat` requires strict `RangeCm < CloseRangeCm`; exact close-range equality does not retreat. D102 documents this and the existing exact-equality test. The helper is unwired, so this is a pure-rule contract only.

No owner decision is needed for the explicit comparison. If product design wants equality included, owner approval is required before changing the rule; Lead reviews integration. Static only; no tests/build/Editor run.
