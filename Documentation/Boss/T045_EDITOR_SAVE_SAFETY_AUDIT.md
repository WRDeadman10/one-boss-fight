# T045 — Editor content first-save and collision-guard audit

Static source inventory only. A listed assertion/guard marker may not validate every field or destination; review call context. Wrapper-driven saves and dynamic helper calls may not appear as literal save sites.

Writer scripts: 140; explicit save found: 79; no explicit save: 61; at least one guard marker before first save: 33.

| Script | T043 category | First explicit save | Earlier assertions/requirements | Earlier collision/refusal guard markers |
|---|---|---|---|---|
| `Scripts/Editor/air_jump_tuning.py` | modifies | save_loaded_asset:15 | none detected | none detected |
| `Scripts/Editor/air_light_attacks.py` | modifies | save_loaded_asset:23 | none detected | none detected |
| `Scripts/Editor/apply_arena_art_fix.py` | map_setup | save_dirty_packages:47 | none detected | none detected |
| `Scripts/Editor/apply_g044_d5_legacy_defaults.py` | modifies | save_loaded_asset:257 | 60,62,80,102,114,139,141,168,175,180,183,195,202,203,206,210,214,217,218,220,222,224,227,228,234,237,239,250,256 | 90,202 |
| `Scripts/Editor/apply_perfect_arena.py` | map_setup | save_loaded_asset:30 | none detected | none detected |
| `Scripts/Editor/arena_use_pack_boss.py` | map_setup | save_map:28 | 13 | none detected |
| `Scripts/Editor/atmosphere.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/boss_poise_armor.py` | modifies | save_loaded_asset:19 | none detected | none detected |
| `Scripts/Editor/boss_pose.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/boss_pose_reset.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/build_asset_proof_map.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/build_boss01_materials.py` | creates | save_loaded_asset:50 | none detected | none detected |
| `Scripts/Editor/candidates_clear.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/check_active_world.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/check_floor.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/cleanup_review11.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/cleanup_review12.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/cleanup_review13.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/copy_sockets_to_greystone.py` | modifies | save_loaded_asset:12 | none detected | none detected |
| `Scripts/Editor/create_g044_encounter_definition.py` | creates | save_loaded_asset:140 | 29,31,61,62,63,64,65,74,77,80,83,89,93,96,98,100,101,102,103,105,109,113,119,130,131,132,133,134,135,136,137,138 | 1,88,89,90,98 |
| `Scripts/Editor/create_g044_typed_definitions.py` | creates | save_loaded_asset:275 | 33,35,51,53,55,63,65,71,72,77,78,85,86,89,92,96,100,105,106,108,111,112,120,123,125,129,131,135,137,139,141,148,150,154,157,159,160,166,169,172,173,175,176,178,179,183,190,192,202,268,271 | 3,63,169,170 |
| `Scripts/Editor/debug_atmos.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/dress_arena.py` | map_setup | save_loaded_asset:99 | 38 | 90 |
| `Scripts/Editor/dump_level.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/export_greystone.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/export_mannequin.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/export_quinn.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/finish_statue_import.py` | map_setup | save_asset:11 | none detected | none detected |
| `Scripts/Editor/fix_grey_blendspaces.py` | modifies | save_loaded_asset:41 | none detected | none detected |
| `Scripts/Editor/fix_grey_default_layer.py` | modifies | save_dirty_packages:14 | none detected | none detected |
| `Scripts/Editor/fix_grey_layers_1.py` | creates | save_loaded_asset:8 | none detected | none detected |
| `Scripts/Editor/fix_grey_layers_2.py` | modifies | save_loaded_asset:17 | none detected | none detected |
| `Scripts/Editor/fix_roll_root_motion.py` | modifies | save_loaded_asset:58 | none detected | none detected |
| `Scripts/Editor/fix_sev_montage_refs.py` | modifies | save_loaded_asset:20 | none detected | none detected |
| `Scripts/Editor/fx_test.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/gate_material_set.py` | modifies | save_loaded_asset:10 | none detected | 6 |
| `Scripts/Editor/greystone_sevarog_11_polish.py` | modifies | save_loaded_asset:34 | none detected | none detected |
| `Scripts/Editor/hide_comp.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/hide_grey_builtin_weapons.py` | creates | save_loaded_asset:17 | none detected | none detected |
| `Scripts/Editor/import_all_builds.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/import_arena_meshes.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/import_audio.py` | modifies | save_loaded_asset:60 | none detected | 39 |
| `Scripts/Editor/import_boss01.py` | modifies | save_loaded_asset:75 | none detected | 58 |
| `Scripts/Editor/import_boss01_clips_r12.py` | modifies | save_loaded_asset:66 | none detected | 2,46 |
| `Scripts/Editor/import_boss01_clips_r14.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/import_corpse_statue.py` | modifies | save_asset:31 | none detected | none detected |
| `Scripts/Editor/import_shiva_shrine.py` | modifies | save_asset:42 | none detected | none detected |
| `Scripts/Editor/import_ui_art.py` | modifies | save_asset:24 | none detected | none detected |
| `Scripts/Editor/inspect_all_instances.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/inspect_arena.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/inspect_arena_actor.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/inspect_arena_floormesh.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/inspect_arena_floormesh2.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/make_abi_test_catalog.py` | creates | save_loaded_asset:38 | 32,35 | 4,26,31 |
| `Scripts/Editor/make_close_montages.py` | creates | save_loaded_asset:79 | none detected | 38 |
| `Scripts/Editor/make_combat_catalog.py` | creates | save_loaded_asset:29 | 21,26 | 18 |
| `Scripts/Editor/make_death_montage.py` | creates | save_loaded_asset:26 | none detected | 9,11 |
| `Scripts/Editor/make_flipbook_materials.py` | creates | save_asset:114 | none detected | 34,89 |
| `Scripts/Editor/make_gate_rune_material.py` | creates | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/make_polish_materials.py` | creates | save_loaded_asset:61 | none detected | 19 |
| `Scripts/Editor/make_remains_material.py` | creates | save_asset:125 | none detected | 39 |
| `Scripts/Editor/make_scratch_route_a.py` | creates | save_loaded_asset:53 | 25,34,37,50 | 17,24,25,27 |
| `Scripts/Editor/make_typed_abi_fixtures.py` | creates | save_asset:75 | 44,50,58,61,73 | 33,43 |
| `Scripts/Editor/make_typed_abi_uncooked_item.py` | creates | save_asset:15 | 11,13 | 2,10,12 |
| `Scripts/Editor/make_weapon_table.py` | creates | save_loaded_asset:21 | none detected | 12 |
| `Scripts/Editor/mesh_test.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/move_grey_abps.py` | modifies | save_dirty_packages:26 | none detected | 17 |
| `Scripts/Editor/no_throttle.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/pie_a2_diag.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/pie_a5_heal_punish.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/pie_death_probe.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/pie_grey_weapons.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/pie_iframes.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/pie_pack_demo.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/pie_poise_scale.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/pie_selection_refusal.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/pie_sevarog_pack.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/pie_trace_audit.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/pie_transition_rules.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/pie_weapons_smoke.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/place_gate_frame.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/place_remains_look.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/place_shiva_shrine.py` | map_setup | save_asset:15 | none detected | none detected |
| `Scripts/Editor/poise_data.py` | modifies | save_loaded_asset:53 | none detected | none detected |
| `Scripts/Editor/polish_arena_stills.py` | modifies | save_loaded_asset:12 | none detected | none detected |
| `Scripts/Editor/probe_death_pose.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/probe_gate_area.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/remove_remains_look.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/repoint_player_refs.py` | modifies | save_loaded_asset:94 | none detected | none detected |
| `Scripts/Editor/reset_component_materials.py` | map_setup | save_dirty_packages:31 | none detected | none detected |
| `Scripts/Editor/resolve_retarget_map.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/retarget_pack_to_greystone.py` | creates | save_loaded_asset:52 | 37 | 45 |
| `Scripts/Editor/review_report10.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/review_report11.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/review_report11b.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/review_report11c.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/review_report12.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/review_report12b.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/review_report12c.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/review_report13.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/review_report13b.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/review_report13c.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/rpg_content_lib.py` | creates | save_loaded_asset:91 | 20 | 25 |
| `Scripts/Editor/save_gate_frame.py` | modifies | save_asset:6 | none detected | none detected |
| `Scripts/Editor/save_shrine.py` | modifies | save_asset:5 | none detected | none detected |
| `Scripts/Editor/set_health_multiplier.py` | modifies | save_loaded_asset:33 | none detected | none detected |
| `Scripts/Editor/set_riposte_root_motion.py` | modifies | save_loaded_asset:14 | none detected | none detected |
| `Scripts/Editor/set_weapon_windows.py` | modifies | save_loaded_asset:49 | none detected | none detected |
| `Scripts/Editor/setup_grey_player.py` | modifies | save_loaded_asset:16 | none detected | none detected |
| `Scripts/Editor/setup_input_fix.py` | creates | save_loaded_asset:53 | none detected | 47 |
| `Scripts/Editor/setup_m1_content.py` | map_setup | save_loaded_asset:73 | 36 | none detected |
| `Scripts/Editor/setup_m3_content.py` | map_setup | save_loaded_asset:115 | 73,89 | 94,110 |
| `Scripts/Editor/setup_m4_content.py` | map_setup | save_loaded_asset:195 | 85,95 | 99 |
| `Scripts/Editor/setup_m4_statetree.py` | modifies | save_loaded_asset:22 | 21 | none detected |
| `Scripts/Editor/setup_m5_content.py` | creates | save_loaded_asset:92 | 65 | 86 |
| `Scripts/Editor/setup_m6_content.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/setup_m7_arena.py` | map_setup | save_loaded_asset:59 | none detected | 38 |
| `Scripts/Editor/setup_m7_beam_materials.py` | creates | save_loaded_asset:41 | none detected | 28 |
| `Scripts/Editor/setup_m7_content.py` | modifies | save_loaded_asset:45 | 36 | none detected |
| `Scripts/Editor/setup_m7_roll.py` | modifies | save_loaded_asset:51 | none detected | none detected |
| `Scripts/Editor/sevarog_pack_01_proxy.py` | creates | save_loaded_asset:61 | none detected | 15 |
| `Scripts/Editor/sevarog_pack_02_montages_abilities.py` | creates | save_loaded_asset:131 | 40,50,90 | 103 |
| `Scripts/Editor/sevarog_pack_03_info_style_pawn.py` | creates | save_loaded_asset:44 | 25 | 21 |
| `Scripts/Editor/sevarog_pack_03b_soft_refs.py` | modifies | save_loaded_asset:13 | none detected | none detected |
| `Scripts/Editor/sevarog_pack_04_level.py` | map_setup | save_map:44 | 19 | none detected |
| `Scripts/Editor/sevarog_pack_05_parity.py` | creates | save_loaded_asset:75 | 36 | none detected |
| `Scripts/Editor/sevarog_pack_05b_death_style.py` | creates | save_loaded_asset:56 | 2,30 | none detected |
| `Scripts/Editor/sevarog_pack_06_director.py` | modifies | save_loaded_asset:29 | none detected | none detected |
| `Scripts/Editor/sevarog_pack_07_bolt_impact.py` | creates | save_loaded_asset:30 | none detected | none detected |
| `Scripts/Editor/sevarog_pack_08_turn.py` | creates | save_loaded_asset:25 | none detected | none detected |
| `Scripts/Editor/sevarog_pack_09_charge.py` | map_setup | save_loaded_asset:36 | none detected | none detected |
| `Scripts/Editor/sevarog_pack_10_combo_telegraph.py` | modifies | save_loaded_asset:38 | none detected | none detected |
| `Scripts/Editor/test_death_ue.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/test_dormant_sword.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/test_import_skm.py` | modifies | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/toggle_post.py` | map_setup | NO EXPLICIT SAVE | — | — |
| `Scripts/Editor/tune_arena_visuals.py` | map_setup | save_loaded_asset:19 | none detected | none detected |
| `Scripts/Editor/tune_floor.py` | modifies | save_loaded_asset:23 | none detected | none detected |
| `Scripts/Editor/update_arena_v2.py` | map_setup | save_loaded_asset:39 | none detected | 13 |
| `Scripts/Editor/update_g044_boss_health_and_manifest.py` | modifies | save_loaded_asset:203 | 39,41,57,80,98,101,103,104,141,152,153,156,160,164,166,169,170,172,174,176,180,181,182,183,192,199,201 | 69,152 |
