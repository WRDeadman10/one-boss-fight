# F3d PIE driver (lead, Claude). Run in the windowed editor through "-ExecCmds=py <script>" so the script stays alive on slate ticks.
# Loads the NEW proof map, starts PIE, waits until the framework logs RESULT or ERROR (or times out), ends PIE and quits the editor explicitly.
# Reads the editor log file only to decide when to stop; all evidence is the raw log. Tags: [F3D_*]
import os
import unreal

MAP = '/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProof'
LOG = open('C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/F3d/current_log.txt').read().strip()  # written by the cycle script before each run
PIE_TIMEOUT = 60.0
S = {'phase': 'load', 't': 0.0, 'n': 0, 'handle': None, 'pie_t': 0.0, 'diag': False}


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
            S.update(phase='begin', n=0)
        elif ph == 'begin':
            if S['n'] < 20:
                return
            log('request_begin_play')
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            S.update(phase='run', pie_t=0.0)
        elif ph == 'run':
            S['pie_t'] += dt
            if S['pie_t'] > 2.0 and not S['diag']:
                S['diag'] = True
                diag()
            if S['pie_t'] > 3.0 and (log_has('[FrameworkProof] RESULT', '[FrameworkProof] ERROR') or S['pie_t'] > PIE_TIMEOUT):
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
