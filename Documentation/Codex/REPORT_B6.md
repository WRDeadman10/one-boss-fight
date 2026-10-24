# B6 - A-3 close-clip offline pre-check

## Commands run

- `python -I Scripts/check_boss01_delivery.py` printed `Pillow missing: texture and render checks skipped` and `0 problem(s)`.
- `python Scripts/check_boss01_delivery.py` printed `0 problem(s)` (with two Pillow deprecation warnings).
- `python -I Scripts/fbx_probe.py` was run for each delivered A-3 FBX.

No editor, build, PIE, package, or game was run.

## Reproduced

| File | `fbx_probe.py` | Timing card |
| --- | --- | --- |
| `AN_Boss01_A1_QuickSlash.fbx` | 89 models, time mode 6, 1.2000 s | commit 0.33; active 0.35-0.50; recovery end 1.200 |
| `AN_Boss01_A3a_Combo1.fbx` | 89 models, time mode 6, 0.8000 s | commit 0.38; active 0.40-0.60; recovery end 0.800 |
| `AN_Boss01_A3b_Combo2.fbx` | 89 models, time mode 6, **1.3333 s** | commit 0.13; active 0.15-0.40; recovery end **1.350** |

## Finding

**Medium — A3b timing-card recovery end does not match its exported FBX.**
`Import/Boss01/Animations/AN_Boss01_A3b_Combo2.txt:2-6` reports length and
recovery end `1.350`, but `fbx_probe.py` reads an animation stack from `0.0000`
to `1.3333` seconds. The card's stated 41 frames (0 to 40) also corresponds to
40 frame intervals at 30 fps, or 1.3333 seconds. Claude should use the measured
1.3333-second end or request a 1.350-second export/card correction before wiring
the tracker recovery timing; otherwise the code will encode a 16.7 ms recovery
that the clip does not have.

The cards' in-place/root and grounded-feet statements are not independently
reproduced by `fbx_probe.py`; it does not sample animation transforms. The
contact-sheet visual claims likewise require the engine/visual review.

## A-6 — M-08 fog gate offline pre-check

### Commands run

- `python -I Scripts/fbx_probe.py Import/Boss01/Weapons/FogGate/SM_Boss01_FogGateFrame.fbx`
- `python -I Scripts/check_boss01_delivery.py` printed `Pillow missing: texture
  and render checks skipped` and `0 problem(s)`.
- `python Scripts/check_boss01_delivery.py` printed `0 problem(s)` (plus two
  Pillow deprecation warnings).
- Visually inspected `Import/Boss01/Weapons/FogGate/FogGateFrame_3Qtr.png`.

No editor, build, PIE, package, or game was run.

### Reproduced

- The FBX reports unit scale `0.99999998`, two models, a zero-transform mesh,
  and `SOCKET_MistCenter` parented to it at `(0, 0, 300)`.
- It has the requested material names: `M_Boss01_Arch_Stone`,
  `M_Boss01_Arch_Trim`, and `M_Boss01_Arch_Rune`.
- The visible render shows an untextured grey stepped lintel and pillar frame,
  a central pale rune/keystone block, a peach scale figure, and the complete
  base/top silhouette inside the image. It is only a three-quarter view; no
  front orthographic scale render was delivered.

### Findings

**Medium — the delivered FBX disagrees with the A-6 stated geometry.**
`fbx_probe.py` reads `224` vertices, `168` polygons, and bounds
`x -535..535`, `y -84..84`, `z 0..723`, while A-6 claims 88 vertices, 66
polygons, and total bounds 1000 by 160 by 720 cm. The measured exported bounds
are 1070 by 168 by 723 cm. The `MistCenter` socket is correct, but the claimed
outer frame envelope is not reproduced. Claude should decide whether the
measured 70 cm width, 8 cm depth, and 3 cm height overruns fit the intended
arena placement before import.

**Medium — clear opening dimensions are not evidenced offline.**
`SM_Boss01_FogGateFrame_Sockets.txt:5` describes an “800 cm wide fog portal
opening”, but neither that text nor `fbx_probe.py` measures the opening's
interior clearance. The one render does not provide an orthographic/front
measurement. Preserve the requested 800 by 600 cm opening until an engine or
geometry review measures it.

**Low — presentation evidence remains incomplete.** The three-quarter render
does now show the entire frame, but cannot answer the requested front-view
proportion comparison against a 190 cm human/box. Claude already requested a
front orthographic render and stepped/corbel silhouette refinement; those
requests remain supported by the visible evidence.

## A-7 — M-08 revised render evidence

- Re-ran `fbx_probe.py`; the FBX remains 224 vertices, 168 polygons, unit
  scale ~1, bounds 1070 by 168 by 723 cm, three stated material slots, and
  `MistCenter` at `(0, 0, 300)`.
- Ran the normal delivery checker; it printed `0 problem(s)` (plus two Pillow
  deprecation warnings).
- Visually inspected `FogGateFrame_Front.png`. It shows the complete front
  silhouette within the canvas, a 190 cm peach scale figure beside the opening,
  stepped plinths, shafts, corbels, lintel/cornice bands, and a central pale
  keystone/rune block. The gold mid-pillar bands appear to meet the shafts in
  this front render; the image cannot prove whether the unseen mesh has a
  through-hole at that joint.

No editor, build, PIE, package, or game was run.
