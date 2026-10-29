# DD11 dormant/wake profile — actual source diff first

X259, Claude implementation. Owner all83/Data Assets and Details first direction. This closes the two private native dormant/wake authoring references without changing existing playback behavior or activating hydration.

## Exact six-file claim

NEW ONLY Player/RPGBossDormantWakeAdapters.h/.cpp and Tests/RPGBossDormantWakeAdaptersTests.cpp. EXISTING ONLY Player/RPGEncounterBinding.h/.cpp and Player/RPGBossDormantWake.h. Native DormantWake.cpp stays unchanged. Save exact preimages/full171-file Source manifest before edits. Current Binding h48d875f76efb0dd1319149f7a8359c6e5b215ec739616e72a3fe3f85e464578e, cpp5f63241d635c52955151fae21d1a455bfdfcc263e33f1ece46c5712e6fe4bb24; native Wake h f6cfdc3a884be0d212b2ccb066927f5c5ddb9a00d7e65a0139f8cd806a34b7f4, cppfd3df15b1530a227750548b4e7241f16d2f3e946e3b04e49bc28ce4ae9524788.

## Typed record/compiler

Add reflected FRPGDormantWakeConfig with EditAnywhere TSoftObjectPtr<UAnimSequence> DormantClip and WakeClip, plus DormantWake on URPGBossDefinition and value copy on FRPGParticipantConfig. Default paths exactly match the current native constructor: AN_Boss01_DormantIdle and AN_Boss01_Wake under the existing Boss01 Animations directory. Read full source strings, do not invent or use retired assets. Additive authoring defaults only, never fallback on invalid input; no schema bump/asset migration/save.

Shared ValidateDormantWake used by CompileParticipantImpl and adapter, both references required, first failure named with DormantWake.DormantClip/WakeClip path. Reuse the DD9/DD10 structural policy: set top-level soft object reference, no whitespace/control/subobject/missing mount/package/asset; no load or asset-registry query, no text parsing of malformed fixture paths, no class-path rule for animations. This is not engine-authoritative path validation, existence/type/cook/skeleton/timing proof. Keep existing identity/Stats/policies/profiles/phase/dependency checks and stale-output clearing unchanged, copy on both production and dev-synthetic paths. No new enabled flag or control over the existing rpg.WakeClip test cvar.

## Minimal private-access seam explicitly released for review

The native references are private. In RPGBossDormantWake.h ONLY add the narrow forward declaration/exported signature and matching friend for the new RPGBossDormantWakeAdapters::ConfigureDormantWake(UActorComponent&, const FRPGParticipantConfig&, FString&) function. Forward-declare the config as needed. Do not make fields public, add reflected setters, generic reflection assignment, a test-author toggle, or expose runtime state. No native cpp/playback/BeginPlay/EndPlay/tick logic or defaults change. Any different/larger indispensable seam must be proposed as an exact delta before expanding.

Adapter exact native class, accepted component/owner lifecycle guards (invalid/destroying first, wrong class, registered/begun, invalid/destroying/beginning/begun owner). Validate entire record BEFORE writing exactly DormantClip/WakeClip via the narrow friend, soft paths only. No creation/registration/load/playback/actor lookup/attributes/timers/tag/cvar mutation. LoadedDormantClip/LoadedWakeClip, montage handles, stage/waking/start time and counters remain unchanged. MakeDormantWakePlan class/name matching native legacy attachment, RequiredFields two DormantWake paths; unwired fragment, no DD5 insertion/readiness/legacy suppression.

## Actual tests, not another plan

Isolated native tests for distinct nondefault references, conflicting manifest Value ignored, null/structurally malformed first and last refs/whole-record no partial writes, diagnostics clear, class/lifecycle/owner/destroyed-retained guards, independent instances/config snapshots/CDO defaults, actual synthetic compiler copy/invalid-clears-prior-output and production early rejection; prior scalar/profile/identity checks retained. Reflection/type/editability/defaults prove declarations only. Include default-reference nonloading object/package presence witness with already-loaded limits. Six focused paths may mirror Assign/Validation/Isolation/Rejections/Compile/Authoring; report actual discovery later rather than assuming total101.

Tests can READ the two private reflected properties through typed FSoftObjectProperty for assertions; no runtime reflection-based adapter. For a begun guard, inspect actual BeginPlay first. A test-only isolated native fixture may clear its two soft references with a narrowly named local reflection helper before DispatchBeginPlay, preventing real asset loads; it must assert prerequisites and never run a real wake/tick or touch a shipped asset. Document such fixture setup. If that cannot be done safely, show exact obstacle; do not weaken the guard or change native behavior.

Deliver actual six-file diff, exact preimages/Review copies/new full manifest/pins/sha256 index, coverage and limits. NO UHT/build/automation until Codex reviews actual source. No other Source/test/script/content/pack/buildflag changes, wiring/activation/reservation/PIEgate/package/noneditor/git. AG continues offline input packet, no engine work or staging while source is evolving. After verification, combine reviewed fragments and address actual production dependencies under separately reviewed integration orders; no Ready claim from these two path assignments.
