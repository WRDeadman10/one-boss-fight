"""Freeze DD26 reviewable source package. No engine/compiler/test execution."""
from pathlib import Path
import sys,json,re,collections
here=Path(__file__).resolve().parent
root=here.parents[4]
sys.path.insert(0,str(here.parent/'EvidenceTools'))
from verify_bundle import digest,verify_receipt
r=json.loads((here/'source_checks.json').read_text(encoding='utf-8'))
assert r['source_count']==212 and r['unchanged']==203 and len(r['changed'])==9
assert verify_receipt(here/'post_source_manifest_sha256.txt',root,root)['all_verified']
assert verify_receipt(here.parent/'DD25/run_2026-10-29/final_binary_sha256.txt',root,root)['all_verified']
groups=collections.defaultdict(list)
for rel in r['changed']:
    if '/Tests/' not in rel:continue
    for name in re.findall(r'"(OneBossFight\.[^"]+)"',(root/rel).read_text(encoding='utf-8')):
        groups[name.rsplit('.',1)[0]].append(name)
(here/'focused_suite_expectations.json').write_text(json.dumps({k:sorted(v) for k,v in sorted(groups.items())},indent=2),encoding='utf-8')
(here/'ARRAY_MUTATION_AUDIT.md').write_text('''# DD26 changed-code collection mutation review

changed_array_mutations.json is the exhaustive changed-test-line Add/AddUnique/Insert/Append/Emplace/SetNum inventory, seven sites. Each is Plans.Add(Make...Plan()) in the pre-existing HydrationPreparation RequiredPaths helper. Every argument is a fresh factory return value, no reference to Plans or any of its elements. This helper was factory-derived before DD26; it is NOT one of the six independently literal-written AllRequiredPaths lists.

The six new field expectation blocks and expected class/name arrays are independent literal initializer additions, not Add of any container element. New prefix/suffix assertions and all-later-name loops read existing arrays only. The fault Ordinals array is immutable; the loop consumes values, it does not insert into Ordinals. No new Insert/Append/Emplace/SetNum or reference/MoveTemp argument aliases its own destination. Existing collection mutations not changed retain their earlier provenance; no runtime claim is made.

Production MakeBossCorePlans appends seven fresh factory returns to Plans; ManagedCoreConsumerClasses returns class literals. Neither references its own array elements. No callback is run in the preflight. This is manual source reasoning, not C++/UE validation.
''',encoding='utf-8')
(here/'FAULT_ORDINAL_DERIVATION.md').write_text('''# DD26 fault ordinals re-derived from frozen allocation code

Preparation.cpp:240 resets GStepCount. Allocate loops MemberIndex then PlanIndex at139/146, skips target-only, and calls InjectedFaultAfterStep after each successfully completed allocation at179. Configure loops in the same member/plan order at190/197 and calls the step hook after successful callback/checks at221. The step hook increments once at24, no preflight or bookkeeping step is counted.

With two boss-core members and twelve plans each: allocations boss1=1..12, boss2=13..24, configures boss1=25..36, boss2=37..48. Target-only contributes zero. Sample first/middle/last of EACH block, extending the original1,3,5 sample positions for a block of5 to positions1,6,12 in a block of12: {1,6,12,13,18,24,25,30,36,37,42,48}. This is re-derived by operation order, NOT multiplying the old numbers.49 is beyond all48 real steps and is the non-firing control (old21 beyond20). No production step counter code changed.

The collision fixture still blocks third component Encounter on boss2: all12 of boss1 and2 earlier boss2 components must be cleaned, blocked third remains, ALL9 later names indexes3..11 absent. Tests now loop over every later name, rather than only the former indexes3,4.

WorldInputCompilerTests old633-634 literals9 are ANIMATION lease counts from the explicit nine-entry BossAnimationPaths array, not plan/component counts. They intentionally remain9. Registry AddSet tags5/6 are encounter IDs, not counts; remain unchanged. Existing scalar0.5/1.5 etc remain unchanged.
''',encoding='utf-8')
(here/'CALLER_AND_FIXTURE_LIMITS.md').write_text('''# DD26 callers and fixture provenance

non_test_pipeline_references.txt records the exact original non-test source references for CompilePreflight, PrepareBatch, TryPrepareAndReserve, excluding Tests by path components (an early shell glob excluded Tests incorrectly; the final Python enumeration is authoritative). Internal library calls EXIST: WorldInputCompiler.cpp:593 and Preparation.cpp:246 call preflight; WorldPreparation.cpp:168 calls PrepareBatch. Registry exposes TryPrepareAndReserve, with no non-test invocation of that entrypoint found. There is no gameplay/startup caller reaching the pipeline in the current Source caller scan. This is why the source-only plan expansion does not automatically activate new runtime consumers. This is not a claim that the internal library methods contain zero calls, nor a runtime proof.

All seven hydration suites construct configs/definitions in memory. Six AllRequiredPaths literal lists (Preflight, ProductionPreflight, ProductionPreparation, WorldPreparation, WorldInputCompiler, PreparationRegistry) now carry110 independent literals;59 newly written per suite in each record's header order. Headers were read for spelling, then capture_source.py compares parity READ-ONLY; it does not generate or write fixture expectations. HydrationPreparation has its separate existing factory-derived RequiredPaths helper, now containing12 factories, intentionally not misrepresented as an independent literal list. This corrects the earlier pre-write table's omission of PreparationRegistry from the literal-list group.

Production-shaped fixtures use real character/mesh/animation assets but TRANSIENT NewObject definitions, not authored DA_Boss definition assets. C290 reports A199/C290 filesystem/byte searches found no such authored asset today. No editor/asset-registry inspection is performed here; absence of a filename/string is not a universal serialized-class inventory proof. Future real definitions must carry all110 required paths (51 prior+59 new); missing paths fail preflight. No asset is created, migrated or edited by DD26.

ExpandedSubset keeps its name and broader structural intent, has12-plan/12-lease/110-path expectations, explicit independent original[0..4] class/name prefix and new[5..11] suffix assertions. No new automation name was added. Callbacks are checked bound and via existing acceptance/wrong-class fixture; individual new values remain covered by separately accepted typed suites, not newly instrumented here.
''',encoding='utf-8')
summary='DD26 C287/C289 SOURCE ONLY: twelve-plan preflight and13managed classes; seven hydration suites updated for12/24/110 and independent prefix/suffix.9existing files changed,212total/203unchanged; adapters/native/Binding/compiler/preparation/registry frozen. Six independent literal lists verified statically, fault ordinals re-derived48steps, test names unchanged. Lead SOURCE REVIEW PENDING; NO build/UE run. Codex/DD26/DELIVERY_TO_CLAUDE.md.'
for n in ['TASKS.md','TEST_PLAN.md','DECISIONS.md']:
    with (root/'Documentation'/n).open('a',encoding='utf-8') as f:f.write('\n\n'+summary+'\n')
ki=root/'Documentation/KNOWN_ISSUES.md'
assert 'KI-134' not in ki.read_text(encoding='utf-8')
with ki.open('a',encoding='utf-8') as f:
    f.write('\n\n| KI-134 | DD26 source-only integration/authoring limits | Future real authored definitions must carry all110 required paths (51prior+59new); preflight refuses missing paths. Serialized asset Fields remain uninspected by Codex (C290 reports no authored DA_Boss asset found). No active production gameplay/startup caller invokes preflight or preparation today in the Source caller scan, so no runtime hook changes; internal library facade calls do exist. Expanded plan list is not BeginPlay chronology, registration/Ready/legacy suppression/activation or complete playable bundle. New seven profiles remain structural/no load/class/skeleton/timing proof; no new UE run yet. | Open; source review pending |\n')
current=root/'Docs/BossCombatReview/Execution/Codex/CURRENT_TASK.md'
current.write_text('CURRENT IMPLEMENTER C289: '+summary+'\n\n'+current.read_text(encoding='utf-8'),encoding='utf-8')
body='''# DD26 source handoff — C287/C289 stops resolved, SOURCE ONLY

Exactly9 existing Source files changed: Preflight.h/.cpp and seven named hydration test suites.212->212 Source,203 other files unchanged. No adapter, native component, Binding, compiler, preparation/registry runtime file edit. CheckPlans function body byte-equal (constant now12). Full preimages/diff/nine pins/Review copies/manifests included. No build/UHT/engine/test/asset/git operation.

BossCorePlanCount12. Original prefix Stagger/Phases/Encounter/DormantWake/Posture preserved; appended Bleed/LowSweep/Shockwave/HealPunish/Look/CloseClipSwap/Death in DD order. ManagedCoreConsumerClasses13 (twelve native classes plus participant) guards every new class against preexisting consumers. Header explicitly says plan order, NOT registration/BeginPlay chronology; still incomplete playable bundle and not Ready/suppression authorization.

All seven suites' relevant assertions updated (12plans/leases,24two-boss components,110path union,13managed,23+1cleanup partitions,+12actor delta). Six AllRequiredPaths blocks were independently written as59 literal paths each in record header order; static read-only header parity reports110unique paths in each. HydrationPreparation's EXISTING factory-derived RequiredPaths helper separately gains7factory calls; it is not one of those6 literal lists. Expected classes/names/callback checks extend indexes5..11; PlannedNames12; ExpandedSubset retains same test name with explicit original0..4 prefix AND new5..11 suffix assertions. Count/label/assertion changes itemised in ASSERTION_CHANGE_TABLE.md and assertion_changes.json (70rows, full multiline old/new expressions).

Fault injection re-derived from frozen preparation loops, not scaled: allocations1..12/13..24, configures25..36/37..48; samples {1,6,12,13,18,24,25,30,36,37,42,48}; non-firing control49. Collision tests now assert ALL nine later names indexes3..11 absent, preserving the original cleanup intent. WorldInputCompiler boss row9 is animation lease count, deliberately unchanged; registry5/6 tags are IDs. FAULT_ORDINAL_DERIVATION.md cites exact step hooks/order.

C289 pre-write widened count/index search had ZERO hits in the five frozen downstream files; exact regex/files/exit1 logged in C289_PREWRITE_COUNT_SCAN.txt/json. No production scope expansion. CALLER_AND_FIXTURE_LIMITS.md traces internal library calls vs absent active gameplay entrypoint, transient fixtures vs authored definitions, and corrects the earlier literal-list grouping to include PreparationRegistry. C290/A199 asset absence report noted with static-inventory limits; no editor inspection. Future authored Fields need all110paths. KI-134 records this future requirement and runtime limitations.

Array audit: seven new test mutation lines are Plans.Add(fresh factory return), no same-array element/reference argument. New field/class/name literal arrays, prefix/suffix assertions, readonly Ordinals and later-name loops introduce no self-alias. ARRAY_MUTATION_AUDIT.md and changed_array_mutations.json contain the audit. No new automation names: total171 remains EXPECTED until actual discovery on an explicitly released run.

Source-only integrity/parity helper completed exit0; it is NOT C++ compilation or Unreal test proof. Static checks prove212count, exact9-file delta,203frozen files, six110-literal lists,12factories,13classes, unchanged CheckPlans body and unchanged automation names. No runtime activation, registration, load/mesh/skeleton/socket fit, serialized authoring, real duel/networking/package/all83 closure.

Suggested focused verification after lead review: the seven prefixes and exact expected source names are in focused_suite_expectations.json; then full OneBossFight conditional on all focused gates passing. No run started and no old171 result inherited across a future binary. Please independently review full diff/pins/assertion table before releasing verification.

Nine Source pins:
'''
body+=(here/'live_pins_sha256.txt').read_text(encoding='utf-8')
body+='\nFocused source expectations (NOT discovery):\n'+''.join(k+': '+str(len(v))+'\n' for k,v in sorted(groups.items()))
(here/'DELIVERY_TO_CLAUDE.md').write_text(body,encoding='utf-8')
rows=[p for p in sorted(here.rglob('*')) if p.is_file() and p.name not in {'evidence_sha256.txt','MESSAGE_TO_CLAUDE.txt'}]
receipt=here/'evidence_sha256.txt'
receipt.write_text(''.join(digest(p)+' *'+p.relative_to(here).as_posix()+'\n' for p in rows),encoding='utf-8')
assert verify_receipt(receipt,here,root)['all_verified']
(here/'MESSAGE_TO_CLAUDE.txt').write_text(body+'\nReceipt '+str(len(rows))+'files SHA256 '+digest(receipt)+'.\n',encoding='utf-8')
print('DD26 source-only frozen:',len(rows),digest(receipt));print({k:len(v) for k,v in sorted(groups.items())})
