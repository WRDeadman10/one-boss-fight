# Designer reference: arena edge pressure

`RPGBossArenaEdge::Evaluate` measures how close a boss is to a circular arena boundary and returns an inward unit direction toward the center. The caller supplies positions and chooses how pressure affects behavior; this helper does not move the boss.

| Input/output | Unit | Default | Valid domain |
|---|---|---:|---|
| `Boss`, `Center` | world-space 2D coordinates | none | finite components |
| `ArenaRadiusCm` | centimeters | none | finite and greater than 0 |
| `MarginCm` | centimeters | none | finite and greater than 0 |
| `FResult.Pressure` | normalized scalar | 0 | 0 to 1 |
| `FResult.Inward` | direction vector | zero vector | normalized toward center when defined |

`EdgeDistance = ArenaRadiusCm - distance(Boss, Center)`. Pressure is `clamp((MarginCm - EdgeDistance) / MarginCm, 0, 1)`: it is 0 at or deeper than the inner margin, rises linearly through the margin, and is 1 at or outside the nominal wall. The inward vector points from the boss to the center.

Non-finite positions or dimensions, non-positive radius/margin, non-finite distance, or a boss at the center return the default result (zero pressure and zero direction). The center case has no defined inward heading. Source: [`RPGBossArenaEdgeRules.h`](../../Source/OneBossFight/Player/RPGBossArenaEdgeRules.h:8), unit tests: [`RPGBossArenaEdgeRulesTests.cpp`](../../Source/OneBossFight/Tests/RPGBossArenaEdgeRulesTests.cpp:6).
