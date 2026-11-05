# E162 decision audit: retreat threat equality

Queue E's D48 cross-reference concerns move-card hold/warp timing, not retreat threat. The relevant rule is D102; Queue E is corrected.

`RPGBossRetreat::ShouldRetreat` requires inclusive `Threat01 >= ThreatThreshold`; exact threshold equality passes the threat gate, provided the strict range gate also passes. D102 records existing default-threshold equality coverage and the missing configurable adjacent-value checks. The helper is unwired.

No owner decision is needed for the explicit comparison. A different equality rule or authored threshold policy would be a gameplay change and needs owner approval; Lead reviews wiring. Static only; no tests/build/Editor run.
