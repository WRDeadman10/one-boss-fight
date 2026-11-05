# Boss arena edge rule audit — D109

**Scope:** geometry assumptions, edge margin response, center behavior, and existing endpoint tests. Static review only; helper is explicitly unwired.

`RPGBossArenaEdge::Evaluate` operates in 2D centimeters on a circular arena centered at `Center`. It computes radial distance `d = |Center - Boss|`, edge distance `ArenaRadiusCm - d`, pressure `clamp((MarginCm - edgeDistance) / MarginCm, 0, 1)`, and normalized inward direction `(Center - Boss)/d` (`RPGBossArenaEdgeRules.h:7-20`). Pressure is zero at or inside the inner edge of the margin (`d <= radius - margin`), rises linearly across the margin, reaches one at the circle wall (`d == radius`), and remains one outside. At the center, the inward vector is undefined, so the helper returns the zero-initialized result. This rule has no capsule/body radius or polygon/nav boundary model.

Invalid/nonfinite radius or margin, nonpositive dimensions, nonfinite vector components, nonfinite distance, and near-zero center distance return zero pressure and zero direction (`:10-13`). The helper does not move the boss back to center; recovery is a separate runtime policy, and this helper is marked unwired.

Tests cover a safe interior point, half-margin point, exact wall, outside clamp, center, zero margin, and infinite radius (`RPGBossArenaEdgeRulesTests.cpp:9-19`). They do not cover exact zero-pressure margin boundary, margin greater than radius, NaN position/center/margin, negative radius, or direction normalization away from center. Margin greater than radius is accepted by the helper; the formula then yields positive pressure even at center-distance zero, but the center early return suppresses it, so such a config has unintuitive geometry and no validation gate is present here.

**Acceptance result:** the circular 2D radial assumptions and linear clamp are explicit; current tests establish representative safe/half/wall/outside values. Exact inner-margin boundary and invalid geometry combinations remain gaps. The helper has no center-recovery behavior and no runtime wiring claim is supported.
