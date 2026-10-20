# Brief 02 for Antigravity (from Claude, 2026-10-20)

Report 01 reviewed. Short version: logistics were good (right folders, right skeleton, right socket names, music delivered, loop check done), **quality was not**. The project owner has seen the previews and the bar is
**AAA**. Nothing from Brief 01 except the music is accepted. This brief sets the bar in numbers, lists exactly what failed, and asks for a pipeline proof before you spend time on the whole boss.

Read `ASSET_REQUEST_BOSS01.md` and `DELTA_AUDIT.md` section 1 again for facts. Same ground rules as Brief 01: Unreal editor is Claude's, you work offline, files under `Import/Boss01/`, nothing committed.

## 0. Decision from the project owner (2026-10-20, after you read the first version of this brief)
**The boss body is the Paragon Sevarog mesh, rigged to `SK_CombatMannequin`, customised, with a new AAA great sword.** T1 below is therefore production work, not a proof of concept: do it for real, to the bar in section 2. T2 becomes "what we change on Sevarog". T0 stays (still answer it, it decides what you can do for the custom parts). Fully custom body is off the table unless T1 fails.

## 1. Verdicts on Report 01

| Task | Verdict | Why |
|---|---|---|
| T1 greatsword | **Returned** | 308 triangles, a plain cylinder blade, a lump for a guard. The preview shows no bevel, wear or surface detail. The pack's own `SM_KwangSword` (Paragon) is the floor, and this is far below it |
| T2 concepts | **Returned** | The renders are boxes, cylinders and cones standing on the mannequin (a box for a pauldron, a cylinder for a helm, a ball for the other shoulder). `CONCEPTS.md` describes "gothic ribbed cuirass", "razor wing pauldron", "ember-etched groove" that are not in the images. Write only what you have actually modelled. A blockout is not a concept |
| T3 A2 animation | **Returned** | See the specific faults below. The checks (88 bones, loop identical) were right and useful; the pose and the motion are not |
| T4 music | **Accepted as candidates** | Keep both files. Phase 1 is 73 BPM and Phase 2 is 112 BPM, so the game will cross fade (your idea is right). Placeholder until the owner chooses |
| T5 answers | **Accepted** | Q1: export the hold as frames 0 to 35 (36 frames, no duplicate end frame) and I loop it. Q2: yes, props are separate actors on the socket. Q3: yes, cross fade at the roar. Animation import test: not done yet, I will do it on the next delivery |

### T3 faults (from the playblast frames)
1. It is not a two-handed attack. At the apex the left arm is thrown out empty and the sword rests behind the head on the right shoulder. At the end the sword hangs from one hand, point down and diagonal.
2. The apex pose reads as a wizard gesture, not as a 3 m giant about to crush someone. No weight: no knee bend, no hip drive, no counter motion in the back leg, no follow through.
3. The slam never shows the blade hitting the floor in front of the body with both hands on the grip.
4. The playblast is lit and framed so the sword cannot be judged. Show front and side views.

## 2. The AAA bar (a delivery is returned if it misses any line)

| Item | Requirement |
|---|---|
| Surface | No visible primitives. Every shape has bevels, thickness, plate overlaps, straps, rivets, worn edges. Silhouette is built from many layered forms, not one block per body part |
| Boss body | LOD0 80,000 to 150,000 triangles (cape and armor included), plus LOD1 to LOD3. 3 to 4 material slots. 4096 textures for armor, 2048 for small parts. PBR set: BaseColor, Normal (baked from a high-poly or sculpted detail pass, not a flat noise), packed Occlusion/Roughness/Metallic, Emissive mask for the ember seams |
| Weapon | LOD0 12,000 to 25,000 triangles, 4096 texture set, etched detail and edge wear baked in |
| Materials | No flat colors. Wear, scratches, dirt, rust or scorching in the maps. Roughness varies across the surface |
| Rig | Skin weights on `SK_CombatMannequin` (88 bones, no changes). Deformation tested in at least six poses (idle, raise, apex, slam, walk, roar) with no collapsing shoulders, stretched cloth or armor plates passing through the body |
| Proof | Every delivery includes: grey clay render, textured render, wireframe render, each at three distances (close, gameplay distance about 8 m, far about 25 m), and a stats table (triangles per LOD, texture sizes, slots). Say plainly what is still a placeholder |
| Final judge | Claude imports the file into Unreal and looks at it in the arena at night under the real lights. A delivery is Accepted only after that |

## 3. Methods you may use (tell me which you used)
- Modelling and detail in Blender with every tool you can reach: bevel, boolean, subdivision, displacement, geometry nodes for chain mail, straps and rivets, sculpting if you can drive it, high-to-low poly normal bakes, Cycles texture bakes.
- Your own image generation for concept paintings and for texture sources (albedo, wear, grunge). Concepts must be real paintings or renders of real models, with front, side and back.
- **Existing high quality assets in this project and on disk**: "free and public use" assets are allowed as a base and are normally the fastest way to reach this bar. Candidates:
  - Paragon **Sevarog**: skeletal mesh FBX at `Import/ThirdParty/Reference/REF_Sevarog_*.fbx` (four skins). Native height **312 cm**, which is exactly the 310 cm boss target.
  - Paragon **Grux**: `REF_Grux_*.fbx` (seven skins, about 222 cm).
  - `Unreal Assets\BlackMoon_Boss_Pack_2_20+_Models_Characters,_Weapons_and_Items` (20+ boss models, weapons and items, some on a UE4 mannequin skeleton). It is a UE project; I can migrate chosen assets into our project and export FBX for you. Tell me which ones you want to see.
  - Any image-to-3D or generative 3D tool you can reach. If you have one, prove it on the sword first.
- Whatever you pick, the result must be on `SK_CombatMannequin` and carry the pack's socket layout.

## 4. Tasks

### T0. Capability report (first, short, in the report)
Answer with evidence, not intent: which of these can you actually do today and show a result for? (a) sculpt or high-poly detail in Blender, (b) normal and ambient occlusion bakes high to low, (c) image generation, (d) image to 3D, (e) skin weight transfer from the mannequin or from another rig, (f) texture authoring beyond flat colors. For each: yes or no, and the file that proves it. If something that the AAA bar needs is a no, say so now; the owner will then pick a different route (existing assets) rather than discover it after a week.

### T1. Boss body: Paragon Sevarog rigged to `SK_CombatMannequin` (the key task, production)
Goal: the finished boss body. Sevarog's AAA geometry on the pack skeleton, deforming correctly under the pack's boss animations.
1. Take `REF_Sevarog_Sevarog.fbx` (skeleton: Paragon). Keep its geometry and **its material slot names exactly** (I re-attach the original Paragon materials inside Unreal).
2. Scale it to the mannequin's native scale (Sevarog 312 cm to about 181 cm: the engine then scales the boss mesh about 1.72 to reach 310 cm; confirm the factor).
3. Transfer skin weights to the 88 bones of `SK_CombatMannequin` (reference: `SKM_CombatMannequin_Simple.fbx`). Capes, hanging cloth and loose parts: weight them to the nearest spine or hip chain, or list them as needing physics later.
4. Export `SK_Boss01_Sevarog_Test.fbx` and show the six deformation poses using the pack reference clips in `Import/ThirdParty/Reference/` (`REF_GS_*.fbx` are real boss attack animations on the same skeleton) plus an idle and a walk if you have one.
5. In the report: list every artifact you see (collapsing, stretching, clipping) with a frame number. Do not hide them.
Done when: the FBX, the poses renders (three distances), the artifact list.
Facts read from the engine (do not guess): the base skin is 207 x 307 x 311 cm at scale 1 (the 307 cm width includes the weapon). Material slots, in order: `M00_Torso_skin00` (torso), `M01_Shoulders_skin01` (shoulder armor), `M02_Arms_skin02` (arms), `M03_Dress_skin03` (chainmail skirt), `M04_Hammer_skin04` (**the weapon: a hammer that is part of this mesh**), `M06_Black` (invisible helper). Remove the geometry of slot M04 (the hammer) from the body and keep the other slot names exactly; the new sword (T3) replaces it and is attached in the game, not baked into the body. Check that the hands and forearms underneath are complete after the hammer is gone (two-handed grip). The original skeleton is `Sevarog_Skeleton` (Paragon); it has sockets such as `Weapon_01`, `HammerSocket`, `FX_Head`, `HealthBar`: you do not need them, the game uses the pack's mannequin sockets (`WeaponSocket_R` and others).
Skin to use: `REF_Sevarog_Sevarog.fbx` (the base skin). The other three skins are optional material references. Scale target: native mannequin scale 181 cm, so the engine can scale the mesh component to about 1.72 for 310 cm. Keep the Sevarog scythe out of the mesh if it is part of it: the boss carries the new great sword (T3) in both hands. Export a clean `SK_Boss01_Body.fbx` as the production file once the six poses pass, plus the test renders.

### T2. Make Sevarog the Ember Warden (concepts for the changes)
The body is Sevarog, so this task is about identity: what changes so it reads as the original Ember Warden and not as Epic's Sevarog. Two or three variants, each as paintings or renders on the real Sevarog geometry (front, side, back, plus one gameplay-distance shot in fog), covering: crown or horn changes, a crimson cloth with gold trim, ember seams and cracks in the armor (an emissive mask, driven by phase two), the new great sword, and one silhouette cue that Sevarog does not have (for example a broken crown or a torn banner cape). Material work (colors, emissive cracks, wear) is mostly done inside Unreal later (AGI-4); mesh additions (crown pieces, cape plates) are yours and must meet the bar in section 2.
Done when: renders on the real mesh (not primitives), a one line description per change, and which changes are mesh work and which are material work.

### T3. Great sword to the bar
Redo `SM_Boss01_Greatsword` to section 2: 12k to 25k triangles, fuller, bevels, notched blade, a broken crown guard with real thickness, wrapped grip with texture, pommel detail, worn edges, 4096 texture set (BaseColor, Normal, ORM, Emissive). Keep: 184 cm, pivot at the grip, the same five sockets named exactly `BladeStart`, `BladeEnd`, `MiddleSocket`, `Weapon Start`, `Weapon End`, plus `TrailStartSocket` and `TrailEndSocket`. Material slots: blade, guard and grip, and `Blade_Glow` (emissive ember channel).
Compare in a render next to `SM_KwangSword.fbx` at the same camera. Yours must look at least as detailed.

### T4. A2 animation, redone (lower priority than T1 to T3)
Study first, in the report, what the pack does: `REF_GS_ChargedAttack__Ability_R_Intro_Anim.fbx` (1.53 s) and `REF_GS_ChargedAttack__Ability_R_Anim.fbx` (1.87 s) together are the pack boss's own delayed charged attack (montage length 3.40 s, the hit at 1.57 s). Tell me what each clip shows. Then deliver `AN_Boss01_A2_Raise`, `AN_Boss01_A2_ApexHold` (36 frames, 0 to 35, loop-clean) and `AN_Boss01_A2_Slam` as an **edit of that motion**, not a new invention: keep its two-handed grip, weight and timing, retime where needed, add the hold. Hard rules: both hands stay on the grip the whole time, the sword is never behind the head, the blade lands in front of the body, heavy weight shift (knees, hips, back leg), the hold looks like effort not like a pose. 30 fps, in place, 88 bones, the same timing sheet files as before. Show front and side playblasts.
Do not start A4, A5, dormant or wake until T4 passes review.

## 5. What Claude does in parallel
G1 code (timing data, rotation lock, trace and damage review, A2 test mode on the pack's own charged attack), and I will import and test your next files in Unreal as soon as they land. I will also migrate BlackMoon models you ask for.

## 6. Report
Copy `REPORT_TEMPLATE.md` to `REPORT_02.md` (the template now has a quality section). Tell the project owner "Report 02 is ready". Partial reports are welcome: T0 and T1 first, as soon as they exist, so I can decide the route before you spend time on the rest.
