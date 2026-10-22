"""
G3 / M13 probe (log prefix [G3Probe]; variable dumps are LogRPGDebug lines): how does the pack give the player a weapon and switch the combat style? Starts a PIE and ends it itself; changes nothing but
what four quickslot presses change (PIE only). Run with Scripts/run_in_editor.py after the warm-up (pie_debug_overlay.py once). Plan: Documentation/M13_BUILDS_PLAN.md sections 1.2 and 1.3.
Before the PIE: the PlayerInfo asset (Default Equipment, Default Inventory = what the player starts with), struct text in full. In the PIE: the components of the pawn and of its controller, the combat,
equipment and inventory components (variables, depth 2), the weapon slot structs in full, three weapon items, five combat styles, the Blueprint functions of the pawn's components with parameter
names (FUNCTION lines), then the pack's own switch: IA_QuickSlotRight twice out of combat, combat entered, twice in combat; style, combat flag, montage and slots are logged after each step.
"""
import unreal

log = lambda m: unreal.log("[G3Probe] " + m)
MEL = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/"
ASSETS = [MEL + "Items/Weapons/" + n for n in ("ToughSword", "KwangSword", "DualSteelSwords")] + [MEL + "Weapons/" + n for n in (
    "Sword/SwordCombatStyle", "Sword/SwordAndShieldCombatStyle", "Claymore/ClaymoreCombatStyle", "DualSwords/DualSwordCombatStyle", "Twinblades/TwinbladeCombatStyle")]
ACTIONS = ["press out of combat", "press out of combat", "enter combat", "press in combat", "press in combat"]
S = {"t": 0.0, "now": 0.0, "phase": "start", "step": 0, "wait": 0.0, "press_until": 0.0}
handle = None


def comp(actor, name):
    return next((c for c in actor.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name() == name), None)


def text_of(v, limit=1800):
    try:
        if hasattr(v, "export_text"):
            s = v.export_text()
        elif hasattr(v, "__iter__") and not isinstance(v, str):
            s = "[" + "; ".join(text_of(x, 700) for x in v) + "]"
        else:
            s = str(v)
    except Exception as e:
        s = "<%s>" % e
    return s[:limit]


def prop(o, n):
    try:
        v = o.get_editor_property(n)
        return v.get_name() if hasattr(v, "get_name") else str(v)
    except Exception as e:
        return "? (%s)" % str(e)[:50]


def show(label, obj, names):
    for n in names:
        for variant in (n, n.replace(" ", "")):
            try:
                log("%s.%s = %s" % (label, n, text_of(obj.get_editor_property(variant))))
                break
            except Exception:
                pass
        else:
            log("%s.%s unreadable from Python" % (label, n))


def state_line(p, tag):
    combat, eq = comp(p["pawn"], "BP_CombatComponent_C"), comp(p["pawn"], "BP_EquipmentComponent_C")
    inst = p["pawn"].get_components_by_class(unreal.SkeletalMeshComponent)[0].get_anim_instance()
    m = inst.get_current_active_montage() if inst else None
    log("%s: style %s, combat enabled %s, montage %s" % (tag, prop(combat, "CurrentCombatStyle"), prop(combat, "bIsCombatEnabled?"), m.get_name() if m else None))
    if eq:
        show("   equipment", eq, ["EquipmentSlots"])


def dump_all(p):
    dbg = p["dbg"]
    for owner in ("pawn", "pc"):
        log("=== components of the %s (%s): %s" % (owner, p[owner].get_class().get_name(), ", ".join(sorted(c.get_class().get_name() for c in p[owner].get_components_by_class(unreal.ActorComponent)))))
        for cls in ("BP_CombatComponent_C", "BP_EquipmentComponent_C", "BP_PlayerInventoryComponent_C", "BP_InventoryComponent_C"):
            c = comp(p[owner], cls)
            if c:
                log("=== BEGIN %s on the %s" % (cls, owner))
                dbg.dump_object(c, 2)
                log("   Python names with 'equip' or 'item': %s" % [n for n in dir(c) if "equip" in n.lower() or "item" in n.lower()][:25])
    for path in ASSETS:
        log("=== BEGIN asset %s" % path.split("/")[-1])
        dbg.dump_object(unreal.load_asset(path), 1)
    log("=== BEGIN Blueprint functions of the pawn's components (FUNCTION lines; the controller's components are not covered)")
    dbg.dump_player_functions()


def script(p):
    """One step per call (after the 10 s settle); returns the seconds to wait, -1 to finish."""
    s = S["step"]
    S["step"] += 1
    if s == 0:
        dump_all(p)
    state_line(p, "STATE before the first action" if s == 0 else "STATE after '%s'" % ACTIONS[s - 1])
    if s >= len(ACTIONS):
        return -1.0
    if ACTIONS[s] == "enter combat":
        tag = unreal.GameplayTagContainer()
        tag.import_text('(GameplayTags=((TagName="Ability.EnterCombat")))')
        comp(p["pawn"], "BP_AdvancedAbilitySystemComponent_C").call_method("Try Activate Abilities By Tag", args=(tag,))
    else:
        S["press_until"] = S["now"] + 0.15
    return 3.5


def finish():
    global handle
    if handle:
        unreal.unregister_slate_post_tick_callback(handle)
        handle = None
    log("=== END (OBJECT and FUNCTION dumps are LogRPGDebug lines)")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


def _tick(dt):
    S["t"] += dt
    S["now"] += dt
    if S["phase"] == "start":
        if S["t"] > 0.5:
            log("=== BEGIN PlayerInfo (what the player starts with)")
            show("PlayerInfo", unreal.EditorAssetLibrary.load_asset(MEL + "DataAssets/PlayerInfo"), ["Default Combat Style", "Default Equipment", "Default Inventory"])
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            S.update(phase="play", t=0.0)
        return
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    dbg = comp(boss, "RPGCombatDebug") if boss else None
    if pawn is None or dbg is None:
        if S["t"] > 40.0:
            log("no pawn or boss debug component after 40 s: stopping")
            finish()
        return
    if S["now"] < S["press_until"]:
        unreal.RPGInputTestUtils.inject_action(pc, unreal.load_asset(MEL + "Input/InputActions/IA_QuickSlotRight"), unreal.Vector(1, 0, 0))
    S["wait"] -= dt
    if S["t"] < 10.0 or S["wait"] > 0:
        return
    S["wait"] = script({"pawn": pawn, "pc": pc, "dbg": dbg})
    if S["wait"] < 0:
        finish()


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        log("tick error " + traceback.format_exc())
        finish()


handle = unreal.register_slate_post_tick_callback(tick)
