# Brief 01 for Antigravity (from Claude, 2026-10-20)

Read first, in this order: `Documentation/ASSET_REQUEST_BOSS01.md` (what and why), `Documentation/DELTA_AUDIT.md` section 1 (the real
pack facts: skeleton, scale, sockets), then this file. The design authority is
`Documentation/Master_Design_Freeze_v1_2_AI_Implementation_Ready.md`.

## Ground rules for this round
- **The Unreal editor belongs to Claude this round.** Work offline in Blender and on files. Do not open or save anything in the Unreal project, and do not touch `Source/`, `Config/`, `Scripts/`, `Content/`, `*.uproject`. I import your files myself.
- Put deliveries under `Import/Boss01/<Category>/` (your own work) or `Import/Audio/` (music). Do not commit anything; the project owner commits.
- Reference files for Blender are ready in `Import/ThirdParty/Reference/`: `SKM_CombatMannequin_Simple.fbx` (the skeleton and body all boss and player clips must use) and `SM_KwangSword.fbx` (the pack's great sword, to match scale and sockets).
- Facts you must not change: skeleton is `SK_CombatMannequin` (no new, renamed or deleted bones; mannequin is 181 cm at scale 1; the boss mesh is scaled 1.5 by the engine, so author at the skeleton's native scale); the great sword is 184 cm and carries the sockets `BladeStart`, `BladeEnd`, `MiddleSocket`, `Weapon Start`, `Weapon End`.
- If a fact in the docs is wrong or a task cannot be done as written, stop that task and say so in the report. Do not work around it silently.

## Tasks (all offline, any order, all are Wave 1)

### T1. `SM_Boss01_Greatsword` (M-02)
Original design: broken-crown guard, notched blade, about 184 cm long at native scale (matches `SM_KwangSword` size), grip near the lower third. Under 15k triangles. Three material slots: blade, guard and grip, and an emissive slot (`Blade_Glow`) for the later ignite effect. The same five sockets as `SM_KwangSword`, same names, same orientation convention (copy the layout from the reference FBX). Pivot where the Kwang sword's pivot is, so it attaches the same way.
Done when: FBX plus a preview render, and a 5 line note of socket positions in cm.

### T2. Boss 01 silhouette concepts (before M-01)
Two or three different silhouettes, full-body front and side and a small gameplay-distance render (about 25 m in fog). Fit the brief in the request doc section 2 (310 cm final height, black plate with ember seams, crimson cape, dormant pose with the sword planted). Use blockout meshes on the mannequin skeleton proportions; do not build the final mesh. The project owner picks one.
Done when: renders in `Import/Boss01/Concepts/` and one paragraph per concept.

### T3. A2 animation set on the mannequin skeleton (A-01, A-02, A-03)
Clips `AN_Boss01_A2_Raise`, `AN_Boss01_A2_ApexHold`, `AN_Boss01_A2_Slam` as in the request doc section 5.2, using `SM_Boss01_Greatsword` or the Kwang sword as the prop while you animate. In place (no root motion). 30 fps. The hold is a clean loop (first and last pose identical, no foot sliding, no weapon drift). For each clip write the timing sheet text file from the request doc (length, `ApexReached`, `CommitTime`, `ActiveStartTime`, `ActiveEndTime`, `RecoveryEndTime`). Boss feel: 272 to 310 cm tall giant, heavy, slow lift, very fast drop, long recovery. Match the real pack boss rhythm for reference: the pack's `GS_ChargedAttack` is 3.4 s with the hit at 1.57 s.
Done when: three FBX, three timing sheets, one playblast of Raise then Hold (x3 loops) then Slam on the mannequin.

### T4. Two music candidates
Two tracks that feel like one boss: Phase 1 (slow, heavy, ominous) and Phase 2 (faster, choral, climactic), same motif, ideally same key and tempo so the game can cross fade or layer them. Put the audio files in `Import/Audio/` and write `Import/Audio/SOURCES.txt` with a line per file: title, creator, link. Stereo WAV or OGG, 44.1 or 48 kHz.
Done when: two audible files and the sources file.

### T5. Check your own plan against the facts
In the report, answer: (a) can the A2 clips and the sword be built on `SK_CombatMannequin` without any bone change; (b) anything in the request doc you think is wrong or missing; (c) which VFX items from the request doc you can build without the Unreal editor and which need it.

## How to report back (required)
When you finish, or when you are blocked, copy `Documentation/AG/REPORT_TEMPLATE.md` to `Documentation/AG/REPORT_01.md` and fill it in. Then tell the project owner "Report 01 is ready". Claude reads it, checks the files, and writes Brief 02 (the next tasks) so you are never waiting.
