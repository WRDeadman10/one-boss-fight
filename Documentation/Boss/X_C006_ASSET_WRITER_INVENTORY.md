# T043 — Editor asset writer inventory

Source-only heuristic inventory of `Scripts/Editor/**/*.py`. Categories come from literal API/map markers; scripts were not executed. Review the source before relying on a row, especially dynamic helper calls.

Scripts scanned: 361. Counts: creates 30, modifies 69, map_setup 42, read-only 220

| Script | Primary classification | Source markers |
|---|---|---|
| `Scripts/Editor/air_jump_tuning.py` | modifies | `save_loaded_asset, set_editor_property` |
| `Scripts/Editor/air_light_attacks.py` | modifies | `save_loaded_asset, set_editor_property` |
| `Scripts/Editor/anim_probe.py` | read-only | `—` |
| `Scripts/Editor/apply_arena_art_fix.py` | map_setup | `—` |
| `Scripts/Editor/apply_g044_d5_legacy_defaults.py` | modifies | `save_loaded_asset, set_editor_property` |
| `Scripts/Editor/apply_perfect_arena.py` | map_setup | `—` |
| `Scripts/Editor/arena_use_pack_boss.py` | map_setup | `, save_map` |
| `Scripts/Editor/atmosphere.py` | map_setup | `—` |
| `Scripts/Editor/body_slots_probe.py` | read-only | `—` |
| `Scripts/Editor/boss01_bounds.py` | read-only | `—` |
| `Scripts/Editor/boss_poise_armor.py` | modifies | `save_loaded_asset, set_editor_property` |
| `Scripts/Editor/boss_pose.py` | map_setup | `—` |
| `Scripts/Editor/boss_pose_reset.py` | map_setup | `—` |
| `Scripts/Editor/build_asset_proof_map.py` | map_setup | `new_level` |
| `Scripts/Editor/build_boss01_materials.py` | creates | `create_asset` |
| `Scripts/Editor/build_off.py` | read-only | `—` |
| `Scripts/Editor/candidates_clear.py` | map_setup | `—` |
| `Scripts/Editor/candidates_spawn.py` | read-only | `—` |
| `Scripts/Editor/check_active_world.py` | map_setup | `—` |
| `Scripts/Editor/check_floor.py` | map_setup | `—` |
| `Scripts/Editor/check_grey_layers.py` | read-only | `—` |
| `Scripts/Editor/check_sev_abilities.py` | read-only | `—` |
| `Scripts/Editor/check_worldblend.py` | read-only | `—` |
| `Scripts/Editor/cleanup_review11.py` | modifies | `delete_asset` |
| `Scripts/Editor/cleanup_review12.py` | modifies | `delete_asset` |
| `Scripts/Editor/cleanup_review13.py` | modifies | `delete_asset` |
| `Scripts/Editor/compare_skeletons.py` | read-only | `—` |
| `Scripts/Editor/copy_sockets_to_greystone.py` | modifies | `save_loaded_asset` |
| `Scripts/Editor/create_g044_encounter_definition.py` | creates | `create_asset` |
| `Scripts/Editor/create_g044_typed_definitions.py` | creates | `create_asset` |
| `Scripts/Editor/create_tier1_art_assets.py` | creates | `duplicate_asset` |
| `Scripts/Editor/debug_atmos.py` | map_setup | `—` |
| `Scripts/Editor/dress_arena.py` | map_setup | `—` |
| `Scripts/Editor/dump_close_attack.py` | read-only | `—` |
| `Scripts/Editor/dump_level.py` | map_setup | `—` |
| `Scripts/Editor/dump_pack_typed_edges.py` | read-only | `—` |
| `Scripts/Editor/export_assets_text.py` | read-only | `—` |
| `Scripts/Editor/export_encounter_definition_sources.py` | read-only | `—` |
| `Scripts/Editor/export_greystone.py` | modifies | `set_editor_property` |
| `Scripts/Editor/export_mannequin.py` | modifies | `set_editor_property` |
| `Scripts/Editor/export_paragon_skins.py` | read-only | `—` |
| `Scripts/Editor/export_quinn.py` | modifies | `set_editor_property` |
| `Scripts/Editor/export_reference.py` | read-only | `—` |
| `Scripts/Editor/export_reference2.py` | read-only | `—` |
| `Scripts/Editor/export_reference3.py` | read-only | `—` |
| `Scripts/Editor/finish_statue_import.py` | map_setup | `—` |
| `Scripts/Editor/fix_grey_blendspaces.py` | modifies | `save_loaded_asset, set_editor_property` |
| `Scripts/Editor/fix_grey_default_layer.py` | modifies | `save_dirty_packages` |
| `Scripts/Editor/fix_grey_layers_1.py` | creates | `duplicate_asset` |
| `Scripts/Editor/fix_grey_layers_2.py` | modifies | `delete_asset, save_loaded_asset` |
| `Scripts/Editor/fix_roll_root_motion.py` | modifies | `save_loaded_asset, set_editor_property` |
| `Scripts/Editor/fix_sev_montage_refs.py` | modifies | `save_loaded_asset, set_editor_property` |
| `Scripts/Editor/fx_test.py` | map_setup | `—` |
| `Scripts/Editor/g0_pack_boss.py` | read-only | `—` |
| `Scripts/Editor/g0_probe_api.py` | read-only | `—` |
| `Scripts/Editor/g0_weapon.py` | read-only | `—` |
| `Scripts/Editor/g1_boss_abilities.py` | read-only | `—` |
| `Scripts/Editor/g1_sevarog_slots.py` | read-only | `—` |
| `Scripts/Editor/g2_probe_a4a5.py` | read-only | `—` |
| `Scripts/Editor/g3_dump_attack_data.py` | read-only | `—` |
| `Scripts/Editor/g3_list_weapon_assets.py` | read-only | `—` |
| `Scripts/Editor/g3_probe_build_hits.py` | read-only | `—` |
| `Scripts/Editor/g3_probe_equip.py` | read-only | `—` |
| `Scripts/Editor/g3_probe_montages.py` | read-only | `—` |
| `Scripts/Editor/gate_material_probe.py` | read-only | `—` |
| `Scripts/Editor/gate_material_set.py` | modifies | `save_loaded_asset` |
| `Scripts/Editor/greystone_sevarog_11_polish.py` | modifies | `save_loaded_asset, set_editor_property` |
| `Scripts/Editor/handle_pie.py` | read-only | `—` |
| `Scripts/Editor/hide_comp.py` | map_setup | `—` |
| `Scripts/Editor/hide_grey_builtin_weapons.py` | creates | `create_asset` |
| `Scripts/Editor/import_all_builds.py` | modifies | `set_editor_property` |
| `Scripts/Editor/import_arena_meshes.py` | modifies | `set_editor_property` |
| `Scripts/Editor/import_audio.py` | modifies | `save_loaded_asset, set_editor_property` |
| `Scripts/Editor/import_boss01.py` | modifies | `delete_asset, save_loaded_asset, set_editor_property` |
| `Scripts/Editor/import_boss01_clips_r12.py` | modifies | `save_loaded_asset, set_editor_property` |
| `Scripts/Editor/import_boss01_clips_r14.py` | modifies | `set_editor_property` |
| `Scripts/Editor/import_corpse_statue.py` | modifies | `save_asset, set_editor_property, set_material` |
| `Scripts/Editor/import_shiva_shrine.py` | modifies | `save_asset, set_editor_property, set_material` |
| `Scripts/Editor/import_ui_art.py` | modifies | `save_asset, set_editor_property` |
| `Scripts/Editor/inspect_actions.py` | read-only | `—` |
| `Scripts/Editor/inspect_all_instances.py` | map_setup | `—` |
| `Scripts/Editor/inspect_all_pillar_mats.py` | read-only | `—` |
| `Scripts/Editor/inspect_arena.py` | map_setup | `—` |
| `Scripts/Editor/inspect_arena_actor.py` | map_setup | `—` |
| `Scripts/Editor/inspect_arena_floor_actual.py` | read-only | `—` |
| `Scripts/Editor/inspect_arena_floormesh.py` | map_setup | `—` |
| `Scripts/Editor/inspect_arena_floormesh2.py` | map_setup | `—` |
| `Scripts/Editor/inspect_assets.py` | read-only | `—` |
| `Scripts/Editor/inspect_bolt.py` | read-only | `—` |
| `Scripts/Editor/inspect_boss_components.py` | read-only | `—` |
| `Scripts/Editor/inspect_boss_montages.py` | read-only | `—` |
| `Scripts/Editor/inspect_boss_style.py` | read-only | `—` |
| `Scripts/Editor/inspect_current_arena.py` | read-only | `—` |
| `Scripts/Editor/inspect_dr_materials.py` | read-only | `—` |
| `Scripts/Editor/inspect_fireball.py` | read-only | `—` |
| `Scripts/Editor/inspect_ga_defaults.py` | read-only | `—` |
| `Scripts/Editor/inspect_greystone_animbp.py` | read-only | `—` |
| `Scripts/Editor/inspect_greystone_combat.py` | read-only | `—` |
| `Scripts/Editor/inspect_imc.py` | read-only | `—` |
| `Scripts/Editor/inspect_m7_assets.py` | read-only | `—` |
| `Scripts/Editor/inspect_master_materials.py` | read-only | `—` |
| `Scripts/Editor/inspect_materials.py` | read-only | `—` |
| `Scripts/Editor/inspect_mats.py` | read-only | `—` |
| `Scripts/Editor/inspect_mesh_mats.py` | read-only | `—` |
| `Scripts/Editor/inspect_more_mats.py` | read-only | `—` |
| `Scripts/Editor/inspect_other_pillars.py` | read-only | `—` |
| `Scripts/Editor/inspect_pack_boss.py` | read-only | `—` |
| `Scripts/Editor/inspect_pack_boss2.py` | read-only | `—` |
| `Scripts/Editor/inspect_pack_bp.py` | read-only | `—` |
| `Scripts/Editor/inspect_pack_notifies.py` | read-only | `—` |
| `Scripts/Editor/inspect_pillar_instances.py` | read-only | `—` |
| `Scripts/Editor/inspect_roll_motion.py` | read-only | `—` |
| `Scripts/Editor/inspect_ruins_materials.py` | read-only | `—` |
| `Scripts/Editor/inspect_samurai_mesh.py` | read-only | `—` |
| `Scripts/Editor/inspect_sevarog.py` | read-only | `—` |
| `Scripts/Editor/inspect_target_types.py` | read-only | `—` |
| `Scripts/Editor/inspect_uvs.py` | read-only | `—` |
| `Scripts/Editor/leap_ability_probe.py` | read-only | `—` |
| `Scripts/Editor/legend_off.py` | read-only | `—` |
| `Scripts/Editor/list_floor_textures.py` | read-only | `—` |
| `Scripts/Editor/list_fx_sounds.py` | read-only | `—` |
| `Scripts/Editor/list_grey_sockets.py` | read-only | `—` |
| `Scripts/Editor/list_instances.py` | read-only | `—` |
| `Scripts/Editor/list_ruin_meshes.py` | read-only | `—` |
| `Scripts/Editor/make_abi_test_catalog.py` | creates | `create_asset` |
| `Scripts/Editor/make_close_montages.py` | creates | `create_asset` |
| `Scripts/Editor/make_combat_catalog.py` | creates | `create_asset` |
| `Scripts/Editor/make_death_montage.py` | creates | `create_asset` |
| `Scripts/Editor/make_flipbook_materials.py` | creates | `create_asset` |
| `Scripts/Editor/make_gate_rune_material.py` | creates | `create_asset` |
| `Scripts/Editor/make_polish_materials.py` | creates | `create_asset` |
| `Scripts/Editor/make_remains_material.py` | creates | `create_asset` |
| `Scripts/Editor/make_scratch_route_a.py` | creates | `duplicate_asset` |
| `Scripts/Editor/make_typed_abi_fixtures.py` | creates | `duplicate_asset` |
| `Scripts/Editor/make_typed_abi_uncooked_item.py` | creates | `duplicate_asset` |
| `Scripts/Editor/make_weapon_table.py` | creates | `create_asset` |
| `Scripts/Editor/map_referencers.py` | read-only | `—` |
| `Scripts/Editor/mesh_origins.py` | read-only | `—` |
| `Scripts/Editor/mesh_test.py` | map_setup | `—` |
| `Scripts/Editor/move_grey_abps.py` | modifies | `rename_asset, save_dirty_packages` |
| `Scripts/Editor/no_throttle.py` | modifies | `set_editor_property` |
| `Scripts/Editor/pack_anim_inventory.py` | read-only | `—` |
| `Scripts/Editor/pie_a2_diag.py` | modifies | `set_editor_property` |
| `Scripts/Editor/pie_a2_interrupts.py` | read-only | `—` |
| `Scripts/Editor/pie_a2_scenarios.py` | read-only | `—` |
| `Scripts/Editor/pie_a4_low_sweep.py` | read-only | `—` |
| `Scripts/Editor/pie_a5_heal_punish.py` | modifies | `set_editor_property` |
| `Scripts/Editor/pie_a5_natural.py` | read-only | `—` |
| `Scripts/Editor/pie_abi_fourth_equip.py` | read-only | `—` |
| `Scripts/Editor/pie_air_attack.py` | read-only | `—` |
| `Scripts/Editor/pie_arena_shots.py` | read-only | `—` |
| `Scripts/Editor/pie_attack_rules.py` | read-only | `—` |
| `Scripts/Editor/pie_attr_probe.py` | read-only | `—` |
| `Scripts/Editor/pie_audio.py` | read-only | `—` |
| `Scripts/Editor/pie_authored_close_clips.py` | read-only | `—` |
| `Scripts/Editor/pie_bleed.py` | read-only | `—` |
| `Scripts/Editor/pie_body_look.py` | read-only | `—` |
| `Scripts/Editor/pie_body_look_short.py` | read-only | `—` |
| `Scripts/Editor/pie_boss01_look.py` | read-only | `—` |
| `Scripts/Editor/pie_boss_abilities.py` | read-only | `—` |
| `Scripts/Editor/pie_boss_arm_diag.py` | read-only | `—` |
| `Scripts/Editor/pie_boss_clips.py` | read-only | `—` |
| `Scripts/Editor/pie_boss_death.py` | read-only | `—` |
| `Scripts/Editor/pie_boss_death_states.py` | read-only | `—` |
| `Scripts/Editor/pie_boss_encounter.py` | read-only | `—` |
| `Scripts/Editor/pie_boss_fireball.py` | read-only | `—` |
| `Scripts/Editor/pie_boss_hitreact.py` | read-only | `—` |
| `Scripts/Editor/pie_boss_hud.py` | read-only | `—` |
| `Scripts/Editor/pie_boss_look.py` | read-only | `—` |
| `Scripts/Editor/pie_boss_look_shots.py` | read-only | `—` |
| `Scripts/Editor/pie_boss_materials.py` | read-only | `—` |
| `Scripts/Editor/pie_boss_phase_two.py` | read-only | `—` |
| `Scripts/Editor/pie_boss_smoke.py` | read-only | `—` |
| `Scripts/Editor/pie_boss_stagger.py` | read-only | `—` |
| `Scripts/Editor/pie_boss_stagger_edge.py` | read-only | `—` |
| `Scripts/Editor/pie_build_fight.py` | read-only | `—` |
| `Scripts/Editor/pie_build_hud.py` | read-only | `—` |
| `Scripts/Editor/pie_build_hyperarmor.py` | read-only | `—` |
| `Scripts/Editor/pie_build_select.py` | read-only | `—` |
| `Scripts/Editor/pie_builds.py` | read-only | `—` |
| `Scripts/Editor/pie_cam_probe.py` | read-only | `—` |
| `Scripts/Editor/pie_camera_clip.py` | read-only | `—` |
| `Scripts/Editor/pie_camera_look.py` | read-only | `—` |
| `Scripts/Editor/pie_camera_probe.py` | read-only | `—` |
| `Scripts/Editor/pie_camera_scenarios.py` | read-only | `—` |
| `Scripts/Editor/pie_clip_look.py` | read-only | `—` |
| `Scripts/Editor/pie_clip_look12.py` | read-only | `—` |
| `Scripts/Editor/pie_clip_look13.py` | read-only | `—` |
| `Scripts/Editor/pie_close_attacks.py` | read-only | `—` |
| `Scripts/Editor/pie_close_combo_watch.py` | read-only | `—` |
| `Scripts/Editor/pie_close_reach.py` | read-only | `—` |
| `Scripts/Editor/pie_combat_catalog.py` | read-only | `—` |
| `Scripts/Editor/pie_combat_smoke.py` | read-only | `—` |
| `Scripts/Editor/pie_damage_path.py` | read-only | `—` |
| `Scripts/Editor/pie_death_probe.py` | modifies | `set_editor_property` |
| `Scripts/Editor/pie_debug_overlay.py` | read-only | `—` |
| `Scripts/Editor/pie_determinism.py` | read-only | `—` |
| `Scripts/Editor/pie_dodge.py` | read-only | `—` |
| `Scripts/Editor/pie_dodge_trials.py` | read-only | `—` |
| `Scripts/Editor/pie_dormant_wake.py` | read-only | `—` |
| `Scripts/Editor/pie_dump_abilities.py` | read-only | `—` |
| `Scripts/Editor/pie_dump_player_functions.py` | read-only | `—` |
| `Scripts/Editor/pie_flask_hud.py` | read-only | `—` |
| `Scripts/Editor/pie_flipbooks.py` | read-only | `—` |
| `Scripts/Editor/pie_fog_gate.py` | read-only | `—` |
| `Scripts/Editor/pie_g3_probe.py` | read-only | `—` |
| `Scripts/Editor/pie_gate_look.py` | read-only | `—` |
| `Scripts/Editor/pie_grey_check.py` | read-only | `—` |
| `Scripts/Editor/pie_grey_layers.py` | read-only | `—` |
| `Scripts/Editor/pie_grey_weapons.py` | map_setup | `—` |
| `Scripts/Editor/pie_health_probe.py` | read-only | `—` |
| `Scripts/Editor/pie_hit_diag.py` | read-only | `—` |
| `Scripts/Editor/pie_hit_intake.py` | read-only | `—` |
| `Scripts/Editor/pie_hud_probe.py` | read-only | `—` |
| `Scripts/Editor/pie_hyperarmor.py` | read-only | `—` |
| `Scripts/Editor/pie_iframes.py` | modifies | `set_editor_property` |
| `Scripts/Editor/pie_input_montage_latency.py` | read-only | `—` |
| `Scripts/Editor/pie_input_smoke.py` | read-only | `—` |
| `Scripts/Editor/pie_jump_probe.py` | read-only | `—` |
| `Scripts/Editor/pie_leap_wave.py` | read-only | `—` |
| `Scripts/Editor/pie_legend.py` | read-only | `—` |
| `Scripts/Editor/pie_look.py` | read-only | `—` |
| `Scripts/Editor/pie_m7_check.py` | read-only | `—` |
| `Scripts/Editor/pie_memory_soak.py` | read-only | `—` |
| `Scripts/Editor/pie_montage_shots.py` | read-only | `—` |
| `Scripts/Editor/pie_montage_travel.py` | read-only | `—` |
| `Scripts/Editor/pie_pack_demo.py` | map_setup | `—` |
| `Scripts/Editor/pie_pack_fight.py` | read-only | `—` |
| `Scripts/Editor/pie_phase_reset.py` | read-only | `—` |
| `Scripts/Editor/pie_player_death_reset.py` | read-only | `—` |
| `Scripts/Editor/pie_player_tags.py` | read-only | `—` |
| `Scripts/Editor/pie_poise_enemy_test.py` | read-only | `—` |
| `Scripts/Editor/pie_poise_scale.py` | map_setup | `—` |
| `Scripts/Editor/pie_poise_test.py` | read-only | `—` |
| `Scripts/Editor/pie_position_log.py` | read-only | `—` |
| `Scripts/Editor/pie_posture_hits.py` | read-only | `—` |
| `Scripts/Editor/pie_posture_regen.py` | read-only | `—` |
| `Scripts/Editor/pie_real_kill.py` | read-only | `—` |
| `Scripts/Editor/pie_remains.py` | read-only | `—` |
| `Scripts/Editor/pie_remains_look.py` | read-only | `—` |
| `Scripts/Editor/pie_remains_material.py` | read-only | `—` |
| `Scripts/Editor/pie_riposte.py` | read-only | `—` |
| `Scripts/Editor/pie_riposte_exec.py` | read-only | `—` |
| `Scripts/Editor/pie_riposte_lethal.py` | read-only | `—` |
| `Scripts/Editor/pie_scratch_route_a.py` | read-only | `—` |
| `Scripts/Editor/pie_selection_refusal.py` | modifies | `set_editor_property` |
| `Scripts/Editor/pie_selector_viewport.py` | read-only | `—` |
| `Scripts/Editor/pie_sevarog_pack.py` | map_setup | `—` |
| `Scripts/Editor/pie_shrine_look.py` | read-only | `—` |
| `Scripts/Editor/pie_soak.py` | read-only | `—` |
| `Scripts/Editor/pie_stamina_cost.py` | read-only | `—` |
| `Scripts/Editor/pie_stamina_trace.py` | read-only | `—` |
| `Scripts/Editor/pie_state.py` | read-only | `—` |
| `Scripts/Editor/pie_stop.py` | read-only | `—` |
| `Scripts/Editor/pie_telegraph.py` | read-only | `—` |
| `Scripts/Editor/pie_trace_audit.py` | modifies | `set_editor_property` |
| `Scripts/Editor/pie_transition_rules.py` | modifies | `set_editor_property` |
| `Scripts/Editor/pie_ui_check.py` | read-only | `—` |
| `Scripts/Editor/pie_vfx_gallery.py` | read-only | `—` |
| `Scripts/Editor/pie_victory_lock.py` | read-only | `—` |
| `Scripts/Editor/pie_weapons_smoke.py` | modifies | `set_editor_property` |
| `Scripts/Editor/place_gate_frame.py` | map_setup | `—` |
| `Scripts/Editor/place_remains_look.py` | map_setup | `—` |
| `Scripts/Editor/place_shiva_shrine.py` | map_setup | `—` |
| `Scripts/Editor/poise_data.py` | modifies | `save_loaded_asset, set_editor_property` |
| `Scripts/Editor/polish_arena_stills.py` | modifies | `save_loaded_asset` |
| `Scripts/Editor/probe_api.py` | read-only | `—` |
| `Scripts/Editor/probe_body_mats.py` | read-only | `—` |
| `Scripts/Editor/probe_bs.py` | read-only | `—` |
| `Scripts/Editor/probe_death_pose.py` | modifies | `set_editor_property` |
| `Scripts/Editor/probe_encounter_parity_snapshot.py` | read-only | `—` |
| `Scripts/Editor/probe_fbx_import.py` | read-only | `—` |
| `Scripts/Editor/probe_gate_area.py` | map_setup | `—` |
| `Scripts/Editor/probe_grey_slots.py` | read-only | `—` |
| `Scripts/Editor/probe_grey_sockets.py` | read-only | `—` |
| `Scripts/Editor/probe_mat_params.py` | read-only | `—` |
| `Scripts/Editor/probe_montage_segments.py` | read-only | `—` |
| `Scripts/Editor/probe_pawn_info.py` | read-only | `—` |
| `Scripts/Editor/probe_player_comps.py` | read-only | `—` |
| `Scripts/Editor/probe_skel.py` | read-only | `—` |
| `Scripts/Editor/probe_skel_api.py` | read-only | `—` |
| `Scripts/Editor/probe_statue_regions.py` | read-only | `—` |
| `Scripts/Editor/probe_struct.py` | read-only | `—` |
| `Scripts/Editor/probe_vars.py` | read-only | `—` |
| `Scripts/Editor/props.py` | read-only | `—` |
| `Scripts/Editor/read_item_sockets.py` | read-only | `—` |
| `Scripts/Editor/read_player_info.py` | read-only | `—` |
| `Scripts/Editor/remove_remains_look.py` | map_setup | `—` |
| `Scripts/Editor/repoint_player_refs.py` | modifies | `save_loaded_asset, set_editor_property` |
| `Scripts/Editor/report_g044_dependency_census.py` | read-only | `—` |
| `Scripts/Editor/report_owner_cleanup_referencers.py` | read-only | `—` |
| `Scripts/Editor/report_selector_setter_callers.py` | read-only | `—` |
| `Scripts/Editor/reset_component_materials.py` | map_setup | `—` |
| `Scripts/Editor/resolve_retarget_map.py` | modifies | `rename_asset` |
| `Scripts/Editor/retarget_pack_to_greystone.py` | creates | `create_asset` |
| `Scripts/Editor/review_report10.py` | modifies | `set_editor_property` |
| `Scripts/Editor/review_report11.py` | modifies | `set_editor_property` |
| `Scripts/Editor/review_report11b.py` | modifies | `set_editor_property` |
| `Scripts/Editor/review_report11c.py` | modifies | `set_editor_property` |
| `Scripts/Editor/review_report12.py` | modifies | `set_editor_property` |
| `Scripts/Editor/review_report12b.py` | modifies | `set_editor_property` |
| `Scripts/Editor/review_report12c.py` | modifies | `set_editor_property` |
| `Scripts/Editor/review_report13.py` | modifies | `set_editor_property` |
| `Scripts/Editor/review_report13b.py` | modifies | `set_editor_property` |
| `Scripts/Editor/review_report13c.py` | modifies | `set_editor_property` |
| `Scripts/Editor/rpg_content_lib.py` | creates | `create_asset` |
| `Scripts/Editor/run_a4_parity_and_quit.py` | read-only | `—` |
| `Scripts/Editor/run_a5_parity_driver_and_quit.py` | read-only | `—` |
| `Scripts/Editor/run_c3_sword_dry_config.py` | read-only | `—` |
| `Scripts/Editor/sample_deps.py` | read-only | `—` |
| `Scripts/Editor/save_gate_frame.py` | modifies | `save_asset` |
| `Scripts/Editor/save_shrine.py` | modifies | `save_asset` |
| `Scripts/Editor/set_health_multiplier.py` | modifies | `save_loaded_asset, set_editor_property` |
| `Scripts/Editor/set_riposte_root_motion.py` | modifies | `save_loaded_asset, set_editor_property` |
| `Scripts/Editor/set_view.py` | read-only | `—` |
| `Scripts/Editor/set_weapon_windows.py` | modifies | `save_loaded_asset, set_editor_property` |
| `Scripts/Editor/setup_grey_player.py` | modifies | `save_loaded_asset, set_editor_property` |
| `Scripts/Editor/setup_input_fix.py` | creates | `create_asset` |
| `Scripts/Editor/setup_m1_content.py` | map_setup | `new_level` |
| `Scripts/Editor/setup_m3_content.py` | map_setup | `—` |
| `Scripts/Editor/setup_m4_content.py` | map_setup | `—` |
| `Scripts/Editor/setup_m4_statetree.py` | modifies | `save_loaded_asset, set_editor_property` |
| `Scripts/Editor/setup_m5_content.py` | creates | `create_asset` |
| `Scripts/Editor/setup_m6_content.py` | map_setup | `—` |
| `Scripts/Editor/setup_m7_arena.py` | map_setup | `—` |
| `Scripts/Editor/setup_m7_beam_materials.py` | creates | `create_asset` |
| `Scripts/Editor/setup_m7_content.py` | modifies | `save_loaded_asset, set_editor_property` |
| `Scripts/Editor/setup_m7_roll.py` | modifies | `delete_asset, rename_asset, save_loaded_asset` |
| `Scripts/Editor/sevarog_pack_01_proxy.py` | creates | `duplicate_asset` |
| `Scripts/Editor/sevarog_pack_02_montages_abilities.py` | creates | `create_asset, duplicate_asset` |
| `Scripts/Editor/sevarog_pack_02b_toggle_only.py` | read-only | `—` |
| `Scripts/Editor/sevarog_pack_03_info_style_pawn.py` | creates | `duplicate_asset` |
| `Scripts/Editor/sevarog_pack_03b_soft_refs.py` | modifies | `save_loaded_asset, set_editor_property` |
| `Scripts/Editor/sevarog_pack_04_level.py` | map_setup | `, save_map` |
| `Scripts/Editor/sevarog_pack_05_parity.py` | creates | `create_asset, duplicate_asset` |
| `Scripts/Editor/sevarog_pack_05b_death_style.py` | creates | `create_asset, duplicate_asset` |
| `Scripts/Editor/sevarog_pack_06_director.py` | modifies | `save_loaded_asset, set_editor_property` |
| `Scripts/Editor/sevarog_pack_07_bolt_impact.py` | creates | `duplicate_asset` |
| `Scripts/Editor/sevarog_pack_08_turn.py` | creates | `create_asset, duplicate_asset` |
| `Scripts/Editor/sevarog_pack_09_charge.py` | map_setup | `, save_map` |
| `Scripts/Editor/sevarog_pack_10_combo_telegraph.py` | modifies | `save_loaded_asset, set_editor_property` |
| `Scripts/Editor/stop_pie.py` | read-only | `—` |
| `Scripts/Editor/survey_all_pillars.py` | read-only | `—` |
| `Scripts/Editor/survey_all_walls.py` | read-only | `—` |
| `Scripts/Editor/survey_deadly_ruins.py` | read-only | `—` |
| `Scripts/Editor/survey_pack_anims.py` | read-only | `—` |
| `Scripts/Editor/test_death_ue.py` | modifies | `set_editor_property` |
| `Scripts/Editor/test_dormant_sword.py` | modifies | `set_editor_property` |
| `Scripts/Editor/test_import_skm.py` | modifies | `set_editor_property` |
| `Scripts/Editor/toggle_post.py` | map_setup | `—` |
| `Scripts/Editor/tune_arena_visuals.py` | map_setup | `—` |
| `Scripts/Editor/tune_floor.py` | modifies | `save_loaded_asset` |
| `Scripts/Editor/ue_editor_values.py` | read-only | `—` |
| `Scripts/Editor/update_arena_v2.py` | map_setup | `—` |
| `Scripts/Editor/update_g044_boss_health_and_manifest.py` | modifies | `save_loaded_asset, set_editor_property` |
| `Scripts/Editor/validate_g044_encounter_selection.py` | read-only | `—` |
| `Scripts/Editor/verify_arena_meshes.py` | read-only | `—` |
| `Scripts/Editor/verify_builds.py` | read-only | `—` |
| `Scripts/Editor/verify_g044_draft_inputs.py` | read-only | `—` |
| `Scripts/Editor/wake_clip_off.py` | read-only | `—` |
| `Scripts/Editor/write_g044_manifest_receipt.py` | read-only | `—` |
