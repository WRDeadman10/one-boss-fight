# 18 — VFX, Sound, Camera, Readability, Accessibility

## Visual signals are part of combat rules

VFX cannot be treated as a final decorative layer. If weapon geometry is narrow, the trail should not visually imply a massive hit wedge. If a ground ring damages at an expanding perimeter, emissive markings need to correspond to the moving ring — not a static full disk.

### Telegraph channels

- **Pose:** low thrust vs high smash vs side arc.
- **Weapon material:** quick glint at release; don't use same light flash for 12 attack types.
- **Sound:** chain movement for backhook, deep bell for radial ring, steel crack for thrust.
- **Ground preview:** warn about localized slam/fissure with shape accurate to damaging region.
- **Animation acceleration:** release cue should coincide with movement onset, not arbitrary camera shake.

## Sound timeline

`Preparation Foley → Warning Accent → Swing Whoosh → Contact or Miss → Aftermath` with optional silence/hold. Different attacks need distinctive rhythms. Sound cues should remain readable at low dynamic range and not vanish during loud global music.

## Camera

- Avoid lock-on target points too high on a tall boss; aim at a stable chest offset.
- Ensure whole weapon threat generally enters view, especially overhead or long lateral sweep.
- Implement camera collision/shoulder adjustment near wall.
- Limit shake duration to impact moments and reduce shake for accessibility.
- Avoid cuts away from the player during any active attack unless temporarily cinematic/invulnerable and clearly safe.
- At very close range, verify boss doesn't completely obscure the incoming blade.

## Lumen / expensive visual effects

UE 5.5 with Lumen enabled can be costly with many translucent Niagara emitters and dynamic lights. Use local emissive/glow carefully, cap spawn rates and overdraw, and test packaged performance. Never let a frame-time spike systematically change attack collision reliability. Light the boss so wind-up silhouettes are readable against the environment.

## Accessibility

Offer optional camera shake reduction, high contrast telegraph alternatives for color vision differences, readable audio cues, hit direction indicators if desired, configurable lock-on distance, and effects intensity slider. Do not rely on red alone to distinguish ground AoE.

## VFX correctness test

For each move capture three images at `BeforeActive`, `FirstContact`, `EndActive`; outline gameplay collision and compare VFX. If player is damaged visibly outside trail, fix geometry or animation rather than enlarging particle effects to disguise the mismatch.
