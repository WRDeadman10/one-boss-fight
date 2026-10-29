# C345 PROPOSED ONLY: a fresh normal PIE, no input/attribute/component/asset mutation.
import unreal
s={'requested':False,'started':False,'elapsed':0.0}
handle=None

def finish(message):
    global handle
    unreal.log('[DD30_CHRONO_DRIVER] '+message)
    if s['requested'] and s['started']:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
    if handle is not None:
        unreal.unregister_slate_post_tick_callback(handle)
        handle=None

def tick(dt):
    s['elapsed']+=dt
    if not s['requested']:
        editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        w=editor.get_editor_world()
        if not w or '/Game/OneBossFight/Levels/L_SevarogArena' not in w.get_path_name():
            finish('FAIL wrong editor map; no map load/save performed')
            return
        if editor.get_game_world():
            finish('FAIL preexisting PIE; cannot observe startup')
            return
        unreal.log('[DD30_CHRONO_DRIVER] REQUEST freshPIE map=L_SevarogArena no gameplay input')
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
        s['requested']=True
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    if w and not s['started']:
        s['started']=True
        unreal.log('[DD30_CHRONO_DRIVER] PIE_WORLD '+w.get_path_name())
    if s['elapsed']>=10.0:
        finish('CAPTURE_END started='+str(s['started'])+'; native chronology must be reviewed, not an automatic PASS')

handle=unreal.register_slate_post_tick_callback(tick)
