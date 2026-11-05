# C-807: measure the real pack player-death/respawn/reset order for C-804 Step B.
# Invoked by run_pie.ps1 through -ExecCmds="py <short path>". It uses the existing
# debug health hook to observe pack order; it never implements respawn/rebind.
import os
import math
import unreal

ROOT = 'C:/UnrealProject/OneBossFight'
MAP = '/Game/OneBossFight/Levels/L_SevarogArena'
LOG = open(ROOT + '/Docs/BossCombatReview/Execution/Codex/H019_ORDER/current_log.txt').read().strip()
WARMUP_SECONDS = 10.0  # KI-150 pack warm-up window
AFTER_RESPAWN_SECONDS = 6.0
RESPAWN_TIMEOUT = 30.0
S = {'phase': 'load', 'ticks': 0, 'time': 0.0, 'pie_time': 0.0,
     'initial_pawn': None, 'boss': None, 'debug': None, 'encounter': None,
     'tracker': None, 'kill_at': None, 'last_health': None,
     'last_dead_tag': None, 'next_health_log': 0.0, 'respawn_pawn': None,
     'respawn_at': None, 'handle': None}


def log(message):
    unreal.log('[H019Order] ' + message)


def log_text():
    try:
        with open(LOG, 'r', encoding='utf-8', errors='replace') as stream:
            return stream.read()
    except OSError:
        return ''


def component(actor, class_name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent)
                 if c.get_class().get_name() == class_name), None)


def player_health(pawn):
    attributes = component(pawn, 'BP_AttributesComponent_C') if pawn else None
    if attributes is None:
        return None
    tag = unreal.GameplayTag()
    tag.import_text('(TagName="Attribute.Health")')
    try:
        return attributes.call_method('Get Current Attribute Value', args=(tag,))
    except Exception as exc:
        return 'ERR ' + str(exc)[:100]


def player_dead_tag(pawn):
    tag = unreal.GameplayTag()
    tag.import_text('(TagName="Status.Dead")')
    try:
        return bool(pawn.call_method('HasMatchingGameplayTag', args=(tag,)))
    except Exception:
        return None


def place_player_in_front(pawn, boss, controller, distance=250.0):
    origin = boss.get_actor_location()
    yaw = math.radians(boss.get_actor_rotation().yaw)
    point = unreal.Vector(origin.x + math.cos(yaw) * distance,
                          origin.y + math.sin(yaw) * distance, origin.z + 20.0)
    face = unreal.MathLibrary.find_look_at_rotation(point, origin)
    pawn.set_actor_location_and_rotation(point, unreal.Rotator(0.0, 0.0, face.yaw), False, True)
    controller.set_control_rotation(unreal.Rotator(0.0, 0.0, face.yaw))


def end_and_quit(reason):
    unreal.SystemLibrary.execute_console_command(None, 'rpg.Debug 0')
    log('finish reason=%s observed_tokens=%s' % (reason, [token for token in (
        'spawn_player', 'reset_detected', 'reset_broadcast', 'binding_released')
        if '[EncounterLifecycle] ' + token in log_text()]))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    S.update(phase='quit', ticks=0)


def tick(dt):
    try:
        S['ticks'] += 1
        S['time'] += dt
        phase = S['phase']
        if phase == 'load':
            if S['ticks'] < 30:
                return
            loaded = unreal.EditorLoadingAndSavingUtils.load_map(MAP)
            log('load_map path=%s success=%s' % (MAP, loaded is not None))
            if loaded is None:
                end_and_quit('map_load_failed')
                return
            S.update(phase='begin', ticks=0)
        elif phase == 'begin':
            if S['ticks'] < 20:
                return
            # Lead (G044 live runs): optional opt-in selection; unset = the unchanged legacy-route run.
            selection = os.environ.get('H019_ENCOUNTER_DEFINITION', '').strip()
            if selection:
                unreal.SystemLibrary.execute_console_command(None, 'rpg.EncounterDefinition ' + selection)
            log('request_begin_play map=%s selection=%s' % (MAP, selection or 'none'))
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            S.update(phase='warmup', ticks=0, pie_time=0.0)
        elif phase == 'warmup':
            S['pie_time'] += dt
            world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
            pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
            pawn = pc.get_controlled_pawn() if pc else None
            if S['pie_time'] < WARMUP_SECONDS:
                return
            bosses = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character) if world else []
            boss = next((a for a in bosses if a.get_class().get_name() == 'BP_ExampleGreatSwordBoss_C'), None)
            debug = component(boss, 'RPGCombatDebug') if boss else None
            encounter = component(boss, 'RPGBossEncounter') if boss else None
            tracker = component(boss, 'RPGAttackTracker') if boss else None
            if pawn is None or boss is None or debug is None or encounter is None or tracker is None:
                log('setup_missing pawn=%s boss=%s debug=%s encounter=%s tracker=%s' %
                    (pawn, boss, debug, encounter, tracker))
                end_and_quit('setup_missing_after_warmup')
                return
            world_for_command = world
            unreal.SystemLibrary.execute_console_command(world_for_command, 'rpg.Debug 2')
            # Match the earlier successful death/reset driver: wake the encounter,
            # hold its harness-owned state, and put the pack player in combat first.
            encounter.wake()
            encounter.hold_for_test(True)
            debug.debug_refill_player()
            tracker.enter_combat()
            ability_system = component(pawn, 'BP_AdvancedAbilitySystemComponent_C')
            if ability_system is None:
                log('setup_missing player AbilitySystemComponent')
                end_and_quit('missing_player_ability_system')
                return
            tags = unreal.GameplayTagContainer()
            tags.import_text('(GameplayTags=((TagName="Ability.EnterCombat")))')
            ability_system.call_method('Try Activate Abilities By Tag', args=(tags,))
            place_player_in_front(pawn, boss, pc)
            S.update(phase='start_action', initial_pawn=pawn.get_name(), boss=boss,
                     debug=debug, encounter=encounter, tracker=tracker,
                     last_health=player_health(pawn), last_dead_tag=player_dead_tag(pawn),
                     next_health_log=S['pie_time'] + 0.25)
            log('encounter_awake player_combat=entered pawn=%s health=%s status_dead=%s' %
                (S['initial_pawn'], S['last_health'], S['last_dead_tag']))
        elif phase == 'start_action':
            S['pie_time'] += dt
            if S['pie_time'] < WARMUP_SECONDS + 3.0:
                return
            world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
            pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
            pawn = pc.get_controlled_pawn() if pc else None
            if pawn is None or pawn.get_name() != S['initial_pawn']:
                log('player_changed_before_kill pawn=%s expected=%s' %
                    (pawn.get_name() if pawn else None, S['initial_pawn']))
                end_and_quit('player_changed_before_kill')
                return
            place_player_in_front(pawn, S['boss'], pc)
            started = S['tracker'].start_move('A4', True)
            log('active_action start_move=A4 accepted=%s player_health=%s' %
                (started, player_health(pawn)))
            if not started:
                end_and_quit('boss_action_start_failed')
                return
            S.update(phase='kill_during_action', action_at=S['pie_time'])
        elif phase == 'kill_during_action':
            S['pie_time'] += dt
            pawn = unreal.GameplayStatics.get_player_pawn(
                unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(), 0)
            if S['pie_time'] - S['action_at'] < 0.8:
                return
            health_before = player_health(pawn)
            log('kill_player_during=A4 via=RPGCombatDebug.debug_set_player_health(0.0) pawn=%s health_before=%s' %
                (pawn.get_name() if pawn else None, health_before))
            S['debug'].debug_set_player_health(0.0)
            S.update(phase='wait_respawn', kill_at=S['pie_time'], last_health=player_health(pawn),
                     last_dead_tag=player_dead_tag(pawn), next_health_log=S['pie_time'])
            log('health_after_kill=%s status_dead=%s' %
                (S['last_health'], S['last_dead_tag']))
        elif phase == 'wait_respawn':
            S['pie_time'] += dt
            world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
            pc = unreal.GameplayStatics.get_player_controller(world, 0) if world else None
            pawn = pc.get_controlled_pawn() if pc else None
            health = player_health(pawn)
            dead_tag = player_dead_tag(pawn)
            if S['pie_time'] >= S['next_health_log']:
                log('death_watch elapsed=%.3f pawn=%s health=%s status_dead=%s' %
                    (S['pie_time'] - S['kill_at'], pawn.get_name() if pawn else None, health, dead_tag))
                S['next_health_log'] = S['pie_time'] + 0.25
            if health != S['last_health'] or dead_tag != S['last_dead_tag']:
                log('death_state_change pawn=%s health=%s status_dead=%s' %
                    (pawn.get_name() if pawn else None, health, dead_tag))
                S.update(last_health=health, last_dead_tag=dead_tag)
            if pawn is not None and pawn.get_name() != S['initial_pawn']:
                S.update(phase='observe', respawn_pawn=pawn.get_name(), respawn_at=S['pie_time'])
                log('respawn pawn=%s old_pawn=%s seconds_after_kill=%.3f' %
                    (S['respawn_pawn'], S['initial_pawn'], S['pie_time'] - S['kill_at']))
            elif S['pie_time'] - S['kill_at'] > RESPAWN_TIMEOUT:
                end_and_quit('respawn_timeout')
        elif phase == 'observe':
            S['pie_time'] += dt
            world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
            pawn = unreal.GameplayStatics.get_player_pawn(world, 0) if world else None
            health = player_health(pawn)
            dead_tag = player_dead_tag(pawn)
            if health != S['last_health'] or dead_tag != S['last_dead_tag']:
                log('post_respawn_state_change pawn=%s health=%s status_dead=%s' %
                    (pawn.get_name() if pawn else None, health, dead_tag))
                S.update(last_health=health, last_dead_tag=dead_tag)
            if S['pie_time'] >= S['next_health_log']:
                log('post_respawn_watch pawn=%s health=%s status_dead=%s' %
                    (pawn.get_name() if pawn else None, health, dead_tag))
                S['next_health_log'] = S['pie_time'] + 1.0
            if S['pie_time'] - S['respawn_at'] >= AFTER_RESPAWN_SECONDS:
                end_and_quit('six_seconds_after_respawn')
        elif phase == 'quit':
            if S['ticks'] >= 90:
                log('quit')
                unreal.unregister_slate_post_tick_callback(S['handle'])
                unreal.SystemLibrary.execute_console_command(None, 'QUIT_EDITOR')
                S['phase'] = 'done'
    except Exception:
        import traceback
        log('tick_error ' + traceback.format_exc())
        unreal.SystemLibrary.execute_console_command(None, 'QUIT_EDITOR')


S['handle'] = unreal.register_slate_post_tick_callback(tick)
log('driver_registered map=%s warmup=%.1f post_respawn=%.1f' %
    (MAP, WARMUP_SECONDS, AFTER_RESPAWN_SECONDS))
