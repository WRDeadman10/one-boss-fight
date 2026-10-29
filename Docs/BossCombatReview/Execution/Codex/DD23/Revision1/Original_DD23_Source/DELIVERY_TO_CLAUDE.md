# DD23 typed Look source handoff — C269

SOURCE ONLY: three NEW adapter/test files; existing ONLY RPGEncounterBinding.h/.cpp. 203->206 Source manifest,201 prior files unchanged, exact Binding preimages/five-file diff/five pins and byte-identical Review copies. No native Look/Bleed/PlayerMoves/preflight/preparation/reservation edit. No engine/build/UHT/automation, asset or git operation.

FRPGLookConfig has exactly bEnabled, Body, Pieces, Sword, SwordSocket with native defaults. The five default asset references (Body, three Pieces, Sword) are EXACT constructor literals from RPGBossLook.cpp:17-23, repeated ONLY in Binding.h. Files statically exist at corresponding Content/OneBossFight/Boss01/Body and Weapons uasset paths; native_default_assets.json records each path/size/SHA256. This is presence/hash evidence, not class/skeleton/load/cook/runtime proof. All other new Source files contain no quoted asset literals under the production mount.

ValidateLook order: required/well-formed Body; each Piece in index order required/well-formed/duplicate; required/well-formed Sword; required/non-whitespace/control SwordSocket. Empty Pieces VALID, both bEnabled values accepted but disabled still validates. First failure returned; no repair/fallback/parse/load/registry/mount/class query. Private PathProblem/CheckRequiredReference exactly restate accepted Bleed policy (Bleed unchanged), including FPackageName::IsValidTextForLongPackageName and FName::IsValidXName. Duplicate is authored, not a native guard. TSet<FSoftObjectPath> uses asset FName identity equality (case-insensitive package/object; subobjects already refused). Per-piece errors include index, e.g. Look.Pieces[2].

Exact-class/live/unregistered/not-begun component plus live not-begun owner check, then complete validator BEFORE five assignments. Array copied by value, no transient/runtime state write or consumer insertion. Native instance RPGBossLook confirmed RPGPlayerMovesSubsystem.cpp:191; exact five required paths. Plan UNWIRED, no Ready/legacy suppression.

Six test sources Look.{Assign,Validation,Isolation,Rejections,Compile,Authoring}, all UNRUN. Forty bad cases include the accepted ten Bleed malformed paths in each of Body/Piece/Sword, nulls, indexed duplicate/case-insensitive duplicate, None/mixed-case None/whitespace/control socket. Cover empty Pieces, first-failure order, disabled full validation, atomic no-write, independent array copies across input/owners/CDO/compiler snapshots, populated-output clearing, retained prior validation, exact reflection/types/native defaults. Plain begun owner receives component only afterwards. No Look BeginPlay/Apply/SetEnabledForTest/Revert or mesh load is invoked; ComponentBegunPlay remains source-only. A long representable FName is a valid fixture; no new1024 record cap/regex/list-shape rule was introduced.

C271 four toolkit alignment points: (1) C++ returns FIRST failure; (2) duplicate detection uses FSoftObjectPath/FTopLevelAssetPath/FName equality, not raw case-sensitive strings, with a mixed-case duplicate fixture; (3) no new SwordSocket length cap and typed TArray needs no JSON-list check (a toolkit JSON-list check must be explicitly toolkit-only); (4) FName IsNone treats mixed-case None as Missing, tested. AG can now mechanically compare this frozen source; no toolkit edit by Codex.

No numeric authored fields, hence no numeric arithmetic audit/ceiling applies. Read-only native review: constructor only sets defaults/tick policy; BeginPlay schedules Apply; Body failure warns and returns with pack mesh retained (:64-67), piece failure warns/omits (:110-116), sword failure warns/no new sword (:137), missing socket warns then hand_r fallback (:127-131). These runtime behaviours remain UNRESOLVED, never executed here. No contradictory lifecycle or empty-Pieces fact found, no stop condition fired.

File capture exit0 proves integrity only, not compilation/Unreal tests. Docs updated REVIEW PENDING, KI-131 preserves limits. Please independently review actual diff/pins/tests and release one scoped run only if accepted. Expected159 is not a measured result; DD21/DD22 remains the last measured153.

Five frozen pins:
Source/OneBossFight/Player/RPGBossLookAdapters.h SHA256 ca3bfb395dfdf9791b771a0139b706751113a2ffe2d55b8972188141642e886d
Source/OneBossFight/Player/RPGBossLookAdapters.cpp SHA256 e99af51eeb4310a0e31d1f063cd8e15445be7b417d94137f9ccea4d88e3ce5ce
Source/OneBossFight/Player/RPGEncounterBinding.h SHA256 1cbc444b2dd126375ec0a798bdf557b6d31b45df09936bdd70bd8136188d7090
Source/OneBossFight/Player/RPGEncounterBinding.cpp SHA256 c12fe14a5f17827d80c11238d2965e0db16a8cb6378dc483263683960fd5a71d
Source/OneBossFight/Tests/RPGBossLookAdaptersTests.cpp SHA256 436a413e300344cab0ed10538d6f37457278e57d101c89a8e6999c5afb33d983
