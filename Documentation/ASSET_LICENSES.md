# Asset License Register

Record every third-party asset before it ships. Verify the current license on the listing at download time.
Third-party packs are **not committed to git** (`Content/Paragon*/` is ignored): re-download them from Fab.

## Candidates (M2, not yet downloaded)

All are free on Fab, creator Epic Games, **Standard License**, listing text checked 2026-10-18. Fab lists UE 5.0 – 5.8 for Steel; the others were not checked individually.

| Candidate | Role | Fab listing | Notes |
|---|---|---|---|
| Paragon: Greystone | Player | https://www.fab.com/listings/122fd7bf-6f12-4304-a930-cccbbacdaebc | Knight; includes AnimBPs |
| Paragon: Steel | Player (alt) | https://www.fab.com/listings/5c0e13c1-8d00-4213-8a05-5c501c01548d | Sword and shield cyborg; includes AnimBPs; UE 5.0 – 5.8 |
| Paragon: Grux | Boss | https://www.fab.com/listings/8c4bac2c-f7f7-4632-a644-47f4e104f5d8 | Brute; now includes AnimBPs |
| Paragon: Sevarog | Boss (alt) | https://www.fab.com/listings/a4882b5e-cfad-4830-a3dd-46a6c31a79b2 | Reaper; now includes AnimBPs |

Terms seen on every listing: may not use the PARAGON trademark to advertise or name the game; "Allows usage with AI: No" (do not use the content to train AI models). Greystone was created from face scans (OTOY).

## Register (fill when an asset is added to the project)

| Asset | Creator | Source URL | License terms | Date | Used for | Restrictions / dependencies |
|---|---|---|---|---|---|---|
| Paragon: Greystone | Epic Games | https://www.fab.com/listings/122fd7bf-6f12-4304-a930-cccbbacdaebc | Fab Standard License; no PARAGON trademark use | 2026-10-18 | Player (provisional) | `Content/ParagonGreystone`, 2.2 GB, git-ignored |
| Paragon: Steel | Epic Games | https://www.fab.com/listings/5c0e13c1-8d00-4213-8a05-5c501c01548d | same | 2026-10-18 | Player alternative / dash source | `Content/ParagonSteel`, 2.2 GB, git-ignored |
| Paragon: Grux | Epic Games | https://www.fab.com/listings/8c4bac2c-f7f7-4632-a644-47f4e104f5d8 | same | 2026-10-18 | Boss alternative | `Content/ParagonGrux`, 3.0 GB, git-ignored |
| Paragon: Sevarog | Epic Games | https://www.fab.com/listings/a4882b5e-cfad-4830-a3dd-46a6c31a79b2 | same | 2026-10-18 | Boss (provisional) | `Content/ParagonSevarog`, 1.4 GB, git-ignored |

Unused packs should be deleted from `Content/` once the pick is final, to keep cook size and load time down.

Other notes:
- Engine tutorial mannequin (`/Engine/Tutorial/.../TutorialTPP`) is used only as a temporary placeholder mesh.

## M7 imports (audio, VFX, animation, font, arena materials)

Creator and licence of these packs were **not recorded in the download folders**. Each needs its listing URL and licence
text added before the game ships; until then treat them as unverified. All are git-ignored (see `.gitignore`).
Source folder: `C:\Users\winss\Documents\Unreal Projects\Unreal Assets\`. Imported with `Scripts/ImportAssetClosure.py`, which
copies an asset with everything it references and keeps the original `/Game/...` package paths (a plain copy into
another folder would break every internal reference). Only what is used is imported.

| Pack (source folder) | Imported to `Content/` | Size | Used for | Creator / licence / listing |
|---|---|---|---|---|
| Advanced ARPG Combat System V3 | `AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX` (Combat/ShieldImpacts, Combat/SwordImpacts, swing cues) and `UI/Fonts/Cinzel` | 4 MB | Block/parry and heavy impact sounds, boss swing, HUD and menu font | **to be filled**. The Cinzel typeface is published under the SIL Open Font License by its authors; confirm the licence file shipped in this pack |
| RealisticSwordSoundEffects (already in the project) | `RealisticSwordSoundEffects/` | 5 MB | Player swing whoosh and sword impact variants | **to be filled** |
| Free_Spells (already in the project) | `Free_Spells/` | 471 MB | Shockwave, ground telegraph circle, spark Niagara systems | **to be filled**; the pack also carries the UE5 mannequin and its IK rig |
| Mage Animation Pack | `Mage/Animations/Sequence1/07_Roll/02_Roll_Combat` (8 sequences) and `Mage/Demo/Mannequin_UE4` (skeleton, mesh, IK rig) | 16 MB | Source of the dodge roll, retargeted to Greystone (`Characters/Greystone/Roll`) | **to be filled**. The retargeted copies are derivative works of these animations |
| Niagara Energy Beam Pack | `BeamPack/` (NS_Thunder_Beam7 with its ribbon material and textures; other lightning systems tried) | 15 MB | Boss lightning bolt | **to be filled**. The download lacks four materials the lightning system references (`M_Dirt`, `M_Dirt_2`, `M_Mesh`, `M_Mesh_7`); stand-ins with the same names are authored by `Scripts/Editor/setup_m7_beam_materials.py` |
| Realistic Blood VFX (Niagara) | `BloodPack/` (NS_Slash_Med, NS_BulletHit_Med and shared materials) | 29 MB | Imported, **not used**: the systems spawn nothing visible in UE 5.5 | **to be filled**. Candidate for deletion |
| Deadly Ruins Modular asset pack | `Deadly_Ruins/` (detail and world-blend master materials, rock wall, brick floor, metal textures) | 166 MB | Stone textures for the arena floor, wall, pillars, arch, rubble and braziers | **to be filled** |
| Arena meshes (authored in Blender, imported by Antigravity) | `OneBossFight/Environment/Meshes` | 1 MB | Pillars, curved walls, entrance arch, brazier, rubble | Project asset, no third-party licence |
| Dark Ruins Megascans sample (Epic project) | Epic Games / Quixel | local project `DarkRuinsMegascansSample` (source URL not recorded: add it) | **not verified**: Megascans content from Epic samples is normally limited to use in Unreal Engine projects, and the exact sample terms have not been read; the user said the build is a portfolio piece, not published or commercial | 2026-10-20 | Arena ruins, floor stone, decals, props, flame and fog materials | `Content/MS`, `MSPresets`, `CustomAssets`, `Smart`, `Materials`, `Blueprints`, `Effects`, `Textures` (about 9.5 GB, git-ignored) |

## Boss music (Import/Audio, imported to Content/OneBossFight/Audio)

Credits as supplied in `Import/Audio/SOURCES.txt` (Kevin MacLeod, incompetech.com, Creative Commons Attribution 3.0 / 4.0 International): the credit lines must appear in the game's credits.

| Asset | Title and creator | Source |
|---|---|---|
| `MX_Boss01_Phase1` | "Darkness is Coming" by Kevin MacLeod | https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100584 |
| `MX_Boss01_Phase2` | "Final Battle of the Dark Wizards" by Kevin MacLeod | https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100224 |
