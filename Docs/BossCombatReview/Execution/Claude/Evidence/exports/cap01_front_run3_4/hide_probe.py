import unreal
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
unreal.log("[HideProbe] pawn %s" % pawn.get_name())
try:
    unreal.log("[HideProbe] before get_actor_hidden_in_game=%r" % (pawn.get_actor_hidden_in_game(),))
except Exception as e:
    unreal.log("[HideProbe] get_actor_hidden_in_game error %s" % e)
pawn.set_actor_hidden_in_game(True)
try:
    unreal.log("[HideProbe] after set True get_actor_hidden_in_game=%r" % (pawn.get_actor_hidden_in_game(),))
except Exception as e:
    unreal.log("[HideProbe] get after error %s" % e)
for name in ("hidden", "b_hidden"):
    try:
        unreal.log("[HideProbe] property %s=%r" % (name, pawn.get_editor_property(name)))
    except Exception as e:
        unreal.log("[HideProbe] property %s unreadable: %s" % (name, str(e)[:80]))
mesh = pawn.get_editor_property("mesh")
try:
    mesh.set_hidden_in_game(True, False)
    unreal.log("[HideProbe] mesh hidden_in_game=%r visible=%r" % (mesh.get_editor_property("hidden_in_game"), mesh.is_visible()))
except Exception as e:
    unreal.log("[HideProbe] mesh error %s" % str(e)[:120])
pawn.set_actor_hidden_in_game(False)
mesh.set_hidden_in_game(False, False)
