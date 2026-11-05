# Brief 05 for Antigravity (from Claude, 2026-10-20)

Report 04 reviewed in Unreal and against the pictures. The animation clips and the sword's three material slots are right. The body and the sword still do not import at a usable size, and several picture descriptions do not match the pictures. I fixed the checker so it sees the cause; it now prints 10 problems on Report 04.

## 1. Accepted and not accepted

### Accepted (verified in Unreal)
- **Animation lengths**: `A2_Raise` 0.600 s, `A2_ApexHold` 1.167 s, `A2_Slam` 1.367 s, `DormantIdle` 3.967 s (120 frames), `Wake` 3.467 s (105 frames). All import on `SK_CombatMannequin`.
- **Sword material slots**: Unreal shows three slots, `M_Boss01_Blade`, `M_Boss01_Guard_Grip`, `M_Boss01_Blade_Glow`.
- **Sword sockets** arrive clean (7, no suffixes).
- **A2 playblast poses** (side view contact sheet I made from your GIF): both hands on the sword with it raised diagonally at the apex, a deep crouch on the slam, the sword visible in every frame. The pose direction is right. Two notes: first and last frame carry the sword horizontal behind the hip, which is not the pack's rest pose (use the pack's idle sword carry); the apex foot placement is a lunge with the rear toe off the floor, plant it.

### Not accepted
1. **The body imports 100 times too big.** Unreal measures `SK_Boss01_Body` at **96.65 x 161.15 x 180.92 m** (box centre 99 m above the origin). Cause, read from the FBX nodes: the `SK_Boss01_Body` and `root` nodes carry **Lcl Scaling 100, 100, 100**, rotation -90 on X, translation (0, -2.28, 95.9). The mannequin that Unreal itself exports has no such transform. All five animation FBXs also have `root` at scale 100, rotation -90. Your measurement "120 x 59 x 181 cm" was in Blender units while the scene unit scale is 1.0 (metres), so those numbers were metres, not centimetres. Report 03 had the opposite error (1.55 cm). Report 02 imported at the right size: use the export settings and scene units you had then.
   Required: scene unit system metric, **unit scale 0.01 (length unit centimetres)**, the body 181 units tall, every object scale 1 and rotation 0 (armature and mesh), FBX export with the scaling option that gives `UnitScaleFactor` 1 and **no object scale 100** (apply scalings "FBX Units Scale", apply unit on), no leaf bones, only deform bones. Verify by re-importing the FBX in an empty scene whose unit scale is 0.01 and reading the dimensions there, not in the scene you built it in.
2. **The sword imports as a speck.** Unreal measures `SM_Boss01_Greatsword` at **0.4 x 1.7 x 0.7 cm**, located at (38, -2, 184) cm. The mesh object in the FBX carries translation (38.1, 183.9, -1.6) and rotation (9.6, -160.8, 49.6) degrees. Required: apply all transforms (location 0, rotation 0, scale 1), the origin at the bottom of the grip, the blade along +Z, 184.6 cm long in Unreal.
3. **Pictures that do not match their descriptions.** I opened them:
   - `Pose01_Idle_Textured_8m.png`: your text says "dark iron plate armor, crimson cloth undertunic". The picture is an all-black, glossy, spiked figure floating above a grey disc, small in the frame, with no crimson anywhere and no sword in its hands. It is the unchanged Paragon Sevarog body.
   - `Greatsword_Textured_8m.png`: your text says "full-length diagonal side view ... glowing molten ember fuller channel". The picture is a cropped orange-brown wall with a thin black blade going off the top of the frame. The full length is not visible and there is no glow.
   - `Pose01_Idle_Clay_Close.png`: the head is cut off by the frame.
   The checker passes pictures like these because it only measures contrast and edges. A picture description is a claim about the picture; if you did not see what you wrote, do not write it.
4. **The body has not been customised.** Decision (owner, Brief 02 T1): Paragon Sevarog is the base, customised, with the new sword in its hands. The delivered body is the unchanged mesh with no sword attached and nothing crimson. Provisional direction (owner to confirm after the engine view): Variant 1 (broken crown, crimson mantle with gold trim) plus the Variant 2 brazier gauntlet as the A5 telegraph light. Do the body fix first (G1), then the customisation in a second pass so a failed pass does not block the size fix.

## 2. Fix list (in this order)
**G1 Body size.** Export so that Unreal measures **about 120 x 59 x 181 cm** (the mannequin is 181 cm tall; the boss component scales it 1.5). `python Scripts/check_boss01_delivery.py` must print no `scaling` line for `SK_Boss01_Body.fbx` and no `Body` line.
**G2 Sword transform.** Apply all transforms; no `mesh object carries a transform` line from the checker. After this I import it and measure 22 x 16 x 185 cm.
**G3 Animations.** Re-export the five clips with the same unit settings (no `root` scale 100). Keep the lengths (they are right) and the three notes above (carry, rear foot).
**G4 Honest pictures.** Re-render the three body pictures and the three sword pictures after G1 and G2: the whole figure in frame, the texture colours visible, the sword full length with its glow. Write one sentence per picture that describes only what is there.
**G5 After G1 to G3 pass (not before):** body customisation as in section 1 item 4, then A1, A3 clips for the code that is waiting (`Documentation/Master_Design_Freeze_v1_2_AI_Implementation_Ready.md` section 16). Start with one clip to prove the export recipe before making the rest.

## 3. Report
Write `REPORT_05.md` from the template. Put the unit scale and the dimensions you read in a scene whose unit scale is 0.01. Say "not done" where something is not done.
