# v2 of the Elden Ring gamepad mapping (lead, Claude, 2026-11-06). pie3 showed the pack starts IA_StrongAttack on the key going DOWN (a Tap trigger still
# starts it on press) and ignores IA_NormalAttack with a Pressed trigger. So the keys now drive two NEW project actions and URPGDodgeTiming replays the
# pack's own actions by injection (the same way every PIE driver presses them):
#   R1 (Pressed)   -> IA_ER_Light     -> C++ injects IA_NormalAttack for 0.12 s       (light on press)
#   R2 (Tap 0.35)  -> IA_ER_HeavyTap  -> C++ injects IA_StrongAttack for 0.12 s       (strong on a short press, at release)
#   R2 (Hold 0.35) -> IA_ChargedAttack directly (proven in pie1/pie3: R2 hold plays ChargedAttack_Montage)
# Creates the two actions if missing (never overwrites), then rewrites the mappings of OUR asset IMC_EldenRing in place (no delete/recreate). Log [ImcER2].
import unreal

PATH = "/Game/OneBossFight/Input"
PACK = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/"
TAP = 0.35
HOLD = 0.35

def log(m):
    unreal.log("[ImcER2] " + m)

def trig(cls, outer, **props):
    t = unreal.new_object(cls, outer=outer)
    for k, v in props.items():
        t.set_editor_property(k, v)
    return t

def mapping(action, key_name, triggers):
    m = unreal.EnhancedActionKeyMapping()
    m.set_editor_property("action", action)
    key = unreal.Key()
    key.set_editor_property("key_name", key_name)
    m.set_editor_property("key", key)
    m.set_editor_property("triggers", triggers)
    return m

def ensure_action(name):
    full = PATH + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        return unreal.load_asset(full)
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    ia = tools.create_asset(name, PATH, unreal.InputAction, unreal.InputAction_Factory())
    ia.set_editor_property("value_type", unreal.InputActionValueType.BOOLEAN)
    unreal.EditorAssetLibrary.save_asset(full, only_if_is_dirty=False)
    log("created " + full)
    return ia

light = ensure_action("IA_ER_Light")
heavy_tap = ensure_action("IA_ER_HeavyTap")
charged = unreal.load_asset(PACK + "IA_ChargedAttack")
imc = unreal.load_asset(PATH + "/IMC_EldenRing")
if not (light and heavy_tap and charged and imc):
    log("FAIL missing light=%s heavy_tap=%s charged=%s imc=%s" % (light, heavy_tap, charged, imc))
else:
    maps = [
        mapping(light, "Gamepad_RightShoulder", [trig(unreal.InputTriggerPressed, imc)]),
        mapping(heavy_tap, "Gamepad_RightTrigger", [trig(unreal.InputTriggerTap, imc, tap_release_time_threshold=TAP)]),
        mapping(charged, "Gamepad_RightTrigger", [trig(unreal.InputTriggerHold, imc, hold_time_threshold=HOLD, is_one_shot=True)]),
    ]
    imc.set_editor_property("mappings", maps)
    ok = unreal.EditorAssetLibrary.save_asset(PATH + "/IMC_EldenRing", only_if_is_dirty=False)
    log("SAVED IMC_EldenRing ok=%s" % ok)
    for m in unreal.load_asset(PATH + "/IMC_EldenRing").get_editor_property("mappings"):
        log("  %s <- %s %s" % (m.get_editor_property("action").get_name(), m.get_editor_property("key").get_editor_property("key_name"),
                               [t.get_class().get_name() for t in m.get_editor_property("triggers") if t]))
log("DONE")
