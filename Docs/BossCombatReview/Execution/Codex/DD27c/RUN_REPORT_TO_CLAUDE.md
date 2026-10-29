# DD27c C307 — measured instance reflection probe

One launch, stage1+stage2 `--instances`, no retry, toolkit edit, authoring helper, build, tests, asset creation or save. Pending Claude review; reflection observations are not authoring/gameplay acceptance.

Preflight read the exact probe hash from AuthoringToolkit/evidence_sha256.txt and matched current bytes. The wrapper calls preflight first, throws on any nonzero exit, requires preflight_verified.json, rehashes the fresh pre-state and probe, and checks processes again BEFORE Start-Process. This fixes the control-flow path for this run; DD27b's historical missing-pre-state finding remains recorded.

Exact command/executable/arguments: command.json; invocation wrapper run_once.ps1. `UnrealEditor-Cmd.exe OneBossFight.uproject -ExecutePythonScript="<AuthoringToolkit>/probe_unreal_api.py --instances" -unattended -nullrhi -nosound -nosplash -abslog=<DD27c>/editor_raw.log`. No --output.

Process exit=0; elapsed=24.262s. Helper emitted stage1 summary ['[PROBE] SUMMARY missing=2 present=53'] and completed stage2 through module-level editor query; no Python Error traceback / SystemExit1 observed. All 1666 PROBE lines extracted verbatim, SHA256 `4ad279a4d302e5b44edfc12d7c6f937100b4f5f3019335fb94cceb99e6da7137`. Error severity=0; Warning severity=17; every Error line below. TraceServer Error0x5 remains Warning severity, not an Error-severity line. The summary counts refer to stage1 API lookup, not property success.

```

```

Fresh BEFORE and AFTER: 212 Source files match DD26 post manifest; 11,752 Content files have equal path+size inventories,16 Data hashes equal; Config hashes, toolkit Python/input pins and binaries equal; HEAD bc3fe6a both. Processes empty before/after; tracked Content/Config/Source status empty and Content status equal. No differences outside Saved under the specified captures: {}. Content outside Data was not all hashed, so equal path/size is not a full byte-level proof. No unexpected repository content mutation is claimed absent solely from git's ignored pack folders.

Saved: 1 new and 3 changed files, enumerated in state_diff.json and SHA-pinned in saved_findings_sha256.json. Preserved in place, no cleanup. These editor side effects are not hidden by the unchanged Content result.

Raw editor log SHA256 `47ad8f3d3bb674668ae080acb09e92634633201f41e9d5bfc4defe6e46428354`. Observed 123 successful instance-property reads across 17 structs; 0 instance error lines; 22 CDO lines. Requested quotations follow WITHOUT interpretation:

```
Every instance error
(none)

One successful property line per struct
[PROBE] INSTANCE RPGBleedConfig prop=effect_height get_editor_property=ok hasattr=False value=170
[PROBE] INSTANCE RPGCloseClipSwapConfig prop=a1_montage get_editor_property=ok hasattr=False
[PROBE] INSTANCE RPGDeathConfig prop=blend_in_seconds get_editor_property=ok hasattr=False value=0.1
[PROBE] INSTANCE RPGDormantWakeConfig prop=dormant_clip get_editor_property=ok hasattr=False
[PROBE] INSTANCE RPGEncounterPolicyConfig prop=gate_radius get_editor_property=ok hasattr=False value=1200
[PROBE] INSTANCE RPGParityField prop=destination get_editor_property=ok hasattr=False
[PROBE] INSTANCE RPGFireballConfig prop=fireball_ability get_editor_property=ok hasattr=False
[PROBE] INSTANCE RPGHealPunishConfig prop=aim_height get_editor_property=ok hasattr=False value=100
[PROBE] INSTANCE RPGLookConfig prop=body get_editor_property=ok hasattr=False
[PROBE] INSTANCE RPGLowSweepConfig prop=blade_height get_editor_property=ok hasattr=False value=40
[PROBE] INSTANCE RPGPhaseDependencyConfig prop=immunity_effect get_editor_property=ok hasattr=False
[PROBE] INSTANCE RPGPhaseFlowConfig prop=attack_ability_prefix get_editor_property=ok hasattr=False
[PROBE] INSTANCE RPGPhaseConfig prop=attack_multiplier get_editor_property=ok hasattr=False value=1
[PROBE] INSTANCE RPGShockwaveConfig prop=damage get_editor_property=ok hasattr=False value=48
[PROBE] INSTANCE RPGStaggerPolicyConfig prop=cooldown_seconds get_editor_property=ok hasattr=False value=0
[PROBE] INSTANCE RPGStaggerProfileConfig prop=critical_on_every_hit get_editor_property=ok hasattr=False
[PROBE] INSTANCE RPGBossStatsConfig prop=max_health get_editor_property=ok hasattr=False value=0

Float-valued property lines
[PROBE] INSTANCE RPGBleedConfig prop=effect_height get_editor_property=ok hasattr=False value=170
[PROBE] INSTANCE RPGBleedConfig prop=hp_fraction get_editor_property=ok hasattr=False value=0.03
[PROBE] INSTANCE RPGBleedConfig prop=initial_threshold get_editor_property=ok hasattr=False value=100
[PROBE] INSTANCE RPGBleedConfig prop=threshold_increase get_editor_property=ok hasattr=False value=20
[PROBE] INSTANCE RPGBleedConfig prop=threshold_max get_editor_property=ok hasattr=False value=200
[PROBE] INSTANCE RPGDeathConfig prop=blend_in_seconds get_editor_property=ok hasattr=False value=0.1
[PROBE] INSTANCE RPGDeathConfig prop=dying_seconds get_editor_property=ok hasattr=False value=2.5
[PROBE] INSTANCE RPGDeathConfig prop=hold_at_seconds get_editor_property=ok hasattr=False value=3
[PROBE] INSTANCE RPGDeathConfig prop=pack_end_time_multiplier get_editor_property=ok hasattr=False value=0
[PROBE] INSTANCE RPGDeathConfig prop=pack_poll_seconds get_editor_property=ok hasattr=False value=1
[PROBE] INSTANCE RPGEncounterPolicyConfig prop=gate_radius get_editor_property=ok hasattr=False value=1200
[PROBE] INSTANCE RPGFireballConfig prop=fireball_max_range get_editor_property=ok hasattr=False value=1800
[PROBE] INSTANCE RPGFireballConfig prop=fireball_min_range get_editor_property=ok hasattr=False value=500
[PROBE] INSTANCE RPGHealPunishConfig prop=aim_height get_editor_property=ok hasattr=False value=100
[PROBE] INSTANCE RPGHealPunishConfig prop=cooldown get_editor_property=ok hasattr=False value=4
[PROBE] INSTANCE RPGHealPunishConfig prop=damage get_editor_property=ok hasattr=False value=12
[PROBE] INSTANCE RPGHealPunishConfig prop=flight_time get_editor_property=ok hasattr=False value=1.2
[PROBE] INSTANCE RPGHealPunishConfig prop=javelin_max_range get_editor_property=ok hasattr=False value=3000
[PROBE] INSTANCE RPGHealPunishConfig prop=javelin_radius get_editor_property=ok hasattr=False value=25
[PROBE] INSTANCE RPGHealPunishConfig prop=max_range get_editor_property=ok hasattr=False value=1000
[PROBE] INSTANCE RPGHealPunishConfig prop=max_speed get_editor_property=ok hasattr=False value=2500
[PROBE] INSTANCE RPGHealPunishConfig prop=min_range get_editor_property=ok hasattr=False value=400
[PROBE] INSTANCE RPGHealPunishConfig prop=min_speed get_editor_property=ok hasattr=False value=450
[PROBE] INSTANCE RPGLowSweepConfig prop=blade_height get_editor_property=ok hasattr=False value=40
[PROBE] INSTANCE RPGLowSweepConfig prop=damage get_editor_property=ok hasattr=False value=20
[PROBE] INSTANCE RPGLowSweepConfig prop=inner_radius get_editor_property=ok hasattr=False value=60
[PROBE] INSTANCE RPGLowSweepConfig prop=reach get_editor_property=ok hasattr=False value=380
[PROBE] INSTANCE RPGLowSweepConfig prop=sweep_from_degrees get_editor_property=ok hasattr=False value=90
[PROBE] INSTANCE RPGLowSweepConfig prop=sweep_to_degrees get_editor_property=ok hasattr=False value=-90
[PROBE] INSTANCE RPGPhaseFlowConfig prop=transition_seconds get_editor_property=ok hasattr=False value=1.8
[PROBE] INSTANCE RPGPhaseConfig prop=attack_multiplier get_editor_property=ok hasattr=False value=1
[PROBE] INSTANCE RPGPhaseConfig prop=entry_health_fraction get_editor_property=ok hasattr=False value=0
[PROBE] INSTANCE RPGPhaseConfig prop=rate_multiplier get_editor_property=ok hasattr=False value=1
[PROBE] INSTANCE RPGPhaseConfig prop=speed_multiplier get_editor_property=ok hasattr=False value=1
[PROBE] INSTANCE RPGShockwaveConfig prop=damage get_editor_property=ok hasattr=False value=48
[PROBE] INSTANCE RPGShockwaveConfig prop=jump_clearance get_editor_property=ok hasattr=False value=50
[PROBE] INSTANCE RPGShockwaveConfig prop=max_radius get_editor_property=ok hasattr=False value=1100
[PROBE] INSTANCE RPGShockwaveConfig prop=speed get_editor_property=ok hasattr=False value=1000
[PROBE] INSTANCE RPGShockwaveConfig prop=start_radius get_editor_property=ok hasattr=False value=200
[PROBE] INSTANCE RPGShockwaveConfig prop=thickness get_editor_property=ok hasattr=False value=180
[PROBE] INSTANCE RPGStaggerPolicyConfig prop=cooldown_seconds get_editor_property=ok hasattr=False value=0
[PROBE] INSTANCE RPGStaggerPolicyConfig prop=critical_multiplier get_editor_property=ok hasattr=False value=2.5
[PROBE] INSTANCE RPGStaggerPolicyConfig prop=freeze_at_position get_editor_property=ok hasattr=False value=1.55
[PROBE] INSTANCE RPGStaggerPolicyConfig prop=get_up_rate get_editor_property=ok hasattr=False value=0.6
[PROBE] INSTANCE RPGStaggerPolicyConfig prop=riposte_align_seconds get_editor_property=ok hasattr=False value=0.3
[PROBE] INSTANCE RPGStaggerPolicyConfig prop=riposte_arm_seconds get_editor_property=ok hasattr=False value=1.2
[PROBE] INSTANCE RPGStaggerPolicyConfig prop=riposte_base_damage get_editor_property=ok hasattr=False value=40
[PROBE] INSTANCE RPGStaggerPolicyConfig prop=riposte_cone_degrees get_editor_property=ok hasattr=False value=120
[PROBE] INSTANCE RPGStaggerPolicyConfig prop=riposte_facing_degrees get_editor_property=ok hasattr=False value=120
[PROBE] INSTANCE RPGStaggerPolicyConfig prop=riposte_impact_seconds get_editor_property=ok hasattr=False value=0.8
[PROBE] INSTANCE RPGStaggerPolicyConfig prop=riposte_player_start_gap get_editor_property=ok hasattr=False value=150
[PROBE] INSTANCE RPGStaggerPolicyConfig prop=riposte_range get_editor_property=ok hasattr=False value=150
[PROBE] INSTANCE RPGStaggerPolicyConfig prop=stagger_seconds get_editor_property=ok hasattr=False value=2.5
[PROBE] INSTANCE RPGBossStatsConfig prop=max_health get_editor_property=ok hasattr=False value=0
[PROBE] INSTANCE RPGBossStatsConfig prop=max_posture get_editor_property=ok hasattr=False value=0
[PROBE] INSTANCE RPGBossStatsConfig prop=posture_regen_delay get_editor_property=ok hasattr=False value=0
[PROBE] INSTANCE RPGBossStatsConfig prop=posture_regen_rate get_editor_property=ok hasattr=False value=0

Array/enum type lines
[PROBE] INSTANCE RPGDeathConfig prop=death_mode get_editor_property=ok hasattr=False type=RPGBossDeathMode
[PROBE] INSTANCE RPGHealPunishConfig prop=spawn_sockets get_editor_property=ok hasattr=False type=Array
[PROBE] INSTANCE RPGLookConfig prop=pieces get_editor_property=ok hasattr=False type=Array

Definition CDO lines (includes soft paths and nested structs)
[PROBE] CDO RPGBossDefinition prop=schema get_editor_property=ok type=int
[PROBE] CDO RPGBossDefinition prop=definition_id get_editor_property=ok type=Name
[PROBE] CDO RPGBossDefinition prop=presentation_id get_editor_property=ok type=Name
[PROBE] CDO RPGBossDefinition prop=skeleton get_editor_property=ok type=NoneType
[PROBE] CDO RPGBossDefinition prop=animations get_editor_property=ok type=Array
[PROBE] CDO RPGBossDefinition prop=phases get_editor_property=ok type=Array
[PROBE] CDO RPGBossDefinition prop=fields get_editor_property=ok type=Array
[PROBE] CDO RPGBossDefinition prop=stats get_editor_property=ok type=RPGBossStatsConfig
[PROBE] CDO RPGBossDefinition prop=encounter_policy get_editor_property=ok type=RPGEncounterPolicyConfig
[PROBE] CDO RPGBossDefinition prop=stagger_policy get_editor_property=ok type=RPGStaggerPolicyConfig
[PROBE] CDO RPGBossDefinition prop=phase_flow get_editor_property=ok type=RPGPhaseFlowConfig
[PROBE] CDO RPGBossDefinition prop=fireball get_editor_property=ok type=RPGFireballConfig
[PROBE] CDO RPGBossDefinition prop=phase_dependencies get_editor_property=ok type=RPGPhaseDependencyConfig
[PROBE] CDO RPGBossDefinition prop=stagger_profile get_editor_property=ok type=RPGStaggerProfileConfig
[PROBE] CDO RPGBossDefinition prop=dormant_wake get_editor_property=ok type=RPGDormantWakeConfig
[PROBE] CDO RPGBossDefinition prop=bleed get_editor_property=ok type=RPGBleedConfig
[PROBE] CDO RPGBossDefinition prop=low_sweep get_editor_property=ok type=RPGLowSweepConfig
[PROBE] CDO RPGBossDefinition prop=shockwave get_editor_property=ok type=RPGShockwaveConfig
[PROBE] CDO RPGBossDefinition prop=heal_punish get_editor_property=ok type=RPGHealPunishConfig
[PROBE] CDO RPGBossDefinition prop=look get_editor_property=ok type=RPGLookConfig
[PROBE] CDO RPGBossDefinition prop=close_clip_swap get_editor_property=ok type=RPGCloseClipSwapConfig
[PROBE] CDO RPGBossDefinition prop=death get_editor_property=ok type=RPGDeathConfig

Module-level editor query
[PROBE] unreal.is_editor exists=True callable=True type=builtin_function_or_method
[PROBE] INSTANCE_CALL call: unreal.is_editor() [read-only editor mode query]
[PROBE] unreal.is_editor() result=True
```

Limits: in-memory reflection report only. No property write, asset creation/readback, persistent definition, compiler/preflight/preparation integration, gameplay/PIE/networking/package proof. Any missing type observations and class-dir MISMATCH lines remain in complete probe_lines.txt; no filtering of the raw report. Await lead-selected bounded toolkit correction and separate authoring rerun release.
