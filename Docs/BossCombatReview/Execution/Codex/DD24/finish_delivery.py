from pathlib import Path
import sys,json
here=Path(__file__).resolve().parent
root=here.parents[4]
sys.path.insert(0,str(here.parent/'EvidenceTools'))
from verify_bundle import digest,verify_receipt
assert verify_receipt(here/'post_source_manifest_sha256.txt',root,root)['all_verified']
assert verify_receipt(here/'live_pins_sha256.txt',root,root)['all_verified']
details=json.loads((here/'source_checks.json').read_text(encoding='utf-8'))
summary='DD24 C275/C281 source-only promotion: typed CloseClipSwap5fields, shared compiler validation/copy and lifecycle-safe unwired plan. Three new+Binding.h/.cpp only,206->209 Source/204 prior unchanged.19collection mutations audited, no same-array alias. Six test sources UNRUN; lead SOURCE REVIEW PENDING. Codex/DD24/DELIVERY_TO_CLAUDE.md. No build/UHT/engine/git/asset operation. DD25 staging next only.'
for n in ['TASKS.md','TEST_PLAN.md','DECISIONS.md']:
    with (root/'Documentation'/n).open('a',encoding='utf-8') as f:f.write('\n\n'+summary+'\n')
with (root/'Documentation/TEST_PLAN.md').open('a',encoding='utf-8') as f:
    f.write('''

DD23 C281 accepted measured record (both attempts retained side by side):

| Attempt | Actual result | Raw evidence |
|---|---|---|
| DD23 attempt1 C275 | Build/UHT exit0; focused Look engine exit3/TArray self-alias assertion,2 completed of6 discovered; full/CookCoverage NOT RUN | Codex/DD23/run_2026-10-29, failed raw bd5c3dcc2948a7167fcc88f0b17787e655331c277009fa18aabc313238bbf624 |
| DD23 attempt2 C277, accepted C281 | Incremental build exit0/5s, no UHT invocation; focused6/full159 unique Success, exact153+6/CookCoverage,206 Source unchanged; warning63 matches DD22 | Codex/DD23/attempt2_2026-10-29, focused14c1dc1459b6a14c12ce9df942d1c2b985cf4af96c45b7768021204fabcdce75/full44274cd35a141b449d62c305a961f7621b51b9502637cb18fcbeb4efd60f9962 |
''')
ki=root/'Documentation/KNOWN_ISSUES.md'
assert 'KI-132' not in ki.read_text(encoding='utf-8')
with ki.open('a',encoding='utf-8') as f:
    f.write('\n\n| KI-132 | DD24 source-only limits | Class/property names and montage references prove syntax only; no ability/reflection/load/class/skeleton/timing/cook/live swap or serialized/Details proof. Native permanent-failure guards and hardcoded pack mapping require runtime validation; missing ability returns waiting, not permanent failure. No numeric authored fields or arithmetic audit. ComponentBegunPlay guard source-only, plan UNWIRED. Six tests UNRUN; source review pending. | Open |\n')
current=root/'Docs/BossCombatReview/Execution/Codex/CURRENT_TASK.md'
current.write_text('CURRENT IMPLEMENTER C281: DD23 attempt2 accepted; '+summary+'\n\n'+current.read_text(encoding='utf-8'),encoding='utf-8')
body='''# DD24 typed CloseClipSwap SOURCE handoff — C275/C281

Three NEW adapter/test files; ONLY existing Binding.h/.cpp edited.206->209 Source manifest,204 old files byte-equal, exact preimages/five-file diff/five pins/Review copies. Staged Binding base was checked against CURRENT accepted1cbc444b/c12fe14a before promotion; no stale Binding overwrite. No build/UHT/engine/asset/git operation or native/profile/planner/wiring edit.

FRPGCloseClipSwapConfig contains exactly native CloseAbilityClassName, AttackMontagesName, A1Montage, A3aMontage, A3bMontage in order. Names/defaults match header; three soft paths match native constructor RPGBossCloseClipSwap.cpp:44-46 exactly, repeated ONLY in Binding.h. Asset files present under Content/OneBossFight/Boss01/Animations (AM_Boss01_A1, AM_Boss01_A3a, AM_Boss01_A3b); native_default_assets.json records paths/hashes. Presence/hash is not load/class/cook proof. Other new Source files have no quoted production-mount path.

Validation first failure in contract order: CloseAbilityClassName required/no whitespace/control; AttackMontagesName same; A1Montage, A3aMontage, A3bMontage required/well-formed via privately restated accepted Bleed/Look PathProblem. Missing/Malformed only. No _C suffix, ASCII regex, length, registry/mount/class/existence query or load. NO duplicate rule: independent scalar replacement slots can share one asset without allocating duplicate components; native mapping checks pack slot identity, not uniqueness of replacement references. No numeric authored fields => no NotFinite/ceiling/numeric arithmetic audit applies.

Lifecycle check exact live class/not destroyed/unregistered/not begun/live not-begun owner, full record validation then all5 writes. No loaded montages/runtime state/test-enable knob assigned. Native instance RPGBossCloseClipSwap confirmed PlayerMoves.cpp:204; exact5paths. Plan UNWIRED, no Ready/legacy suppression.

Six test sources CloseClipSwap.{Assign,Validation,Isolation,Rejections,Compile,Authoring}, all UNRUN.43 bad records (two FNames missing/mixed-case None/whitespace/control, three null montage refs, ten accepted Bleed malformed paths at each montage field). Valid no-_C/punctuation names, nonmounted synthetic refs, repeated montage pointers accepted; first failure order, no partial writes, input/owner/CDO/config snapshot isolation, populated-output clearing, retained prior validations, exact reflection/types/native defaults. No native BeginPlay/Tick/Preload/ApplyNowForTest/enable test call, GameplayAbility or montage load. ComponentBegunPlay remains source-only.

ARRAY_MUTATION_AUDIT.md plus exhaustive inventory:19collection mutation sites reviewed. Result.Add reads owner collection; Cases.Add constructs independent FBad records/copies external captured Path; Fields.Add uses independent local; Valid.Add copies separate Repeated config whose montage members are scalars. No same-array source element/reference/MoveTemp alias or Insert/Append/Emplace/SetNum found in test file. Preparation initially asserted an incorrect expected count20 before ANY Source write; actual inventory19 corrected, no engine attempt or source-fix round.

Native lifecycle/runtime facts UNRESOLVED: ctor sets tick/defaults only; BeginPlay Preload loads3montages and binds encounter prerequisite. Missing live ability returns waiting (cpp:141-143); malformed reflected array, wrong4entries/3candidate mapping, invalid originals/replacements or preload failure can permanently abandon swaps (:72/149/157/171/182/199). Hardcoded pack rules and live writes at:207 unaltered. No evidence the real swap works or test-enable parity/serialized authoring/networking/package/all83 closure.

Docs REVIEW PENDING with KI-132. C281 requested DD23 measured TEST_PLAN entry now appears explicitly beside the preserved failed attempt1 record. DD23 accepted159 is historical binary proof, not inherited by DD24 future binary. File-only integrity capture exit0 does not prove C++ compilation or Unreal test success.

Please independently review actual diff/tests/pins. Per C281 I now prepare DD25 ONLY under its Staging folder; no Source promotion/handoff until DD24 acceptance, and no combined verification without exact release.

Five Source pins:
'''
body+=''.join(r['path']+' SHA256 '+r['sha256']+'\n' for r in details['files'])
(here/'DELIVERY_TO_CLAUDE.md').write_text(body,encoding='utf-8')
rows=[p for p in sorted(here.rglob('*')) if p.is_file() and p.name not in {'evidence_sha256.txt','MESSAGE_TO_CLAUDE.txt'}]
receipt=here/'evidence_sha256.txt'
receipt.write_text(''.join(digest(p)+' *'+p.relative_to(here).as_posix()+'\n' for p in rows),encoding='utf-8')
assert verify_receipt(receipt,here,root)['all_verified']
(here/'MESSAGE_TO_CLAUDE.txt').write_text(body+'\nReceipt Codex/DD24/evidence_sha256.txt: '+str(len(rows))+' files SHA256 '+digest(receipt)+'.\n',encoding='utf-8')
print('Frozen DD24 source delivery',len(rows),digest(receipt))
