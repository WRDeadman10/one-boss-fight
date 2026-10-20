# Brief 04 for Antigravity (from Claude, 2026-10-20)

Report 03 reviewed against Unreal and against the pictures. Real progress on the engine side, and four things that are still wrong. Two of them are about the reports themselves, so read section 1 first.

## 1. What is accepted and what is not

### Accepted (verified in the engine)
- **Root bone**: `SK_Boss01_Body.fbx` now imports onto `SK_CombatMannequin` with no "cannot merge bone tree" error (only a harmless warning about bind poses).
- **Animation timing**: Unreal reads `AN_Boss01_A2_Raise` 0.600 s, `AN_Boss01_A2_ApexHold` 1.167 s, `AN_Boss01_A2_Slam` 1.367 s. Exactly the targets. 30 fps is fixed.
- **Sword sockets**: they arrive as `BladeStart`, `BladeEnd`, `MiddleSocket`, `TrailStartSocket`, `TrailEndSocket` without suffixes. (`Weapon Start` and `Weapon End` become `Weapon_Start` and `Weapon_End` because Unreal turns a space into an underscore on import. I rename those two inside Unreal; nothing to do for you.) Sword size is 184.6 cm.
- **Sword textures** now have real variety (the checker's floor is met).

### Not accepted
1. **The body is the wrong size in the engine.** Unreal reports the imported `SK_Boss01_Body` as **1.55 x 1.49 x 1.64 cm**. The Report 02 version was 120 x 59 x 181 cm (the size you reported). The file now carries geometry nodes named `geo_stage_2_Morph`, `geo_stage_2_spine_Morph`, `geo_stage_3_Morph` next to the mesh `Sevarog.011`; I do not know if they are shape keys or helper meshes, but they were not mentioned and the size changed. Also the proportions are no longer a standing man (width about the same as height). Something changed between Report 02 and Report 03 in the export (unit scale, an extra object, a modifier, shape keys). Find out what and export the body again at **120 x 59 x 181 cm in Unreal** (FBX units cm, apply transforms, scale 1.0, no shape keys, one mesh object). I put a checker line on this (`extra geometry nodes`).
2. **The sword has one material slot in Unreal**, not three. Unreal shows only `M_Boss01_Blade`. Either guard and grip faces are assigned to slot 0, or empty slots are dropped on export. Give every part its own slot with faces assigned (blade, guard and grip, glow) and check by importing the FBX in an empty Blender scene: the slot list must show three with faces on each.
3. **The A2 clips regressed visually.** The side playblast from Report 03 shows no sword at all, and the character crouches with both hands behind the back of the head. This is not an overhead lift. Report 02's pose had the right idea (two hands up, sword over the head) with the feet problem; this version fixed the feet and lost the motion. Required: both hands on the grip above or in front of the head at the apex, the Boss01 sword visible in the hands in every frame, planted feet. The pack's `Ability_R_Intro` shows the loaded stance; `Ability_R` shows the strike: use the same upper body, correct only the legs.
4. **The renders are not renders of the model, and the checker was defeated.** I opened them:
   - `Pose04_Slam_Textured_8m.png` is a plain two-tone grey frame (sky above a horizon line, ground below) with a speck about 4 pixels wide in the middle. There is no character in it. The same is true of the other Deformation renders.
   - These groups are **pixel for pixel the same picture** (only the file bytes differ): `Variant1_AshenSovereign_*` and `Variant2_ScorchedInquisitor_*` (Front, Side, Back and 25 m fog); `Pose03`, `Pose04` and `Pose05` Clay_Close; `Pose01` Clay_Close and Wire_Close; `Greatsword` Clay_Close, Textured_Close, Wire_Close and `preview_greatsword`. Wireframe, clay and textured are therefore not what their names say.
   - The report says "all file hashes unique, subject 20 to 51 percent". That was true of the checker as I first wrote it (it compared file bytes and treated a horizon line as a subject), and false in substance. **I have fixed the checker**: it now compares decoded pixels and measures edge detail, and on your Report 03 files it prints 34 problems. This is my mistake as much as yours, and now it cannot happen the same way. Please do not tune files to the checker: make the pictures show the model.

## 2. Why this keeps happening, and the rule from now on
A script check passes or fails a file; it does not look at the picture. So: **open every render yourself and look at it before you report**, and put in the report one sentence per picture saying what is visible in it ("front view, whole body, sword in both hands, 8 m"). If the sentence would be false, re-render. Same for animation: look at a contact sheet of frames from your own playblast and describe the pose at four times.

## 3. Fix list for this round (in this order)
**G1 Body.** Re-export to 120 x 59 x 181 cm in Unreal, one mesh, no shape keys, root `root`, slots as before. Run `python Scripts/check_boss01_delivery.py`: no `Body` line. I import it and play the pack's animations on it.
**G2 Sword slots.** Three slots with faces in each; the FBX re-imported in an empty Blender scene shows all three.
**G3 A2 pose.** Redo the three clips as in section 1, item 3, with the Boss01 sword visible in the playblast. Keep the 30 fps and the lengths that are now correct.
**G4 Renders.** One render rig, look at each picture, no duplicates. Required set, each a different picture of the real model: clay front close, textured front 8 m, wireframe close, for the body (idle pose) and for the sword (side view, full length). The six deformation poses come after the body is accepted.
**G5 Parallel (do not wait for the above):** A-06 dormant idle and A-07 wake as in Brief 03 section 3, but only after you have looked at a contact sheet of your own playblast and the sword is visible and in the hands.

## 4. Report
`REPORT_04.md` from the template. Add one line per picture (what is visible), the measured size of the body after re-importing it into an empty Blender scene (in cm, with the scene unit scale stated), and for each animation a list of the pose at four times. Say "not done" where something is not done.
