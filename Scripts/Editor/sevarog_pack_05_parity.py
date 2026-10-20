"""Sevarog on the pack, step 5: the features the C++ boss had that step 2-4 left out. Run in the open editor after steps 1-4.

  * AM_SevPack_Shockwave: radial hit (the collision trace sphere is widened by TraceRadiusModifier), ground Niagara ring and sound
  * GA_Sev_Lightning: copy of the pack's fireball enemy ability; fires BP_SevBolt (copy of the fireball projectile with Sevarog's comet
    particle) from the scythe bone when the cast montage sends GameplayEvent.FireProjectile.RightHand
  * GA_Sev_PhaseRoar: copy of GA_Sev_EnterCombat with the roar montage (the director component activates it at 50 % health)
  * GA_Sev_Death: copy of the pack's GA_EnemyDeath with Sevarog's death montage (replaces the ragdoll death in his combat style)
Idempotent for the montage and ability assets; the style entries are rebuilt from the saved style text each run."""
import re
import unreal

HEAD = open(r"C:/Users/winss/Documents/Unreal Projects/OneBossFight/Scripts/Editor/sevarog_pack_02_montages_abilities.py", encoding="utf-8").read()
exec(HEAD[:HEAD.index("ONLY_TOGGLE = globals()")])  # helper functions and constants of step 2

log = lambda m: unreal.log("[SevPack5] " + m)
OUT = "/Game/OneBossFight/SevarogPack"
STYLE = OUT + "/SevarogCombatStyle"
AN_SEND = A + "AdvancedCombatFramework/AbilitySystem/AnimNotifes/AN_SendEventToAbility.AN_SendEventToAbility_C"
NS_SHOCKWAVE = "/Game/Free_Spells/VFX_Niagara/NS_Free_Spells_Shockwave"
SHOCK_SOUND = "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_Ability_Ultimate"
CAST_SOUND = "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_Ability_Q"
COMET = "/Game/ParagonSevarog/FX/Particles/Abilities/Primary/FX/P_SevarogComet"
tools = unreal.AssetToolsHelpers.get_asset_tools()
lib = unreal.AnimationLibrary


def delete_if_loaded(path):
    if unreal.load_asset(path) is not None:
        unreal.EditorAssetLibrary.delete_asset(path)


def dup(src, folder, name):
    delete_if_loaded(folder + "/" + name)
    asset = tools.duplicate_asset(name, folder, unreal.load_asset(src))
    if asset is None:
        raise RuntimeError("duplicate failed " + src)
    return asset


def new_montage(name, sequence_name):
    delete_if_loaded(MONT + "/" + name)
    sequence = find_pack_asset("AnimSequence", sequence_name)
    factory = unreal.AnimMontageFactory()
    factory.set_editor_property("source_animation", sequence)
    montage = tools.create_asset(name, MONT, unreal.AnimMontage, factory)
    unreal.RPGMontageUtils.set_montage_slot(montage, SLOT)
    lib.add_animation_notify_track(montage, "PackCombat")
    return montage, sequence


# ---- Shockwave: wide trace sphere + ring effect --------------------------------------------------------------------------------
shock = unreal.load_asset(MONT + "/AM_SevPack_Shockwave")
lib.remove_animation_notify_track(shock, "PackCombat")
lib.add_animation_notify_track(shock, "PackCombat")
seq = find_pack_asset("AnimSequence", "Ultimate_Swing_120fps")
start, end = motion_window(seq)
peak = (start + end) / 2.0
length = shock.get_play_length()
lib.add_animation_notify_state_event(shock, "PackCombat", 0.0, length * 0.9, load_class(ANS_DISABLE))
rot = lib.add_animation_notify_state_event(shock, "PackCombat", 0.0, max(start * 0.9, 0.1), load_class(ANS_ROTATE))
rot.set_editor_property("RotationInterpSpeed", 520.0)
rot.set_editor_property("Desired Rotation Type", FACE_TARGET)
trace = lib.add_animation_notify_state_event(shock, "PackCombat", max(peak - 0.12, 0.0), 0.3, load_class(ANS_COLLISION))
trace.set_editor_property("Collision Target Tag", tag("TargetType.MainWeapon"))
trace.set_editor_property("EventTag", tag("GameplayEvent.AttackHit"))
trace.set_editor_property("TraceRadiusModifier", 400.0)  # ~450 cm sphere around the scythe tip as it hits the ground
trace.set_editor_property("AttackData", unreal.load_asset(KNOCKDOWN_DATA))
fx = lib.add_animation_notify_event(shock, "PackCombat", peak, unreal.RPGAN_SpawnEffect)
fx.set_editor_property("niagara_effect", unreal.load_asset(NS_SHOCKWAVE))
fx.set_editor_property("sound", unreal.load_asset(SHOCK_SOUND))
fx.set_editor_property("forward_offset", 200.0)
fx.set_editor_property("ground_drop", 155.0)
fx.set_editor_property("scale", 5.0)
lib.add_animation_notify_event(shock, "PackCombat", length * 0.9, load_class(AN_END))
unreal.EditorAssetLibrary.save_loaded_asset(shock)
log("Shockwave rebuilt: hit window %.2f-%.2f peak %.2f" % (peak - 0.12, peak + 0.18, peak))

# ---- Lightning cast montage ----------------------------------------------------------------------------------------------------
cast, cast_seq = new_montage("AM_SevPack_Lightning", "Cast")
clen = cast.get_play_length()
lib.add_animation_notify_state_event(cast, "PackCombat", 0.0, clen * 0.9, load_class(ANS_DISABLE))
rot = lib.add_animation_notify_state_event(cast, "PackCombat", 0.0, clen * 0.5, load_class(ANS_ROTATE))
rot.set_editor_property("RotationInterpSpeed", 720.0)
rot.set_editor_property("Desired Rotation Type", FACE_TARGET)
send = lib.add_animation_notify_event(cast, "PackCombat", clen * 0.5, load_class(AN_SEND))
send.set_editor_property("Event Tag", tag("GameplayEvent.FireProjectile.RightHand"))
cue = lib.add_animation_notify_event(cast, "PackCombat", clen * 0.5, unreal.RPGAN_SpawnEffect)
cue.set_editor_property("sound", unreal.load_asset(CAST_SOUND))
lib.add_animation_notify_event(cast, "PackCombat", clen * 0.9, load_class(AN_END))
unreal.EditorAssetLibrary.save_loaded_asset(cast)
log("Lightning montage %.2fs, projectile at %.2fs" % (clen, clen * 0.5))

# ---- Roar montage ----------------------------------------------------------------------------------------------------------------
roar, _ = new_montage("AM_SevPack_Roar", "Ultimate_Targeting")
rlen = roar.get_play_length()
lib.add_animation_notify_state_event(roar, "PackCombat", 0.0, rlen * 0.9, load_class(ANS_DISABLE))
lib.add_animation_notify_event(roar, "PackCombat", rlen * 0.7, load_class(AN_END))
unreal.EditorAssetLibrary.save_loaded_asset(roar)

# ---- Death montage (holds its last pose) -----------------------------------------------------------------------------------------
death, _ = new_montage("AM_SevPack_Death", "Death_front")
try:
    death.set_editor_property("enable_auto_blend_out", False)
except Exception as exc:
    log("auto blend out not settable: %s" % str(exc)[:80])
unreal.EditorAssetLibrary.save_loaded_asset(death)

# ---- Projectile -------------------------------------------------------------------------------------------------------------------
bolt = dup(A + "MagicCombatSystem/Blueprints/Abilities/FireBall/BP_FireBallProjectile", OUT, "BP_SevBolt")
sub = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lb = unreal.SubobjectDataBlueprintFunctionLibrary
for h in sub.k2_gather_subobject_data_for_blueprint(bolt):
    d = lb.get_data(h)
    o = lb.get_object(d)
    name = str(lb.get_display_name(d))
    if name.startswith("ProjectileParticle") and isinstance(o, unreal.ParticleSystemComponent):
        o.set_editor_property("template", unreal.load_asset(COMET))
        log("projectile particle = P_SevarogComet")
    elif name.startswith("ProjectileMesh") and isinstance(o, unreal.StaticMeshComponent):
        o.set_editor_property("visible", False)
unreal.BlueprintEditorLibrary.compile_blueprint(bolt)
unreal.EditorAssetLibrary.save_loaded_asset(bolt)

# ---- Abilities --------------------------------------------------------------------------------------------------------------------
lightning = dup(A + "MagicCombatSystem/Blueprints/AI/ExampleMagicEnemy/GA_Fireball_Enemy", ABIL, "GA_Sev_Lightning")
cdo = unreal.get_default_object(lightning.generated_class())
template = cdo.get_editor_property("AttackMontages")[0]
cdo.set_editor_property("AttackMontages", [ability_montage(template, cast)])
cdo.set_editor_property("ProjectilesToFire", [bolt.generated_class()])
sockets = cdo.get_editor_property("ProjectileHandSocketNames")
for key in list(sockets.keys()):
    sockets[key] = "weapon_r"
cdo.set_editor_property("ProjectileHandSocketNames", sockets)
unreal.BlueprintEditorLibrary.compile_blueprint(lightning)
unreal.EditorAssetLibrary.save_loaded_asset(lightning)
log("GA_Sev_Lightning ready")

phase = dup(ABIL + "/GA_Sev_EnterCombat", ABIL, "GA_Sev_PhaseRoar")
set_single_montage("GA_Sev_PhaseRoar", "Enter Combat Montage", roar)

sev_death = dup(A + "MeleeCombatSystem/Blueprints/Abilities/AI/GA_EnemyDeath", ABIL, "GA_Sev_Death")
cdo = unreal.get_default_object(sev_death.generated_class())
# The pack's death ability has no montage entry to copy, so borrow an F_AbilityMontage struct from the enter-combat ability.
enter_cdo = unreal.get_default_object(unreal.load_asset(ABIL + "/GA_Sev_EnterCombat").generated_class())
template = enter_cdo.get_editor_property("Enter Combat Montage")
cdo.set_editor_property("DeathMontages", [ability_montage(template, death)])
unreal.BlueprintEditorLibrary.compile_blueprint(sev_death)
unreal.EditorAssetLibrary.save_loaded_asset(sev_death)
log("GA_Sev_Death ready")

# ---- Combat style: new abilities, death replaced ------------------------------------------------------------------------------------
style = unreal.load_asset(STYLE)
entry = style.get_editor_property("AbilitiesSet")[0]
text = entry.export_text()


def cls(name):
    return '"/Script/Engine.BlueprintGeneratedClass\'%s/%s.%s_C\'"' % (ABIL, name, name)


text = re.sub(r'"[^"]*GA_EnemyRagdollDeath[^"]*"', cls("GA_Sev_Death"), text)
for name in ("GA_Sev_Lightning", "GA_Sev_PhaseRoar"):
    if name not in text:
        text = re.sub(r"(Abilities_\d+_[0-9A-F]+=\()", lambda m: m.group(1) + cls(name) + ",", text, count=1)
entry.import_text(text)
style.set_editor_property("AbilitiesSet", [entry])
unreal.EditorAssetLibrary.save_loaded_asset(style)
log("style abilities: %s" % re.findall(r"GA_\w+?\.", text))
