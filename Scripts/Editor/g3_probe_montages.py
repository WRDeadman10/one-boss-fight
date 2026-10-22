"""
G3 / M13 probe (log prefix [G3Montage]), editor only, NO PIE: for the four weapon abilities of the pack (sword, claymore, dual swords, twinblades) prints, for every montage of
AttackMontages, StrongAttackMontages, ChargedAttackMontages, FallingAttackMontages, SprintAttackMontages and DodgeAttackMontages: the length, rate scale, the ability's PlayRate and
EndTimeMultiplier, every notify (class, time, duration of states) from URPGMontageUtils::DescribeNotifies (Python cannot read montage notify times itself), the properties of each
ANS_CollisionTrace (read from the Python notify objects, paired by index), the pack's own ANS_HitStunImmune windows, and one parseable summary line per montage:
  [G3Montage] WIN <style> <array> <montage> len=<s> rate=<r> trace=<a>-<b> [...] immune=<a>-<b>|none propose=<start>,<end>|none
propose = (first trace start - LEAD, last trace end) in montage seconds = the numbers for HyperArmorStart / HyperArmorEnd of the table rows (Documentation/M13_BUILDS_PLAN.md section 4).
Also prints the Claymore rows and every hyperarmor window now in /Game/OneBossFight/Data/DA_WeaponAttacks. Reads only; changes and saves nothing. Run with Scripts/run_in_editor.py (editor open, no PIE).
"""
import re
import unreal

log = lambda m: unreal.log("[G3Montage] " + m)
W = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/"
ABILITIES = [("SwordCombatStyle", "Sword/GA_Sword_Melee"), ("ClaymoreCombatStyle", "Claymore/GA_Claymore_Melee"),
             ("DualSwordCombatStyle", "DualSwords/GA_DuaSword_Melee"), ("TwinbladeCombatStyle", "Twinblades/GA_Twinblades_Melee")]
ARRAYS = ("AttackMontages", "StrongAttackMontages", "ChargedAttackMontages", "FallingAttackMontages", "SprintAttackMontages", "DodgeAttackMontages")
TRACE_PROPS = ("Collision Target Tag", "EventTag", "AttackData", "Swing Direction", "TraceRadiusModifier")
LEAD = 0.08  # seconds before the first trace window that the hyperarmor may start (open question Q4 of the plan)
LINE = re.compile(r"(\[state\] )?(\S+) at ([-0-9.]+) s(?: for ([-0-9.]+) s)?")


def text_of(v):
    try:
        return v.export_text() if hasattr(v, "export_text") else str(v)
    except Exception:
        return str(v)


def num(text, field):
    m = re.search(field + r"[^=]*=\s*([-0-9.]+)", text)
    return float(m.group(1)) if m else None


def prop(o, name):
    try:
        return text_of(o.get_editor_property(name))[:90]
    except Exception:
        return "?"


def notifies(montage):
    """(header line, [(class, is state, time, duration)]) from the project's C++ helper: one line per notify in the montage's own order."""
    lines = list(unreal.RPGMontageUtils.describe_notifies(montage)) if hasattr(unreal, "RPGMontageUtils") else []
    evs = []
    for ln in lines[1:]:
        m = LINE.match(ln)
        evs.append((m.group(2), bool(m.group(1)), float(m.group(3)), float(m.group(4) or 0.0)) if m else ("?", False, -1.0, 0.0))
    return (lines[0] if lines else "no RPGMontageUtils (build the editor module first)"), evs


def span(items):
    return " ".join("%.3f-%.3f" % (t, t + d) for _, _, t, d in items) or "none"


def describe(style, array, el):
    text = text_of(el)
    m = re.search(r"AnimMontage'(/Game/[^']+)'", text) or re.search(r"(/Game/[A-Za-z0-9_/.\-]+)", text)
    montage = unreal.EditorAssetLibrary.load_asset(m.group(1)) if m else None
    if montage is None:
        log("   %s %s: no montage found in element %s" % (style, array, text[:120]))
        return
    name = montage.get_name()
    head, evs = notifies(montage)
    log("== %s %s %s | %s | struct PlayRate %s EndTimeMultiplier %s InTimeToStartMontageAt %s" % (style, array, name, head, num(text, "PlayRate"), num(text, "EndTimeMultiplier"), num(text, "InTimeToStartMontageAt")))
    try:
        py = list(unreal.AnimationLibrary.get_animation_notify_events(montage))  # same order as the C++ lines
    except Exception:
        py = []
    for i, (cls, state, t, d) in enumerate(evs):
        extra = ""
        if cls.startswith("ANS_CollisionTrace") and len(py) == len(evs):
            extra = " | " + " | ".join("%s=%s" % (p, prop(py[i].get_editor_property("notify_state_class"), p)) for p in TRACE_PROPS)
        log("     %s%s at %.3f s%s%s" % ("[state] " if state else "", cls, t, " for %.3f s (ends %.3f)" % (d, t + d) if state else "", extra))
    trace = [e for e in evs if e[0].startswith("ANS_CollisionTrace")]
    immune = [e for e in evs if e[0].startswith("ANS_HitStunImmune")]
    propose = "none"
    if trace:
        propose = "%.3f,%.3f" % (max(0.0, trace[0][2] - LEAD), trace[-1][2] + trace[-1][3])
        gap = trace[1][2] - (trace[0][2] + trace[0][3]) if len(trace) > 1 else 0.0
        if gap > 0.3:
            propose += " (gap of %.2f s between two windows: one row window covers both)" % gap
    try:
        rate = montage.get_editor_property("rate_scale")
    except Exception:
        rate = -1.0
    log("WIN %s %s %s len=%.3f rate=%.2f trace=%s immune=%s propose=%s" % (style, array, name, montage.get_play_length(), rate, span(trace), span(immune), propose))


for style, rel in ABILITIES:
    bp = unreal.EditorAssetLibrary.load_asset(W + rel)
    cls = bp.generated_class() if bp else None
    if cls is None:
        log("MISSING ability %s" % rel)
        continue
    cdo = unreal.get_default_object(cls)
    log("######## %s: %s  AttackData=%s  cost=%s" % (style, rel.split("/")[-1], prop(cdo, "AttackData"), prop(cdo, "Cost Gameplay Effect Class")))
    for array in ARRAYS:
        try:
            items = list(cdo.get_editor_property(array))
        except Exception as e:
            log("   %s.%s unreadable: %s" % (style, array, str(e)[:80]))
            continue
        log("---- %s %s: %d element(s)" % (style, array, len(items)))
        for el in items:
            describe(style, array, el)

table = unreal.EditorAssetLibrary.load_asset("/Game/OneBossFight/Data/DA_WeaponAttacks")
try:
    for row in (table.get_editor_property("rows") if table else []):
        g = row.get_editor_property
        if g("hyper_armor_end") > 0 or "Claymore" in str(g("weapon")):
            log("TABLE %s %s posture %.0f stamina %.0f bleed %.0f hyperarmor %.3f-%.3f" % (g("weapon"), g("kind").name, g("posture_damage"), g("stamina_cost"), g("bleed_buildup"), g("hyper_armor_start"), g("hyper_armor_end")))
except Exception as e:
    log("TABLE unreadable: %s (the property names of a row: %s)" % (e, [n for n in dir(unreal.RPGWeaponAttackRow()) if not n.startswith("_")][:20]))
log("done")
