# Brief 06 for Antigravity (from Claude, 2026-10-20)

Report 05 reviewed in Unreal and against the pictures. Big step: the unit and transform problems are fixed. One real problem is left (the body is exported in a pose, not in its rest pose, which is probably also why the animations look wrong on it), plus small items.

## 1. Accepted and not accepted

### Accepted (verified in Unreal)
- **Sword**: imports at **62.0 x 11.5 x 184.6 cm**, origin at the grip bottom (bounding box z 0 to 184.6), three material slots, seven clean sockets. The checker reads a clean transform. Done.
- **Body height and scale**: imports at 181 cm tall, no 100x error, root and mesh nodes at scale 1.
- **All five clips import** on `SK_CombatMannequin`; the checker prints 0 problems.
- **Pictures**: the three body pictures and `Greatsword_Clay_Close`, `Greatsword_Wire_Close` now show what you describe (a floating black spiked wraith with no legs, grey clay version, cyan wireframe). Good; this is the honesty I asked for.

### Not accepted
1. **The body footprint does not match its own numbers, and the body is probably exported in a pose.** Unreal measures the body at **97 x 161 x 181 cm** (box centre 11, 40, 99 cm). Your report gives two sets of numbers for the same file: vertex bounding box 120.1 x 59.3 x 180.5 cm (unposed) and evaluated object dimensions 96.65 x 161.15 x 180.92 cm. Unreal agrees with the *evaluated* set. Two different shapes for one mesh means the armature was in a pose (or a modifier was active) when you exported. The mesh must be exported in the **rest pose** (armature pose position "Rest Position", all pose bones cleared, no active shape keys or modifiers other than the armature). Required check in your report: the evaluated dimensions and the vertex bounding box must be **the same numbers**.
   Why I think this matters: in the engine the pack's idle looks right on the body, but the A2 apex clip makes the figure splay its hanging blades and limbs sideways. A bind pose that is not the rest pose breaks every animation on the mesh.
2. **Clip lengths are one frame short**: Unreal reads `A2_Raise` 0.567 s (target 0.600), `A2_ApexHold` 1.133 s (1.167), `A2_Slam` 1.333 s (1.367). `DormantIdle` 3.967 s and `Wake` 3.467 s are right. Report 04 had the three A2 clips right; restore the last frame of each (frame span 0 to 18, 0 to 35, 0 to 41).
3. **`Greatsword_Textured_8m.png`**: your description says "all 184.6 cm from pommel to tip". The picture shows the sword cropped at the top (the tip is cut off) and a second, silver curved blade crossing the lower right (the Kwang reference sword, left in the scene). Re-render with only the boss sword in the frame and the whole sword visible.
4. **Scratch files in the delivery folder**: `Import/Boss01/test_*.fbx` (eight files) are not deliveries. Move them to `Archive/`.

## 2. Notes from my side (no action for you)
- In the engine the body shows red and white stripes on the cloth with the original Paragon materials. The slot-to-material mapping is the original one, so I look at this myself (textures, streaming); it is not on your list.
- I attach your sword to the boss's right hand socket in the engine to look at poses; the sword origin at the grip is right for that.

## 3. Fix list (in this order)
**G1 Rest pose and numbers.** Re-export the body in the rest pose; evaluated dimensions and vertex bounding box equal. After the export I import it and read the size back.
**G2 Clip lengths.** Re-export the three A2 clips with their last frame (same unit recipe as now).
**G3 Sword render.** One sword in the frame, fully visible.
**G4 Housekeeping.** Archive the `test_*.fbx` files.
**G5 After G1 passes in the engine (not before):** the body customisation as in Brief 05 section 1 item 4 (Variant 1 broken crown and crimson mantle with gold trim; Variant 2's brazier gauntlet as the A5 telegraph light; owner still to confirm the variant after the engine view, so keep both separable as their own mesh pieces). A1 and A3 clips are not needed now: the code runs on the pack's attacks until authored clips exist, and the attack code for A4 (low sweep) and A5 (throw) is next on my side, so the next clips I need are **A4** (low sweeping cane/sword, Freeze section 16) and **A5** (ember javelin throw telegraph and throw).

## 4. Report
`REPORT_06.md` from the template. Give both dimension sets for the body (they must match), say what pose and modifier state the armature was in at export, and "not done" where something is not done.
