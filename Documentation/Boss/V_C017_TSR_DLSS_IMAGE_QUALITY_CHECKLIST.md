# V-C017 — TSR vs DLSS image-quality review checklist

Use this checklist for the same fight moments, resolution, display, camera, settings and capture path. Compare TSR and each accepted DLSS mode from Round 6; do not choose a default from FPS alone. The benchmark's upscaler and primary fraction upper bound must be captured with Dynamic Resolution disabled as specified in the Round 6 kit prompt.

| Scene or event | Inspect for | Record |
|---|---|---|
| Static arena wide shot | Fine stone/brick detail, thin edges, distant geometry, shadow boundaries | Mode, screenshot pair, visible loss/artifact and severity |
| Slow camera pan / lock-on orbit | Temporal shimmer, crawling edges, ghost trails on high-contrast edges | Exact motion and whether artifact persists after camera stops |
| Player and boss traversal | Silhouette breakup, disocclusion trails, motion clarity, animation readability | Attack/movement segment and visual impact |
| Fast attack / dodge / phase effect | Particle trails, alpha/translucent effects, blood/fire/glow stability, effect clipping | Ability/event and whether either mode obscures a telegraph |
| Volumetric clouds and cloud shadows | Banding, softness, temporal noise, shadow edge stability, horizon silhouette | Cloud state and camera view; use matched exposure |
| HUD and thin text | UI sharpness, scaling, legibility, edge halos | Screenshot at native display scale |
| Frame transitions | First frames after camera cut, phase transition, boss effect, or reset | Whether temporal history visibly settles or smears |

## Controlled review

1. Use identical captures and side-by-side or rapid A/B comparison at native 1920x1080; preserve one unscaled crop for detail and one full-frame view for composition.
2. Blind-label the files if practical. Reviewers independently classify each mode: acceptable, acceptable with noted artifact, or reject due to combat-readability loss.
3. Record the exact active DLSS mode witness, primary fraction upper bound, AA method, build/GPU/driver, and capture scene with every judgment. A quality score without an evidence-linked capture is inconclusive.
4. Require owner image-quality acceptance before Round 6 Phase 2, a preset, or player-facing default. This checklist itself makes no visual-quality decision.
