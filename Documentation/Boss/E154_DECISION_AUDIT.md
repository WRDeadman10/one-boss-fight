# E154 decision audit: yaw probe profile authorship

Queue E's D39 reference is reposition-budget coverage. The relevant helper is `RPGBossYawProbe::YawAt`; the related math audit is D43. Queue E is corrected.

The probe is a deterministic test signal, not a designer-authored gameplay profile: it returns center plus amplitude times a sine of sample index and period, and fails to zero for non-finite center/amplitude or nonpositive period. The boss console variable is explicitly a test hook and defaults off. No shipped profile authors this signal.

No owner decision is needed while this remains test-only. Any proposal to expose it as gameplay or profile data requires owner approval of purpose/range/authoring surface before implementation; Lead reviews wiring. Static inspection only; no tests/build/Editor run.
