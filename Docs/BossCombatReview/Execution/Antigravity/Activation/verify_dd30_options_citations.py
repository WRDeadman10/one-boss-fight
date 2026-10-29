import os

citations = [
    ("Source/OneBossFight/Player/RPGBossActivation.h", "enum class ERPGWorldActivationOutcome : uint8"),
    ("Source/OneBossFight/Player/RPGBossActivation.h", "ActivateWorld(UWorld* ExpectedWorld"),
    ("Source/OneBossFight/Player/RPGBossActivation.cpp", "RPGBossWorldPreparation::PrepareWorldBatch"),
    ("Source/OneBossFight/Player/RPGBossActivation.cpp", "RegisterOwnedComponents"),
    ("Source/OneBossFight/Player/RPGBossWorldPreparation.h", "PrepareWorldBatch"),
    ("Source/OneBossFight/Player/RPGBossWorldInputCompiler.h", "CompileWorldInput"),
    ("Source/OneBossFight/Player/RPGBossWorldInputCompiler.cpp", "IsManifestHashShape"),
    ("Source/OneBossFight/Player/RPGEncounterBinding.h", "class ONEBOSSFIGHT_API ARPGEncounterBinding : public AActor"),
    ("Source/OneBossFight/Player/RPGEncounterBinding.h", "struct FRPGPlacedParticipantBinding"),
    ("Source/OneBossFight/Player/RPGEncounterBinding.h", "class ONEBOSSFIGHT_API URPGBossDefinition : public UPrimaryDataAsset"),
    ("Source/OneBossFight/Player/RPGEncounterBinding.cpp", "CompileParticipantImpl"),
    ("Source/OneBossFight/Player/RPGPlayerMovesSubsystem.h", "class ONEBOSSFIGHT_API URPGPlayerMovesSubsystem"),
    ("Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp", "void URPGPlayerMovesSubsystem::OnWorldBeginPlay(UWorld& InWorld)"),
    ("Source/OneBossFight/Player/RPGStartupChronology.cpp", "void RPGStartupChronology::AtWorldBeginPlay(UWorld& World)"),
    ("Scripts/RunEditorScript.ps1", "-ExecutePythonScript would exit the editor as soon as the script returns"),
    ("Docs/BossCombatReview/Execution/Antigravity/EngineRuns/DD30ChronologyRun1/chronology_raw.log", "Cmd: QUIT_EDITOR"),
    ("Docs/BossCombatReview/Execution/Antigravity/EngineRuns/DD30ChronologyRun1/chronology_raw.log", "census pawns=2 bosses=1 players=1"),
]

all_passed = True
for path, snippet in citations:
    if not os.path.exists(path):
        print(f"MISSING FILE: {path}")
        all_passed = False
        continue
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    if snippet not in text:
        print(f"MISSING SNIPPET in {path}: {snippet}")
        all_passed = False
    else:
        for idx, line in enumerate(text.splitlines()):
            if snippet in line:
                print(f"VERIFIED: {path}:{idx+1} -> {line.strip()[:60]}")
                break

if all_passed:
    print("\nALL 17 CITATIONS VERIFIED AGAINST DISK.")
else:
    raise SystemExit("Citation verification failed!")
