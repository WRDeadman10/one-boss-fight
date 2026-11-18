from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HEADER = (ROOT / "Source/OneBossFight/Player/RPGPlayerMovesSubsystem.h").read_text(encoding="utf-8")
SOURCE = (ROOT / "Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp").read_text(encoding="utf-8")
SELECTION = (ROOT / "Source/OneBossFight/Player/RPGEncounterSelectionSubsystem.cpp").read_text(encoding="utf-8")
PIE_DRIVER = (ROOT / "Scripts/Editor/pie_sevarog_arena_route_acceptance.py").read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


require("bool bEnableSevarogFrameworkArenaRoute = false;" in HEADER, "arena route must default off")
require('SevarogFrameworkRouteDefinition = TEXT("/Game/OneBossFight/Data/Sevarog/DA_Sevarog_Framework_Encounter.DA_Sevarog_Framework_Encounter");' in HEADER,
        "route definition path must match Sevarog framework encounter asset")
require("RefuseSevarogFrameworkArenaRoute" in SOURCE and "DefinitionInvalid" in SOURCE
        and "PlacedPackBossMissing" in SOURCE and "PlayerPossessionTimeout" in SOURCE,
        "refusal tokens must cover all invalid route states")
require("AddOnActorPreSpawnInitialization" in SOURCE and "OnActorPreSpawnInitialization" in SOURCE,
        "pack actor must be flagged before PostSpawnInitialize")
require("FWorldDelegates::OnWorldInitializedActors.AddUObject" in SOURCE
        and "FWorldDelegates::OnWorldInitializedActors.Remove" in SOURCE,
        "placed boss route must bind and release the pre-BeginPlay actor-initialized delegate")
placed = SOURCE.split("void URPGPlayerMovesSubsystem::ReplacePlacedArenaBosses", 1)[1].split(
    "void URPGPlayerMovesSubsystem::SuppressArenaBoss", 1)[0]
require("IsPackBoss(Actor)" in placed and "ResolveSevarogFrameworkArenaDefinition" in placed
        and "PendingArenaFrameworkBossTransform = SpawnTransform" in placed
        and "TrySpawnPendingArenaFrameworkBoss(World)" in placed
        and "bArenaFrameworkReplacementAttempted = true" in placed,
        "placed pack bosses must be validated and suppressed before one pending framework replacement")
runtime_replace = SOURCE.split("void URPGPlayerMovesSubsystem::ReplaceSuppressedArenaBoss", 1)[1].split(
    "void URPGPlayerMovesSubsystem::SpawnFrameworkArenaBoss", 1)[0]
require("bArenaFrameworkReplacementAttempted || bPendingArenaFrameworkBossSpawn" in runtime_replace
        and "SuppressArenaBoss(PackBoss)" in runtime_replace,
        "runtime-spawn fallback must suppress later pack bosses without creating duplicate framework bosses")
retry = SOURCE.split("void URPGPlayerMovesSubsystem::TrySpawnPendingArenaFrameworkBoss", 1)[1].split(
    "void URPGPlayerMovesSubsystem::SuppressArenaBoss", 1)[0]
require("IsLocalController()" in retry and "IsPackPlayer(Controller->GetPawn())" in retry
        and "MaxPossessionRetries = 100" in retry and "0.05f" in retry
        and "PlayerPossessionTimeout" in retry,
        "framework binding must wait for possessed local player with a bounded timeout")
require("BossCount=%d PlayerCount=%d CompetingPackBossCount=%d BossClasses=%s" in retry
        and "BuildArenaCensusDiagnostic(World)" in SOURCE,
        "route census refusal must include counts and visible boss class names")
pre = SOURCE.split("void URPGPlayerMovesSubsystem::OnActorPreSpawnInitialization", 1)[1].split(
    "void URPGPlayerMovesSubsystem::OnActorSpawned", 1)[0]
require('Actor->Tags.AddUnique(TEXT("ArenaRoute.Suppressed"))' in pre and "GetActorTransform()" in pre,
        "pre-spawn hook must tag and capture transform")
spawned = SOURCE.split("void URPGPlayerMovesSubsystem::OnActorSpawned", 1)[1].split(
    "bool URPGPlayerMovesSubsystem::IsSevarogFrameworkArenaRouteEnabled", 1)[0]
require('Actor->Tags.Contains(TEXT("ArenaRoute.Suppressed"))' in spawned
        and "ReplaceSuppressedArenaBoss(Actor)" in spawned, "post-spawn handler must route flagged pack boss immediately")
replace = SOURCE.split("void URPGPlayerMovesSubsystem::ReplaceSuppressedArenaBoss", 1)[1].split(
    "void URPGPlayerMovesSubsystem::ReplacePackPlayerWithGreystoneForTest", 1)[0]
require("SuppressArenaBoss(PackBoss)" in replace and "PackBoss->Destroy()" in SOURCE.split(
    "void URPGPlayerMovesSubsystem::SuppressArenaBoss", 1)[1].split(
        "void URPGPlayerMovesSubsystem::ReplaceSuppressedArenaBoss", 1)[0]
        and "bDeferConstruction = true" in replace,
        "replacement must destroy pack actor and defer framework construction")
require("BuildWorldBindingForRebind" in replace and "ActivateWorldForRebind" in replace
        and "InitializeSelectedEncounter(*Binding" in replace,
        "begun-world replacement must use production selection initialization, not test initialization")
world_begin = SOURCE.split("void URPGPlayerMovesSubsystem::OnWorldBeginPlay", 1)[1].split(
    "void URPGPlayerMovesSubsystem::Deinitialize", 1)[0]
require(world_begin.find("if (bSelectionRequested)") < world_begin.find("AttachBossDiagnostics(*It)"),
        "data-route world-begin branch must retain boss diagnostics attachment")
diagnostics = SOURCE.split("void URPGPlayerMovesSubsystem::AttachBossDiagnostics", 1)[1].split(
    "void URPGPlayerMovesSubsystem::", 1)[0]
require('Pawn->Tags.Contains(TEXT("ArenaRoute.Suppressed"))' in diagnostics,
        "project boss diagnostics must ignore pre-spawn-suppressed actors")
binding = SELECTION.split("bool URPGEncounterSelectionSubsystem::BuildWorldBindingInternal", 1)[1]
require('Pawn->Tags.Contains(TEXT("ArenaRoute.Suppressed"))' in binding,
        "world binding census must ignore flagged pack actor")
require("IsSevarogFrameworkArenaRouteEnabled" in SELECTION,
        "framework route must be explicitly admitted by the named production switch")
suppress = SOURCE.split("void URPGPlayerMovesSubsystem::SuppressArenaBoss", 1)[1].split(
    "void URPGPlayerMovesSubsystem::ReplaceSuppressedArenaBoss", 1)[0]
require("StopMovement()" in suppress and "StopLogic(" in suppress,
        "suppression must stop controller movement and brain logic before destruction")
require("bt_attack_ticks=%d" not in suppress and "BehaviorTreeAttackTicks = 0" not in suppress,
        "suppression log must not claim a hard-coded zero as a measured BehaviorTree tick count")

require("arena_pack_boss_suppressed actor=(\\S+) began_play=(\\d) montage_active=(\\d)" in PIE_DRIVER,
        "driver suppression parser must only consume observed lifecycle/montage fields")
require('"raw_behavior_tree_tick_count": True if bt_ticks_verified_zero else "BLOCKED_NOT_INSTRUMENTED"' in PIE_DRIVER,
        "driver must not mark raw BehaviorTree ticks verified without an actual counter observation")
require("RAW_BEHAVIOR_TREE_TICK_COUNTER_NOT_INSTRUMENTED" in PIE_DRIVER
        and "if not bt_ticks_verified_zero:" in PIE_DRIVER,
        "driver must retain the uninstrumented blocker until measured tick evidence exists")

require("FrameworkProfile->Mesh.LoadSynchronous()" in replace
        and "MeshComponent->SetSkeletalMesh(ProfileMesh)" in replace
        and "MeshComponent->SetRelativeTransform(FrameworkProfile->MeshRelativeTransform)" in replace
        and replace.find("MeshComponent->SetSkeletalMesh(ProfileMesh)") < replace.find("BuildWorldBindingForRebind"),
        "deferred framework boss must bind selected profile mesh and transform before production preflight")
require("FrameworkProfileMissing" in SOURCE and "FrameworkMeshMissing" in SOURCE,
        "missing profile or mesh dependencies must refuse route with fail-closed tokens")
require('unreal.SystemLibrary.execute_console_command(None, "rpg.Build Starter")' in PIE_DRIVER
        and 'unreal.SystemLibrary.execute_console_command(None, \'rpg.Build ""\')' in PIE_DRIVER,
        "PIE driver must set rpg.Build Starter for Smoke and reset on finish")
require('outcome=PlayerHealthReady hp=([0-9.eE+-]+) max_hp=([0-9.eE+-]+)' in PIE_DRIVER
        and '"player_health_current": float(player_health.group(1)) if player_health else None' in PIE_DRIVER
        and '"player_health_max": float(player_health.group(2)) if player_health else None' in PIE_DRIVER,
        "driver must parse the observed production player current/max health log fields")
require('"production_player_health_800_800": (' in PIE_DRIVER
        and 'checks.get("player_health_current") == 800.0' in PIE_DRIVER
        and 'checks.get("player_health_max") == 800.0' in PIE_DRIVER,
        "Smoke acceptance must fail closed unless current and maximum player health are both 800")
require('"smoke_starter_loadout_observed": checks.get("rpg_build_observed") == "Starter" if MODE == "Smoke" else True' in PIE_DRIVER
        and 'and STATE["checks"].get("rpg_build_observed") == "Starter"' in PIE_DRIVER,
        "PIE driver must evaluate starter loadout for Smoke criteria and readiness")
require("HealthDiag.Value == 0.0 && HealthDiag.bMaxValueReadable" in SOURCE
        and "FMath::IsFinite(MaxBack) && FMath::IsNearlyEqual(MaxBack, TargetHealthValue)" in SOURCE
        and "FMath::IsFinite(CurrentBack) && FMath::IsNearlyEqual(CurrentBack, TargetHealthValue)" in SOURCE,
        "sentinel health initialization must use exact zero check and finite readback verification")

require('"pie_world_observed": False' in PIE_DRIVER
        and '"pie_world_lost_at": None' in PIE_DRIVER
        and 'STATE["pie_world_observed"] = True' in PIE_DRIVER
        and 'STATE["pie_world_lost_at"] = None' in PIE_DRIVER
        and 'fail("PIE session ended prematurely without boss defeat (Escape or manual PIE stop observed)")' in PIE_DRIVER
        and 'fail("PIE world not observed within 60 seconds of begin_play request")' in PIE_DRIVER,
        "PIE driver must detect premature PIE teardown/Escape and bound initial PIE world startup")

full_defeat_pos = PIE_DRIVER.find('if MODE == "Full" and STATE["checks"].get("boss_defeated"):')
world_loss_pos = PIE_DRIVER.find('fail("PIE session ended prematurely without boss defeat (Escape or manual PIE stop observed)")')
require(full_defeat_pos != -1 and world_loss_pos != -1 and full_defeat_pos < world_loss_pos,
        "Full-mode BossDefeated evaluation must precede world teardown/loss failure")

print("C-1619 arena source contract: 29/29 PASS")
