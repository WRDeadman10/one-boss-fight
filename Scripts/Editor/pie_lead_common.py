"""Shared, read-only PIE probe operations. Pass ``ue`` in offline tests."""


def engine(ue=None):
    if ue is not None:
        return ue
    import unreal
    return unreal


def component(actor, class_name, ue=None):
    api = engine(ue)
    if actor is None:
        return None
    return next((item for item in actor.get_components_by_class(api.ActorComponent)
                 if item.get_class().get_name() == class_name), None)


def boss_actor(world, ue=None):
    api = engine(ue)
    if world is None:
        return None
    return next((actor for actor in api.GameplayStatics.get_all_actors_of_class(world, api.Character)
                 if actor.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None)


def game_time(world, ue=None):
    return engine(ue).GameplayStatics.get_time_seconds(world)


def player_montage(pawn, ue=None):
    api = engine(ue)
    if pawn is None:
        return None, None
    for mesh in pawn.get_components_by_class(api.SkeletalMeshComponent):
        instance = mesh.get_anim_instance()
        montage = instance.get_current_active_montage() if instance else None
        if montage:
            return montage.get_name(), instance.montage_get_position(montage)
    return None, None


def enter_combat_tag(ue=None):
    tags = engine(ue).GameplayTagContainer()
    tags.import_text('(GameplayTags=((TagName="Ability.EnterCombat")))')
    return tags


def enter_combat(pawn, ue=None):
    asc = component(pawn, "BP_AdvancedAbilitySystemComponent_C", ue)
    if not asc:
        raise RuntimeError("player ability component not found")
    asc.call_method("Try Activate Abilities By Tag", args=(enter_combat_tag(ue),))


def place_player(pc, pawn, location, yaw, ue=None):
    api = engine(ue)
    rotation = api.Rotator(0.0, 0.0, yaw)
    pawn.set_actor_location_and_rotation(api.Vector(*location), rotation, False, True)
    pc.set_control_rotation(rotation)


def boss_debug(boss, ue=None):
    return component(boss, "RPGCombatDebug", ue)


def refill_player(boss, ue=None):
    debug = boss_debug(boss, ue)
    if not debug:
        raise RuntimeError("RPGCombatDebug missing on boss")
    debug.debug_refill_player()


def health(actor, ue=None):
    api = engine(ue)
    attributes = component(actor, "BP_AttributesComponent_C", api)
    if not attributes:
        return None
    tag = api.GameplayTag()
    tag.import_text('(TagName="Attribute.Health")')
    return float(attributes.call_method("Get Current Attribute Value", args=(tag,)))


def finished(log, reason, ue=None):
    api = engine(ue)
    log("SUMMARY finished: " + reason)
    end_play(api)


def end_play(ue=None):
    api = engine(ue)
    api.get_editor_subsystem(api.LevelEditorSubsystem).editor_request_end_play()
