# Scripts/Editor inventory

This directory has 340 Python editor scripts. This index uses each module docstring first sentence when present; scripts without one are marked for manual inspection. Names are historical and include probes or one-off repair scripts, not a supported ordered pipeline.

## Safety

- Scripts require an open Unreal Editor with the Python scripting plugin and usually mutate assets or the current level. Read the script before running it; many assume a specific map, selection, or prior setup.
- Use Scripts/RunEditorScript.ps1 or Scripts/run_in_editor.py where appropriate; PIE drivers use Scripts/RunDrivers.ps1. Never run two editor/driver chains at once.
- Never delete and recreate referenced assets. Save, reopen, and read back authored values where the task requires proof.
- Before rerunning any script that creates, duplicates, or imports assets, check its collision policy and referencer risk in `Documentation/Boss/EDITOR_ASSET_OVERWRITE_AUDIT_S162.md` and `Documentation/Boss/EDITOR_ASSET_DELETION_AUDIT_S161.md`.
- Before running map authoring scripts, check their load/save destination and current-world assumptions in `Documentation/Boss/EDITOR_MAP_SAVE_AUDIT_S163.md`; it identifies a destination mismatch in `sevarog_pack_04_level.py` and destructive map recreation paths.
- Check reflected property-name evidence in `Documentation/Boss/EDITOR_PROPERTY_NAME_AUDIT_S164.md`; the inventory is static, and fields without source/getter evidence still need target-object validation.
- Boolean property naming follows the reflected target field, not a blanket `b` prefix rule; see `Documentation/Boss/EDITOR_BOOLEAN_PROPERTY_AUDIT_S165.md` for source matches and remaining limits.
- Former-user absolute paths and repo-relative/configurable replacements are listed in `Documentation/Boss/EDITOR_ABSOLUTE_PATH_AUDIT_S166.md`.
- Syntax-only Python inventory: `Documentation/Boss/PYTHON_SYNTAX_INVENTORY_S167.md`; syntax success does not establish Unreal API/runtime correctness.
- PowerShell syntax and process-exit review: `Documentation/Boss/POWERSHELL_PARSE_AND_EXIT_AUDIT_S168.md`; parse failures and wrappers that only print child exit codes are listed there.
- Python subprocess/editor task exit review: `Documentation/Boss/SUBPROCESS_EXIT_CODE_AUDIT_S169.md`; Blender, editor-task, and launcher failures that do not reach caller exit status are listed.
- Path handling and its isolated spaces/separators/Unicode fixture are recorded in `Documentation/Boss/PATH_NORMALIZATION_AUDIT_S170.md`.
- Offline tool manifest/report writes now use atomic publication where needed; see `Documentation/Boss/JSON_WRITE_ATOMICITY_AUDIT_S171.md` and its unrun failure-injection fixture.
- Scratch cleanup scope and legacy scripts deleting shared frame files are recorded in `Documentation/Boss/TEMP_DIRECTORY_CLEANUP_AUDIT_S172.md`.
- Required-input, malformed-file diagnostic, and pre-validation side-effect gaps in offline CLIs are recorded in `Documentation/Boss/CLI_INPUT_VALIDATION_AUDIT_S173.md`.
- Offline tool network use was statically scanned; the only URL-related use is parsing, documented in `Documentation/Boss/OFFLINE_TOOL_NETWORK_AUDIT_S174.md`.
- Top-level utility import behavior was scanned for filesystem/editor/process effects in `Documentation/Boss/SCRIPT_IMPORT_SIDE_EFFECT_AUDIT_S175.md`.
- Repeated output comparisons on isolated temporary fixtures are recorded in `Documentation/Boss/DETERMINISTIC_TOOL_OUTPUT_AUDIT_S176.md`.
- Absolute-path and raw-input disclosures in offline CLI reports are recorded in `Documentation/Boss/REPORT_REDACTION_AUDIT_S177.md`.
- Generated scaffold headers and evidence caveats are checked in `Documentation/Boss/SCAFFOLD_HEADER_AUDIT_S178.md`.
- Documented offline tool command syntax is checked in `Documentation/Boss/TOOL_USAGE_CONSISTENCY_AUDIT_S179.md`.
- The complete offline CLI inventory and support-file exclusions are recorded in `Documentation/Boss/OFFLINE_TOOL_INVENTORY_AUDIT_S180.md`.
- Test/proof console-variable build guards and documented Shipping-visible exceptions are reviewed in `Documentation/Boss/SHIPPING_GUARD_INVENTORY_AUDIT_S181.md`.
- Inspect driver-specific comments and Documentation/TEST_PLAN.md; a script name does not imply a passing result.

## Script index

| Script | Purpose from module docstring |
|---|---|
| air_jump_tuning.py | Longer jump for the jump heavy: the pack player jumps with JumpZVelocity 600 at gravity scale 1.7 (about 0.72 s in the air, 108 cm apex). The heavy |
| air_light_attacks.py | Jump light attack for every weapon. The pack picks Ability.Melee.FallingAttack when the player is airborne and the weapon has FallingAttackMontages |
| anim_probe.py | Reads bone transforms of imported Boss01 clips at several times to see whether they really move. Log prefix [AnimProbe]. |
| apply_arena_art_fix.py | No module docstring; inspect the script body before running. |
| apply_perfect_arena.py | No module docstring; inspect the script body before running. |
| arena_use_pack_boss.py | L_SevarogArena: the boss is the pack's own great-sword boss (mannequin), placed at the arena centre facing the player start. |
| atmosphere.py | Sets the arena's mood: a low warm dusk sun raking across the ruins, volumetric fog with light shafts and a ground mist layer, a cloud deck, |
| body_slots_probe.py | Logs the material slots of the imported Boss01 body. Log prefix [BodySlots]. |
| boss01_bounds.py | Logs bounds of the imported Boss01 body and sword by two APIs. Log prefix [Bounds]. |
| boss_poise_armor.py | Poise is the pack boss's armor (Elden Ring): BP_ExampleGreatSwordBoss is born with GameplayTags = (Enemy.Character, Status.HitStunImmune). Its hit stun ability lists |
| boss_pose.py | Poses the level's boss mesh with an imported clip at a time (editor world, no PIE). Reads Saved/pose.txt: "<clip asset name> <seconds>". Log prefix [Pose]. |
| boss_pose_reset.py | Puts the level boss's mesh back to Animation Blueprint mode after boss_pose.py, and removes the failed SK_Boss01_Body import (nothing references it). Log prefix [Pose]. |
| build_asset_proof_map.py | Builds /Game/OneBossFight/Levels/L_AssetProof: a visual proof that the chosen player (Greystone) |
| build_boss01_materials.py | AGI-4: builds the Boss 01 materials from Antigravity's texture files (log prefix [BossMats]). |
| build_off.py | Clears the console variable rpg.Build (the build of the player, process wide: a value left by an aborted pie_builds.py run would equip a weapon in every later PIE). Part of the warm-up of RunDrivers.ps1. |
| candidates_clear.py | Removes the CandTest actors again. Log prefix [Cand]. |
| candidates_spawn.py | Spawns the boss body candidates in a row far outside the arena (folder CandTest) so they can be photographed. Log prefix [Cand]. Cleanup: candidates_clear.py. |
| check_active_world.py | No module docstring; inspect the script body before running. |
| check_floor.py | Prints the floor material the arena actor holds and the one on its floor component, and the brazier mesh. Log prefix [Floor]. |
| check_grey_layers.py | Loads every retargeted animation Blueprint of GreystonePack and reports whether it compiled and its parent. |
| check_sev_abilities.py | Prints which montage every Sevarog ability points at (a deleted-and-recreated montage once left the saved references empty). |
| check_worldblend.py | No module docstring; inspect the script body before running. |
| cleanup_review11.py | Deletes the scratch assets of review_report11.py in /Game/OneBossFight/_Review11 (nothing references them; an unsaved scratch asset would be saved to disk by the editor's Save Content on a rebuild). Deletes asset by asset, then the folder. Log prefix [Review11]. |
| cleanup_review12.py | Deletes the scratch assets of review_report12.py in /Game/OneBossFight/_Review12 (nothing references them; an unsaved scratch asset would be written to disk by the editor's Save Content on the next rebuild). |
| cleanup_review13.py | Deletes the scratch assets of review_report13*.py in /Game/OneBossFight/_Review13 (nothing references them; an unsaved scratch asset would be written to disk by the editor's Save Content on the next rebuild). |
| compare_skeletons.py | Compares the bone hierarchy of the imported SK_Boss01_Body with the pack mannequin (log prefix [SkelCmp]). |
| copy_sockets_to_greystone.py | Copies the pack mannequin's sockets (weapon hand and sheath sockets, consumables, ...) to the Greystone skeleton under the same |
| debug_atmos.py | Debug switches for the atmosphere: Saved/debug.txt holds words: nocloud, nofog, novol, nopost, nomist. Any word listed turns that piece off, everything else is on. Log prefix [DbgAtmos]. |
| dress_arena.py | Dresses L_SevarogArena with the Megascans ruin kits copied from the Dark Ruins sample: a double ring of ruin walls around the existing arena wall, |
| dump_close_attack.py | Read-only dump for the authored-clips design (log prefix [CloseDump]): the properties of the pack's GA_GS_Boss_CloseAttack_C (class defaults) and the notifies of the four pack montages GS_Attack01..04 (class, trigger time, duration), plus the montage slot and section names, and the authored clips' lengths. |
| dump_level.py | Lists the actors of the open level grouped by class (count, one sample location and folder), plus the lighting actors in detail. Log prefix [Level]. |
| dump_pack_typed_edges.py | READ-ONLY typed property dump of the pack weapon classes (owner approval 2026-10-26, scratch only; asks Codex X-140). Writes text files PR5_*.txt |
| export_assets_text.py | Exports assets to text under Saved/asset_text/ so their default values can be read with grep. Edit ASSETS below. |
| export_greystone.py | No module docstring; inspect the script body before running. |
| export_mannequin.py | No module docstring; inspect the script body before running. |
| export_paragon_skins.py | No module docstring; inspect the script body before running. |
| export_quinn.py | No module docstring; inspect the script body before running. |
| export_reference.py | Exports the pack mannequin (the skeleton every boss and player asset must use) as FBX for Blender work. Log prefix [Export]. |
| export_reference2.py | Brief 02 reference export (log prefix [Export2]): the pack's GS_ChargedAttack animation (FBX), Paragon body candidates (skeletal mesh FBX plus their textures as PNG), and the Kwang sword textures as the |
| export_reference3.py | Finds the animation sequences behind the pack boss montages through asset dependencies and exports them as FBX (log prefix [Export3]). Output: Import/ThirdParty/Reference/. |
| finish_statue_import.py | Removes the scratch actor StatueLook, saves the imported corpse statue mesh (/Game/OneBossFight/Boss01/Remains/SM_Boss01_CorpseStatue) and the level (log prefix [StatueImport]). The statue is spawned by code on the boss's death, never placed in the level. |
| fix_grey_blendspaces.py | Greystone repair, step 3: blend spaces saved with stale animation references (name-collision duplicates at /Game root). For every blend space in |
| fix_grey_default_layer.py | ABP_CombatCharacter_Grey (retargeted copy) still imports the pack's ORIGINAL ABP_UnarmedLayer as its default linked layer, so Greystone ran the mannequin layer |
| fix_grey_layers_1.py | Greystone layer repair, step 1: the layer ABPs were saved with their parent at /Game/ABP_CombatAnimLayersBase_Grey (its location before it was moved), |
| fix_grey_layers_2.py | Greystone layer repair, step 2: re-parent every layer ABP to the real retargeted base, compile and save, then remove the temporary copy at /Game |
| fix_roll_root_motion.py | The IK retargeter put the roll's travel in the pelvis (the source animation moves its root bone, which is not retargeted), |
| fix_sev_montage_refs.py | Re-points the Sevarog abilities at their entrance, exit and death montages. Those three montages were deleted and recreated at the same path during |
| fx_test.py | Spawns a row of candidate fire / ember systems at (700, y, 0) so they can be compared in a viewport shot (folder "FxTest"); run again to clear and respawn. |
| g0_pack_boss.py | Gate 0 pack facts (G0-2, G0-3): the pack boss and player assets the art request depends on. Log prefix [G0]. Read only. |
| g0_probe_api.py | Finds which Python names exist for montage notifies, sections and sockets in this engine build. Log prefix [Probe]. |
| g0_weapon.py | Finds the boss weapon mesh (Kwang sword) and prints its sockets. Log prefix [G0W]. Run with Scripts/run_in_editor.py. |
| g1_boss_abilities.py | Gate 1: which montages each pack boss ability plays, and its trigger/tag variables. Log prefix [G1A]. Read only. Run with Scripts/run_in_editor.py. |
| g1_sevarog_slots.py | Material slots, size and sockets of the Paragon Sevarog base skin (for Brief 02 T1). Log prefix [SevSlots]. |
| g2_probe_a4a5.py | Probe for the A4 and A5 stand-ins (log prefix [ProbeA45]): lengths of the A4 and A5 clips. Read only. |
| g3_dump_attack_data.py | G3 audit step 2 (log prefix [G3A]): prints the editable properties of the pack's melee attack data assets and of the weapon abilities' default objects (Claymore, Sword, DualSword, Twinblades melee abilities), to find where the player's posture damage, attack power, stamina cost and hit data live. |
| g3_list_weapon_assets.py | G3 audit step 1 (log prefix [G3A]): lists the pack's player weapon assets (abilities, attack data, weapon data) so the per-weapon-attack data of Gate 3 can be designed from what exists. |
| g3_probe_build_hits.py | Probe (M13, log prefix [HitProbe], no checks): why do the claymore's and the dual swords' light and strong swings land no hit in pie_builds.py (the swing tracker sees them, the hit intake sees none, only the claymore's charged attack hit)? |
| g3_probe_equip.py | G3 / M13 probe (log prefix [G3Probe]; variable dumps are LogRPGDebug lines): how does the pack give the player a weapon and switch the combat style? Starts a PIE and ends it itself; changes nothing but |
| g3_probe_montages.py | G3 / M13 probe (log prefix [G3Montage]), editor only, NO PIE: for the four weapon abilities of the pack (sword, claymore, dual swords, twinblades) prints, for every montage of |
| gate_material_probe.py | Lists the parameters of MI_Arena_FogGate and its parent. Log prefix [GateMat]. |
| gate_material_set.py | Sets the emissive intensity of MI_Arena_FogGate from Saved/gate_emissive.txt (default 60) and saves it. Log prefix [GateMat]. |
| greystone_sevarog_11_polish.py | Polish pass (needs the C++ built): Greystone's baked-in sword and shield are hidden by bone with URPGHideBones (instead of hiding material slot 3, which also hid |
| handle_pie.py | No module docstring; inspect the script body before running. |
| hide_comp.py | Debug: hides or shows arena actor components by name (NAMES, VISIBLE). Log prefix [HideComp]. |
| hide_grey_builtin_weapons.py | Greystone ships with a sword, shield and some fur baked into material slot 3 (M03_SwordShieldFur). The pack's own weapons are attached at runtime, so the built-in |
| import_all_builds.py | import_all_builds.py - Imports all 6 character builds into Unreal Engine as SkeletalMeshes |
| import_arena_meshes.py | Imports the custom FBX arena meshes generated by Blender into /Game/OneBossFight/Environment/Meshes. |
| import_audio.py | Imports the two boss music tracks from Import/Audio into /Game/OneBossFight/Audio (log prefix [ImportAudio]): MX_Boss01_Phase1 (the battle theme) and MX_Boss01_Phase2 (the choral climax). |
| import_boss01.py | Imports Antigravity's Boss 01 deliveries into /Game/OneBossFight/Boss01 (log prefix [Import]): body on SK_CombatMannequin, sword, A2 clips, dormant idle and wake clips. Then reattaches the original Paragon Sevarog materials by slot name. |
| import_boss01_clips_r12.py | Imports the Boss 01 clips accepted from Antigravity's Report 12 into /Game/OneBossFight/Boss01/Animations (log prefix [ImportClips]). |
| import_boss01_clips_r14.py | Imports the clips accepted on the numbers from Antigravity's Brief 13/14 deliveries (log prefix [ImportClips14]) into /Game/OneBossFight/Boss01/Animations as assets that nothing references yet (an older delivery of the same name is replaced in place when no asset references it): DormantIdle, Wake, A1_QuickSlash, A3a_Combo1, A3b_Combo2, A2_Raise, A2_ApexHold, A2_Slam. |
| import_corpse_statue.py | Imports (or re-imports in place) the corpse statue /Game/OneBossFight/Boss01/Remains/SM_Boss01_CorpseStatue from Import/Boss01/Weapons/CorpseStatue and prints what the engine reads (log prefix [Statue]): bounds, triangles, UV channels, slots. The three slots get the arena stand-in materials (the remains actor overrides them with its own dissolve MIDs by slot name). Saves the mesh. |
| import_shiva_shrine.py | Imports (or re-imports in place) AG's engine-ready Lord Shiva shrine /Game/OneBossFight/Environment/Shrine/SM_Boss01_ShivaShrine from Import/Boss01/Weapons/Shrine and prints what the engine reads (log prefix [Shrine]): bounds, vertex count, UV channels, slots, sockets, and the centroids of the vertices per height band (the front of the statue must face +Y: the face and the chest centroid y > 0). The slots get the arena's stand-in materials; saves the mesh. Run with Scripts/run_in_editor.py. |
| import_ui_art.py | Imports AG's UI art from Import/Boss01/UI into /Game/OneBossFight/UI/Art (log prefix [UIArt]): the three build icons and the flask counter textures (full, half, empty, plate), as UI textures (no mips, clamp, sRGB, UI compression, never streamed). Re-imports in place. Run with Scripts/run_in_editor.py. |
| inspect_actions.py | Prints action-level modifiers/triggers and settings for every IA_ asset. |
| inspect_all_instances.py | No module docstring; inspect the script body before running. |
| inspect_all_pillar_mats.py | No module docstring; inspect the script body before running. |
| inspect_arena.py | Prints the arena actor's components (class, mesh, relative transform, instance count) and the parameters of a few Megascans material instances. Log prefix [Inspect]. |
| inspect_arena_actor.py | No module docstring; inspect the script body before running. |
| inspect_arena_floor_actual.py | No module docstring; inspect the script body before running. |
| inspect_arena_floormesh.py | No module docstring; inspect the script body before running. |
| inspect_arena_floormesh2.py | No module docstring; inspect the script body before running. |
| inspect_assets.py | Asset pipeline inspection for One Boss Fight (milestone M2). |
| inspect_bolt.py | No module docstring; inspect the script body before running. |
| inspect_boss_components.py | Lists the Blueprint components (SCS subobjects) of the pack's great-sword boss and the weapon static mesh sockets. |
| inspect_boss_montages.py | Compares notifies of a pack boss montage and our Sevarog montages, and exports BT_ExampleBoss to text (Saved/bt_exampleboss.t3d). |
| inspect_boss_style.py | Prints the ability set entries of the pack great-sword boss combat style and the Anim Layer behaviour. |
| inspect_current_arena.py | No module docstring; inspect the script body before running. |
| inspect_dr_materials.py | No module docstring; inspect the script body before running. |
| inspect_fireball.py | Fireball enemy ability defaults, its montage notifies, and the projectile Blueprint components. |
| inspect_ga_defaults.py | For each pack boss ability: lists the Blueprint variables of the whole parent chain and the values on the boss child's defaults. |
| inspect_greystone_animbp.py | Prints the Greystone AnimBP parent class and its variables/functions (what it expects from the pawn). |
| inspect_greystone_combat.py | Prints what the combat setup needs to know about Greystone: mesh sockets, weapon-related bones, |
| inspect_imc.py | Prints every mapping in IMC_Default with its modifiers and triggers, and each action's value type. |
| inspect_m7_assets.py | Inspect the imported audio, font, Niagara and animation assets before wiring them. |
| inspect_master_materials.py | No module docstring; inspect the script body before running. |
| inspect_materials.py | inspect_materials.py - Inspects material assignments for all 6 character builds. |
| inspect_mats.py | Prints the parent and parameters of material instances (paths in PATHS) and the existing arena floor material. Log prefix [Mats]. |
| inspect_mesh_mats.py | No module docstring; inspect the script body before running. |
| inspect_more_mats.py | No module docstring; inspect the script body before running. |
| inspect_other_pillars.py | No module docstring; inspect the script body before running. |
| inspect_pack_boss.py | Dumps the pack's great-sword boss: Blueprint CDO values, EnemyInfo data asset, combat style and ability CDOs. Run in the open editor. |
| inspect_pack_boss2.py | Second pass over the pack's great-sword boss: exact EnemyInfo / CombatStyle / AbilitySet values and the montage element type. |
| inspect_pack_bp.py | Reflect over key pack Blueprints: own variables of their CDOs and the values of the data assets they use. Headless. |
| inspect_pack_notifies.py | Reads the property values of the pack boss montage notifies (GS_Attack01, GS_LeapAttack) so our Sevarog montages can copy them. |
| inspect_pillar_instances.py | No module docstring; inspect the script body before running. |
| inspect_roll_motion.py | Where does the retargeted roll travel? Component-space root and pelvis positions over time. Headless. |
| inspect_ruins_materials.py | Texture and key scalar values of candidate Deadly Ruins material instances. Headless. |
| inspect_samurai_mesh.py | No module docstring; inspect the script body before running. |
| inspect_sevarog.py | Prints Sevarog's bones that look like a weapon, mesh size, and AnimBP asset names. |
| inspect_target_types.py | How the pack configures trace targets: PlayerInfo.Default Target Types, BP_UnarmedTraceTarget.CollisionSocketNames, enemy infos. |
| inspect_uvs.py | No module docstring; inspect the script body before running. |
| leap_ability_probe.py | Reads default properties of the boss leap ability class. Log prefix [LeapGA]. |
| legend_off.py | Switches the legend pass off for this editor session: rpg.Legend 0 (log prefix [Legend]). The console variable is process wide, so it survives PIE sessions; every older driver measures timings that hit stop, slow motion and |
| list_floor_textures.py | No module docstring; inspect the script body before running. |
| list_fx_sounds.py | Lists SoundCue and ParticleSystem asset names in the Greystone and Sevarog packs (for choosing combat audio/VFX). |
| list_grey_sockets.py | No module docstring; inspect the script body before running. |
| list_instances.py | No module docstring; inspect the script body before running. |
| list_ruin_meshes.py | Lists the copied Megascans / custom static meshes with size (cm), Nanite flag and vertex count, plus the surface material instances. Log prefix [Meshes]. |
| make_abi_test_catalog.py | Isolated TEST catalog for the live fourth-weapon equip (Codex lead decision C170, X-156 2026-10-26). Creates three NEW assets only under |
| make_close_montages.py | Creates the project-owned close attack montages AM_Boss01_A1, AM_Boss01_A3a, AM_Boss01_A3b (log prefix [CloseMontages]) from AG's authored clips, with the notify classes of the pack's close attack montages (read from GS_Attack03 for A1, GS_Attack01 for A3a, GS_Attack02 for A3b: damage trace state, movement lock, desired rotation, sound, end-of-ability, follow-up) placed at the authored times of the timing sheets: |
| make_combat_catalog.py | DD-1 step1 authoring helper. NOT run by Codex. Creates seven NEW assets only. |
| make_death_montage.py | Creates the montage AM_Boss01_DeathLegend (log prefix [DeathMontage]) from the clip AN_Boss01_DeathLegend: the pack's death ability (GA_EnemyRagdollDeath) plays montages from its DeathMontages array, and a montage asset is what that array holds. |
| make_flipbook_materials.py | Imports AG's three effect flipbook sheets and builds their materials (log prefix [Flipbook]). |
| make_gate_rune_material.py | Creates M_Gate_Rune (log prefix [GateRune]): the dim ember glow for the rune slot of the M-08 fog gate frame (M_Ember is far too bright for a big lintel panel: it blooms to white). Dark base, emissive ember orange with a slow pulse. New asset only; run once (skips when it exists). |
| make_polish_materials.py | Creates the materials the arena polish needs (all under /Game/OneBossFight/Environment/Materials, recreated in place so references stay valid): |
| make_remains_material.py | Imports AG's V-09 textures and builds M_Boss01_Remains (log prefix [Remains]), the dissolve material of the boss's corpse statue. |
| make_scratch_route_a.py | Scratch route (a) authoring (owner approval G-3, 2026-10-26). Creates NEW assets only under /Game/OneBossFight/Scratch/RouteA: |
| make_typed_abi_fixtures.py | Typed-ABI test fixtures (owner approval 2026-10-26: "Yes"; names from Codex/C155_A100_REVIEW.md). Creates NEW assets only under |
| make_typed_abi_uncooked_item.py | Replaces the uncooked typed-ABI fixture (Codex X-153 review): `DA_ABI_UncookedWeaponItem` is now a copy of the REWIRED cooked fourth weapon item, so its typed edges |
| make_weapon_table.py | Creates the weapon attack table asset /Game/OneBossFight/Data/DA_WeaponAttacks (log prefix [WeaponTable]) with the Freeze starting values that the class constructor fills in (Player/RPGWeaponAttackTable). |
| map_referencers.py | Which assets reference the original pack animations that were retargeted? Writes Saved/grey_referencers.json |
| mesh_origins.py | Prints bounds origin (offset of the box centre from the pivot, cm) and size for the structural meshes used by the arena dressing. Log prefix [Origins]. |
| mesh_test.py | Spawns a row of candidate meshes at x = 700 (folder "MeshTest") with their bounds logged, so they can be compared in a viewport shot. Run again to clear and respawn. |
| move_grey_abps.py | Moves the retargeted animation Blueprints that the batch left at /Game into the mirrored GreystonePack folders and saves them. |
| no_throttle.py | Turns off the editor's background CPU throttling for this session (the viewport and PIE otherwise render at a crawl when the window is not focused). |
| pack_anim_inventory.py | Lists the animation assets of the Advanced ARPG Combat pack by folder, so the asset request only asks for what the pack lacks. |
| pie_a2_diag.py | Diagnosis for the A2 scenarios: does the frozen boss have its sword in hand, does the forced move play, does the player lose health. Log prefix [A2D]. |
| pie_a2_interrupts.py | Gate 1 scenario 7 (Freeze 35.3): the stand-in A2 is interrupted at four moments (windup 0.5 s, committed 1.8 s, just before the hit 1.95 s, recovery 2.3 s) by a stance break, an encounter reset or the boss's death. |
| pie_a2_scenarios.py | Gate 1 / G1-9: scripted A2 timing scenarios (Freeze 35.3) against the stand-in attack (the pack's GS_ChargedAttack, tag Ability.Melee.CloseRare). |
| pie_a4_low_sweep.py | Gate 2 / G2-2: the A4 low sweep (Freeze 16 A4, test B09). The boss is frozen awake (RPGBossEncounter.hold_for_test), each trial puts the player in front, starts the move through |
| pie_a5_heal_punish.py | Gate 2 / G2-3: the A5 heal punish (Freeze 16 A5, tests P01 to P08). The boss is frozen awake; the player stands in front of it. |
| pie_a5_natural.py | Gate 2 / G2-3, informational: A5 in a natural fight. The boss is awake and NOT held (the pack's behaviour tree runs); the player is teleported to 700 cm in front of it and drinks with the real input (IA_UseTool) |
| pie_abi_fourth_equip.py | DD-1 step 1, live equip of the DISTINCT fourth weapon through the isolated test catalog (Codex lead decision C170, X-156 2026-10-26). |
| pie_air_attack.py | PIE check of the jump attacks: the pack player enters combat, jumps, and while airborne triggers the melee ability (what the input buffer does on a light |
| pie_arena_shots.py | PIE arena stills: teleports the idle player to a few vantage points and raises Saved/m7_flag.txt with the shot name so |
| pie_attack_rules.py | Gate 2 / G2-11: attack priority rules (Freeze 21, B06, B10). R1 no attack during a stance break, R2 none during the phase transition, R3 none while dormant, R4 a second non-chained attack that replaces a running one is |
| pie_attr_probe.py | Probe (log prefix [AttrProbe]): what the pack's 'Modify Attribute' does to the player's stamina when called from Python (the same function the swing tracker calls from C++): -20, +5, -20 again, with a wait of one frame and of 0.5 s between. |
| pie_audio.py | PIE check of the audio components: the player walks and runs forward (add_movement_input) and its footstep component must count steps; the boss stays dormant |
| pie_authored_close_clips.py | B10 authored close clips: validates the live pack-ability swap and the A1/A3 tracker timing source. Log prefix [AuthoredClose]. |
| pie_bleed.py | Gate 3, M12: the bleed status (URPGBossBleed): buildup per hit, a proc at the threshold (100, then +20 up to 200) that takes 3 percent of the boss's maximum health once, never during death, sleep or the phase |
| pie_body_look.py | Swaps the boss mesh for the imported SK_Boss01_Body in PIE (scale from Saved/body_scale.txt, default 100) and takes screenshots from the player camera: idle, then the A2 clips at set times. Log prefix [BodyLook]. |
| pie_body_look_short.py | Swaps the boss mesh for the imported SK_Boss01_Body in PIE (scale from Saved/body_scale.txt, default 100) and takes screenshots from the player camera: idle, then the A2 clips at set times. Log prefix [BodyLook]. |
| pie_boss01_look.py | Plays Antigravity's A2 clips on the pack boss mesh (same skeleton) in PIE and takes high resolution shots at set times, front and side. Files: Saved/Screenshots/WindowsEditor/. Log prefix [B01Look] |
| pie_boss_abilities.py | PIE probe (read only): lists the abilities the pack's great-sword boss was granted (class, ability tags, bUsesPoise) and what its attribute component holds, so |
| pie_boss_arm_diag.py | Where does the pack boss get its sword? Wakes the boss by proximity and logs its montage, state and weapon-like actors each second for 25 s. Log prefix [Arm]. |
| pie_boss_clips.py | Boss clips (Brief 12 deliveries wired in): the phase two roar and the stance break play the project's own clips (AN_Boss01_PhaseRoar, AN_Boss01_StaggerFall, AN_Boss01_StaggerDown) instead of the pack's montages. |
| pie_boss_death.py | The boss's death clip (G2-9, A-12; URPGBossDeath, see Documentation/DEATH_CLIP_NOTES.md): the boss is held awake, killed through the pack's attribute (debug_kill_boss: health 0 and the pack's Ability.Dead) and sampled every 0.2 s for 8 s |
| pie_boss_death_states.py | The boss's death clip where the other systems are busy (review D of RPGBossDeath): three scenarios, each in its own PIE (a dead boss is destroyed by the pack, so one death per PIE; the driver stops and starts PIE itself). |
| pie_boss_encounter.py | PIE check of the boss encounter flow (URPGBossEncounter): the boss must sleep at home while the player is far, wake when the player walks inside the gate, fight and |
| pie_boss_fireball.py | PIE probe: can the pack great-sword boss be given the pack magic enemy's fireball ability (GA_Fireball_Enemy) at runtime and fire it at the player? The player stands |
| pie_boss_hitreact.py | PIE probe of the boss's hit reaction: the player walks up and lands real light attacks (IA_NormalAttack) and then heavy attacks (IA_StrongAttack) on the pack's |
| pie_boss_hud.py | PIE test of the boss HUD and the victory signal (RPGBossHud): dormant -> fighting (banner, bar), phase two subtitle, stance break flash, riposte prompt, victory once, reset, second victory. |
| pie_boss_look.py | The boss's final look (G2-15, URPGBossLook): Antigravity's body, crown, mantle, gauntlet and the greatsword on top of the pack mesh, which keeps driving the fight. |
| pie_boss_look_shots.py | Pictures of the boss with its final look (G2-15) in PIE, for the owner's eye: standing (front, side), in the kneel of a stance break (front, side) and in the death clip (front, 1.0 s and 3.0 s after the kill). The boss is held awake and |
| pie_boss_materials.py | AGI-4 check (log prefix [BossMat]): in PIE the boss gets the Boss 01 body, crown, mantle and gauntlet; the M_Boss01_* instances on them get dynamic copies and |
| pie_boss_phase_two.py | PIE check of the boss's phase two (URPGBossPhases): wake the boss, push it below 50% health, and log the transition (roar clip, held behaviour), then the buffs (walk |
| pie_boss_smoke.py | Play-in-editor smoke test for M4 (boss and encounter loop). Run inside the open editor with L_Greybox loaded, |
| pie_boss_stagger.py | PIE check of the boss stance break (URPGBossStagger): the player (kept alive) hits the pack boss with real heavy presses until its poise breaks, then lands a light and |
| pie_boss_stagger_edge.py | PIE edge cases of the boss stance break (URPGBossStagger). MODE "boss_dies": during the stance break the boss is put at 3 percent of its runtime maximum health and hit with a light attack (a critical, |
| pie_build_fight.py | Gate 3, M14 (G3-6): the balance run. A scripted PLAYER BOT fights the REAL boss (not held: no hold_for_test, the pack's behaviour tree runs) with the build named in Saved/build_fight_build.txt (Starter, Strength or Dex, |
| pie_build_hud.py | Gate 3, M13: the build line of the HUD (URPGBossHudWidget::BuildTextBlock, filled by URPGBossHud from the player's URPGBuildLoadout; log prefix [BuildHud]). |
| pie_build_hyperarmor.py | Gate 3, M14: the hyperarmor windows AUTHORED into the weapon attack table (DA_WeaponAttacks, Scripts/Editor/set_weapon_windows.py), with the real build and real swings against the held boss (log prefix [BuildArmor]). |
| pie_build_select.py | Gate 3, G3-5: the pre-fight build selector (URPGBuildSelect, B key; log prefix [BuildSelect]). Drives it through its test hooks (the key and mouse paths call the same functions): |
| pie_builds.py | Gate 3, M13: the builds (RPGBuildLoadout). Real presses against the held boss (the player stands 110 cm in front of it); the player never gets a weapon through a property: only the console variable rpg.Build (through the loadout's |
| pie_cam_probe.py | No module docstring; inspect the script body before running. |
| pie_camera_clip.py | Camera ground clipping test. Scenarios (log prefix [CamClip]): |
| pie_camera_look.py | Screenshots the player's own camera at three pitches (32 up, 0, -60 down) on the arena floor. Log prefix [CamLook]. Needs a warm-up PIE first. |
| pie_camera_probe.py | PIE probe of the player's camera setup: spring arm and camera component properties, the camera manager's pitch limits, what the camera trace channel hits on the arena floor. Log prefix [CamProbe]. |
| pie_camera_scenarios.py | Camera scenarios after the rig (log prefix [CamScn]): C1 death and ragdoll, C2 dodge roll with the camera low, C3 standing against the arena wall with the camera behind towards the wall, C4 jump and land with the |
| pie_clip_look.py | Look at the Report 11 clips on the final body in PIE (log prefix [ClipLook]): the boss gets SK_Boss01_Body with crown, mantle, gauntlet and the sword, plays each clip of SHOTS (a full asset path and a time) frozen at that time, one 1280x720 shot per entry. |
| pie_clip_look12.py | Look at the Report 12 clips on the final body in PIE (log prefix [ClipLook12]): the boss gets SK_Boss01_Body with crown, mantle, gauntlet and the sword, plays each clip of SHOTS (a clip name of the review scratch folder |
| pie_clip_look13.py | Look at the Report 12 clips on the final body in PIE (log prefix [ClipLook12]): the boss gets SK_Boss01_Body with crown, mantle, gauntlet and the sword, plays each clip of SHOTS (a clip name of the review scratch folder |
| pie_close_attacks.py | Gate 2 / G2-1: A1 and A3 on the tracker (commitment, heading lock, branch check). Montages are played on a frozen awake boss (RPGAttackTracker.PlayMoveMontageForTest). |
| pie_close_combo_watch.py | Watches which montages the awake pack boss plays against a player that stays at close range (refilled and put back every 0.4 s). Logs each montage change with its start time, the distance |
| pie_close_reach.py | Reach probe of the pack's real close attack with the authored clips swapped in (log prefix [Reach]): the player is put in front of the held boss at 60, 90 and 120 cm, the pack ability is started (it picks A1, A1b, A3a or A3b itself), and each trial logs whether the player lost health. The stage names come from the LogRPGAttack lines between two TRIAL markers (Scripts/Editor/pie_close_reach.py output is read with grep, nothing is asserted here: it is a measurement). Needs the editor in PIE after a warm-up like the other drivers. |
| pie_combat_catalog.py | DD-1 catalog integration driver, NOT RUN by Codex. Fresh PIE per source mode. |
| pie_combat_smoke.py | Play-in-editor smoke test for M3 combat. Run inside the open editor (L_Greybox loaded): |
| pie_damage_path.py | Gate 2 / M2 (SPEC_M2_damage.md): the damage path of the boss's own moves through URPGDamageResolver (Freeze 12.1, 488, 489; tests D14, D15, H04, H05, H08). |
| pie_death_probe.py | What the pack does when the boss dies (log prefix [DeathProbe]): finds the boss's GA_EnemyRagdollDeath instance, logs its DeathMontages and the Death Task class, kills the boss through the pack's attribute (DebugKillBoss) and samples |
| pie_debug_overlay.py | Starts PIE, switches the combat debug overlay on (rpg.Debug 2), lets it log for a few seconds, stops PIE. Log lines appear under LogRPGDebug. Log prefix [DebugOverlay]. |
| pie_dodge.py | PIE measurement of the dodge input with the pack's real IA_Dodge pressed through URPGInputTestUtils: a tap, a hold (while pushing forward), and a double tap. |
| pie_dodge_trials.py | G0-7: scripted PIE trials of the double tap rule with the pack's real IA_Dodge key (RPGInputTestUtils), Freeze tests D01 to D07. |
| pie_input_montage_latency.py | V-C041 diagnostic: logs injected attack/dodge/parry input to first observed player montage change; run separately on legacy and selected encounter routes. Lead-run only; tick-sampled, not device latency. |
| pie_dormant_wake.py | B11: authored dormant loop and wake gate. Exercises normal wake, direct attack veto, reset during wake, and death during wake. Log prefix [DormantWake]. |
| pie_dump_abilities.py | Starts PIE, asks the boss's debug component to log all ability variables (LogRPGDebug "ABILITY" lines), stops PIE. Log prefix [DumpAb]. |
| pie_dump_player_functions.py | PIE: logs the Blueprint functions of the player pawn and its components ([RPGDebug] FUNCTION lines). Needs a warm-up PIE first. |
| pie_flask_hud.py | G3-5 flask overlay. Reads only the reflected live HealthPotion stack; one real IA_UseTool press consumes it after the boss debug helper lowers player health. Log prefix [FlaskHud]. |
| pie_flipbooks.py | Combat-flipbook driver: observes the real bleed, weapon-hit and dodge start edges. Log prefix [Flipbook]. |
| pie_fog_gate.py | Fog gate states in PIE (Gate 2 entrance moment): Idle while the boss sleeps, Closed (blocking, full mist) when it wakes, Idle again after an encounter reset, Cleared (open, mist gone) when the boss dies. |
| pie_g3_probe.py | G3 audit (log prefix [G3Probe], variables appear as LogRPGDebug OBJECT lines): starts PIE, asks the boss's debug component to dump what decides the player's hit on the boss: |
| pie_gate_look.py | Screenshots the fog gate from the arena side: sleeping boss (thin mist), then awake (closed). Log prefix [GateLook]. |
| pie_grey_check.py | PIE visual check of the Greystone player on the Advanced ARPG framework. Run via execute_script with the pack demo level open and |
| pie_grey_layers.py | PIE check of every retargeted weapon layer on Greystone: links each layer class on the mesh, stands then runs, frames are tagged with the layer name |
| pie_grey_weapons.py | PIE check of weapon socket fit on Greystone: for each pack weapon actor, attach it to its own WeaponHandSocket then DisabledSocket (sheath) on Greystone's |
| pie_health_probe.py | Probe for the natural-wake health reset (Q7, 2026-10-23): logs the boss's current and maximum health from PIE start, wakes the encounter with the same calls the failing drivers use, and logs again every 0.2 s. No checks, no RESULT line is needed: read the [HealthProbe] lines. |
| pie_hit_diag.py | Why does a forced A2 not hurt? Part 1: the pack AI fights a standing player (health changes logged with the boss montage). Part 2: the boss is held and A2 is started by hand at several distances. |
| pie_hit_intake.py | Gate 3, M7: the hit intake (URPGHitIntake on the player) sees every hit the player lands on the boss once, with the right weapon and attack data. The boss is held awake and the player stands 110 cm in front of it; |
| pie_hud_probe.py | Starts PIE, wakes the boss, lists every UserWidget alive (class name, visibility) and takes a screenshot of the player view. Log prefix [HudProbe]. |
| pie_hyperarmor.py | Gate 3, M11: hyperarmor (Freeze 20.1). Inside the window of a swing the player carries the pack's hit stun immunity effect (Status.HitStunImmune, the tag the player's GA_PlayerHitStun lists in its blocked tags), outside |
| pie_iframes.py | Gate 2 / M2 (SPEC_M2_damage.md section 6): the dodge's invulnerability windows measured in MONTAGE seconds at fixed 30, 60 and 120 FPS (Freeze D12), and the cleanup of the tag (D13). |
| pie_input_smoke.py | PIE input smoke test: starts PIE, then presses real keys through the player controller's input pipeline |
| pie_jump_probe.py | PIE probe: presses a key (Saved/jump_key.txt, default SpaceBar) and logs the player's height above its start for 2 s. Log prefix [JumpProbe]. Needs a warm-up PIE once. |
| pie_leap_wave.py | Gate 2 / G2-4: the A6 leap. W1 leap blocked in phase one, W2 wave hits a grounded player, W3 a jump clears it, W4 central hit priority, W5 reset mid wave stops it, W6 leap unlocked after phase two, |
| pie_legend.py | Gate 2 / M3 and C-916 P1: legend pass on the boss fight (log prefix [Legend]); opt-in L8 witnesses player parry slow motion via a real A4 contact. |
| pie_look.py | PIE look check: plays the arena and takes high resolution screenshots from the player's own camera at a few spots (player start, mid arena facing the boss, |
| pie_m7_check.py | PIE visual check for the M7 assets: roll montage, block/parry sparks, shockwave and lightning effects. |
| pie_montage_shots.py | PIE frame capture of montages on the pack player: plays each clip of CLIPS on the idle player (boss removed) and takes a high resolution screenshot every |
| pie_montage_travel.py | PIE measurement of how far and how long montages move the pack player (root motion): plays each montage in MONTAGES directly on the idle player, one after the |
| pie_pack_demo.py | Opens the Advanced ARPG pack's test level inside this project, plays it, and logs what exists (pawn, game mode, enemies, |
| pie_pack_fight.py | PIE check of the pack's own player (BP_CombatPlayerCharacter, mannequin) against the pack's great-sword boss (BP_ExampleGreatSwordBoss) in L_SevarogArena. |
| pie_phase_reset.py | Gate 2 checks on phase two and the reset (Freeze L01 to L04, L10, 18.1): runs on the awake, frozen boss. |
| pie_player_death_reset.py | Gate 2 / G2-10, Freeze S11 and L09: the player dies in the middle of a boss action and respawns; both combatants must be reset correctly. Scenarios: during a stance break, during a riposte, during the A4 sweep, |
| pie_player_tags.py | PIE probe: presses the pack's dodge key and logs the player's owned gameplay tags whenever they change (to find the i-frame state). Log prefix [PlayerTags]. Needs a warm-up PIE once. |
| pie_poise_enemy_test.py | PIE test of enemy poise: the player (kept alive) stands next to a sword enemy and fires the melee attack ability by tag |
| pie_poise_scale.py | PIE check of poise scaling by attack power (GA_BaseHitReaction gate): the pack player walks up to the pack boss and presses IA_NormalAttack (light) and then |
| pie_poise_test.py | PIE test of poise on the pack's demo level (run via execute_script with the level already open and the editor unattended). |
| pie_position_log.py | Starts PIE and logs the player's position, camera yaw, combat state and stamina every 0.4 s for DURATION seconds. |
| pie_posture_hits.py | Gate 3, M9: the boss's posture is a pool of its own, drained by the weapon attack table's value of every real hit; the pack's poise stays full; a pool at zero starts the stance break. |
| pie_posture_regen.py | Freeze S03/S04: boss posture regeneration. Drains posture to 40, samples it for 16 s; a second drain at 3 s must restart the delay. Expected: no gain for 6 s after the LAST drain, then 13 per second. |
| pie_real_kill.py | Gate 2 death priority (Freeze 18.2, L08): the boss is killed by a REAL player hit while its stand-in A2 attack is running (windup, hit due at 2.0 s). Checks: the boss dies, the attack instance ends in the tracker, |
| pie_remains.py | Death-remains driver: kill through debug_kill_boss (health 0 and the pack's Ability.Dead, the path pie_boss_death uses; a single injected light attack is not reliable here: the boss has to be fully awake first), wait for the pack to destroy the boss, verify the statue forms, then retry. Log prefix [Remains]. |
| pie_remains_look.py | Look test of the death remains in place (log prefix [RemainsPlace]): kills the boss like pie_remains.py, shoots the dead boss 1.5 s after the death (the pose to match), then the statue once formed, from the same camera spot. Screenshots land in Saved/Screenshots/WindowsEditor. |
| pie_remains_material.py | Look test of M_Boss01_Remains (log prefix [RemainsLook]): in PIE gives the corpse statue actor RemainsLook the three slot MIDs, and takes a shot at Dissolve 0.35, 0.6 and 1.0. Needs the scratch actor RemainsLook (Scripts/Editor/place_remains_look.py places it, remove_remains_look.py removes it). |
| pie_riposte.py | Gate 2 riposte checks (Freeze S08 to S10, 17.4) with the pack's real Light Attack input on the frozen boss: |
| pie_riposte_exec.py | Synchronized riposte (Freeze 17.4, G2-7): an accepted Light Attack press on the downed boss plays the paired clips (AN_Riposte_Player_Front on the player, AN_Riposte_Boss_Reaction on the boss) with one critical hit at the impact. |
| pie_riposte_lethal.py | A lethal synchronized riposte (Freeze 17.4 and 18.2): the boss is set to 3 percent of its runtime maximum health, the riposte impact (100) takes it to zero and the pack's death must start: Status.Dead / the boss destroyed by the pack, one impact, no second damage. |
| pie_scratch_route_a.py | Scratch route (a) PIE proof (owner approval G-3, 2026-10-26). Spawns a SECOND boss inside PIE whose EnemyInfoRef names the scratch info |
| pie_selector_viewport.py | DD-1 step 1 condition 3 (measurement driver, Codex lead work order 02, C-L2 part 2): records what the build selector does in the REAL PIE viewport. |
| pie_sevarog_pack.py | PIE check of Sevarog on the pack framework: spawns BP_SevarogBossPack in the pack demo level in front of the Greystone player and logs |
| pie_shrine_look.py | Shoots the Shiva shrine in PIE from three pawn positions (log prefix [ShrineLook]): from the player start, from 600 cm and from 350 cm in front of the face. The pawn is hidden (the third-person camera sits behind it). Screenshots land in Saved/Screenshots/WindowsEditor. |
| pie_soak.py | Gate 4 G4-4: deterministic 30-encounter soak. |
| pie_stamina_cost.py | Gate 3, M10: every swing of the player costs what the weapon attack table's row says, on top of or instead of the pack's own 15 (URPGSwingTracker). Real presses against the held boss (the player stands 110 cm in front of it): |
| pie_stamina_trace.py | Probe (log prefix [StaminaTrace]): samples the player's stamina every frame around one swing, with and without a cost override, to see when the pack's own cost and the swing tracker's extra land. |
| pie_state.py | Logs whether PIE is running and the boss HUD state. Log prefix [PieState]. |
| pie_stop.py | No module docstring; inspect the script body before running. |
| pie_telegraph.py | Q13: close-stage telegraph coverage (rpg.CloseTelegraph, default 0.4 since 2026-10-24). Logs [Telegraph] and restores the value the session had at the start. |
| pie_trace_audit.py | Gate 1 / M1 (SPEC_M1_trace.md): the pack's weapon trace on the boss's close attacks, measured with URPGTraceAudit (an observer) and kept in order by URPGTraceGuard (Freeze 12, 13; tests H01 to H11). |
| pie_transition_rules.py | Gate 2 / M4 (SPEC_M4_transition.md): stance break versus phase transition and the boss's own moves. The boss is frozen awake (hold_for_test) and every scenario starts from fresh() (reset, wake, hold). |
| pie_ui_check.py | PIE UI check: enters the boss fight, logs READY_HUD (capture the viewport then), opens the pause menu, logs |
| pie_vfx_gallery.py | PIE gallery: spawns each candidate Niagara system a few metres in front of the player (arena start, boss idle) and |
| pie_victory_lock.py | Gate 2 / L11: after the victory no combat action can run and a retry is offered. V0 control: a Light Attack press plays a player montage; V1 the boss dies, victory fires once and the player is locked; |
| pie_weapons_smoke.py | Play-in-editor smoke test for M5 weapons: walks the player into the boss fight, then for each of the player's |
| place_gate_frame.py | Imports Antigravity's M-08 fog gate frame (SM_Boss01_FogGateFrame) into /Game/OneBossFight/Environment/Gate, gives its three slots the arena's own materials and places it around the FogGate actor (log prefix [GateFrame]). |
| place_remains_look.py | Places the scratch actor RemainsLook (corpse statue, scale 1.5) at (-1200, -900, 0) for pie_remains_material.py (log prefix [RemainsLook]). Remove it again with remove_remains_look.py before anything is saved. |
| place_shiva_shrine.py | Places the Lord Shiva shrine (/Game/OneBossFight/Environment/Shrine/SM_Boss01_ShivaShrine) in L_SevarogArena behind the player start, turned to face it, with a box collision (log prefix [ShrinePlace]). Idempotent: an earlier actor labelled ShivaShrine is replaced. The mesh's face points to -Y in the engine (the exporter mirrors Y; AG's sockets read y -120 for the front), so the actor yaw is the direction to the spawn plus 90. Does not save the level: look first (Scripts/Editor/save_gate_frame.py style save, or save_shrine.py). |
| poise_data.py | Adds the Poise attribute to every PlayerInfo and EnemyInfo data asset of the Advanced ARPG pack: a Default Attributes entry |
| polish_arena_stills.py | No module docstring; inspect the script body before running. |
| probe_api.py | No module docstring; inspect the script body before running. |
| probe_body_mats.py | Prints the material slots of SK_Boss01_Body and the textures each referenced material uses (log prefix [BodyMats]); reports missing files. |
| probe_bs.py | No module docstring; inspect the script body before running. |
| probe_death_pose.py | Measures the last frame of the boss death clip in component space (log prefix [DeathPose]): head, pelvis, feet, hands, sword tip, overall bounds. Read-only. Compare with the corpse statue (SM_Boss01_CorpseStatue, bounds min -55 -190 -2, max 64 32 101). |
| probe_fbx_import.py | No module docstring; inspect the script body before running. |
| probe_gate_area.py | Lists the level actors near the fog gate with their bounds (log prefix [GateArea]): read-only, to place the M-08 frame. |
| probe_grey_slots.py | No module docstring; inspect the script body before running. |
| probe_grey_sockets.py | No module docstring; inspect the script body before running. |
| probe_mat_params.py | Prints the parameters of a few materials (log prefix [MatProbe]), read-only. |
| probe_montage_segments.py | No module docstring; inspect the script body before running. |
| probe_pawn_info.py | No module docstring; inspect the script body before running. |
| probe_player_comps.py | No module docstring; inspect the script body before running. |
| probe_skel.py | No module docstring; inspect the script body before running. |
| probe_skel_api.py | No module docstring; inspect the script body before running. |
| probe_statue_regions.py | Prints, for the corpse statue mesh as the engine holds it (log prefix [StatueRegions]), the centroid and extent of its vertices in height bands, per material slot: to compare with the DeathLegend final pose (head (0, 52, 76), pelvis (0, 1, 48), hands (47,-9,79) and (-55,11,55), feet (30,-38,14) and (-33,13,4)) without pixels. |
| probe_struct.py | No module docstring; inspect the script body before running. |
| probe_vars.py | No module docstring; inspect the script body before running. |
| props.py | Lists python attribute names of a class matching a substring (CLASS and PATTERN below). Log prefix [Props]. |
| read_item_sockets.py | No module docstring; inspect the script body before running. |
| read_player_info.py | No module docstring; inspect the script body before running. |
| remove_remains_look.py | Removes the scratch actor RemainsLook (log prefix [RemainsLook]). |
| repoint_player_refs.py | Stage 3: points the player-side abilities and combat styles at the Greystone retargets. For each referencing Blueprint (CDO) or |
| reset_component_materials.py | No module docstring; inspect the script body before running. |
| resolve_retarget_map.py | Matches duplicates that the batch renamed (name_Grey1, _Grey2) to their source assets by class and play length, then moves them |
| retarget_pack_to_greystone.py | Stage 3 (option A): retargets the Advanced ARPG pack's player animation set from its UE5 combat mannequin to Greystone. |
| review_report10.py | Review of Antigravity's Report 10 inside the engine (log prefix [Review10]): imports the delivered files into the scratch folder /Game/OneBossFight/_Review10 (nothing that exists is touched or deleted), then prints |
| review_report11.py | Review of Antigravity's Report 11 inside the engine (log prefix [Review11]): imports the delivered clips and the sword and javelin into the scratch folder /Game/OneBossFight/_Review11 |
| review_report11b.py | Second part of the Report 11 engine review (log prefix [Review11b]); needs the scratch clips of review_report11.py in /Game/OneBossFight/_Review11. |
| review_report11c.py | Third part of the Report 11 engine review (log prefix [Review11c]): where the knees, ankles and toes of the kneeling poses are (component space, floor at z = 0), and the torso's lean (head minus pelvis) in the clips that should recoil or slump. |
| review_report12.py | Review of Antigravity's Report 12 inside the engine (log prefix [Review12]): imports the delivered clips into the scratch folder /Game/OneBossFight/_Review12 (nothing that exists is touched or deleted) and checks, from the |
| review_report12b.py | Second part of the Report 12 engine review (log prefix [Review12b]); needs the scratch clips of review_report12.py in /Game/OneBossFight/_Review12. |
| review_report12c.py | Third part of the Report 12 engine review (log prefix [Review12c]): how the boss's sword sits in the hand in the engine, and what that does to the dormant and wake poses. |
| review_report13.py | Engine review of Antigravity's Brief 13/14 deliveries (log prefix [Review13]): imports the clips into the scratch folder /Game/OneBossFight/_Review13 (nothing that exists is touched) and prints, from the engine's own animation data in component space (floor z = 0, |
| review_report13b.py | Second part of the engine review of Antigravity's deliveries (log prefix [Review13b]): the boss's in-game scale, the path of the sword tip through the active window of the close clips and the A2 slam (does the blade reach the height of a 190 cm player or the floor?) and the foot heights of the accepted combat idle for comparison. |
| review_report13c.py | Third part of the engine review of Antigravity's deliveries (log prefix [Review13c]): imports the fog gate frame and the statue (static meshes) into the scratch folder /Game/OneBossFight/_Review13 and prints bounds, triangles, material slots and sockets as the engine reads them. |
| rpg_content_lib.py | Shared helpers for the editor content scripts (used by setup_m5_content.py). |
| sample_deps.py | Runs inside the DarkRuinsMegascansSample project (commandlet: UnrealEditor-Cmd <sample uproject> -run=pythonscript -script=<this file>). |
| save_gate_frame.py | Saves the M-08 gate frame work (log prefix [GateFrame]): the mesh, the rune material and the level. Nothing else. |
| save_shrine.py | Saves the Shiva shrine mesh and the level (log prefix [ShrineSave]). |
| set_health_multiplier.py | Writes the health damage multiplier (KI-097) of the starter sword into the weapon attack table asset /Game/OneBossFight/Data/DA_WeaponAttacks (log prefix [HealthMultiplier]). Run in the open editor, no PIE. |
| set_riposte_root_motion.py | Switches root motion on for the player's riposte clip AN_Riposte_Player_Front (log prefix [RootMotion]): the clip travels the player 90 cm along the facing (0 to 0.7 s, then holds), and the |
| set_view.py | Moves the editor viewport camera to the pose in Saved/view.txt ("x y z pitch yaw", cm and degrees; default: the player start looking at the arena centre). |
| set_weapon_windows.py | Writes the hyperarmor windows of the Strength build (M13/M14) into the weapon attack table asset /Game/OneBossFight/Data/DA_WeaponAttacks (log prefix [WeaponWindows]). Run in the open editor, no PIE. |
| setup_grey_player.py | Gives BP_GreystonePlayer Greystone's mesh and the retargeted pack animation Blueprint. Run in the editor. |
| setup_input_fix.py | Rebuilds the movement and look mappings in IMC_Default with real modifiers, and adds block/parry input. |
| setup_m1_content.py | M1 content setup for One Boss Fight. Idempotent: safe to re-run. |
| setup_m3_content.py | M3 content setup for One Boss Fight. Idempotent: safe to re-run. |
| setup_m4_content.py | M4 content setup for One Boss Fight (boss and encounter). Idempotent: safe to re-run. |
| setup_m4_statetree.py | Builds the boss StateTree asset and assigns it to BP_SevarogBoss. Idempotent. |
| setup_m5_content.py | M5 content setup (weapons, audio, effects, presentation data). Idempotent: safe to re-run. |
| setup_m6_content.py | M6 content setup: puts a benchmark runner into L_Greybox so the real boss fight can be benchmarked |
| setup_m7_arena.py | M7 arena art pass: configures authentic Deadly Ruins modular meshes and PBR materials |
| setup_m7_beam_materials.py | The Niagara Energy Beam Pack as downloaded lacks four materials that NS_Thunder_Beam7 references |
| setup_m7_content.py | M7: wires the imported audio, Niagara effects and roll animations into the existing data assets and blueprints. |
| setup_m7_roll.py | Retargets the Mage pack roll animations (UE4 mannequin skeleton) onto Greystone and builds the dodge montages. |
| sevarog_pack_01_proxy.py | Sevarog on the pack, step 1: SM_SevarogScytheProxy, a copy of the pack boss's weapon static mesh whose sockets (trace points) lie along |
| sevarog_pack_02_montages_abilities.py | Sevarog on the pack, step 2: pack-format attack montages and the boss ability copies. Run in the open editor, after step 1. |
| sevarog_pack_02b_toggle_only.py | No module docstring; inspect the script body before running. |
| sevarog_pack_03_info_style_pawn.py | Sevarog on the pack, step 3: pawn Blueprint (child copy of the pack great-sword boss), combat style (his ability copies), enemy info. |
| sevarog_pack_03b_soft_refs.py | Sevarog on the pack, step 3b: the two soft references (info -> pawn class, pawn -> info). Python needs the object itself, not a path. |
| sevarog_pack_04_level.py | Sevarog on the pack, step 4: L_SevarogPack, a copy of the art arena level (L_Greybox) for the pack framework. |
| sevarog_pack_05_parity.py | Sevarog on the pack, step 5: the features the C++ boss had that step 2-4 left out. Run in the open editor after steps 1-4. |
| sevarog_pack_05b_death_style.py | Sevarog on the pack, step 5b: GA_Sev_Death and the combat style entries (step 5 stopped before them: deleting assets that other assets reference makes the |
| sevarog_pack_06_director.py | Sevarog on the pack, step 6: adds URPGSevarogDirector to BP_SevarogBossPack (needs the C++ built) and keeps AutoPossessAI on (the director holds the behaviour until the player is near). Idempotent (does nothing if the component is already there). |
| sevarog_pack_07_bolt_impact.py | Sevarog on the pack, step 7: Lightning impact. SevBoltAttackData (copy of the fireball attack data) with generic magic damage instead of fire and a |
| sevarog_pack_08_turn.py | Sevarog on the pack, step 8: turn in place. The pack's behaviour tree calls GA_*_TurnInPlace when the target is outside the front cone; without it the boss |
| sevarog_pack_09_charge.py | Sevarog on the pack, step 9 (KI-047): the mid-range attack closes the distance. AM_SevPack_Charge is the Overhead swing with URPGANS_ChargeToTarget over its wind-up |
| sevarog_pack_10_combo_telegraph.py | Sevarog on the pack, step 10: the triple combo and the Shockwave telegraph. |
| stop_pie.py | Ends a running PIE session (no log). |
| survey_all_pillars.py | No module docstring; inspect the script body before running. |
| survey_all_walls.py | No module docstring; inspect the script body before running. |
| survey_deadly_ruins.py | No module docstring; inspect the script body before running. |
| survey_pack_anims.py | Survey of animation assets in the pack: class, skeleton, folder. Run in the editor (execute_script). Writes Saved/pack_anim_survey.json. |
| test_death_ue.py | No module docstring; inspect the script body before running. |
| test_dormant_sword.py | No module docstring; inspect the script body before running. |
| test_import_skm.py | No module docstring; inspect the script body before running. |
| toggle_post.py | Debug: enables or disables an actor class by label. Edit LABEL/ENABLED. Log prefix [Toggle]. |
| tune_arena_visuals.py | No module docstring; inspect the script body before running. |
| tune_floor.py | Tunes MI_Arena_RomanFloor (wetness off, rougher, darker) and reports the switch states. Log prefix [Floor]. |
| update_arena_v2.py | No module docstring; inspect the script body before running. |
| verify_arena_meshes.py | No module docstring; inspect the script body before running. |
| verify_builds.py | verify_builds.py - Verifies all 6 character builds in Unreal Engine. |
| wake_clip_off.py | Switches the authored wake clip off for this editor session: rpg.WakeClip 0 (log prefix [WakeClip]). The console variable is process wide, so it survives PIE sessions; the older drivers call Wake() and attack at once, which the 3.5 s wake gate (B11) would veto. Scripts/RunDrivers.ps1 runs this before every run; pie_dormant_wake.py sets rpg.WakeClip 1 itself and back to 0 when it ends. Run with Scripts/run_in_editor.py. |
