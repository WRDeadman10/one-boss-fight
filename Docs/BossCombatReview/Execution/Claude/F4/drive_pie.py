# F4 PIE driver (copy of the F3d driver; map and log path come from files) (lead, Claude). Run in the windowed editor through "-ExecCmds=py <script>" so the script stays alive on slate ticks.
# Loads the NEW proof map, starts PIE, waits until the framework logs RESULT or ERROR (or times out), ends PIE and quits the editor explicitly.
# Reads the editor log file only to decide when to stop; all evidence is the raw log. Tags: [F3D_*]
import os
import unreal

MAP = open('C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/F4/current_map.txt').read().strip()  # written by the run script
LOG = open('C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/F4/current_log.txt').read().strip()  # written by the run script
PIE_TIMEOUT = 60.0
DODGE = open('C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/F4/current_dodge.txt').read().strip() if os.path.exists('C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/F4/current_dodge.txt') else ''  # seconds after playback_start to press the dodge key (empty = no dodge)
KEY = 'Gamepad_FaceButton_Right'
INJECT = [float(x) for x in open('C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/F4/current_inject.txt').read().strip().split(',') if x] if os.path.exists('C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/F4/current_inject.txt') else []  # seconds after the first playback_start: injected player hits on the boss (F6)
INJECTED = []
RESTART = os.path.exists('C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/F4/current_restart.txt')  # F6b: restart the encounter (generation 2) once the boss is dead and wait for the second RESULT
RESTARTED = []
LIVE = float(open('C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/F4/current_live.txt').read().strip()) if os.path.exists('C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/F4/current_live.txt') else None  # C-443: seconds after playback_start to call restart_encounter_for_test(2) on a LIVE boss (must be refused, X-370)
LIVED = []
INJECT_PIE = [float(x) for x in open('C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/F4/current_inject_pie.txt').read().strip().split(',') if x] if os.path.exists('C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/F4/current_inject_pie.txt') else []  # C-449: injected player hits at these seconds after PIE start (the boss may still be walking: a neutral stance break)
INJECTED_PIE = []
INJECT_ROW = [(float(x.split(':')[0]), x.split(':')[1], x.split(':')[2], (x.split(':')[3] if len(x.split(':'))>3 else '')) for x in open('C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/F4/current_inject_row.txt').read().strip().split(',') if x] if os.path.exists('C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/F4/current_inject_row.txt') else []  # C-457 (F10): "seconds:WeaponStyle:AttackKind,..." after playback_start: hits carrying the DA_WeaponAttacks row
INJECTED_ROW = []
DIAG_LONG = os.path.exists('C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/F4/current_diag_long.txt')  # C-449 (KI-150 follow-up): DIAG every second until 20 s of PIE and do not stop on a FrameworkProof ERROR
DIAG_LAST = [-1.0]
S = {'dodge_t': None, 'down': False, 'up': False, 'phase': 'load', 't': 0.0, 'n': 0, 'handle': None, 'pie_t': 0.0, 'diag': False}


def log(m):
    unreal.log('[F3D] ' + m)


def log_has(*needles):
    try:
        with open(LOG, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
    except OSError:
        return False
    return any(n in text for n in needles)


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def attr(actor, tag_name, current=True):
    c = comp(actor, 'BP_AttributesComponent_C')
    if c is None:
        return 'NO_ATTRIBUTES_COMPONENT'
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % tag_name)
    try:
        return c.call_method('Get Current Attribute Value' if current else 'GetMaxAttributeValue', args=(t,))
    except Exception as e:
        return 'ERR ' + str(e)[:80]


def diag():
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pawn = unreal.GameplayStatics.get_player_pawn(w, 0) if w else None
    if pawn is None:
        log('DIAG no player pawn')
        return
    log('DIAG pawn=%s class=%s health=%s max=%s' % (pawn.get_name(), pawn.get_class().get_name(), attr(pawn, 'Attribute.Health'), attr(pawn, 'Attribute.Health', False)))


def log_count(needle):
    try:
        with open(LOG, 'r', encoding='utf-8', errors='replace') as f:
            return f.read().count(needle)
    except OSError:
        return 0


def tick(dt):
    try:
        S['t'] += dt
        S['n'] += 1
        ph = S['phase']
        if ph == 'load':
            if S['n'] < 30:
                return
            ok = unreal.EditorLoadingAndSavingUtils.load_map(MAP) is not None
            log('load_map %s ok=%s' % (MAP, ok))
            S.update(phase='navwait', n=0, nav_t=0.0)
            unreal.SystemLibrary.execute_console_command(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(), 'RebuildNavigation')
        elif ph == 'navwait':
            # A proof map is saved without baked navigation: the editor builds it after the load, and PIE copies the editor state. Wait until a projection works.
            S['nav_t'] += dt
            w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
            building = None
            projected = None
            try:
                building = unreal.NavigationSystemV1.is_navigation_being_built(w)
            except Exception as ex:
                building = 'ERR ' + str(ex)[:80]
            try:
                projected = unreal.NavigationSystemV1.project_point_to_navigation(w, unreal.Vector(300.0, 0.0, 10.0), None, None)
            except Exception as ex:
                projected = 'ERR ' + str(ex)[:80]
            if S['n'] % 60 == 1:
                log('navwait t=%.1f building=%s projected=%s' % (S['nav_t'], building, projected))
            ok = isinstance(projected, unreal.Vector) and abs(projected.x - 300.0) < 1.0  # a failed projection does not return the requested point
            if (building is False and ok and S['nav_t'] > 2.0) or S['nav_t'] > 60.0:
                log('nav wait done after %.1f s building=%s projected=%s' % (S['nav_t'], building, projected))
                S.update(phase='begin', n=0)
        elif ph == 'begin':
            if S['n'] < 20:
                return
            log('request_begin_play')
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            S.update(phase='run', pie_t=0.0)
        elif ph == 'run':
            S['pie_t'] += dt
            if INJECT:
                if S['dodge_t'] is None and log_has('[FrameworkProof] playback_start'):
                    S['dodge_t'] = S['pie_t']
                    log('playback_start seen at pie_t=%.3f; injected hits scheduled %s' % (S['pie_t'], INJECT))
                if S['dodge_t'] is not None and len(INJECTED) < len(INJECT) and (S['pie_t'] - S['dodge_t']) >= INJECT[len(INJECTED)]:
                    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
                    pawn = unreal.GameplayStatics.get_player_pawn(w, 0) if w else None
                    intake = pawn.get_component_by_class(unreal.RPGHitIntake) if pawn else None
                    bosses = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.RPGFrameworkBossCharacter) if w else []
                    if intake is None or not bosses:
                        log('inject hit %d impossible: intake=%s bosses=%d' % (len(INJECTED) + 1, intake is not None, len(bosses)))
                        INJECTED.append(-1)
                    else:
                        intake.inject_boss_hit_for_test(bosses[0])
                        log('injected hit %d at %.3f s after playback_start' % (len(INJECTED) + 1, S['pie_t'] - S['dodge_t']))
                        INJECTED.append(S['pie_t'])
            if INJECT_ROW:
                if S['dodge_t'] is None and log_has('[FrameworkProof] playback_start'):
                    S['dodge_t'] = S['pie_t']
                if S['dodge_t'] is not None and len(INJECTED_ROW) < len(INJECT_ROW) and (S['pie_t'] - S['dodge_t']) >= INJECT_ROW[len(INJECTED_ROW)][0]:
                    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
                    pawn = unreal.GameplayStatics.get_player_pawn(w, 0) if w else None
                    intake = pawn.get_component_by_class(unreal.RPGHitIntake) if pawn else None
                    bosses = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.RPGFrameworkBossCharacter) if w else []
                    sec, weapon, kind, via = INJECT_ROW[len(INJECTED_ROW)]  # via: '' immediate row hit, 'p1' / 'p2' (C-465, KI-151): through Pending/FinalizePending with 1 / 2 blades of the same swing
                    enum_name = ''.join('_' + c if c.isupper() and i else c for i, c in enumerate(kind)).upper()
                    if intake is not None and bosses:
                        if via.startswith('p'):
                            intake.inject_boss_pending_hit_for_test(bosses[0], weapon, getattr(unreal.RPGAttackKind, enum_name), int(via[1:]))
                        else:
                            intake.inject_boss_attack_hit_for_test(bosses[0], weapon, getattr(unreal.RPGAttackKind, enum_name))
                        log('injected row hit %d %s %s at %.3f s after playback_start' % (len(INJECTED_ROW) + 1, weapon, kind, S['pie_t'] - S['dodge_t']))
                    else:
                        log('inject row hit impossible')
                    INJECTED_ROW.append(S['pie_t'])
            if INJECT_PIE and len(INJECTED_PIE) < len(INJECT_PIE) and S['pie_t'] >= INJECT_PIE[len(INJECTED_PIE)]:
                w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
                pawn = unreal.GameplayStatics.get_player_pawn(w, 0) if w else None
                intake = pawn.get_component_by_class(unreal.RPGHitIntake) if pawn else None
                bosses = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.RPGFrameworkBossCharacter) if w else []
                if intake is not None and bosses:
                    intake.inject_boss_hit_for_test(bosses[0])
                    log('injected PIE-time hit %d at pie_t=%.3f' % (len(INJECTED_PIE) + 1, S['pie_t']))
                    INJECTED_PIE.append(S['pie_t'])
            if LIVE is not None and not LIVED:
                if S['dodge_t'] is None and log_has('[FrameworkProof] playback_start'):
                    S['dodge_t'] = S['pie_t']
                if S['dodge_t'] is not None and (S['pie_t'] - S['dodge_t']) >= LIVE:
                    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
                    fixes = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.RPGFrameworkProofFixture) if w else []
                    res = fixes[0].restart_encounter_for_test(2) if fixes else None
                    LIVED.append(res)
                    log('LIVE restart_encounter_for_test(2) at %.3f s after playback_start -> %s (expected False)' % (S['pie_t'] - S['dodge_t'], res))
            if DODGE:
                if S['dodge_t'] is None and log_has('[FrameworkProof] playback_start'):
                    S['dodge_t'] = S['pie_t']
                    log('playback_start seen at pie_t=%.3f; dodge press scheduled +%s s' % (S['pie_t'], DODGE))
                if S['dodge_t'] is not None:
                    since = S['pie_t'] - S['dodge_t']
                    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
                    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
                    if pc is not None and not S['down'] and since >= float(DODGE):
                        unreal.RPGInputTestUtils.set_key_down(pc, KEY, True)
                        S['down'] = True
                        log('dodge key down since_playback_start=%.3f' % since)
                    if pc is not None and S['down'] and not S['up'] and since >= float(DODGE) + 0.08:
                        unreal.RPGInputTestUtils.set_key_down(pc, KEY, False)
                        S['up'] = True
                        log('dodge key up since_playback_start=%.3f' % since)
            if DIAG_LONG and S['pie_t'] - DIAG_LAST[0] >= 1.0:
                DIAG_LAST[0] = S['pie_t']
                w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
                pawn = unreal.GameplayStatics.get_player_pawn(w, 0) if w else None
                if pawn is not None:
                    log('DIAGLONG pie_t=%.2f health=%s max=%s' % (S['pie_t'], attr(pawn, 'Attribute.Health'), attr(pawn, 'Attribute.Health', False)))
            if S['pie_t'] > 2.0 and not S['diag']:
                S['diag'] = True
                diag()
            if RESTART and not RESTARTED and log_has('[FrameworkProof] boss_dead'):
                w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
                fixes = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.RPGFrameworkProofFixture) if w else []
                ok = bool(fixes) and fixes[0].restart_encounter_for_test(2)
                RESTARTED.append(ok)
                log('restart_encounter_for_test(2) -> %s' % ok)
            need = 2 if RESTART else 1
            if DIAG_LONG:
                stop_now = S['pie_t'] > 20.0
            else:
                stop_now = S['pie_t'] > 3.0 and ((log_count('[FrameworkProof] RESULT') >= need) or log_has('[FrameworkProof] ERROR') or S['pie_t'] > PIE_TIMEOUT)
            if stop_now:
                log('stopping PIE after %.1f s (timeout=%s)' % (S['pie_t'], S['pie_t'] > PIE_TIMEOUT))
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
                S.update(phase='quit', n=0)
        elif ph == 'quit':
            if S['n'] >= 90:
                log('quit')
                unreal.unregister_slate_post_tick_callback(S['handle'])
                unreal.SystemLibrary.execute_console_command(None, 'QUIT_EDITOR')
                S['phase'] = 'done'
    except Exception:
        import traceback
        log('tick error ' + traceback.format_exc())
        unreal.SystemLibrary.execute_console_command(None, 'QUIT_EDITOR')


S['handle'] = unreal.register_slate_post_tick_callback(tick)
log('driver registered')
