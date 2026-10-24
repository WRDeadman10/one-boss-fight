# B1 - Report 13 offline pre-review

## Scope

This is an offline pre-review only. It does not accept the delivery: socket-space
poses, sampled transforms, contact-sheet visuals, and engine import behaviour need
Claude's engine review.

## Commands run

- `python -I Scripts/check_boss01_delivery.py` printed `Pillow missing: texture and render checks skipped` and `0 problem(s)`.
- `python Scripts/check_boss01_delivery.py` (without `-I`, as required by the art brief) printed `0 problem(s)` after two Pillow deprecation warnings.
- `python -I Scripts/fbx_probe.py <each delivered FBX>` for the eight animation files and three weapon meshes listed below.

No editor, build, PIE, package, or game was run.

## Reproduced from the files

| Report 13 claim | Offline evidence | Result |
| --- | --- | --- |
| The eight animation durations in `REPORT_13.md:59-66` | `fbx_probe` reads exactly 3.5, 5.0, 3.5, 1.8, 0.7, 1.0, 2.0, and 1.6 seconds respectively. | Reproduced |
| Animation skeleton size implied by the 88-bone assertions in `REPORT_13.md:13` and `REPORT_13.md:96` | Every probed animation contains 89 FBX models (the skeleton plus FBX scene/root representation). | Consistent, but not a transform audit |
| Greatsword material set | `SM_Boss01_Greatsword.fbx` has `M_Boss01_Blade`, `M_Boss01_Guard_Grip`, and `M_Boss01_Blade_Glow`. | Reproduced |
| Dex sword size/material structure in `REPORT_13.md:48` and `REPORT_13.md:113` | Each dex mesh has a 100 cm Y extent (`-18..82`), three named material slots, and 342 vertices / 340 polygons. | Reproduced for extent and material names |
| Unit recipe | Animation FBXs report unit scale 1.0; weapon FBXs report 0.99999998 (floating-point equivalent of 1.0). | Reproduced |

The raw greatsword mesh is 541 vertices / **569 polygons**, with bounds `x -31..31`, `y -21.33..163.30`, `z -3.82..3.82`. This is the current file measurement, not the earlier 548-polygon reference in `BRIEF_13.md:29`.

## Claims the prescribed offline tools cannot reproduce

- All sampled bone values, loop/seam errors, feet clearance, breathing amplitude, and exact held-pose comparisons in `REPORT_13.md:11-25` and `REPORT_13.md:59-66`. `fbx_probe.py` reads scene structure and stack duration, not sampled pose transforms.
- Socket composition, sword grip/tip positions, hand distances, or engine-frame claims in `REPORT_13.md:72-96`. The mandatory engine socket transform originates in `BRIEF_13.md:8`; an FBX-only probe cannot apply it as Unreal does.
- Wireframe deltas, amber counts, image bounds, edge clipping, brightness, and contact-sheet descriptions in `REPORT_13.md:28-36` and `REPORT_13.md:102-129`. The `python -I` checker explicitly skipped Pillow image checks; the non-isolated checker did report zero problems, but that is not an independent pixel audit.
- Exact seven-socket claims: `fbx_probe.py` reports the weapon mesh structure but does not expose socket names/count in its concise output used here. The sockets text file and engine import remain review items.

## Findings for Claude's engine review

1. **Medium — numeric art assertions remain unverified offline.** Report 13 states the dormant tip is `z=0.74` (`REPORT_13.md:18`) and Wake ends in the PhaseRoar frame with zero difference (`REPORT_13.md:21-25`), but those are precisely the engine-space assertions `BRIEF_13.md:8-17` requires the socket attachment to validate. Verify these first after import; do not accept them from the report alone.
2. **Low — checker result must be qualified.** `REPORT_13.md:3` claims a checker result of zero problems. The required isolated invocation returns zero only after saying Pillow is missing, so it skips render/texture checks. The normal-Python invocation returned zero with Pillow available, but neither outcome independently validates Report 13's quoted pixel counts.
3. **Info — mesh count differs from the historical reference.** The current greatsword is 569 polygons, while the old structure target says `548 polygons` in `BRIEF_13.md:29`. Report 13 does not claim a polygon total, so this is not a contradiction; decide during asset import whether the earlier target is still binding.

## Recommendation

Proceed to Claude's scratch-import/engine-space review. The delivery is structurally complete according to both checker modes and all eight advertised animation lengths match. Do not mark the socket-dependent dormant/wake, animation-pose, or render-quality claims accepted until the engine review measures them.
