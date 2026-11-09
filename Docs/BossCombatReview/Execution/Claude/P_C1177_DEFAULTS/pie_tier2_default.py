"""Lead PIE check (C-1177): NO rpg.Art.Tier2 cvar (config default), set the boss to 50 % health, then report Niagara components on the boss
and the RPGTier2BossPresentation state. Saves nothing. Log prefix [Tier2Default]; stop marker "[Tier2Default] finished:"."""
import unreal

S = {"t": 0.0, "phase": "start"}
HANDLE = None


def log(m):
    unreal.log("[Tier2Default] " + str(m))


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def attr_call(actor, fn, tag_name, *extra):
    c = comp(actor, "BP_AttributesComponent_C")
    t = unreal.GameplayTag()
    t.import_text('(TagName="%s")' % tag_name)
    return c.call_method(fn, args=(t,) + extra)


def niagara_state(boss):
    rows = []
    for n in boss.get_components_by_class(unreal.NiagaraComponent):
        asset = n.get_asset()
        rows.append("%s asset=%s active=%s" % (n.get_name(), asset.get_name() if asset else None, n.is_active()))
    return rows


def finish(reason):
    unreal.unregister_slate_post_tick_callback(HANDLE)
    log("finished: " + reason)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def tick(dt):
    S["t"] += dt
    try:
        if S["phase"] == "start" and S["t"] > 0.5:
            pass  # C-1177: NO Tier 2 cvar, proves the config default
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            S.update(phase="wait", t=0.0)
            return
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)
                     if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if world else None
        if S["phase"] == "wait" and boss and S["t"] > 6.0:
            pres = comp(boss, "RPGTier2BossPresentation")
            log("presentation_component=%s niagara_before=%s" % (bool(pres), niagara_state(boss)))
            mx = attr_call(boss, "GetMaxAttributeValue", "Attribute.Health")
            attr_call(boss, "Set Current Attribute Value", "Attribute.Health", float(mx) * 0.5)
            log("boss health set to %.1f of %.1f" % (attr_call(boss, "Get Current Attribute Value", "Attribute.Health"), mx))
            S.update(phase="observe", t=0.0)
        elif S["phase"] == "observe" and boss and S["t"] > 3.0:
            log("niagara_after=%s" % niagara_state(boss))
            finish("observed")
        elif S["t"] > 40.0:
            finish("timeout (no boss)")
    except Exception:
        import traceback
        log("error " + traceback.format_exc())
        finish("exception")


HANDLE = unreal.register_slate_post_tick_callback(tick)
