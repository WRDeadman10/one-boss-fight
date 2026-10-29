"""C285 source handoff freeze only; no compiler/UE run."""
from pathlib import Path
import sys,json,subprocess
here=Path(__file__).resolve().parent
root=here.parents[4]
sys.path.insert(0,str(here.parent/'EvidenceTools'))
from verify_bundle import digest,verify_receipt
# Expand the scalar declaration to match the surrounding validator style.
for p in [root/'Source/OneBossFight/Player/RPGBossDeathAdapters.cpp',here/'Staging/RPGBossDeathAdapters.cpp']:
    s=p.read_text(encoding='utf-8').replace('struct FScalar { const TCHAR* Field; float Value; };','struct FScalar\n\t\t{\n\t\t\tconst TCHAR* Field;\n\t\t\tfloat Value;\n\t\t};')
    p.write_bytes(s.replace('\r\n','\n').replace('\n','\r\n').encode('utf-8'))
r=subprocess.run([sys.executable,str(here/'prepare_source.py')],cwd=root,capture_output=True,text=True)
(here/'source_capture_output.txt').write_text(r.stdout+'\n'+r.stderr,encoding='utf-8')
assert r.returncode==0,r.stdout+r.stderr
assert verify_receipt(here/'post_source_manifest_sha256.txt',root,root)['all_verified']
assert verify_receipt(here/'live_pins_sha256.txt',root,root)['all_verified']
assert verify_receipt(here/'native_pins_sha256.txt',root,root)['all_verified']
details=json.loads((here/'source_checks.json').read_text(encoding='utf-8'))
(here/'NATIVE_ARITHMETIC_AUDIT.md').write_text('''# DD25 C281/C284 final source arithmetic audit

Source reasoning only; no runtime reproduction or unrestricted arithmetic proof.
Historical pre-write findings/lead request remain separately preserved in C281_PREWRITE_SOURCE_FINDINGS.md. C284 resolved both findings; nothing below requests a pending contract decision.

| Field/operation | Source reasoning and explicit limits |
|---|---|
| PackPollSeconds | Native cpp:223 adds bounded float to double Now; authored >0,<=1e6. It does not repair arbitrary nonfinite world time, guarantee a real poll interval or validate scheduling. For finite extreme double time a small1e6 offset rounds away, not a float-add overflow. |
| PackEndTimeMultiplier | Native:296/303 injects only when >0, zero/negative/NaN skip injection. Authored finite>=0,<=1e6 with0 OFF. Reflected downstream timing/clip length is external; no montage duration/playback proof. |
| HoldAtSeconds | Native pause comparisons:446/:494; Clamp(float(Age),0,HoldAt):519. Authored finite>0,<=1e6 prevents negative upper bound/inverted authored interval; prior double-to-float Age narrowing and external invalid ages remain residuals. No frame/pose/timing proof. |
| DyingSeconds | Native:419 compares with double Age. Authored finite>0,<=1e6; external clock/age/state semantics not certified. |
| BlendInSeconds | Native:439 passes value to RPGBossClips::Play (Clips.h:52/59); restart with positive StartAt instead selects0. Authored finite>=0,<=1e6; no engine blending/duration capability claim. |
| MaxClipRestarts | C284 amended authored int32 range0..1000000. Native comparison:508 and equality-warning increment:510-512 plus normal increment:517. After zero-initialized per-death counter and normal invariant-preserving flow, legal limit permits at most1000001 at the one-time warning, belowINT32_MAX. This closes that local overflow reasoning, not cumulative ClipRestartCount at518 or lifetime/external counters. Ceiling is AUTHORED CONTRACT, not native guard or tuning value. Zero disables restarts. No native edit/reproduction. |

DeathMode/name/ref/bool fields have no numeric arithmetic. Both required soft paths are uniform authoring policy, while native Preload:160-173 on first Tick:343 loads only the selected mode. Asset-file presence/hashes are not load/class/skeleton/cook/pose proof.

Attach:47-49 returns Existing before allocation WITHOUT Mode assignment. Typed mode remains authoritative on this reuse path. Possible-second-instance claim from C281 is retracted by C284; no reservation/race/activation-order guarantee is inferred. Constructor:31-39 enables tick and assigns soft defaults; no runtime operation is invoked by the adapter/tests. KI-083 pack destruction/remains EndPlay:119-128 remains unexecuted here.
''',encoding='utf-8')
summary='DD25 C281/C284/C285 source-only: typed Death12fields including native enum, five floats, int restarts0..1000000. Three new+Binding.h/.cpp only,209->212Source/207prior unchanged. Six test sources UNRUN; array audit and arithmetic residuals included. Codex/DD25/DELIVERY_TO_CLAUDE.md, lead SOURCE REVIEW PENDING; NO build/UHT/engine/native/asset/git operation.'
for n in ['TASKS.md','TEST_PLAN.md','DECISIONS.md']:
    with (root/'Documentation'/n).open('a',encoding='utf-8') as f:f.write('\n\n'+summary+'\n')
with (root/'Documentation/DECISIONS.md').open('a',encoding='utf-8') as f:
    f.write('\nC284 DD25 amended policy: MaxClipRestarts authored int32 ceiling1000000 closes per-death equality-increment overflow reasoning; not native guard/tuning. Cumulative ClipRestartCount and external time/Age narrowing remain separate. Attach internally reuses Existing without Mode overwrite; possible-second-instance assertion retracted, no reservation/activation guarantee.\n')
ki=root/'Documentation/KNOWN_ISSUES.md'
assert 'KI-133' not in ki.read_text(encoding='utf-8')
with ki.open('a',encoding='utf-8') as f:
    f.write('\n\n| KI-133 | DD25 source-only limits | C284 authored restarts ceiling1e6 closes local per-death equality increment only; cumulative ClipRestartCount, external Age double-to-float narrowing/world times remain residuals. Not native guard/tuning. Attach internally reuses Existing without changing Mode, so typed mode remains authoritative there; no second-instance/race/reservation/activation claim. First Tick preloads selected mode only; both-path requirement is uniform authoring policy. Pack ability reflection, KI-083 destruction/remains, ragdoll/pose/playback/serialized authoring/wiring/Ready/networking/package unproven. ComponentBegunPlay source-only; six tests UNRUN; plan UNWIRED. | Open; lead source review pending |\n')
current=root/'Docs/BossCombatReview/Execution/Codex/CURRENT_TASK.md'
current.write_text('CURRENT IMPLEMENTER C285: DD24 run accepted; '+summary+'\n\n'+current.read_text(encoding='utf-8'),encoding='utf-8')
body='''# DD25 typed Death SOURCE handoff — C281/C284/C285

Exactly THREE new adapter/test files and existing ONLY Binding.h/.cpp.209->212 Source,207 prior files byte-equal, exact preimages/five-file diff/five pins/Review copies. Binding promoted from accepted ac593fdc/87637344; native Death header/cpp still match X310 pins. Binding includes the native Death header so FRPGDeathConfig uses actual ERPGBossDeathMode, no duplicate enum. No build/UHT/engine, native/otherconsumer/planner/asset/script/git edit.

FRPGDeathConfig has all12 native fields/defaults in header order. Two default paths match native constructor:37-38 (AN_Boss01_DeathLegend and AM_Boss01_DeathLegend), repeated ONLY in Binding.h; native_default_assets.json confirms corresponding Content/OneBossFight/Boss01/Animations uasset files/hashes. Presence/hash is not class/skeleton/load/cook proof. Other new Source files have no quoted production-mount path.

Validator order EXACT amended contract: FIVE floats finite first in header order; DeathMode two-enumerator check; numeric domains in header order, five float ceiling1e6, C284 int32 MaxClipRestarts0..1000000; two required well-formed FNames; DeathClip then DeathMontage required/well-formed regardless of mode. Zero multiplier OFF, zero Blend legal, zero restarts OFF; poll/hold/dying strictly positive; both guard values legal. No editor floors/repair/parse/default substitution, class/registry/mount/existence query/load. Private accepted Bleed/Look PathProblem restated unchanged. BadMode/NotFinite/NotPositive/Negative/AboveCeiling and Missing/Malformed tokens, first failure only.

Exact-class/live/destruction/registration/BeginPlay/owner checks then full validation BEFORE12writes. No transient/runtime fields, loaded clips or test knobs assigned. Native instance RPGBossDeath from Attach:51, exact12required paths, plan UNWIRED. No Ready/legacy suppression/reservation/activation claim.

SIX test sources Death.{Assign,Validation,Isolation,Rejections,Compile,Authoring}, all UNRUN.65bad records:15nonfinite,2bad enums,13float domain cases,3bad restart values(-1/1000001/INT32_MAX),10name cases,2null references and10Bleed malformed paths at each reference. Valid1e6float/int ceilings,0restart/off multiplier/Blend, sub-editor-floor positive values, both modes/guards; test finite-before-enum/domain/name/path order and both paths required in either mode. Full no-write/runtime getter snapshots, independent input/owners/CDO/compiler-copy snapshots, populated-output clearing on rejection, retained prior compiler checks, exact native reflection/types/defaults. No Death BeginPlay/Tick/Attach/Preload, pack ability, remains, playback/pose/guard/test knob operation. ComponentBegunPlay source-only.

ARRAY_MUTATION_AUDIT.md/inventory trace every collection mutation: Result.Add reads a distinct owner set, Cases.Add constructs new records/captures copied external Path, Fields.Add copies independent stack Field, seven Valid.Add copy separate local configs before iteration; runtime counters initializer uses getter values. No same-array element/reference/MoveTemp argument or Insert/Append/Emplace/SetNum in test source.

NATIVE_ARITHMETIC_AUDIT.md carries C284 decisions and field-by-field source reasoning: per-death counter bounded locally by authored1e6 limit (NOT native guard/tuning); cumulative ClipRestartCount and external time/Age narrowing remain separate. Attach at47-49 reuses Existing WITHOUT Mode assignment: typed mode authoritative on reuse; earlier second-instance claim withdrawn. Uniform both-path authoring differs from native first-Tick mode-specific load. KI-083/ability reflection/pack-death/remains/ragdoll/timing remain UNRESOLVED, not executed.

Docs source REVIEW PENDING with KI-133 and C284 decision. Source-only capture exit0 is file integrity, NOT C++/UE success. Expected focused6/full171 not assumed. Please independently review actual diff/tests/pins before any run release. DD24 accepted165 and DD23 attempt1 failure retain their separate provenance/limits.

Five Source pins:
'''
body+=''.join(r['path']+' SHA256 '+r['sha256']+'\n' for r in details['files'])
(here/'DELIVERY_TO_CLAUDE.md').write_text(body,encoding='utf-8')
rows=[p for p in sorted(here.rglob('*')) if p.is_file() and p.name not in {'evidence_sha256.txt','MESSAGE_TO_CLAUDE.txt'}]
receipt=here/'evidence_sha256.txt'
receipt.write_text(''.join(digest(p)+' *'+p.relative_to(here).as_posix()+'\n' for p in rows),encoding='utf-8')
assert verify_receipt(receipt,here,root)['all_verified']
(here/'MESSAGE_TO_CLAUDE.txt').write_text(body+'\nReceipt Codex/DD25/evidence_sha256.txt: '+str(len(rows))+'files SHA256 '+digest(receipt)+'.\n',encoding='utf-8')
print('Frozen DD25 SOURCE ONLY',len(rows),digest(receipt))
