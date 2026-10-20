"""Prints which montage every Sevarog ability points at (a deleted-and-recreated montage once left the saved references empty)."""
import re
import unreal

ABIL = "/Game/OneBossFight/SevarogPack/Abilities/"
CHECK = {"GA_Sev_EnterCombat": ["Enter Combat Montage"], "GA_Sev_ExitCombat": ["ExitCombatMontage"], "GA_Sev_TurnInPlace": ["Turn Left 90", "Turn Right 90", "Turn Left 180", "Turn Right 180"],
         "GA_Sev_Death": ["DeathMontages"], "GA_Sev_HitStun": ["Hit React Montages"], "GA_Sev_CloseAttack": ["AttackMontages"], "GA_Sev_CloseRare": ["AttackMontages"],
         "GA_Sev_MidRangeAttack": ["AttackMontages"], "GA_Sev_LeapAttack": ["AttackMontages"], "GA_Sev_SprintAttack": ["AttackMontages"], "GA_Sev_RetaliationAttack": ["AttackMontages"],
         "GA_Sev_Lightning": ["AttackMontages"]}
for name, props in CHECK.items():
    cdo = unreal.get_default_object(unreal.load_asset(ABIL + name).generated_class())
    for prop in props:
        v = cdo.get_editor_property(prop)
        texts = []
        if isinstance(v, (unreal.Map, dict)):
            texts = [x.export_text() for x in v.values()]
        elif isinstance(v, (unreal.Array, list)):
            texts = [x.export_text() for x in v]
        else:
            texts = [v.export_text()]
        names = [(re.search(r'AnimMontage_5_[0-9A-F]+=("[^"]*"|None)', t).group(1).split(".")[-1].strip("\"'")) for t in texts]
        print("[SA] %s.%s -> %s" % (name, prop, names))
