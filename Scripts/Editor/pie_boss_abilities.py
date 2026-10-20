"""
PIE probe (read only): lists the abilities the pack's great-sword boss was granted (class, ability tags, bUsesPoise) and what its attribute component holds, so
a missing hit reaction ability or poise attribute shows up. Open L_SevarogArena first; run with Scripts/run_in_editor.py (editor throttling off). Log prefix [BossAbil].
"""
import unreal

log = lambda m: unreal.log("[BossAbil] " + m)
state = {"phase": "start", "t": 0.0}
handle = None


def world():
    try:
        return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    except Exception:
        return None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def finish(reason):
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("finished: " + reason)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def describe(owner, label):
    asc = comp(owner, "BP_AdvancedAbilitySystemComponent_C")
    log("== %s: %s, ASC %s" % (label, owner.get_class().get_name(), asc is not None))
    if not asc:
        return
    for prop in ("CreatedAbilities", "Default Abilities"):
        try:
            items = list(asc.get_editor_property(prop))
        except Exception as e:
            log("  %s: unreadable (%s)" % (prop, str(e)[:60]))
            continue
        log("  %s: %d" % (prop, len(items)))
        for a in items:
            if a is None:
                log("    None")
                continue
            try:
                tags = a.get_editor_property("AbilityTags").export_text()
            except Exception:
                tags = "?"
            try:
                poise = a.get_editor_property("bUsesPoise")
            except Exception:
                poise = "-"
            log("    %-34s tags %s bUsesPoise %s" % (a.get_class().get_name(), tags[:110], poise))
    for prop in ("ActiveGameplayEffects", "OwnedAbilityTags", "BlockedAbilityTags"):
        try:
            v = asc.get_editor_property(prop)
            if hasattr(v, "export_text"):
                log("  %s = %s" % (prop, v.export_text()[:200]))
            else:
                log("  %s (%d): %s" % (prop, len(list(v)), [(x.get_class().get_name() + " " + str(x.get_name())) if x is not None else "None" for x in list(v)][:8]))
        except Exception as e:
            log("  %s unreadable: %s" % (prop, str(e)[:60]))
    attrs = comp(owner, "BP_AttributesComponent_C")
    if attrs:
        for tag in ("Attribute.Health", "Attribute.Poise", "Attribute.Stamina"):
            t = unreal.GameplayTag()
            t.import_text('(TagName="%s")' % tag)
            try:
                log("  %s = %s (max %s)" % (tag, attrs.call_method("Get Current Attribute Value", args=(t,)), attrs.call_method("GetMaxAttributeValue", args=(t,))))
            except Exception as e:
                log("  %s: %s" % (tag, str(e)[:60]))


def _tick(dt):
    s = state
    s["t"] += dt
    if s["t"] > 60:
        finish("timeout")
        return
    if s["phase"] == "start":
        if s["t"] > 0.5:
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="wait", t=0.0)
        return
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    if pawn is None or s["t"] < 8.0:
        return
    boss = next(iter([a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"]), None)
    describe(pawn, "player")
    if boss:
        describe(boss, "boss")
    finish("done")


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish("error")


assert unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name() == "L_SevarogArena", "open L_SevarogArena first"
handle = unreal.register_slate_post_tick_callback(tick)
