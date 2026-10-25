"""P0 read-only probe: logs the live console variable values of the running editor. Log prefix [P0Cvar]. Changes nothing."""
import unreal
S = unreal.SystemLibrary
for n in ("rpg.WakeClip", "rpg.CloseTelegraph", "rpg.Legend", "rpg.LegendShakeScale", "rpg.Debug", "t.MaxFPS", "t.FixedFrameRate", "r.VSync"):
    try:
        v = S.get_console_variable_float_value(n)
    except Exception as e:
        v = "ERR %s" % e
    unreal.log("[P0Cvar] %s = %s" % (n, v))
try:
    unreal.log("[P0Cvar] rpg.Build = %r" % S.get_console_variable_string_value("rpg.Build") if hasattr(S, "get_console_variable_string_value") else "[P0Cvar] rpg.Build: no string getter")
except Exception as e:
    unreal.log("[P0Cvar] rpg.Build ERR %s" % e)
w = unreal.EditorLevelLibrary.get_editor_world() if hasattr(unreal, "EditorLevelLibrary") else None
unreal.log("[P0Cvar] editor world = %s; global time dilation = %s" % (w.get_name() if w else None, unreal.GameplayStatics.get_global_time_dilation(w) if w else None))
