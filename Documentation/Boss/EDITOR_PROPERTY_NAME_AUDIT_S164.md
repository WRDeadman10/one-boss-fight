# Editor reflected property-name audit (S164)

The unverified `Damage Gampelay Effect` setter at `Scripts/Editor/sevarog_pack_07_bolt_impact.py:33` is tracked as KI-169; do not change it by guess. It still needs a reflected Editor inspection and readback.

Offline static audit of literal `set_editor_property` property names in `Scripts/Editor/*.py`. No Editor was started and no script was executed. This check cannot query Unreal reflection or Blueprint/plugin assets; a text occurrence is evidence to inspect, not proof that a name is valid on the target object. Dynamic property-name expressions are outside this literal-name inventory.

## Inventory

- Python files: 340; files parsed: 339; parse failures: 1.
- Literal setter calls: 661; distinct literal names: 261.
- Project C++ source/header files searched: 372. “Source text” below means the exact property spelling occurs somewhere in those files; declarations are not parsed and target-class correspondence is not inferred.
- “Getter in script” lists `get_editor_property` calls with that exact name in the same editor script. This is only a candidate readback/precedent; it is not asserted to target the same object or follow the setter.

## Literal property inventory

| Property | Setter sites | C++ text occurrence | Getter site in same script |
|---|---|---|---|
| `AI Pawn Class` | `Scripts/Editor/sevarog_pack_03_info_style_pawn.py:76`, `Scripts/Editor/sevarog_pack_03b_soft_refs.py:9` | no | `Scripts/Editor/sevarog_pack_03b_soft_refs.py:10` |
| `AbilitiesSet` | `Scripts/Editor/sevarog_pack_03_info_style_pawn.py:42`, `Scripts/Editor/sevarog_pack_05_parity.py:166`, `Scripts/Editor/sevarog_pack_05b_death_style.py:74`, `Scripts/Editor/sevarog_pack_08_turn.py:45` | yes | `Scripts/Editor/inspect_boss_style.py:7`; `Scripts/Editor/sevarog_pack_03_info_style_pawn.py:31`; `Scripts/Editor/sevarog_pack_05_parity.py:153`; `Scripts/Editor/sevarog_pack_05b_death_style.py:61`; `Scripts/Editor/sevarog_pack_08_turn.py:39`; `Scripts/Editor/sevarog_pack_08_turn.py:47` |
| `Anim Class` | `Scripts/Editor/sevarog_pack_03_info_style_pawn.py:72` | no | none found |
| `Anim Layer Class` | `Scripts/Editor/sevarog_pack_03_info_style_pawn.py:43` | no | none found |
| `ArchMaterial` | `Scripts/Editor/apply_arena_art_fix.py:40`, `Scripts/Editor/apply_perfect_arena.py:63`, `Scripts/Editor/setup_m7_arena.py:96`, `Scripts/Editor/update_arena_v2.py:77` | yes | none found |
| `Attack Impact Effects` | `Scripts/Editor/sevarog_pack_07_bolt_impact.py:34` | no | none found |
| `AttackData` | `Scripts/Editor/sevarog_pack_05_parity.py:67`, `Scripts/Editor/sevarog_pack_07_bolt_impact.py:39` | yes | none found |
| `AttackMontages` | `Scripts/Editor/sevarog_pack_05_parity.py:128`, `Scripts/Editor/sevarog_pack_09_charge.py:44`, `Scripts/Editor/sevarog_pack_10_combo_telegraph.py:53` | yes | `Scripts/Editor/air_light_attacks.py:16`; `Scripts/Editor/inspect_pack_boss2.py:41`; `Scripts/Editor/probe_struct.py:5`; `Scripts/Editor/sevarog_pack_05_parity.py:127`; `Scripts/Editor/sevarog_pack_09_charge.py:41`; `Scripts/Editor/sevarog_pack_10_combo_telegraph.py:48` |
| `Brazier` | `Scripts/Editor/apply_arena_art_fix.py:33`, `Scripts/Editor/apply_perfect_arena.py:54`, `Scripts/Editor/setup_m7_arena.py:87`, `Scripts/Editor/update_arena_v2.py:80` | yes | none found |
| `BrazierMaterial` | `Scripts/Editor/apply_arena_art_fix.py:41`, `Scripts/Editor/apply_perfect_arena.py:61`, `Scripts/Editor/setup_m7_arena.py:94`, `Scripts/Editor/update_arena_v2.py:81` | yes | none found |
| `ChanceToPerformFollowUp` | `Scripts/Editor/sevarog_pack_10_combo_telegraph.py:34` | no | none found |
| `Close Anim Montage` | `Scripts/Editor/sevarog_pack_10_combo_telegraph.py:36` | no | none found |
| `CloseRangeAttacksMaxDistance` | `Scripts/Editor/sevarog_pack_10_combo_telegraph.py:35` | no | none found |
| `Collision Target Tag` | `Scripts/Editor/sevarog_pack_05_parity.py:64`, `Scripts/Editor/sevarog_pack_09_charge.py:32` | no | none found |
| `Damage Gampelay Effect` | `Scripts/Editor/sevarog_pack_07_bolt_impact.py:33` | no | none found |
| `DeathMontages` | `Scripts/Editor/fix_sev_montage_refs.py:17`, `Scripts/Editor/pie_death_probe.py:64`, `Scripts/Editor/sevarog_pack_05_parity.py:146`, `Scripts/Editor/sevarog_pack_05b_death_style.py:54` | yes | `Scripts/Editor/pie_death_probe.py:65`; `Scripts/Editor/pie_death_probe.py:54` |
| `Default Attributes` | `Scripts/Editor/poise_data.py:49`, `Scripts/Editor/sevarog_pack_03_info_style_pawn.py:87` | no | `Scripts/Editor/inspect_pack_boss2.py:24`; `Scripts/Editor/poise_data.py:26`; `Scripts/Editor/read_player_info.py:4`; `Scripts/Editor/sevarog_pack_03_info_style_pawn.py:79` |
| `DefaultCombatStyle` | `Scripts/Editor/sevarog_pack_03_info_style_pawn.py:73` | no | none found |
| `Desired Rotation Type` | `Scripts/Editor/sevarog_pack_05_parity.py:62`, `Scripts/Editor/sevarog_pack_05_parity.py:84`, `Scripts/Editor/sevarog_pack_08_turn.py:23`, `Scripts/Editor/sevarog_pack_09_charge.py:26` | no | none found |
| `EnemyInfo` | `Scripts/Editor/sevarog_pack_03_info_style_pawn.py:93`, `Scripts/Editor/sevarog_pack_03b_soft_refs.py:16` | yes | `Scripts/Editor/sevarog_pack_03b_soft_refs.py:17` |
| `EnemyInfoRef` | `Scripts/Editor/arena_use_pack_boss.py:24`, `Scripts/Editor/sevarog_pack_03b_soft_refs.py:21` | yes | `Scripts/Editor/arena_use_pack_boss.py:25`; `Scripts/Editor/pie_sevarog_pack.py:165`; `Scripts/Editor/sevarog_pack_03b_soft_refs.py:22` |
| `EnemyName` | `Scripts/Editor/sevarog_pack_03_info_style_pawn.py:74` | no | none found |
| `EntranceArch` | `Scripts/Editor/apply_arena_art_fix.py:32`, `Scripts/Editor/apply_perfect_arena.py:53`, `Scripts/Editor/setup_m7_arena.py:86`, `Scripts/Editor/update_arena_v2.py:76` | yes | none found |
| `Event Tag` | `Scripts/Editor/sevarog_pack_05_parity.py:86` | no | none found |
| `EventTag` | `Scripts/Editor/sevarog_pack_05_parity.py:65`, `Scripts/Editor/sevarog_pack_09_charge.py:33` | no | none found |
| `ExtendedAttributes` | `Scripts/Editor/poise_data.py:52` | no | `Scripts/Editor/poise_data.py:27`; `Scripts/Editor/read_player_info.py:17` |
| `FallingAttackMontages` | `Scripts/Editor/air_light_attacks.py:21` | yes | `Scripts/Editor/air_light_attacks.py:15` |
| `FloorMaterial` | `Scripts/Editor/apply_arena_art_fix.py:37`, `Scripts/Editor/apply_perfect_arena.py:59`, `Scripts/Editor/setup_m7_arena.py:92`, `Scripts/Editor/update_arena_v2.py:53` | yes | none found |
| `GameplayTags` | `Scripts/Editor/boss_poise_armor.py:17` | no | `Scripts/Editor/arena_use_pack_boss.py:27`; `Scripts/Editor/boss_poise_armor.py:13`; `Scripts/Editor/boss_poise_armor.py:20` |
| `Impact Emitters` | `Scripts/Editor/sevarog_pack_07_bolt_impact.py:29` | no | `Scripts/Editor/sevarog_pack_07_bolt_impact.py:19` |
| `PillarBroken` | `Scripts/Editor/apply_arena_art_fix.py:31`, `Scripts/Editor/apply_perfect_arena.py:50`, `Scripts/Editor/setup_m7_arena.py:85`, `Scripts/Editor/tune_arena_visuals.py:34`, `Scripts/Editor/update_arena_v2.py:62` | yes | none found |
| `PillarCracked` | `Scripts/Editor/apply_arena_art_fix.py:30`, `Scripts/Editor/apply_perfect_arena.py:49`, `Scripts/Editor/setup_m7_arena.py:84`, `Scripts/Editor/tune_arena_visuals.py:33`, `Scripts/Editor/update_arena_v2.py:61` | yes | none found |
| `PillarIntact` | `Scripts/Editor/apply_arena_art_fix.py:29`, `Scripts/Editor/apply_perfect_arena.py:48`, `Scripts/Editor/setup_m7_arena.py:83`, `Scripts/Editor/tune_arena_visuals.py:32`, `Scripts/Editor/update_arena_v2.py:60` | yes | none found |
| `PillarMaterial` | `Scripts/Editor/apply_arena_art_fix.py:38`, `Scripts/Editor/apply_perfect_arena.py:62`, `Scripts/Editor/setup_m7_arena.py:95`, `Scripts/Editor/update_arena_v2.py:63` | yes | none found |
| `ProjectileHandSocketNames` | `Scripts/Editor/sevarog_pack_05_parity.py:133` | no | `Scripts/Editor/sevarog_pack_05_parity.py:130` |
| `ProjectilesToFire` | `Scripts/Editor/sevarog_pack_05_parity.py:129` | no | none found |
| `RotationInterpSpeed` | `Scripts/Editor/sevarog_pack_05_parity.py:61`, `Scripts/Editor/sevarog_pack_05_parity.py:83`, `Scripts/Editor/sevarog_pack_08_turn.py:22`, `Scripts/Editor/sevarog_pack_09_charge.py:25` | no | none found |
| `Rubble` | `Scripts/Editor/apply_arena_art_fix.py:34`, `Scripts/Editor/apply_perfect_arena.py:55`, `Scripts/Editor/setup_m7_arena.py:88`, `Scripts/Editor/update_arena_v2.py:67` | yes | none found |
| `RubbleCount` | `Scripts/Editor/apply_arena_art_fix.py:45`, `Scripts/Editor/apply_perfect_arena.py:56`, `Scripts/Editor/setup_m7_arena.py:89` | yes | none found |
| `RubbleMaterial` | `Scripts/Editor/apply_arena_art_fix.py:42`, `Scripts/Editor/apply_perfect_arena.py:64`, `Scripts/Editor/setup_m7_arena.py:97`, `Scripts/Editor/update_arena_v2.py:68` | yes | none found |
| `TraceRadiusModifier` | `Scripts/Editor/sevarog_pack_05_parity.py:66`, `Scripts/Editor/sevarog_pack_09_charge.py:34` | no | none found |
| `WallMaterial` | `Scripts/Editor/apply_arena_art_fix.py:39`, `Scripts/Editor/apply_perfect_arena.py:60`, `Scripts/Editor/setup_m7_arena.py:93`, `Scripts/Editor/update_arena_v2.py:72` | yes | none found |
| `a` | `Scripts/Editor/make_remains_material.py:71`, `Scripts/Editor/make_remains_material.py:73` | yes | none found |
| `address_x` | `Scripts/Editor/import_ui_art.py:19`, `Scripts/Editor/make_flipbook_materials.py:26`, `Scripts/Editor/make_remains_material.py:30`, `Scripts/Editor/make_remains_material.py:32` | no | none found |
| `address_y` | `Scripts/Editor/import_ui_art.py:20`, `Scripts/Editor/make_flipbook_materials.py:27`, `Scripts/Editor/make_remains_material.py:31`, `Scripts/Editor/make_remains_material.py:33` | no | none found |
| `alias_hud_words` | `Scripts/Editor/make_combat_catalog.py:59` | no | none found |
| `anim_class` | `Scripts/Editor/setup_grey_player.py:13`, `Scripts/Editor/setup_m1_content.py:67`, `Scripts/Editor/setup_m3_content.py:294`, `Scripts/Editor/setup_m4_content.py:268` | no | `Scripts/Editor/boss_pose_reset.py:8`; `Scripts/Editor/inspect_pack_boss.py:23`; `Scripts/Editor/pie_combat_smoke.py:86`; `Scripts/Editor/pie_sevarog_pack.py:168`; `Scripts/Editor/setup_grey_player.py:8`; `Scripts/Editor/setup_grey_player.py:14` |
| `anim_to_play` | `Scripts/Editor/build_asset_proof_map.py:136` | no | none found |
| `animation` | `Scripts/Editor/fix_grey_blendspaces.py:38` | yes | `Scripts/Editor/fix_grey_blendspaces.py:30`; `Scripts/Editor/fix_grey_blendspaces.py:18` |
| `animation_data` | `Scripts/Editor/build_asset_proof_map.py:139` | no | `Scripts/Editor/build_asset_proof_map.py:135` |
| `animation_mode` | `Scripts/Editor/setup_grey_player.py:12`, `Scripts/Editor/setup_m1_content.py:66`, `Scripts/Editor/setup_m3_content.py:293`, `Scripts/Editor/setup_m4_content.py:267` | no | `Scripts/Editor/boss_pose_reset.py:8` |
| `attack` | `Scripts/Editor/setup_m4_content.py:216` | yes | none found |
| `attacks` | `Scripts/Editor/pie_a5_heal_punish.py:399`, `Scripts/Editor/pie_a5_heal_punish.py:409`, `Scripts/Editor/setup_m4_content.py:278` | yes | `Scripts/Editor/pie_a5_heal_punish.py:395`; `Scripts/Editor/pie_a5_heal_punish.py:407`; `Scripts/Editor/pie_build_fight.py:1190`; `Scripts/Editor/pie_m7_check.py:74` |
| `attenuation_radius` | `Scripts/Editor/dress_arena.py:375` | no | none found |
| `auto_generate_collision` | `Scripts/Editor/import_arena_meshes.py:50` | no | none found |
| `auto_possess_ai` | `Scripts/Editor/sevarog_pack_06_director.py:27` | no | `Scripts/Editor/inspect_pack_boss.py:25`; `Scripts/Editor/sevarog_pack_06_director.py:30` |
| `automated` | `Scripts/Editor/import_arena_meshes.py:40` | no | none found |
| `b` | `Scripts/Editor/make_remains_material.py:71`, `Scripts/Editor/make_remains_material.py:73` | yes | none found |
| `bThrottleCPUWhenNotForeground` | `Scripts/Editor/no_throttle.py:3` | no | none found |
| `base_intensity` | `Scripts/Editor/dress_arena.py:374` | no | none found |
| `base_property_overrides` | `Scripts/Editor/build_boss01_materials.py:228` | no | `Scripts/Editor/build_boss01_materials.py:225` |
| `base_reflect_fraction` | `Scripts/Editor/build_boss01_materials.py:168` | no | none found |
| `blend_mode` | `Scripts/Editor/build_boss01_materials.py:130`, `Scripts/Editor/hide_grey_builtin_weapons.py:12`, `Scripts/Editor/make_flipbook_materials.py:40`, `Scripts/Editor/make_remains_material.py:48`, `Scripts/Editor/setup_m7_beam_materials.py:32` | no | none found |
| `blend_time` | `Scripts/Editor/setup_m7_content.py:113` | no | none found |
| `block_action` | `Scripts/Editor/setup_input_fix.py:68` | no | none found |
| `block_niagara` | `Scripts/Editor/setup_m7_content.py:89` | no | none found |
| `block_sound` | `Scripts/Editor/setup_m7_content.py:87` | no | none found |
| `block_through_walls` | `Scripts/Editor/pie_trace_audit.py:413`, `Scripts/Editor/pie_trace_audit.py:450`, `Scripts/Editor/pie_trace_audit.py:391` | no | none found |
| `bloom_scale` | `Scripts/Editor/atmosphere.py:63` | no | none found |
| `bloom_threshold` | `Scripts/Editor/atmosphere.py:64` | no | none found |
| `bone_names` | `Scripts/Editor/greystone_sevarog_11_polish.py:29` | no | `Scripts/Editor/greystone_sevarog_11_polish.py:35` |
| `boss_name` | `Scripts/Editor/setup_m4_content.py:272` | no | none found |
| `boss_state_tree` | `Scripts/Editor/setup_m4_statetree.py:28` | no | none found |
| `box_extent` | `Scripts/Editor/setup_m4_content.py:306` | no | none found |
| `capsule_half_height` | `Scripts/Editor/setup_m3_content.py:286`, `Scripts/Editor/setup_m4_content.py:260`, `Scripts/Editor/sevarog_pack_03_info_style_pawn.py:50` | no | `Scripts/Editor/g0_pack_boss.py:67`; `Scripts/Editor/g0_pack_boss.py:81`; `Scripts/Editor/inspect_pack_boss.py:24`; `Scripts/Editor/probe_player_comps.py:12` |
| `capsule_radius` | `Scripts/Editor/setup_m3_content.py:287`, `Scripts/Editor/setup_m4_content.py:261`, `Scripts/Editor/sevarog_pack_03_info_style_pawn.py:51` | no | `Scripts/Editor/g0_pack_boss.py:67`; `Scripts/Editor/g0_pack_boss.py:81`; `Scripts/Editor/inspect_pack_boss.py:24`; `Scripts/Editor/probe_player_comps.py:12` |
| `card_material` | `Scripts/Editor/dress_arena.py:305` | no | none found |
| `card_mesh` | `Scripts/Editor/dress_arena.py:304` | no | none found |
| `cast_shadow` | `Scripts/Editor/dress_arena.py:348` | no | none found |
| `cast_shadows` | `Scripts/Editor/atmosphere.py:59`, `Scripts/Editor/dress_arena.py:376` | no | none found |
| `cast_volumetric_shadow` | `Scripts/Editor/atmosphere.py:60` | no | none found |
| `clip_path` | `Scripts/Editor/pie_a5_heal_punish.py:398`, `Scripts/Editor/pie_a5_heal_punish.py:408` | no | `Scripts/Editor/pie_a5_heal_punish.py:397` |
| `collision` | `Scripts/Editor/dress_arena.py:347`, `Scripts/Editor/export_greystone.py:19`, `Scripts/Editor/export_mannequin.py:19`, `Scripts/Editor/export_quinn.py:19` | yes | none found |
| `combine_meshes` | `Scripts/Editor/import_arena_meshes.py:52` | no | none found |
| `compression_settings` | `Scripts/Editor/build_boss01_materials.py:43`, `Scripts/Editor/build_boss01_materials.py:46`, `Scripts/Editor/import_ui_art.py:21`, `Scripts/Editor/make_flipbook_materials.py:28`, `Scripts/Editor/make_remains_material.py:29` | no | none found |
| `constant` | `Scripts/Editor/make_gate_rune_material.py:13`, `Scripts/Editor/make_gate_rune_material.py:16`, `Scripts/Editor/make_polish_materials.py:41`, `Scripts/Editor/make_polish_materials.py:69`, `Scripts/Editor/make_polish_materials.py:71`, `Scripts/Editor/setup_m7_beam_materials.py:38` | yes | none found |
| `cooldown` | `Scripts/Editor/pie_a5_heal_punish.py:103`, `Scripts/Editor/pie_a5_heal_punish.py:225`, `Scripts/Editor/pie_a5_heal_punish.py:278` | yes | none found |
| `cooldown_seconds` | `Scripts/Editor/pie_transition_rules.py:108`, `Scripts/Editor/pie_transition_rules.py:530`, `Scripts/Editor/pie_transition_rules.py:505`, `Scripts/Editor/pie_transition_rules.py:586` | no | none found |
| `count` | `Scripts/Editor/dress_arena.py:424` | yes | none found |
| `crackle_sound` | `Scripts/Editor/dress_arena.py:384` | no | none found |
| `damage` | `Scripts/Editor/rpg_content_lib.py:109`, `Scripts/Editor/setup_m3_content.py:242`, `Scripts/Editor/setup_m4_content.py:221` | yes | `Scripts/Editor/pie_leap_wave.py:71` |
| `data_asset_class` | `Scripts/Editor/setup_m3_content.py:250`, `Scripts/Editor/setup_m4_content.py:208`, `Scripts/Editor/setup_m4_content.py:232`, `Scripts/Editor/setup_m5_content.py:142`, `Scripts/Editor/setup_m5_content.py:116` | no | none found |
| `death_montage` | `Scripts/Editor/setup_m3_content.py:297`, `Scripts/Editor/setup_m4_content.py:271` | yes | none found |
| `default_game_mode` | `Scripts/Editor/sevarog_pack_04_level.py:24` | no | `Scripts/Editor/sevarog_pack_04_level.py:25` |
| `default_value` | `Scripts/Editor/build_boss01_materials.py:65`, `Scripts/Editor/build_boss01_materials.py:72`, `Scripts/Editor/make_flipbook_materials.py:72`, `Scripts/Editor/make_flipbook_materials.py:52`, `Scripts/Editor/make_remains_material.py:113`, `Scripts/Editor/make_remains_material.py:65` | no | none found |
| `destination_name` | `Scripts/Editor/import_arena_meshes.py:38` | no | none found |
| `destination_path` | `Scripts/Editor/import_arena_meshes.py:37` | no | none found |
| `display_name` | `Scripts/Editor/setup_m3_content.py:254`, `Scripts/Editor/setup_m4_content.py:235`, `Scripts/Editor/setup_m5_content.py:118` | no | `Scripts/Editor/pie_weapons_smoke.py:94` |
| `dodge_action` | `Scripts/Editor/setup_m3_content.py:309` | no | none found |
| `dodge_back_montage` | `Scripts/Editor/setup_m7_content.py:126` | no | none found |
| `dodge_montage` | `Scripts/Editor/setup_m7_content.py:125` | no | none found |
| `dynamic_shadow_distance_movable_light` | `Scripts/Editor/atmosphere.py:65` | no | none found |
| `effect` | `Scripts/Editor/setup_m4_content.py:179` | yes | none found |
| `effect_ground_drop` | `Scripts/Editor/setup_m4_content.py:175` | no | none found |
| `enable_auto_blend_out` | `Scripts/Editor/make_close_montages.py:51`, `Scripts/Editor/make_death_montage.py:24`, `Scripts/Editor/sevarog_pack_05_parity.py:103` | no | none found |
| `enable_light_shaft_bloom` | `Scripts/Editor/atmosphere.py:62` | no | none found |
| `enable_root_motion` | `Scripts/Editor/fix_roll_root_motion.py:57`, `Scripts/Editor/import_boss01_clips_r12.py:65`, `Scripts/Editor/set_riposte_root_motion.py:13` | no | `Scripts/Editor/g2_probe_a4a5.py:8`; `Scripts/Editor/import_boss01_clips_r12.py:64`; `Scripts/Editor/import_boss01_clips_r12.py:67`; `Scripts/Editor/inspect_m7_assets.py:48`; `Scripts/Editor/inspect_roll_motion.py:7`; `Scripts/Editor/inspect_roll_motion.py:24`; `Scripts/Editor/set_riposte_root_motion.py:11`; `Scripts/Editor/set_riposte_root_motion.py:15`; `Scripts/Editor/setup_m7_content.py:103` |
| `enable_volumetric_fog` | `Scripts/Editor/debug_atmos.py:14` | no | none found |
| `enabled` | `Scripts/Editor/debug_atmos.py:19`, `Scripts/Editor/toggle_post.py:6` | yes | `Scripts/Editor/list_ruin_meshes.py:21` |
| `entrance_ability` | `Scripts/Editor/sevarog_pack_06_director.py:24` | no | none found |
| `entrance_montage` | `Scripts/Editor/setup_m4_content.py:279` | no | none found |
| `evaluation_type` | `Scripts/Editor/review_report11.py:63` | no | none found |
| `exponent` | `Scripts/Editor/build_boss01_materials.py:167` | yes | none found |
| `extract_root_motion` | `Scripts/Editor/import_boss01_clips_r14.py:49`, `Scripts/Editor/probe_death_pose.py:9`, `Scripts/Editor/review_report11.py:65`, `Scripts/Editor/review_report11b.py:16`, `Scripts/Editor/review_report11c.py:14`, `Scripts/Editor/review_report12.py:71`, `Scripts/Editor/review_report12b.py:16`, `Scripts/Editor/review_report12c.py:41`, `Scripts/Editor/review_report13.py:92`, `Scripts/Editor/review_report13b.py:26`, `Scripts/Editor/review_report13b.py:56`, `Scripts/Editor/test_death_ue.py:27`, `Scripts/Editor/test_dormant_sword.py:20` | no | none found |
| `feedback` | `Scripts/Editor/setup_m5_content.py:160`, `Scripts/Editor/setup_m5_content.py:168`, `Scripts/Editor/setup_m5_content.py:177` | yes | none found |
| `filename` | `Scripts/Editor/import_arena_meshes.py:36` | yes | none found |
| `fire_scale` | `Scripts/Editor/dress_arena.py:373` | no | none found |
| `fire_sources` | `Scripts/Editor/dress_arena.py:423` | no | none found |
| `fire_template` | `Scripts/Editor/dress_arena.py:378` | no | none found |
| `floor_material` | `Scripts/Editor/dress_arena.py:100` | no | `Scripts/Editor/check_floor.py:5`; `Scripts/Editor/inspect_arena_floormesh.py:7`; `Scripts/Editor/inspect_arena_floormesh2.py:6` |
| `fog_density` | `Scripts/Editor/debug_atmos.py:16` | no | none found |
| `follow_ups` | `Scripts/Editor/setup_m4_content.py:225` | no | none found |
| `force_root_lock` | `Scripts/Editor/fix_roll_root_motion.py:56` | no | `Scripts/Editor/inspect_roll_motion.py:7` |
| `forward_offset` | `Scripts/Editor/setup_m4_content.py:174`, `Scripts/Editor/setup_m4_content.py:190`, `Scripts/Editor/sevarog_pack_05_parity.py:71`, `Scripts/Editor/sevarog_pack_10_combo_telegraph.py:69` | no | none found |
| `g` | `Scripts/Editor/make_polish_materials.py:74`, `Scripts/Editor/make_remains_material.py:71`, `Scripts/Editor/make_remains_material.py:73` | yes | none found |
| `gate_radius` | `Scripts/Editor/sevarog_pack_06_director.py:22` | no | none found |
| `ground_drop` | `Scripts/Editor/setup_m4_content.py:191`, `Scripts/Editor/sevarog_pack_05_parity.py:72`, `Scripts/Editor/sevarog_pack_10_combo_telegraph.py:70` | no | none found |
| `guard_montage` | `Scripts/Editor/setup_input_fix.py:69` | no | none found |
| `health_damage_multiplier` | `Scripts/Editor/set_health_multiplier.py:27` | no | `Scripts/Editor/set_health_multiplier.py:25`; `Scripts/Editor/set_health_multiplier.py:38`; `Scripts/Editor/set_health_multiplier.py:39` |
| `heavy_attack` | `Scripts/Editor/setup_m3_content.py:258`, `Scripts/Editor/setup_m5_content.py:122` | no | none found |
| `heavy_attack_action` | `Scripts/Editor/setup_m3_content.py:308` | no | none found |
| `hidden_in_game` | `Scripts/Editor/dress_arena.py:451`, `Scripts/Editor/sevarog_pack_03_info_style_pawn.py:65` | no | `Scripts/Editor/check_floor.py:9`; `Scripts/Editor/inspect_arena.py:17`; `Scripts/Editor/pie_boss_death.py:116`; `Scripts/Editor/pie_boss_death_states.py:110`; `Scripts/Editor/pie_boss_look.py:126`; `Scripts/Editor/pie_boss_look.py:153`; `Scripts/Editor/pie_boss_look.py:129`; `Scripts/Editor/pie_boss_look.py:128` |
| `hit_react_montage` | `Scripts/Editor/setup_m3_content.py:296`, `Scripts/Editor/setup_m4_content.py:270` | no | none found |
| `hit_stop_seconds` | `Scripts/Editor/setup_m5_content.py:128` | no | none found |
| `horizontal_alignment` | `Scripts/Editor/build_asset_proof_map.py:97` | no | none found |
| `hyper_armor_end` | `Scripts/Editor/set_weapon_windows.py:38` | no | `Scripts/Editor/set_weapon_windows.py:34`; `Scripts/Editor/set_weapon_windows.py:57` |
| `hyper_armor_start` | `Scripts/Editor/set_weapon_windows.py:37` | no | `Scripts/Editor/set_weapon_windows.py:56`; `Scripts/Editor/set_weapon_windows.py:34`; `Scripts/Editor/set_weapon_windows.py:57` |
| `icon` | `Scripts/Editor/make_combat_catalog.py:65` | yes | `Scripts/Editor/make_combat_catalog.py:65` |
| `impact_effect` | `Scripts/Editor/setup_m5_content.py:132`, `Scripts/Editor/setup_m5_content.py:185` | no | none found |
| `impact_niagara` | `Scripts/Editor/setup_m7_content.py:75` | no | none found |
| `impact_sound_variants` | `Scripts/Editor/setup_m7_content.py:74` | no | none found |
| `import_animations` | `Scripts/Editor/import_boss01.py:39`, `Scripts/Editor/import_boss01.py:51`, `Scripts/Editor/import_boss01.py:148`, `Scripts/Editor/import_boss01.py:66`, `Scripts/Editor/import_boss01.py:132`, `Scripts/Editor/import_boss01_clips_r12.py:37`, `Scripts/Editor/import_boss01_clips_r14.py:23`, `Scripts/Editor/import_corpse_statue.py:18`, `Scripts/Editor/import_shiva_shrine.py:18`, `Scripts/Editor/place_gate_frame.py:27`, `Scripts/Editor/review_report10.py:70`, `Scripts/Editor/review_report10.py:97`, `Scripts/Editor/review_report10.py:33`, `Scripts/Editor/review_report11.py:158`, `Scripts/Editor/review_report11.py:39`, `Scripts/Editor/review_report12.py:45`, `Scripts/Editor/review_report13.py:34`, `Scripts/Editor/review_report13c.py:23`, `Scripts/Editor/test_death_ue.py:18` | no | none found |
| `import_as_skeletal` | `Scripts/Editor/import_arena_meshes.py:47`, `Scripts/Editor/import_boss01.py:34`, `Scripts/Editor/import_boss01.py:63`, `Scripts/Editor/import_boss01.py:127`, `Scripts/Editor/import_boss01_clips_r12.py:36`, `Scripts/Editor/import_boss01_clips_r14.py:22`, `Scripts/Editor/import_corpse_statue.py:14`, `Scripts/Editor/import_shiva_shrine.py:14`, `Scripts/Editor/place_gate_frame.py:23`, `Scripts/Editor/review_report10.py:92`, `Scripts/Editor/review_report10.py:32`, `Scripts/Editor/review_report11.py:38`, `Scripts/Editor/review_report12.py:44`, `Scripts/Editor/review_report13.py:33`, `Scripts/Editor/review_report13c.py:22`, `Scripts/Editor/test_death_ue.py:17` | no | none found |
| `import_materials` | `Scripts/Editor/import_arena_meshes.py:46`, `Scripts/Editor/import_boss01.py:37`, `Scripts/Editor/import_boss01.py:49`, `Scripts/Editor/import_boss01.py:146`, `Scripts/Editor/import_boss01.py:67`, `Scripts/Editor/import_boss01.py:130`, `Scripts/Editor/import_corpse_statue.py:16`, `Scripts/Editor/import_shiva_shrine.py:16`, `Scripts/Editor/place_gate_frame.py:25`, `Scripts/Editor/review_report10.py:68`, `Scripts/Editor/review_report10.py:95`, `Scripts/Editor/review_report11.py:156` | no | none found |
| `import_mesh` | `Scripts/Editor/import_arena_meshes.py:44`, `Scripts/Editor/import_boss01.py:33`, `Scripts/Editor/import_boss01.py:47`, `Scripts/Editor/import_boss01.py:144`, `Scripts/Editor/import_boss01.py:62`, `Scripts/Editor/import_boss01.py:126`, `Scripts/Editor/import_boss01_clips_r12.py:35`, `Scripts/Editor/import_boss01_clips_r14.py:21`, `Scripts/Editor/import_corpse_statue.py:13`, `Scripts/Editor/import_shiva_shrine.py:13`, `Scripts/Editor/place_gate_frame.py:22`, `Scripts/Editor/review_report10.py:66`, `Scripts/Editor/review_report10.py:91`, `Scripts/Editor/review_report10.py:31`, `Scripts/Editor/review_report11.py:154`, `Scripts/Editor/review_report11.py:37`, `Scripts/Editor/review_report12.py:43`, `Scripts/Editor/review_report13.py:32`, `Scripts/Editor/review_report13c.py:21`, `Scripts/Editor/test_death_ue.py:16` | no | none found |
| `import_morph_targets` | `Scripts/Editor/import_boss01.py:40` | no | none found |
| `import_textures` | `Scripts/Editor/import_arena_meshes.py:45`, `Scripts/Editor/import_boss01.py:38`, `Scripts/Editor/import_boss01.py:50`, `Scripts/Editor/import_boss01.py:147`, `Scripts/Editor/import_boss01.py:68`, `Scripts/Editor/import_boss01.py:131`, `Scripts/Editor/import_corpse_statue.py:17`, `Scripts/Editor/import_shiva_shrine.py:17`, `Scripts/Editor/place_gate_frame.py:26`, `Scripts/Editor/review_report10.py:69`, `Scripts/Editor/review_report10.py:96`, `Scripts/Editor/review_report11.py:157` | no | none found |
| `instances` | `Scripts/Editor/dress_arena.py:346` | yes | none found |
| `intensity` | `Scripts/Editor/atmosphere.py:56`, `Scripts/Editor/atmosphere.py:89` | yes | none found |
| `jump_z_velocity` | `Scripts/Editor/air_jump_tuning.py:13` | no | `Scripts/Editor/air_jump_tuning.py:16` |
| `key_name` | `Scripts/Editor/setup_input_fix.py:35`, `Scripts/Editor/setup_m3_content.py:79`, `Scripts/Editor/setup_m5_content.py:78` | no | `Scripts/Editor/inspect_imc.py:7` |
| `layer_bottom_altitude` | `Scripts/Editor/atmosphere.py:128` | no | none found |
| `layer_height` | `Scripts/Editor/atmosphere.py:129` | no | none found |
| `light_attack_action` | `Scripts/Editor/setup_m3_content.py:307` | no | none found |
| `light_color` | `Scripts/Editor/atmosphere.py:57` | no | none found |
| `light_combo` | `Scripts/Editor/setup_m3_content.py:255`, `Scripts/Editor/setup_m5_content.py:119` | no | none found |
| `lightning_ability` | `Scripts/Editor/sevarog_pack_06_director.py:25` | no | `Scripts/Editor/sevarog_pack_06_director.py:30` |
| `lock_on_action` | `Scripts/Editor/setup_m3_content.py:310` | no | none found |
| `lod_group` | `Scripts/Editor/import_ui_art.py:22` | no | none found |
| `lower_hemisphere_color` | `Scripts/Editor/atmosphere.py:91` | no | none found |
| `lower_hemisphere_is_black` | `Scripts/Editor/atmosphere.py:90` | no | none found |
| `material` | `Scripts/Editor/atmosphere.py:127`, `Scripts/Editor/dress_arena.py:422` | yes | none found |
| `material_interface` | `Scripts/Editor/build_boss01_materials.py:260`, `Scripts/Editor/import_boss01.py:99` | no | `Scripts/Editor/body_slots_probe.py:5`; `Scripts/Editor/body_slots_probe.py:5`; `Scripts/Editor/g1_sevarog_slots.py:7`; `Scripts/Editor/g1_sevarog_slots.py:7`; `Scripts/Editor/inspect_materials.py:24`; `Scripts/Editor/inspect_samurai_mesh.py:9`; `Scripts/Editor/probe_body_mats.py:7`; `Scripts/Editor/probe_grey_slots.py:6`; `Scripts/Editor/probe_grey_slots.py:6` |
| `material_override` | `Scripts/Editor/dress_arena.py:350` | no | none found |
| `materials` | `Scripts/Editor/import_boss01.py:101` | yes | `Scripts/Editor/body_slots_probe.py:4`; `Scripts/Editor/g1_sevarog_slots.py:6`; `Scripts/Editor/import_boss01.py:92`; `Scripts/Editor/import_boss01.py:138`; `Scripts/Editor/inspect_assets.py:122`; `Scripts/Editor/inspect_materials.py:21`; `Scripts/Editor/inspect_samurai_mesh.py:6`; `Scripts/Editor/probe_body_mats.py:6`; `Scripts/Editor/probe_grey_slots.py:5`; `Scripts/Editor/verify_builds.py:30` |
| `max_health` | `Scripts/Editor/pie_weapons_smoke.py:82` | no | none found |
| `max_speed` | `Scripts/Editor/sevarog_pack_09_charge.py:29` | no | none found |
| `mesh` | `Scripts/Editor/dress_arena.py:421`, `Scripts/Editor/dress_arena.py:345` | yes | `Scripts/Editor/g0_pack_boss.py:58`; `Scripts/Editor/g0_pack_boss.py:79`; `Scripts/Editor/greystone_sevarog_11_polish.py:31`; `Scripts/Editor/hide_grey_builtin_weapons.py:20`; `Scripts/Editor/inspect_pack_boss.py:22`; `Scripts/Editor/pie_combat_smoke.py:41`; `Scripts/Editor/pie_combat_smoke.py:86`; `Scripts/Editor/pie_grey_weapons.py:71`; `Scripts/Editor/probe_grey_slots.py:9`; `Scripts/Editor/setup_grey_player.py:7`; `Scripts/Editor/setup_grey_player.py:10`; `Scripts/Editor/setup_m1_content.py:55`; `Scripts/Editor/setup_m3_content.py:289`; `Scripts/Editor/setup_m4_content.py:263`; `Scripts/Editor/sevarog_pack_03_info_style_pawn.py:52` |
| `mesh_type_to_import` | `Scripts/Editor/import_boss01.py:35`, `Scripts/Editor/import_boss01.py:48`, `Scripts/Editor/import_boss01.py:145`, `Scripts/Editor/import_boss01.py:64`, `Scripts/Editor/import_boss01.py:128`, `Scripts/Editor/import_boss01_clips_r12.py:39`, `Scripts/Editor/import_boss01_clips_r14.py:25`, `Scripts/Editor/import_corpse_statue.py:15`, `Scripts/Editor/import_shiva_shrine.py:15`, `Scripts/Editor/place_gate_frame.py:24`, `Scripts/Editor/review_report10.py:67`, `Scripts/Editor/review_report10.py:93`, `Scripts/Editor/review_report10.py:35`, `Scripts/Editor/review_report11.py:155`, `Scripts/Editor/review_report11.py:41`, `Scripts/Editor/review_report12.py:47`, `Scripts/Editor/review_report13.py:36`, `Scripts/Editor/review_report13c.py:24`, `Scripts/Editor/test_death_ue.py:20` | no | none found |
| `mip_gen_settings` | `Scripts/Editor/import_ui_art.py:18`, `Scripts/Editor/make_flipbook_materials.py:25`, `Scripts/Editor/make_remains_material.py:34` | no | none found |
| `mobility` | `Scripts/Editor/place_gate_frame.py:50`, `Scripts/Editor/place_remains_look.py:11` | yes | none found |
| `montage` | `Scripts/Editor/rpg_content_lib.py:108`, `Scripts/Editor/setup_m3_content.py:241`, `Scripts/Editor/setup_m4_content.py:213`, `Scripts/Editor/setup_m4_content.py:220` | yes | none found |
| `never_stream` | `Scripts/Editor/import_ui_art.py:23` | no | none found |
| `niagara_effect` | `Scripts/Editor/setup_m4_content.py:184`, `Scripts/Editor/setup_m4_content.py:189`, `Scripts/Editor/sevarog_pack_05_parity.py:69`, `Scripts/Editor/sevarog_pack_10_combo_telegraph.py:68` | no | none found |
| `note` | `Scripts/Editor/set_weapon_windows.py:40` | yes | `Scripts/Editor/make_weapon_table.py:24`; `Scripts/Editor/set_weapon_windows.py:39`; `Scripts/Editor/set_weapon_windows.py:57` |
| `one_convex_hull_per_ucx` | `Scripts/Editor/import_arena_meshes.py:51` | no | none found |
| `opacity_mask_clip_value` | `Scripts/Editor/build_boss01_materials.py:131` | no | none found |
| `options` | `Scripts/Editor/import_arena_meshes.py:54` | no | none found |
| `orbit_height` | `Scripts/Editor/setup_m6_content.py:22` | no | none found |
| `orbit_radius` | `Scripts/Editor/setup_m6_content.py:21` | no | none found |
| `override_materials` | `Scripts/Editor/greystone_sevarog_11_polish.py:31`, `Scripts/Editor/hide_grey_builtin_weapons.py:22` | no | `Scripts/Editor/hide_grey_builtin_weapons.py:25`; `Scripts/Editor/probe_grey_slots.py:10` |
| `override_two_sided` | `Scripts/Editor/build_boss01_materials.py:223`, `Scripts/Editor/build_boss01_materials.py:226` | no | none found |
| `parameter_name` | `Scripts/Editor/build_boss01_materials.py:64`, `Scripts/Editor/build_boss01_materials.py:71`, `Scripts/Editor/build_boss01_materials.py:78`, `Scripts/Editor/make_flipbook_materials.py:68`, `Scripts/Editor/make_flipbook_materials.py:71`, `Scripts/Editor/make_flipbook_materials.py:51`, `Scripts/Editor/make_remains_material.py:112`, `Scripts/Editor/make_remains_material.py:64` | no | none found |
| `parent` | `Scripts/Editor/apply_perfect_arena.py:13`, `Scripts/Editor/build_boss01_materials.py:216`, `Scripts/Editor/dress_arena.py:95`, `Scripts/Editor/dress_arena.py:108`, `Scripts/Editor/make_flipbook_materials.py:93`, `Scripts/Editor/make_polish_materials.py:120`, `Scripts/Editor/make_polish_materials.py:129`, `Scripts/Editor/make_polish_materials.py:139`, `Scripts/Editor/make_polish_materials.py:149`, `Scripts/Editor/setup_m7_arena.py:44`, `Scripts/Editor/update_arena_v2.py:21` | yes | `Scripts/Editor/gate_material_probe.py:12`; `Scripts/Editor/inspect_arena.py:25`; `Scripts/Editor/inspect_arena.py:25`; `Scripts/Editor/inspect_arena_floor_actual.py:4`; `Scripts/Editor/inspect_dr_materials.py:9`; `Scripts/Editor/inspect_mats.py:18`; `Scripts/Editor/inspect_more_mats.py:9`; `Scripts/Editor/inspect_pillar_instances.py:10`; `Scripts/Editor/inspect_ruins_materials.py:7`; `Scripts/Editor/list_instances.py:9`; `Scripts/Editor/probe_mat_params.py:17` |
| `parent_class` | `Scripts/Editor/setup_m1_content.py:83`, `Scripts/Editor/setup_m3_content.py:322`, `Scripts/Editor/setup_m4_content.py:253` | no | `Scripts/Editor/inspect_pack_bp.py:24` |
| `parry_effect` | `Scripts/Editor/setup_input_fix.py:78` | no | none found |
| `parry_niagara` | `Scripts/Editor/setup_m7_content.py:90` | no | none found |
| `parry_sound` | `Scripts/Editor/setup_input_fix.py:76`, `Scripts/Editor/setup_m7_content.py:88` | no | none found |
| `phase_health_thresholds` | `Scripts/Editor/setup_m4_content.py:281` | no | none found |
| `phase_roar_montage` | `Scripts/Editor/sevarog_pack_06_director.py:23` | no | `Scripts/Editor/sevarog_pack_06_director.py:30` |
| `phase_transition_montage` | `Scripts/Editor/setup_m4_content.py:280` | no | none found |
| `pillar_material` | `Scripts/Editor/dress_arena.py:336` | no | `Scripts/Editor/check_floor.py:10` |
| `pitch_multiplier` | `Scripts/Editor/make_close_montages.py:74` | no | `Scripts/Editor/make_close_montages.py:74` |
| `play_rate` | `Scripts/Editor/rpg_content_lib.py:113` | no | none found |
| `poise_damage` | `Scripts/Editor/rpg_content_lib.py:110`, `Scripts/Editor/setup_m3_content.py:243`, `Scripts/Editor/setup_m4_content.py:222` | no | none found |
| `r` | `Scripts/Editor/build_boss01_materials.py:100`, `Scripts/Editor/hide_grey_builtin_weapons.py:14`, `Scripts/Editor/make_gate_rune_material.py:21`, `Scripts/Editor/make_gate_rune_material.py:27`, `Scripts/Editor/make_gate_rune_material.py:32`, `Scripts/Editor/make_gate_rune_material.py:37`, `Scripts/Editor/make_polish_materials.py:43`, `Scripts/Editor/make_polish_materials.py:47`, `Scripts/Editor/make_polish_materials.py:49`, `Scripts/Editor/make_polish_materials.py:75`, `Scripts/Editor/make_polish_materials.py:81`, `Scripts/Editor/make_polish_materials.py:86`, `Scripts/Editor/make_polish_materials.py:92`, `Scripts/Editor/make_polish_materials.py:111`, `Scripts/Editor/make_remains_material.py:71`, `Scripts/Editor/make_remains_material.py:73`, `Scripts/Editor/make_remains_material.py:59` | yes | none found |
| `radius` | `Scripts/Editor/setup_m4_content.py:173` | yes | none found |
| `real_time_capture` | `Scripts/Editor/atmosphere.py:88`, `Scripts/Editor/setup_m1_content.py:120` | no | none found |
| `relative_location` | `Scripts/Editor/setup_m1_content.py:62`, `Scripts/Editor/setup_m3_content.py:291`, `Scripts/Editor/setup_m4_content.py:265`, `Scripts/Editor/sevarog_pack_01_proxy.py:56`, `Scripts/Editor/sevarog_pack_03_info_style_pawn.py:54` | no | `Scripts/Editor/g0_pack_boss.py:62`; `Scripts/Editor/g0_weapon.py:25`; `Scripts/Editor/inspect_boss_components.py:17`; `Scripts/Editor/pie_boss_death.py:97`; `Scripts/Editor/pie_boss_death_states.py:96`; `Scripts/Editor/pie_camera_probe.py:33`; `Scripts/Editor/probe_player_comps.py:10`; `Scripts/Editor/review_report10.py:78`; `Scripts/Editor/review_report11.py:166`; `Scripts/Editor/review_report12c.py:31`; `Scripts/Editor/review_report12c.py:16`; `Scripts/Editor/review_report12c.py:24`; `Scripts/Editor/review_report13.py:68`; `Scripts/Editor/review_report13b.py:11`; `Scripts/Editor/setup_grey_player.py:8`; `Scripts/Editor/test_death_ue.py:31`; `Scripts/Editor/test_dormant_sword.py:9` |
| `relative_rotation` | `Scripts/Editor/setup_m1_content.py:63`, `Scripts/Editor/setup_m3_content.py:292`, `Scripts/Editor/setup_m4_content.py:266`, `Scripts/Editor/sevarog_pack_03_info_style_pawn.py:55` | no | `Scripts/Editor/probe_player_comps.py:10`; `Scripts/Editor/review_report12c.py:31`; `Scripts/Editor/review_report12c.py:16`; `Scripts/Editor/review_report12c.py:24`; `Scripts/Editor/review_report13.py:68`; `Scripts/Editor/review_report13b.py:11`; `Scripts/Editor/setup_grey_player.py:8`; `Scripts/Editor/test_death_ue.py:32`; `Scripts/Editor/test_dormant_sword.py:10` |
| `replace_existing` | `Scripts/Editor/import_arena_meshes.py:39` | no | none found |
| `rows` | `Scripts/Editor/set_health_multiplier.py:32`, `Scripts/Editor/set_weapon_windows.py:48` | yes | `Scripts/Editor/g3_probe_montages.py:110`; `Scripts/Editor/make_weapon_table.py:23`; `Scripts/Editor/make_weapon_table.py:14`; `Scripts/Editor/make_weapon_table.py:22`; `Scripts/Editor/set_health_multiplier.py:37`; `Scripts/Editor/set_health_multiplier.py:18`; `Scripts/Editor/set_weapon_windows.py:55`; `Scripts/Editor/set_weapon_windows.py:25` |
| `run_label` | `Scripts/Editor/setup_m6_content.py:20` | no | none found |
| `sample_data` | `Scripts/Editor/fix_grey_blendspaces.py:40` | no | `Scripts/Editor/fix_grey_blendspaces.py:17`; `Scripts/Editor/fix_grey_blendspaces.py:27` |
| `sampler_type` | `Scripts/Editor/build_boss01_materials.py:80` | no | none found |
| `save` | `Scripts/Editor/import_arena_meshes.py:41` | yes | none found |
| `saved_looping` | `Scripts/Editor/build_asset_proof_map.py:137` | no | none found |
| `saved_playing` | `Scripts/Editor/build_asset_proof_map.py:138` | no | none found |
| `scale` | `Scripts/Editor/setup_m4_content.py:192`, `Scripts/Editor/sevarog_pack_05_parity.py:73`, `Scripts/Editor/sevarog_pack_10_combo_telegraph.py:71` | yes | none found |
| `second_fog_data` | `Scripts/Editor/debug_atmos.py:17` | no | `Scripts/Editor/atmosphere.py:110`; `Scripts/Editor/debug_atmos.py:15` |
| `sets` | `Scripts/Editor/dress_arena.py:355` | yes | none found |
| `settings` | `Scripts/Editor/atmosphere.py:163` | yes | `Scripts/Editor/atmosphere.py:139` |
| `shading_model` | `Scripts/Editor/make_flipbook_materials.py:39`, `Scripts/Editor/make_polish_materials.py:39`, `Scripts/Editor/setup_m7_beam_materials.py:31` | no | none found |
| `should_retarget` | `Scripts/Editor/import_boss01_clips_r14.py:48`, `Scripts/Editor/probe_death_pose.py:8`, `Scripts/Editor/review_report11.py:64`, `Scripts/Editor/review_report11b.py:15`, `Scripts/Editor/review_report11c.py:13`, `Scripts/Editor/review_report12.py:70`, `Scripts/Editor/review_report12b.py:15`, `Scripts/Editor/review_report12c.py:40`, `Scripts/Editor/review_report13.py:91`, `Scripts/Editor/review_report13b.py:25`, `Scripts/Editor/review_report13b.py:55`, `Scripts/Editor/test_death_ue.py:26`, `Scripts/Editor/test_dormant_sword.py:19` | no | none found |
| `size_max` | `Scripts/Editor/dress_arena.py:426` | no | none found |
| `size_min` | `Scripts/Editor/dress_arena.py:425` | no | none found |
| `skeletal_mesh_asset` | `Scripts/Editor/build_asset_proof_map.py:124`, `Scripts/Editor/setup_grey_player.py:11`, `Scripts/Editor/setup_m1_content.py:59`, `Scripts/Editor/setup_m3_content.py:290`, `Scripts/Editor/setup_m4_content.py:264`, `Scripts/Editor/sevarog_pack_03_info_style_pawn.py:53` | no | `Scripts/Editor/g0_pack_boss.py:59`; `Scripts/Editor/g0_pack_boss.py:79`; `Scripts/Editor/inspect_pack_boss.py:23`; `Scripts/Editor/pie_boss_look.py:124`; `Scripts/Editor/pie_grey_check.py:87`; `Scripts/Editor/pie_grey_weapons.py:76`; `Scripts/Editor/pie_grey_weapons.py:76`; `Scripts/Editor/pie_pack_fight.py:99`; `Scripts/Editor/pie_pack_fight.py:100`; `Scripts/Editor/pie_sevarog_pack.py:167`; `Scripts/Editor/setup_grey_player.py:8`; `Scripts/Editor/setup_grey_player.py:14` |
| `skeleton` | `Scripts/Editor/import_boss01.py:36`, `Scripts/Editor/import_boss01.py:65`, `Scripts/Editor/import_boss01.py:129`, `Scripts/Editor/import_boss01_clips_r12.py:38`, `Scripts/Editor/import_boss01_clips_r14.py:24`, `Scripts/Editor/review_report10.py:94`, `Scripts/Editor/review_report10.py:34`, `Scripts/Editor/review_report11.py:40`, `Scripts/Editor/review_report12.py:46`, `Scripts/Editor/review_report13.py:35`, `Scripts/Editor/test_death_ue.py:19` | yes | `Scripts/Editor/compare_skeletons.py:18`; `Scripts/Editor/compare_skeletons.py:18`; `Scripts/Editor/copy_sockets_to_greystone.py:13`; `Scripts/Editor/g0_pack_boss.py:26`; `Scripts/Editor/g1_sevarog_slots.py:10`; `Scripts/Editor/g2_probe_a4a5.py:8`; `Scripts/Editor/import_all_builds.py:55`; `Scripts/Editor/import_boss01.py:138`; `Scripts/Editor/import_boss01.py:138`; `Scripts/Editor/inspect_greystone_combat.py:29`; `Scripts/Editor/inspect_m7_assets.py:49`; `Scripts/Editor/probe_skel.py:8`; `Scripts/Editor/review_report12c.py:11`; `Scripts/Editor/review_report13.py:55`; `Scripts/Editor/test_death_ue.py:19`; `Scripts/Editor/test_import_skm.py:33`; `Scripts/Editor/verify_builds.py:29` |
| `skinned_asset` | `Scripts/Editor/setup_m1_content.py:61` | no | none found |
| `smoke_template` | `Scripts/Editor/dress_arena.py:380` | no | none found |
| `socket_name` | `Scripts/Editor/import_boss01.py:113`, `Scripts/Editor/sevarog_pack_01_proxy.py:55` | no | `Scripts/Editor/g0_pack_boss.py:40`; `Scripts/Editor/g0_weapon.py:18`; `Scripts/Editor/g0_weapon.py:14`; `Scripts/Editor/g1_sevarog_slots.py:8`; `Scripts/Editor/import_boss01.py:111`; `Scripts/Editor/import_boss01.py:115`; `Scripts/Editor/inspect_boss_components.py:19`; `Scripts/Editor/probe_grey_sockets.py:5`; `Scripts/Editor/probe_skel.py:7`; `Scripts/Editor/review_report12c.py:16` |
| `sound` | `Scripts/Editor/make_close_montages.py:74`, `Scripts/Editor/setup_m4_content.py:181`, `Scripts/Editor/sevarog_pack_05_parity.py:70`, `Scripts/Editor/sevarog_pack_05_parity.py:88` | yes | `Scripts/Editor/make_close_montages.py:74` |
| `source_animation` | `Scripts/Editor/make_close_montages.py:48`, `Scripts/Editor/make_death_montage.py:15`, `Scripts/Editor/rpg_content_lib.py:74`, `Scripts/Editor/rpg_content_lib.py:99`, `Scripts/Editor/setup_m3_content.py:142`, `Scripts/Editor/setup_m4_content.py:148`, `Scripts/Editor/setup_m7_content.py:106`, `Scripts/Editor/sevarog_pack_05_parity.py:44`, `Scripts/Editor/sevarog_pack_05b_death_style.py:38`, `Scripts/Editor/sevarog_pack_08_turn.py:17`, `Scripts/Editor/sevarog_pack_09_charge.py:17` | no | none found |
| `spark_template` | `Scripts/Editor/dress_arena.py:382` | no | none found |
| `srgb` | `Scripts/Editor/build_boss01_materials.py:44`, `Scripts/Editor/build_boss01_materials.py:47`, `Scripts/Editor/build_boss01_materials.py:49`, `Scripts/Editor/import_ui_art.py:17`, `Scripts/Editor/make_flipbook_materials.py:24`, `Scripts/Editor/make_remains_material.py:28` | no | none found |
| `stagger_seconds` | `Scripts/Editor/pie_transition_rules.py:107`, `Scripts/Editor/pie_transition_rules.py:267`, `Scripts/Editor/pie_transition_rules.py:288`, `Scripts/Editor/pie_transition_rules.py:318`, `Scripts/Editor/pie_transition_rules.py:531`, `Scripts/Editor/pie_transition_rules.py:297`, `Scripts/Editor/pie_transition_rules.py:380`, `Scripts/Editor/pie_transition_rules.py:414`, `Scripts/Editor/pie_transition_rules.py:444`, `Scripts/Editor/pie_transition_rules.py:506`, `Scripts/Editor/pie_transition_rules.py:585`, `Scripts/Editor/pie_transition_rules.py:362`, `Scripts/Editor/pie_transition_rules.py:390`, `Scripts/Editor/pie_transition_rules.py:424` | no | `Scripts/Editor/pie_build_fight.py:1211` |
| `stale_grace_seconds` | `Scripts/Editor/pie_iframes.py:244`, `Scripts/Editor/pie_iframes.py:252` | no | none found |
| `stamina_cost` | `Scripts/Editor/rpg_content_lib.py:111`, `Scripts/Editor/setup_m3_content.py:244` | no | `Scripts/Editor/make_weapon_table.py:24` |
| `static_mesh` | `Scripts/Editor/sevarog_pack_03_info_style_pawn.py:63` | no | `Scripts/Editor/inspect_arena.py:12`; `Scripts/Editor/inspect_boss_components.py:16`; `Scripts/Editor/pie_boss_look.py:93`; `Scripts/Editor/pie_boss_look.py:125` |
| `stop_distance` | `Scripts/Editor/sevarog_pack_09_charge.py:28` | no | none found |
| `strike_bolt_effect` | `Scripts/Editor/greystone_sevarog_11_polish.py:40` | no | none found |
| `strike_telegraph_effect` | `Scripts/Editor/greystone_sevarog_11_polish.py:39` | no | none found |
| `style_aliases` | `Scripts/Editor/make_combat_catalog.py:58` | no | none found |
| `sway_degrees` | `Scripts/Editor/dress_arena.py:352` | no | none found |
| `sway_pivot` | `Scripts/Editor/dress_arena.py:353` | no | none found |
| `swing_sound` | `Scripts/Editor/setup_m5_content.py:130`, `Scripts/Editor/setup_m5_content.py:183` | no | none found |
| `swing_sound_variants` | `Scripts/Editor/setup_m7_content.py:73` | no | none found |
| `switch_weapon_action` | `Scripts/Editor/setup_m5_content.py:156` | no | none found |
| `template` | `Scripts/Editor/sevarog_pack_05_parity.py:117` | yes | `Scripts/Editor/inspect_bolt.py:20` |
| `test_freeze` | `Scripts/Editor/pie_a2_diag.py:64` | no | `Scripts/Editor/pie_build_fight.py:397` |
| `text` | `Scripts/Editor/build_asset_proof_map.py:93` | yes | none found |
| `texture` | `Scripts/Editor/build_boss01_materials.py:79`, `Scripts/Editor/make_remains_material.py:81`, `Scripts/Editor/make_remains_material.py:102` | yes | none found |
| `trace_base_socket` | `Scripts/Editor/setup_m3_content.py:260`, `Scripts/Editor/setup_m4_content.py:236`, `Scripts/Editor/setup_m5_content.py:124` | no | none found |
| `trace_radius` | `Scripts/Editor/setup_m3_content.py:262`, `Scripts/Editor/setup_m4_content.py:238`, `Scripts/Editor/setup_m5_content.py:126` | no | none found |
| `trace_samples` | `Scripts/Editor/setup_m3_content.py:263`, `Scripts/Editor/setup_m4_content.py:239`, `Scripts/Editor/setup_m5_content.py:127` | no | none found |
| `trace_tip_socket` | `Scripts/Editor/setup_m3_content.py:261`, `Scripts/Editor/setup_m4_content.py:237`, `Scripts/Editor/setup_m5_content.py:125` | no | none found |
| `two_sided` | `Scripts/Editor/build_boss01_materials.py:132`, `Scripts/Editor/build_boss01_materials.py:227`, `Scripts/Editor/make_flipbook_materials.py:41`, `Scripts/Editor/make_polish_materials.py:67`, `Scripts/Editor/make_remains_material.py:49`, `Scripts/Editor/setup_m7_beam_materials.py:33` | no | none found |
| `unblockable` | `Scripts/Editor/rpg_content_lib.py:112` | no | none found |
| `unbound` | `Scripts/Editor/atmosphere.py:138` | yes | none found |
| `use_t0_as_ref_pose` | `Scripts/Editor/import_all_builds.py:42`, `Scripts/Editor/test_import_skm.py:24` | no | none found |
| `use_temperature` | `Scripts/Editor/atmosphere.py:58` | no | none found |
| `value_type` | `Scripts/Editor/setup_input_fix.py:52`, `Scripts/Editor/setup_m3_content.py:114`, `Scripts/Editor/setup_m5_content.py:91` | no | `Scripts/Editor/inspect_actions.py:12`; `Scripts/Editor/inspect_imc.py:22` |
| `vertex_color` | `Scripts/Editor/export_greystone.py:20`, `Scripts/Editor/export_mannequin.py:20`, `Scripts/Editor/export_quinn.py:20` | no | none found |
| `visibility_based_anim_tick_option` | `Scripts/Editor/build_asset_proof_map.py:129` | no | none found |
| `visible` | `Scripts/Editor/dress_arena.py:452`, `Scripts/Editor/hide_comp.py:7`, `Scripts/Editor/sevarog_pack_03_info_style_pawn.py:64`, `Scripts/Editor/sevarog_pack_05_parity.py:120` | yes | `Scripts/Editor/inspect_boss_components.py:17` |
| `volumetric_scattering_intensity` | `Scripts/Editor/atmosphere.py:61` | no | none found |
| `weapon` | `Scripts/Editor/setup_m3_content.py:301`, `Scripts/Editor/setup_m4_content.py:275`, `Scripts/Editor/setup_m5_content.py:159` | yes | `Scripts/Editor/make_weapon_table.py:24`; `Scripts/Editor/pie_weapons_smoke.py:94`; `Scripts/Editor/set_health_multiplier.py:21`; `Scripts/Editor/set_health_multiplier.py:39`; `Scripts/Editor/set_weapon_windows.py:29`; `Scripts/Editor/set_weapon_windows.py:57`; `Scripts/Editor/setup_m5_content.py:178` |
| `weapons` | `Scripts/Editor/setup_m5_content.py:157` | yes | none found |
| `wind` | `Scripts/Editor/dress_arena.py:437` | yes | none found |
| `window_end_time` | `Scripts/Editor/sevarog_pack_09_charge.py:30` | no | none found |
| `world_size` | `Scripts/Editor/build_asset_proof_map.py:94` | no | none found |

## Findings requiring follow-up

**UNSUPPORTED / unverified:** any inventory row with `C++ text occurrence = no` and `Getter site in same script = none found` lacks both repository C++ text precedent and a same-script getter candidate. This is not proof the name is invalid: the field may be defined by Unreal, the pack plugin, or a Blueprint, which this static pass cannot inspect. These rows should be validated against the target object’s reflected fields or through a guarded readback before the scripts are treated as safe to rerun.

- Unverified by those two static signals: 153 of 261 distinct names. See the exact write sites in the inventory above.
- High-risk spelling candidate: `Scripts/Editor/sevarog_pack_07_bolt_impact.py:33` sets `Damage Gampelay Effect`. No C++ source/header spelling or same-script getter was found; “Gampelay” may be a misspelling, but the intended plugin field cannot be established without inspecting the reflected data object. Do not silently change the field name based on this scan.
- Other representative unverified plugin/Blueprint fields include `Anim Class` (`sevarog_pack_03_info_style_pawn.py:72`), `Anim Layer Class` (`:43`), `Attack Impact Effects` (`sevarog_pack_07_bolt_impact.py:34`), and `Close Anim Montage` (`sevarog_pack_10_combo_telegraph.py:36`). The inventory records all remaining names and call sites.

## Files not parsed

- `Scripts\Editor\sevarog_pack_02_montages_abilities.py`: `unexpected indent (<unknown>, line 215)`

## Disposition

S164 acceptance is **not met by static repository evidence alone**: the scan records source-text occurrences and candidate same-script getters for every literal setter, but cannot establish reflected fields for the unverified rows, content-only properties, or dynamic property expressions. The immediate priority for Lead’s review is the `Damage Gampelay Effect` setter and the unverified map of plugin/Blueprint names. No source property strings were changed; no tests/build/editor/runtime were run.
