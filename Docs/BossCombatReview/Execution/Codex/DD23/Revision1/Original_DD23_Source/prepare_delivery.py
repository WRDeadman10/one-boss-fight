"""C269 source-only evidence capture and documentation. Does not execute Unreal."""
from pathlib import Path
import sys,subprocess,json,re,hashlib
here=Path(__file__).resolve().parent
root=here.parents[4]
test=root/'Source/OneBossFight/Tests/RPGBossLookAdaptersTests.cpp'
s=test.read_text(encoding='utf-8').replace('FString::ChrN(1100,','FString::ChrN(1000,').replace('no invented 1024-character policy','long representable FName; no new record length cap')
s=s.replace('\tauto Defaults = Definition(FRPGLookConfig());','\tauto EmptyPieces = Definition(RecordA());\n\tEmptyPieces->Look.Pieces.Reset();\n\tTestTrue(TEXT("empty pieces compile without defaults substituted"), Compile(*EmptyPieces, Out).IsReady() && Out.IsValid() && Out->Look.Pieces.IsEmpty());\n\tauto Defaults = Definition(FRPGLookConfig());')
test.write_text(s,encoding='utf-8')
s=(here.parent/'DD22/prepare_source.py').read_text(encoding='utf-8').replace('DD22','DD23').replace('HealPunish','Look').replace('==200','==203').replace('==203\n','==206\n').replace('"baseline":200,"current":203','"baseline":203,"current":206').replace('"old_files_unchanged":198','"old_files_unchanged":201')
# Explicit assertion, independent of textual substitutions above.
s=s.replace('assert len(baseline)==203 and len(current)==206','assert len(baseline)==203 and len(current)==206')
(here/'prepare_source.py').write_text(s,encoding='utf-8')
completed=subprocess.run([sys.executable,str(here/'prepare_source.py')],cwd=root,capture_output=True,text=True)
(here/'source_capture_output.txt').write_text(completed.stdout+'\n'+completed.stderr,encoding='utf-8')
assert completed.returncode==0,completed.stdout+completed.stderr
details=json.loads((here/'source_checks.json').read_text(encoding='utf-8'))
assert details['baseline']==203 and details['current']==206 and details['old_files_unchanged']==201
summary='DD23 C269 source-only (2026-10-29): typed Look five-field profile/defaults, compiler shared validation/copy and unwired lifecycle-safe adapter, six test sources UNRUN. Source203->206,201 prior unchanged; Codex/DD23/DELIVERY_TO_CLAUDE.md. Claude SOURCE REVIEW PENDING; no build/UHT/engine run. C269 independently accepted DD21/DD22 scoped run; its limits remain.'
for n in ['TASKS.md','TEST_PLAN.md','DECISIONS.md']:
    with (root/'Documentation'/n).open('a',encoding='utf-8') as f:f.write('\n\n'+summary+'\n')
ki=root/'Documentation/KNOWN_ISSUES.md'
assert 'KI-131' not in ki.read_text(encoding='utf-8')
with ki.open('a',encoding='utf-8') as f:
    f.write('\n\n| KI-131 | DD23 source-only limits | Required mesh paths prove structure only; no registry/class/existence/load/skeleton/pose/socket-fit/cook proof. Native body load failure warns and leaves pack mesh; piece failure warns/omits; sword failure warns/leaves no new sword. Missing socket uses hand_r with warning (wrong grip). Empty Pieces valid; duplicates refused by authored record contract. No numeric authored fields, so no magnitude ceiling/arithmetic audit. ComponentBegunPlay source-only; no Apply/enable-for-test/runtime appearance or serialized/Details proof. Six tests UNRUN; plan UNWIRED. | Open; lead source review pending |\n')
current=root/'Docs/BossCombatReview/Execution/Codex/CURRENT_TASK.md'
current.write_text('CURRENT IMPLEMENTER C269/C274: '+summary+'\n\n'+current.read_text(encoding='utf-8'),encoding='utf-8')
body='''# DD23 typed Look source handoff — C269

SOURCE ONLY: three NEW adapter/test files; existing ONLY RPGEncounterBinding.h/.cpp. 203->206 Source manifest,201 prior files unchanged, exact Binding preimages/five-file diff/five pins and byte-identical Review copies. No native Look/Bleed/PlayerMoves/preflight/preparation/reservation edit. No engine/build/UHT/automation, asset or git operation.

FRPGLookConfig has exactly bEnabled, Body, Pieces, Sword, SwordSocket with native defaults. The five default asset references (Body, three Pieces, Sword) are EXACT constructor literals from RPGBossLook.cpp:17-23, repeated ONLY in Binding.h. Files statically exist at corresponding Content/OneBossFight/Boss01/Body and Weapons uasset paths; native_default_assets.json records each path/size/SHA256. This is presence/hash evidence, not class/skeleton/load/cook/runtime proof. All other new Source files contain no quoted asset literals under the production mount.

ValidateLook order: required/well-formed Body; each Piece in index order required/well-formed/duplicate; required/well-formed Sword; required/non-whitespace/control SwordSocket. Empty Pieces VALID, both bEnabled values accepted but disabled still validates. First failure returned; no repair/fallback/parse/load/registry/mount/class query. Private PathProblem/CheckRequiredReference exactly restate accepted Bleed policy (Bleed unchanged), including FPackageName::IsValidTextForLongPackageName and FName::IsValidXName. Duplicate is authored, not a native guard. TSet<FSoftObjectPath> uses asset FName identity equality (case-insensitive package/object; subobjects already refused). Per-piece errors include index, e.g. Look.Pieces[2].

Exact-class/live/unregistered/not-begun component plus live not-begun owner check, then complete validator BEFORE five assignments. Array copied by value, no transient/runtime state write or consumer insertion. Native instance RPGBossLook confirmed RPGPlayerMovesSubsystem.cpp:191; exact five required paths. Plan UNWIRED, no Ready/legacy suppression.

Six test sources Look.{Assign,Validation,Isolation,Rejections,Compile,Authoring}, all UNRUN. Forty bad cases include the accepted ten Bleed malformed paths in each of Body/Piece/Sword, nulls, indexed duplicate/case-insensitive duplicate, None/mixed-case None/whitespace/control socket. Cover empty Pieces, first-failure order, disabled full validation, atomic no-write, independent array copies across input/owners/CDO/compiler snapshots, populated-output clearing, retained prior validation, exact reflection/types/native defaults. Plain begun owner receives component only afterwards. No Look BeginPlay/Apply/SetEnabledForTest/Revert or mesh load is invoked; ComponentBegunPlay remains source-only. A long representable FName is a valid fixture; no new1024 record cap/regex/list-shape rule was introduced.

C271 four toolkit alignment points: (1) C++ returns FIRST failure; (2) duplicate detection uses FSoftObjectPath/FTopLevelAssetPath/FName equality, not raw case-sensitive strings, with a mixed-case duplicate fixture; (3) no new SwordSocket length cap and typed TArray needs no JSON-list check (a toolkit JSON-list check must be explicitly toolkit-only); (4) FName IsNone treats mixed-case None as Missing, tested. AG can now mechanically compare this frozen source; no toolkit edit by Codex.

No numeric authored fields, hence no numeric arithmetic audit/ceiling applies. Read-only native review: constructor only sets defaults/tick policy; BeginPlay schedules Apply; Body failure warns and returns with pack mesh retained (:64-67), piece failure warns/omits (:110-116), sword failure warns/no new sword (:137), missing socket warns then hand_r fallback (:127-131). These runtime behaviours remain UNRESOLVED, never executed here. No contradictory lifecycle or empty-Pieces fact found, no stop condition fired.

File capture exit0 proves integrity only, not compilation/Unreal tests. Docs updated REVIEW PENDING, KI-131 preserves limits. Please independently review actual diff/pins/tests and release one scoped run only if accepted. Expected159 is not a measured result; DD21/DD22 remains the last measured153.

Five frozen pins:
'''
body+=''.join(r['path']+' SHA256 '+r['sha256']+'\n' for r in details['files'])
(here/'DELIVERY_TO_CLAUDE.md').write_text(body,encoding='utf-8')
sys.path.insert(0,str(here.parent/'EvidenceTools'))
from verify_bundle import digest,verify_receipt
assert verify_receipt(here/'post_source_manifest_sha256.txt',root,root)['all_verified']
assert verify_receipt(here/'live_pins_sha256.txt',root,root)['all_verified']
rows=[p for p in sorted(here.rglob('*')) if p.is_file() and p.name not in {'evidence_sha256.txt','MESSAGE_TO_CLAUDE.txt'}]
receipt=here/'evidence_sha256.txt'
receipt.write_text(''.join(digest(p)+' *'+p.relative_to(here).as_posix()+'\n' for p in rows),encoding='utf-8')
assert verify_receipt(receipt,here,root)['all_verified']
(here/'MESSAGE_TO_CLAUDE.txt').write_text(body+'\nReceipt Codex/DD23/evidence_sha256.txt: '+str(len(rows))+' files; SHA256 '+digest(receipt)+'.\n',encoding='utf-8')
print('DD23 source capture/receipt integrity verified, NOT compilation or Unreal execution:',len(rows),digest(receipt))
