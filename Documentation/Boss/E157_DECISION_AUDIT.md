# E157 decision audit: grounded-height missing sample

Queue E's D42 link is LOS proof-token coverage, not grounded-height behavior. The matching finite fallback is D91; Queue E is corrected.

`RPGBossTrack::GroundedZ` takes a floor Z value directly; it does not query or represent a missing trace sample. A non-finite floor value returns 0, while finite floor Z with invalid capsule/surface values returns the floor Z. If adding capsule half-height and skin overflows, it returns the finite floor Z. The actor's `FloorSeparationCm` uses capsule dimensions and actor locations; it does not call GroundedZ.

No decision is needed for the current pure helper fallback. Any runtime trace failure policy belongs to the eventual caller and needs owner direction only if that caller is introduced. Static inspection only; no tests/build/Editor run.
