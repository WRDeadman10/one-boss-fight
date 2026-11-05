# E160 decision audit: invalid elapsed handling

Queue E's D45 link is the warp-curve edge audit. The key distinction is that `RPGBossWarpCurve::Fraction` accepts normalized `T01`, not elapsed seconds or duration; Queue E is corrected to avoid promising an elapsed-time policy.

For nonfinite normalized time or invalid/nonfinite overshoot amount, `Fraction` returns 0. Valid normalized time is clamped to [0,1]. The helper is unwired; the executor's separate timed warp uses its own elapsed/remaining-time logic. No elapsed value is passed to this helper, so a missing/negative elapsed policy cannot be inferred here.

No decision is needed for the helper's current normalized-input contract. If a caller is added, owner/Lead must decide and verify how it converts elapsed time to normalized input and handles invalid duration before integration. Static inspection only; no tests/build/Editor run.
