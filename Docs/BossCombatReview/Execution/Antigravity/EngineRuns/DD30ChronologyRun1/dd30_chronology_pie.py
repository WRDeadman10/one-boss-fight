# C352 / DD30 Chronology PIE Driver
# Adapted from Codex C345 staging (24b7a39e...) with bounded QUIT_EDITOR shutdown.
import unreal

s = {
    'requested': False,
    'started': False,
    'elapsed': 0.0,
    'quit_requested': False
}
handle = None
quit_handle = None
quit_ticks = 0

def quit_tick(_dt):
    global quit_ticks, quit_handle
    quit_ticks += 1
    # Allow 60 slate ticks (~1 second at 60Hz) for LevelEditorSubsystem to tear down PIE cleanly
    if quit_ticks >= 60 and not s['quit_requested']:
        s['quit_requested'] = True
        unreal.log('[DD30_CHRONO_DRIVER] REQUEST QUIT_EDITOR (slate ticks=' + str(quit_ticks) + ')')
        try:
            unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")
        except Exception as e:
            unreal.log_error('[DD30_CHRONO_DRIVER] QUIT_EDITOR exception: ' + str(e))
    # Safety fallback if editor is still ticking after 120 ticks
    if quit_ticks >= 120:
        if quit_handle is not None:
            try:
                unreal.unregister_slate_post_tick_callback(quit_handle)
            except Exception:
                pass
            quit_handle = None
        try:
            unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")
        except Exception:
            pass

def finish(message):
    global handle, quit_handle
    unreal.log('[DD30_CHRONO_DRIVER] ' + message)
    if s['requested'] and s['started']:
        try:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        except Exception as e:
            unreal.log_error('[DD30_CHRONO_DRIVER] editor_request_end_play exception: ' + str(e))
    if handle is not None:
        try:
            unreal.unregister_slate_post_tick_callback(handle)
        except Exception:
            pass
        handle = None
    # Schedule bounded editor quit
    if quit_handle is None:
        quit_handle = unreal.register_slate_post_tick_callback(quit_tick)

def tick(dt):
    s['elapsed'] += dt
    if not s['requested']:
        editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        w = editor.get_editor_world()
        if not w or '/Game/OneBossFight/Levels/L_SevarogArena' not in w.get_path_name():
            finish('FAIL wrong editor map; no map load/save performed')
            return
        if editor.get_game_world():
            finish('FAIL preexisting PIE; cannot observe startup')
            return
        unreal.log('[DD30_CHRONO_DRIVER] REQUEST freshPIE map=L_SevarogArena no gameplay input')
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
        s['requested'] = True
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    if w and not s['started']:
        s['started'] = True
        unreal.log('[DD30_CHRONO_DRIVER] PIE_WORLD ' + w.get_path_name())
    if s['elapsed'] >= 10.0:
        finish('CAPTURE_END started=' + str(s['started']) + '; native chronology must be reviewed, not an automatic PASS')

handle = unreal.register_slate_post_tick_callback(tick)
