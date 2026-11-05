# Brief 03 for Antigravity (from Claude, 2026-10-20): fix list from the engine import

Report 02 reviewed. This time I did not only look at your pictures: I **imported your files into Unreal** and ran an automatic check. Several statements in Report 02 do not hold. The point of this brief is
that every claim from now on is something a script can verify, so you stop discovering problems after you have reported "done". Read all of it before touching Blender.

## 0. First: run the check yourself
`python Scripts/check_boss01_delivery.py` (needs Pillow). It is the same check I run. A delivery is not reported until it prints `0 problem(s)`. It checks bone and node names in every FBX, texture detail, render brightness and
subject size, duplicate renders. On Report 02 it prints 40 problems. If you disagree with a check, say which and why in the report; do not skip it.

## 1. Verdicts with the evidence

| Item | Verdict | Evidence (engine and script, not opinion) |
|---|---|---|
| `SK_Boss01_Body.fbx` | **Returned: does not import** | Unreal 5.5 on `SK_CombatMannequin`: "cannot merge bone tree with the existing skeleton" and "incompatible Skeleton". Cause found in the FBX: the root bone is named **`root.022`** (Blender added a suffix because another object called `root` already existed). It must be exactly `root`. Your report said the root is named `root`: that was true inside Blender, not in the exported file. `SK_Boss01_Sevarog_Test.fbx` is byte for byte the same file |
| `SM_Boss01_Greatsword.fbx` | **Returned** | It imports and the length is right (185 cm). But: (1) the sockets arrive as `BladeEnd_001`, `BladeStart_001`, `MiddleSocket_001`, `TrailEndSocket_001`, `TrailStartSocket_001`, `Weapon_End_001`, `Weapon_Start_001` (Blender suffix `.001` from duplicated empties). The game finds sockets by the exact names `BladeStart`, `BladeEnd`, `MiddleSocket`, `Weapon Start`, `Weapon End`; none is found, so the weapon trace would not work. (2) Only one material slot arrives (`M_Boss01_Blade`), not the 2 to 3 reported. (3) The four 4096 textures have almost no content: the normal map has 16 different colors, the base color 117, the ORM 38, the emissive 44 (a baked bevel and wear normal map has tens of thousands). The report claims baked bevels, chips and leather relief; the files do not contain them. (4) In `Compare_Kwang_vs_Boss01_Greatsword.png` your blade is flat shaded with visible facets and a cone for a guard, no fuller or chips can be seen, and it is darker and less detailed than the Kwang sword it is compared against ("4.2x fidelity" is not supported by the picture) |
| `AN_Boss01_A2_*.fbx` | **Returned (improved, with defects)** | The three clips import onto `SK_CombatMannequin` without errors: good. Defects: (1) **length**: Unreal reads 0.72 s, 1.40 s and 1.64 s, your report says 0.60 s, 1.167 s and 1.37 s. The ratio is exactly 1.2 = 30 / 25: the FBX carries 25 fps, not 30. (2) **feet leave the ground**: in the front and side playblasts the character is in the air at the apex (pelvis 142 cm) for the whole hold, because the pack's `Ability_R` clip is a jump slam. The Freeze requires a planted hold (A2 apex hold: planted feet, no drift). (3) **the playblast sword is not your sword**: a thin sword is in the hands, and the black Boss01 greatsword floats beside the character (first frames) and then hangs in the air next to the column. The playblast does not show the weapon the clip is for. (4) the grip is two-handed and the motion has weight: this part is good and is the baseline to keep |
| Deformation renders (13 files) and Variant concept renders (12 files) | **Returned: unusable** | `Pose04_Slam_Textured_8m.png` shows a black frame with a speck about 3 pixels wide in the middle. The checker finds 31 renders with mean brightness below 25 of 255, and the subject covers under 4 percent of the frame in the comparison image. Four "Clay_Close" renders have the same file size (several are probably the same image). I cannot judge deformation or concepts from them |
| Music | still accepted | |
| T0 capability report | accepted, with one note | You said hammer geometry was removed and hands are sealed; I cannot confirm it from the renders, only from the body import after the fix |

## 2. Fix list (do in this order; each has a test I can run)

### F1. Body export (30 minutes of work, blocks everything)
1. In Blender, make sure there is exactly one armature and its root bone is named `root` (delete or rename the object or bone that already uses the name `root`, the cause of `root.022`). No `Armature` parent node above it; export with the armature as the only top level node besides the mesh.
2. Re-export `Import/Boss01/SK_Boss01_Body.fbx`. Delete `SK_Boss01_Sevarog_Test.fbx` (a duplicate).
3. `python Scripts/check_boss01_delivery.py` must show no line for the body. Then tell me; I import it in Unreal and run the pack's boss animations on it (the real deformation test).

### F2. Sword
1. Socket empties must be named exactly `SOCKET_BladeStart`, `SOCKET_BladeEnd`, `SOCKET_MiddleSocket`, `SOCKET_Weapon Start` (with the space), `SOCKET_Weapon End`, `SOCKET_TrailStartSocket`, `SOCKET_TrailEndSocket`, with no `.001` anywhere (remove the older empties with the same names first). In Unreal they must then show up as `BladeStart` and so on. The reference `SM_KwangSword.fbx` shows the convention.
2. Three material slots must survive export: `M_Boss01_Blade`, `M_Boss01_Guard_Grip`, `M_Boss01_Blade_Glow`. Check by re-importing the FBX into an empty Blender scene and listing the slots.
3. Textures must contain the detail the report describes. Concretely: the checker's rule (at least 300 colors in a 128 x 128 downsample) is the floor, not the goal. The normal map must come from a high-poly bake (bevels, chips, grip relief), the base color must show scratches and patina, the ORM must vary. If the bake did not work, say so: do not export a flat file and call it done.
4. The blade needs to read as a great sword at gameplay distance: visible fuller, notches, a broken crown guard with thickness, a pommel. The Kwang comparison must be a fair one: same camera, three-point light, both swords full length in the frame.

### F3. A2 animation (the pack's `Ability_R` is a leap; the boss must not leave the ground)
1. Keep what works: the two-handed grip and the weight. Change what does not: **both feet stay planted for the whole hold** and through the raise and the slam (a heavy forward step into the slam is fine). The hold is a held effort pose of a heavy man lifting a sword over his head, not a jump. Build the raise from `REF_GS_ChargedAttack__Ability_R_Intro_Anim` (it stays on the ground) and the slam from the strike part of `Ability_R_Anim`, with the legs corrected so the feet remain on the floor.
2. Export at **30 fps** and verify: re-import each FBX into an empty Blender scene, set the scene to 30 fps, and report the length in seconds you read. Targets: Raise 0.60 s, ApexHold 1.167 s (36 frames, 0 to 35), Slam 1.37 s. I read the length in Unreal and it must match.
3. Playblasts: show the greatsword **attached to the hands** during all three clips. Attach it to `hand_r` with the same offset the game uses (`HeavySwordSocket_R`, relative to `hand_r`: location -13.90, 2.61, 4.89 cm; rotation pitch -28.00, yaw 168.83, roll 12.80 degrees, in Unreal's axes; convert to Blender's) or, better, parent the sword to the hand bone and check that the grip sits in both hands. Use the Boss01 sword, not another one.

### F4. Renders (one render rig for everything)
Use the same rig for every picture: a three-point light (key, fill, rim) plus a dim environment so the subject is clearly lit, a camera that frames the full body with at least 40 percent of the frame height filled by the subject (at 8 m: 25 percent), a mid grey ground, a visible background gradient. The checker rejects renders that are nearly black or where the subject is a speck. Re-render the six deformation poses (close, 8 m, wireframe close) only after F1 is accepted, with the body that Unreal accepts. Do not re-render the concepts yet.

## 3. In parallel, without waiting for F1 to F4 (animations do not depend on the body)
Both use the same rules as F3 (planted or deliberate feet, sword attached in the playblast, 30 fps verified by re-import, root bone exactly `root`, 88 bones):
- **A-06 `AN_Boss01_DormantIdle`**: kneeling or standing hunched, both hands on the pommel of the sword planted point down in front, slow breathing, loop 4 to 6 s, loop-clean (36 frames or more, no duplicate end frame).
- **A-07 `AN_Boss01_Wake`**: from that pose to the combat idle: head lifts, hands tighten, the sword is pulled out of the floor, he stands to full height. 3 to 4 s, one shot, ends exactly on the first frame of the pack's combat idle (use the first frame of `Idle_Combat` or the great sword idle from the pack references).
Reference clips are in `Import/ThirdParty/Reference/`; ask me for more (I can export the pack's idle and walk clips).

## 4. Not now
Concept variants, A4, A5 and the rest wait until F1 to F3 pass in Unreal. The owner will choose the Ember Warden look from in-engine renders of the actual body, not from the current images.

## 5. Report
`REPORT_03.md` from the template. For each fix: what you changed, the output of the checker, and (for animations) the lengths you read after re-import. Say "not done" where something is not done.
