from pathlib import Path
import sys,json
here=Path(__file__).resolve().parent
root=here.parents[4]
rev=here/'Revision1'
sys.path.insert(0,str(here.parent/'EvidenceTools'))
from verify_bundle import digest,verify_receipt
assert verify_receipt(rev/'post_source_manifest_sha256.txt',root,root)['all_verified']
assert verify_receipt(here/'run_2026-10-29/evidence_sha256.txt',here/'run_2026-10-29',root)['all_verified']
summary='DD23 C276 source-only revision1: three self-alias fixture Add sites now copy selected soft-pointer into independent local before Add. Only Look tests Source changed,206total/205unchanged; four adapter/Binding pins unchanged. Generator updated, original source20-receipt bundle and failed attempt23-receipt/logs preserved. Array mutation audit includes DD24 four staged files (tests not yet written). NO build/retry; Claude diff review pending. Codex/DD23/Revision1/one_file.diff.'
for n in ['TASKS.md','TEST_PLAN.md','DECISIONS.md']:
    with (root/'Documentation'/n).open('a',encoding='utf-8') as f:f.write('\n\n'+summary+'\n')
with (root/'Documentation/KNOWN_ISSUES.md').open('a',encoding='utf-8') as f:
    f.write('\n\nKI-131 C276 correction revision1: source-only fix uses local value before each of3 Pieces.Add calls. No retry measured; failed C275 exit3/two completions remains on record. Native adapter/domain/Binding bytes unchanged; not evidence Look suite passes. Exact independent lead diff acceptance and attempt2 release required.\n')
current=root/'Docs/BossCombatReview/Execution/Codex/CURRENT_TASK.md'
current.write_text('CURRENT IMPLEMENTER C276: '+summary+'\n\n'+current.read_text(encoding='utf-8'),encoding='utf-8')
body='''# DD23 C276 bounded fixture correction — SOURCE ONLY

Applied exactly the three approved fixture corrections; no additional Source change. At original test:165/290/292, selected TSoftObjectPtr<USkeletalMesh> is copied into an independent LOCAL VALUE, then Add(local). Same duplicate identity, indexed error expectations and validation order. Generator has the corresponding three substitutions. Review Revision1/one_file.diff and generator.diff.

Source206 total,205 unchanged against frozen accepted DD23 manifest. ONLY Tests/RPGBossLookAdaptersTests.cpp changed. New test SHA25664fc3399928fb20ddf39d8b6207daa7c98a9077537da3db308eef0b2385f9711. Four adapter/Binding pins remain ca3bfb39/e99af51e/1cbc444b/c12fe14a (full pins in Revision1/live_pins_sha256.txt). No validator/domain/default/control/array-identity-rule change.

Array audit (Revision1/ARRAY_MUTATION_AUDIT.md, exhaustive array_mutation_inventory.txt): original166 Add(Mesh(MakePath(...))) creates an independent temporary; original190 Add(Mesh(Path)) uses an external by-value captured Path; original317 assignment and318 Add(new constructed pointer) are independent. Other Cases.Add, Fields.Add, Result.Add and Valid.Add use local/new values from other containers. No further same-array source-reference mutation found. DD24 currently FOUR staging files only, NO tests yet; audited all staged collection mutations, no new self-alias found. Tests will receive this check before DD24 freeze; no DD24 test audit/completion claim now.

Preservation: failed test and generator bytes under Revision1/Preimages; complete ORIGINAL20-file DD23 source bundle and byte-identical receipt24c61c96... under Revision1/Original_DD23_Source, independently verified20/20. Root historical source receipt is not re-frozen to hide the generator revision; use its archived original bundle for that receipt. Failed run23-file receipt55658b44... still verifies unchanged, with raw focused bd5c3dcc... exit3/assertion/2completions and build40224a10... exit0. No log overwritten or failure erased. Docs TASKS/TEST_PLAN/DECISIONS/KI-131 now say correction SOURCE REVIEW PENDING, not measured success.

NO BUILD, UHT, engine, retry, asset/git operation, or DD24 Source promotion. Current failed-attempt DLL f6eebc6071f2f0c31dbcd96e2d45695743063cd0f694c3ef123d6b1ad317e9c2 remains the proposed attempt2 binary baseline; EXE5495fb88.../HEAD79d55906 unchanged by this source correction. No engine liveness inferred from earlier capture. Please independently review exact one-file diff and release a NEW attempt2 only if accepted. Focused6/full159 remain expectations, NOT results.

Exact Source diff:
'''
body+=(rev/'one_file.diff').read_text(encoding='utf-8')
(rev/'DELIVERY_TO_CLAUDE.md').write_text(body,encoding='utf-8')
rows=[(p,p.relative_to(rev).as_posix()) for p in sorted(rev.rglob('*')) if p.is_file() and p.name!='MESSAGE_TO_CLAUDE.txt' and p!=rev/'evidence_sha256.txt']
for n in ['apply_c276_correction.py','finish_c276_delivery.py','generate_tests.py']:rows.append((here/n,'../'+n))
receipt=rev/'evidence_sha256.txt'
receipt.write_text(''.join(digest(p)+' *'+rel+'\n' for p,rel in rows),encoding='utf-8')
assert verify_receipt(receipt,rev,root)['all_verified']
(rev/'MESSAGE_TO_CLAUDE.txt').write_text(body+'\nRevision1 receipt '+str(len(rows))+'files SHA256 '+digest(receipt)+'.\n',encoding='utf-8')
print('Revision1 frozen',len(rows),digest(receipt))
