import json
import os
import traceback
import unreal

ROOT = 'C:/UnrealProject/OneBossFight'
TASK_DIR = ROOT + '/Docs/BossCombatReview/Execution/Codex/PACK_ARENA_DRIVER'
CONFIG_PATH = TASK_DIR + '/current_config.json'
MAP_PATH = '/Game/OneBossFight/Levels/L_SevarogArena'
IA_PATHS = {
    'parry': '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Parry.IA_Parry',
    'block': '/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Block.IA_Block',
}
BOSS_CLASS_NAME = 'BP_SevarogBossPack_C'
S = {'phase': 'load', 'elapsed': 0.0, 'play_elapsed': 0.0, 'handle': None, 'last_montage': None,
     'montage_started_at': None, 'parry_sent': set(), 'hold_until': -1.0, 'preflight_logged': False,
     'last_health': None, 'last_stamina': None, 'last_sample': -1.0, 'gate_elapsed': 0.0,
     'binding_logged': False, 'combat_requested': False}


def log(text):
    unreal.log('[PACK_ARENA_DRIVER] ' + str(text))


def read_attr(actor, tag_name, current=True):
    comps = actor.get_components_by_class(unreal.ActorComponent) if actor else []
    comp = next((c for c in comps if c.get_class().get_name() == 'BP_AttributesComponent_C'), None)
    if comp is None:
        return None
    tag = unreal.GameplayTag()
    tag.import_text('(TagName="%s")' % tag_name)
    try:
        method = 'Get Current Attribute Value' if current else 'GetMaxAttributeValue'
        return float(comp.call_method(method, args=(tag,)))
    except Exception as exc:
        log('attribute_read_failed tag=%s error=%s' % (tag_name, str(exc)[:100]))
        return None


def montage(actor):
    try:
        meshes = actor.get_components_by_class(unreal.SkeletalMeshComponent)
        inst = meshes[0].get_anim_instance() if meshes else None
        active = inst.get_current_active_montage() if inst else None
        if active is None:
            return None, None
        return active.get_name(), float(inst.montage_get_position(active))
    except Exception as exc:
        return 'READ_ERROR:' + str(exc)[:80], None


def all_world_actors(world):
    try:
        return unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
    except Exception as exc:
        log('actor_inventory_failed error=%s' % str(exc)[:120])
        return []


def player_parry_component(pawn):
    comps = pawn.get_components_by_class(unreal.ActorComponent) if pawn else []
    return next((c for c in comps if c.get_class().get_name() == 'RPGPlayerParry'), None)


def read_tag(actor, name):
    if actor is None:
        return None
    tag = unreal.GameplayTag()
    tag.import_text('(TagName="%s")' % name)
    try:
        return bool(actor.call_method('HasMatchingGameplayTag', args=(tag,)))
    except Exception:
        try:
            return bool(actor.call_method('Has Matching Gameplay Tag', args=(tag,)))
        except Exception:
            return None


def parry_open(component):
    if component is None:
        return None
    try:
        return bool(component.call_method('IsWindowOpen'))
    except Exception as exc:
        log('parry_window_read_failed error=%s' % str(exc)[:100])
        return None


def player_style(pawn):
    try:
        loadout = pawn.get_component_by_class(unreal.RPGBuildLoadout)
        return str(loadout.get_actual_style_name()) if loadout else 'UNKNOWN_NO_LOADOUT'
    except Exception as exc:
        return 'UNKNOWN:' + str(exc)[:80]


def game_world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()


def get_pair(world):
    actors = all_world_actors(world)
    boss = next((a for a in actors if a.get_class().get_name() == BOSS_CLASS_NAME), None)
    pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
    pawn = pc.get_controlled_pawn() if pc else None
    return boss, pc, pawn


def end_play(reason):
    if S['phase'] in ('end', 'quit', 'done'):
        return
    log('ending reason=%s; no actors/assets were spawned or saved by this driver' % reason)
    try:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    except Exception as exc:
        log('end_play_request_failed error=%s' % str(exc)[:100])
    S['phase'] = 'quit'
    S['elapsed'] = 0.0


def tick(dt):
    try:
        if S['phase'] == 'load':
            with open(CONFIG_PATH, 'r', encoding='utf-8-sig') as stream:
                cfg = json.load(stream)
            S['config'] = cfg
            if cfg.get('mode') not in ('control', 'block', 'parry'):
                raise ValueError('mode must be control, block, or parry')
            if cfg.get('duration_seconds', 75) < 15 or cfg.get('duration_seconds', 75) > 180:
                raise ValueError('duration_seconds must be within 15..180')
            loaded = unreal.EditorLevelLibrary.load_level(MAP_PATH)
            if not loaded:
                raise RuntimeError('could not load required arena map ' + MAP_PATH)
            editor_world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
            package = editor_world.get_outermost().get_name() if editor_world else 'UNKNOWN'
            log('preflight run_id=%s map=%s expected=%s mode=%s config=%s' % (cfg.get('run_id'), package, MAP_PATH, cfg['mode'], CONFIG_PATH))
            if package != MAP_PATH:
                raise RuntimeError('loaded map package mismatch: ' + package)
            S['phase'] = 'begin'
            S['elapsed'] = 0.0
            return
        if S['phase'] == 'begin':
            S['elapsed'] += dt
            if S['elapsed'] >= 0.5:
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
                log('PIE begin requested mode=%s' % S['config']['mode'])
                S['phase'] = 'observe'
                S['elapsed'] = 0.0
            return
        if S['phase'] == 'quit':
            S['elapsed'] += dt
            if S['elapsed'] >= 1.5:
                log('editor quit requested after normal PIE end')
                if S['handle'] is not None:
                    try:
                        unreal.unregister_slate_post_tick_callback(S['handle'])
                    except Exception as exc:
                        log('callback_cleanup_failed error=%s' % str(exc)[:100])
                    S['handle'] = None
                unreal.SystemLibrary.execute_console_command(None, 'QUIT_EDITOR')
                S['phase'] = 'done'
            return
        if S['phase'] != 'observe':
            return

        S['elapsed'] += dt
        S['play_elapsed'] += dt
        world = game_world()
        if world is None:
            if S['play_elapsed'] > 10.0:
                raise RuntimeError('PIE world/player not available')
            return
        boss, pc, pawn = get_pair(world)
        if pawn is None or boss is None:
            if S['play_elapsed'] > 10.0:
                raise RuntimeError('required possessed player or actual BP_SevarogBossPack_C not found')
            return

        parry = player_parry_component(pawn)
        health = read_attr(pawn, 'Attribute.Health')
        stamina = read_attr(pawn, 'Attribute.Stamina')
        health_max = read_attr(pawn, 'Attribute.Health', False)
        stamina_max = read_attr(pawn, 'Attribute.Stamina', False)
        current_montage, montage_pos = montage(boss)
        style = player_style(pawn)
        if not S['preflight_logged']:
            S['preflight_logged'] = True
            log('identity map=%s boss=%s boss_class=%s boss_loc=%s player=%s player_class=%s player_loc=%s style=%s health=%s/%s stamina=%s/%s parry_component=%s' % (
                world.get_outermost().get_name(), boss.get_name(), boss.get_class().get_name(), boss.get_actor_location(),
                pawn.get_name(), pawn.get_class().get_name(), pawn.get_actor_location(), style, health, health_max,
                stamina, stamina_max, parry.get_class().get_name() if parry else 'MISSING'))
            if parry is None:
                log('SETUP_INCONCLUSIVE missing URPGPlayerParry; no parry input will be injected')
                end_play('missing parry component')
                return
            if style not in ('SwordCombatStyle', 'ClaymoreCombatStyle'):
                log('SETUP_INCONCLUSIVE style does not match the granted parry routes: %s' % style)
                end_play('unsupported parry style')
                return

        director = next((c for c in boss.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == 'RPGSevarogDirector'), None)
        gate_open = None
        if director:
            try:
                gate_open = bool(director.is_gate_open())
            except Exception:
                try:
                    gate_open = bool(director.call_method('IsGateOpen'))
                except Exception:
                    gate_open = None
        if gate_open is not True and S['gate_elapsed'] < 12.0:
            to_boss = boss.get_actor_location() - pawn.get_actor_location()
            if to_boss.length() > 5.0:
                pawn.add_movement_input(unreal.Vector(to_boss.x, to_boss.y, 0.0).normal(), 1.0, False)
            S['gate_elapsed'] += dt
            return

        if current_montage != S['last_montage']:
            S['last_montage'] = current_montage
            S['montage_started_at'] = S['play_elapsed'] if current_montage else None
            log('boss_montage name=%s position=%s game_elapsed=%.4f player_distance=%.2f' % (
                current_montage, montage_pos, S['play_elapsed'], (boss.get_actor_location() - pawn.get_actor_location()).length()))
        asc = next((c for c in pawn.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == 'BP_AdvancedAbilitySystemComponent_C'), None)
        if asc is not None and not S['combat_requested'] and (boss.get_actor_location() - pawn.get_actor_location()).length() < 420.0:
            tags = unreal.GameplayTagContainer()
            tags.import_text('(GameplayTags=((TagName="Ability.EnterCombat")))')
            try:
                result = asc.call_method('Try Activate Abilities By Tag', args=(tags,))
                log('real_enter_combat_requested result=%s style=%s' % (result, style))
                S['combat_requested'] = True
            except Exception as exc:
                log('enter_combat_request_failed error=%s' % str(exc)[:100])
        action_mode = S['config']['mode']
        if action_mode == 'parry' and not S['binding_logged']:
            try:
                log_path = S['config'].get('editor_log_path', '')
                with open(log_path, 'r', encoding='utf-8', errors='replace') as stream:
                    log_text = stream.read()
                marker = 'parry window bound to IA_Parry' if action_mode == 'parry' else 'IA_Block'
                if marker in log_text:
                    log('input_binding_observed action=%s' % ('IA_Parry' if action_mode == 'parry' else 'IA_Block'))
                    S['binding_logged'] = True
            except Exception:
                pass
        if action_mode == 'block' and not S['binding_logged']:
            log('input_binding_status=UNKNOWN IA_Block action injection will be checked only through observed runtime effects')
            S['binding_logged'] = True
        if action_mode == 'parry' and not S['binding_logged'] and S['play_elapsed'] > 10.0:
            log('SETUP_INCONCLUSIVE no LogRPGParry IA_Parry binding line observed within 10 seconds')
            end_play('parry binding not observed')
            return
        if current_montage and action_mode in ('parry', 'block') and parry is not None:
            action_path = IA_PATHS[action_mode]
            action = unreal.load_asset(action_path)
            if action is None:
                raise RuntimeError('input action asset did not load: ' + action_path)
            offset = float(S['config'].get('parry_offset_seconds', 0.0))
            key = '%s@%.3f' % (current_montage, S['montage_started_at'] or 0.0)
            if key not in S['parry_sent'] and S['play_elapsed'] - (S['montage_started_at'] or 0.0) >= offset:
                S['parry_sent'].add(key)
                S['hold_until'] = S['play_elapsed'] + float(S['config'].get('input_hold_seconds', 0.12))
                log('real_input_press action=%s montage=%s montage_position=%s offset=%.4f before_health=%s before_stamina=%s' % (
                    'IA_Parry' if action_mode == 'parry' else 'IA_Block', current_montage, montage_pos, offset, health, stamina))
            if S['play_elapsed'] <= S['hold_until']:
                unreal.RPGInputTestUtils.inject_action(pc, action, unreal.Vector(1.0, 0.0, 0.0))

        opened = parry_open(parry)
        blocking_tag = read_tag(pawn, 'Status.Blocking')
        if health is not None and S['last_health'] is not None and health != S['last_health']:
            delta = health - S['last_health']
            log('health_delta hp_before=%.3f hp_after=%.3f delta=%.3f parry_window=%s blocking_tag=%s stamina_before=%s stamina_after=%s boss_montage=%s montage_position=%s distance=%.2f' % (
                S['last_health'], health, delta, opened, blocking_tag, S['last_stamina'], stamina, current_montage, montage_pos,
                (boss.get_actor_location() - pawn.get_actor_location()).length()))
        S['last_health'] = health
        S['last_stamina'] = stamina
        interval = float(S['config'].get('sample_interval_seconds', 0.25))
        if S['play_elapsed'] - S['last_sample'] >= interval:
            S['last_sample'] = S['play_elapsed']
            log('sample t=%.3f boss_montage=%s montage_position=%s parry_window=%s blocking_tag=%s health=%s stamina=%s' % (
                S['play_elapsed'], current_montage, montage_pos, opened, blocking_tag, health, stamina))
        if S['play_elapsed'] >= float(S['config'].get('duration_seconds', 75)):
            log('bounded_observation_finished; health samples and montage timing alone do not identify a pack impact branch')
            end_play('duration elapsed')
    except Exception as exc:
        log('driver_error=%s\n%s' % (str(exc), traceback.format_exc()))
        end_play('driver error')


S['handle'] = unreal.register_slate_post_tick_callback(tick)
log('driver registered; pack-specific contact and response remain UNKNOWN until raw engine/Blueprint evidence identifies them')
