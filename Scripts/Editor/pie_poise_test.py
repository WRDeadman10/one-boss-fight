"""
PIE test of poise on the pack's demo level (run via execute_script with the level already open and the editor unattended).
The player stands still next to a sword enemy and takes hits. Every change of the player's poise, health and playing
montage is logged with [PoiseTest]. Expected with 40 poise and 20 per hit: hits absorbed (no hit-reaction montage) until
poise reaches 0, then one stun and poise refilled to 40.
"""
import unreal

log = lambda m: unreal.log("[PoiseTest] " + m)
POISE = unreal.GameplayTag(); POISE.import_text('(TagName="Attribute.Poise")')
HEALTH = unreal.GameplayTag(); HEALTH.import_text('(TagName="Attribute.Health")')
state = {"phase": "start", "t": 0.0, "last": None, "montage": None, "total": 0.0}
handle = None


def world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def value(comp, tag, fn="Get Current Attribute Value"):
    try:
        return comp.call_method(fn, args=(tag,))
    except Exception as e:
        return "ERR " + str(e)[:80]


def finish(reason):
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("finished: " + reason)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish("error")


def _tick(dt):
    s = state
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="wait", t=0.0)
        return
    w = world()
    if w is None:
        return
    pc = unreal.GameplayStatics.get_player_controller(w, 0)
    pawn = pc.get_controlled_pawn() if pc else None
    if pawn is None:
        return
    s["total"] += dt
    comps = pawn.get_components_by_class(unreal.ActorComponent)
    attr = next((c for c in comps if c.get_class().get_name() == "BP_AttributesComponent_C"), None)
    if s["phase"] == "wait":
        if s["t"] > 20.0:
            enemies = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleSwordEnemy_C"]
            log("%d sword enemies; attributes component: %s" % (len(enemies), attr))
            if enemies and attr:
                e = enemies[0]
                loc = e.get_actor_location() + e.get_actor_forward_vector() * 300.0
                pawn.set_actor_location(loc, False, True)
                log("player moved next to %s at %s; poise %s health %s" % (e.get_name(), loc, value(attr, POISE), value(attr, HEALTH)))
            s.update(phase="watch", t=0.0)
        return
    if s["phase"] == "watch":
        mesh = pawn.get_components_by_class(unreal.SkeletalMeshComponent)[0]
        anim = mesh.get_anim_instance()
        montage = anim.get_current_active_montage() if anim else None
        mname = montage.get_name() if montage else "-"
        snap = (value(attr, POISE), value(attr, HEALTH), mname)
        if snap != s["last"]:
            log("t=%.1f poise=%s health=%s montage=%s" % (s["t"], *snap))
            s["last"] = snap
        if s["t"] > 40.0:
            finish("watched 40 s")


handle = unreal.register_slate_post_tick_callback(tick)
log("registered")
