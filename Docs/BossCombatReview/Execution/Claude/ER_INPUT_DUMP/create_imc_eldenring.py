# Creates /Game/OneBossFight/Input/IMC_EldenRing (lead, Claude, 2026-11-06; owner "All three": hold heavy = charged attack).
# A NEW project asset (no pack asset is edited). Added at a higher priority than the pack's IMC_AdvancedControls by URPGDodgeTiming, so the keys it maps
# are consumed here and the pack's own mappings of the same keys no longer fire (R1 hold = charged and R1-on-release are replaced).
#   Gamepad R1: IA_NormalAttack on press (Elden Ring light attack starts on press).
#   Gamepad R2: IA_StrongAttack on a tap (released within TAP s); IA_ChargedAttack after a hold of HOLD s (Elden Ring hold R2 = charge attack).
#   Keyboard/mouse: NOT remapped (the chord trigger's ChordAction cannot be set from Python on a template); the pack's mouse scheme stays (LMB release light, LMB hold charged, Shift+LMB strong).
# Refuses to overwrite an existing asset (CLAUDE.md: never delete and recreate referenced assets). Log prefix [ImcER].
import unreal

PATH = "/Game/OneBossFight/Input"
NAME = "IMC_EldenRing"
TAP = 0.35
HOLD = 0.35
IA = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/"

def log(m):
    unreal.log("[ImcER] " + m)

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

if unreal.EditorAssetLibrary.does_asset_exist(PATH + "/" + NAME):
    log("EXISTS: refusing to overwrite " + PATH + "/" + NAME)
else:
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    imc = tools.create_asset(NAME, PATH, unreal.InputMappingContext, unreal.InputMappingContext_Factory())
    normal = unreal.load_asset(IA + "IA_NormalAttack")
    strong = unreal.load_asset(IA + "IA_StrongAttack")
    charged = unreal.load_asset(IA + "IA_ChargedAttack")
    second = unreal.load_asset(IA + "IA_StrongAttackSecondInput")
    if not (imc and normal and strong and charged and second):
        log("FAIL: asset or action missing imc=%s normal=%s strong=%s charged=%s second=%s" % (imc, normal, strong, charged, second))
    else:
        maps = [
            mapping(normal, "Gamepad_RightShoulder", [trig(unreal.InputTriggerPressed, imc)]),
            mapping(strong, "Gamepad_RightTrigger", [trig(unreal.InputTriggerTap, imc, tap_release_time_threshold=TAP)]),
            mapping(charged, "Gamepad_RightTrigger", [trig(unreal.InputTriggerHold, imc, hold_time_threshold=HOLD, is_one_shot=True)]),
        ]
        imc.set_editor_property("mappings", maps)
        ok = unreal.EditorAssetLibrary.save_asset(PATH + "/" + NAME, only_if_is_dirty=False)
        log("SAVED %s ok=%s" % (NAME, ok))

# read back
imc = unreal.load_asset(PATH + "/" + NAME)
if imc:
    for m in imc.get_editor_property("mappings"):
        ts = [t.get_class().get_name() for t in m.get_editor_property("triggers") if t]
        log("  %s <- %s %s" % (m.get_editor_property("action").get_name(), m.get_editor_property("key").get_editor_property("key_name"), ts))
log("DONE")
