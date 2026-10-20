"""Gate 1: which montages each pack boss ability plays, and its trigger/tag variables. Log prefix [G1A]. Read only. Run with Scripts/run_in_editor.py."""
import unreal

log = lambda m: unreal.log("[G1A] " + m)
base = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/"
names = ["GA_GS_Boss_CloseAttack", "GA_GS_Boss_CloseRare", "GA_GS_Boss_MidRangeAttack", "GA_GS_Boss_LeapAttack", "GA_GS_Boss_SprintAttack", "GA_GS_Boss_RetaliationAttack", "GA_GS_Boss_EnterCombat", "GA_GS_Boss_HitStun"]
for n in names:
    cls = unreal.load_class(None, base + n + "." + n + "_C")
    if cls is None:
        log("%s: class not found" % n)
        continue
    cdo = unreal.get_default_object(cls)
    log("== %s" % n)
    for p in dir(cdo):
        if p.startswith("_") or p.startswith("get_") or p.startswith("set_") or callable(getattr(cdo, p, None)):
            continue
        try:
            v = cdo.get_editor_property(p)
        except Exception:
            continue
        s = str(v)
        if "Montage" in s or "montage" in p or "tag" in p or "cooldown" in p or "range" in p or "cost" in p or "damage" in p or "attack" in p:
            log("  %s = %s" % (p, s[:600]))
log("done")
