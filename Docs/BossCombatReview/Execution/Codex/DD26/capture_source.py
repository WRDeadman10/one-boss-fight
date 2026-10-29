"""C289 source integrity, independent-literal parity and review tables. No UE tests."""
from pathlib import Path
import sys,re,json,difflib
here=Path(__file__).resolve().parent
root=here.parents[4]
sys.path.insert(0,str(here.parent/'EvidenceTools'))
from verify_bundle import digest,parse_receipt
scope=json.loads((here/'scope_files.json').read_text(encoding='utf-8'))
prior={r['relative_path']:r['expected_sha256'] for r in parse_receipt((here/'pre_source_manifest_sha256.txt').read_text(encoding='utf-8'))}
for rel in scope:
    p=root/rel
    p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))
current={p.relative_to(root).as_posix():digest(p) for p in (root/'Source').rglob('*') if p.is_file()}
changed=sorted(k for k in prior if prior[k]!=current[k])
assert current.keys()==prior.keys() and len(current)==212 and changed==sorted(scope)
def body(text,signature):
    start=text.index(signature)
    a=text.index('{',start);depth=0
    for i in range(a,len(text)):
        if text[i]=='{':depth+=1
        if text[i]=='}':
            depth-=1
            if depth==0:return text[a:i+1]
    raise AssertionError(signature)
names=['Bleed','LowSweep','Shockwave','HealPunish','Look','CloseClipSwap','Death']
# READ-ONLY comparison to the already manually authored literals; never writes or
# generates a test's expectations from a header or another suite.
headerpaths=[]
for n in names:
    h=(root/f'Source/OneBossFight/Player/RPGBoss{n}Adapters.h').read_text(encoding='utf-8')
    headerpaths+=re.findall(r'Field\w+\s*=\s*TEXT\("([^"]+)"\)',h)
assert len(headerpaths)==59 and len(set(headerpaths))==59
literal_checks=[]
for rel in scope:
    if '/Tests/' not in rel:continue
    text=(root/rel).read_text(encoding='utf-8')
    if 'TArray<FString> AllRequiredPaths(' not in text:continue
    literals=re.findall(r'TEXT\("([^"]+)"\)',body(text,'TArray<FString> AllRequiredPaths('))
    assert len(literals)==110 and len(set(literals))==110,(rel,len(literals))
    assert literals[-59:]==headerpaths,rel
    literal_checks.append({'file':rel,'paths':110,'appended_literal_paths':59,'header_order_parity':True})
assert len(literal_checks)==6
production=(root/'Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp').read_text(encoding='utf-8')
oldprod=(here/'Preimages/RPGBossHydrationPreflight.cpp').read_text(encoding='utf-8')
assert body(production,'TArray<FString> CheckPlans(')==body(oldprod,'TArray<FString> CheckPlans('),'CheckPlans changed beyond frozen scope'
plans=re.findall(r'Plans.Add\(([^;]+)\);',body(production,'TArray<FRPGComponentPlan> MakeBossCorePlans('))
assert len(plans)==12 and [p.split('::')[1].split('(')[0] for p in plans[5:]]==['Make'+n+'Plan' for n in names]
managed=re.findall(r'(\w+)::StaticClass\(',body(production,'TArray<UClass*> ManagedCoreConsumerClasses('))
assert len(managed)==13 and len(set(managed))==13
review=here/'Review';review.mkdir(exist_ok=True)
diff=[];pins=[];assertions=[];mutation=[]
def assertcalls(text):
    result=[]
    for m in re.finditer(r'\bTest(?:True|False|Equal|NotNull|Null)\s*\(',text):
        a=text.index('(',m.start());depth=0;quote=False;escape=False
        for i in range(a,len(text)):
            c=text[i]
            if quote:
                if escape:escape=False
                elif c=='\\':escape=True
                elif c=='"':quote=False
                continue
            if c=='"':quote=True
            elif c=='(':depth+=1
            elif c==')':
                depth-=1
                if depth==0:
                    result.append((text.count('\n',0,m.start())+1,text[m.start():i+1]));break
    return result
for rel in scope:
    p=root/rel
    old=(here/'Preimages'/p.name).read_text(encoding='utf-8');new=p.read_text(encoding='utf-8')
    (review/p.name).write_bytes(p.read_bytes())
    diff.extend(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),fromfile=rel,tofile=rel))
    pins.append(digest(p)+' *'+rel+'\n')
    if '/Tests/' in rel:
        a=assertcalls(old);b=assertcalls(new)
        sm=difflib.SequenceMatcher(a=[s for _,s in a],b=[s for _,s in b],autojunk=False)
        for tag,i,j,k,l in sm.get_opcodes():
            if tag=='equal':continue
            for off in range(max(j-i,l-k)):
                prior_assert=a[i+off] if i+off<j else None
                next_assert=b[k+off] if k+off<l else None
                assertions.append({'file':rel,'old':prior_assert,'new':next_assert,'reason':'C289 expanded plan/lease/component/union expectations, preserving assertion intent; explicit prefix/suffix assertions added'})
        sm=difflib.SequenceMatcher(a=old.splitlines(),b=new.splitlines(),autojunk=False)
        added={i for tag,_,_,a1,b1 in sm.get_opcodes() if tag!='equal' for i in range(a1,b1)}
        for i,line in enumerate(new.splitlines()):
            if i in added and re.search(r'\.(Add|AddUnique|Insert|Append|Emplace|SetNum)\w*\(',line):mutation.append({'file':rel,'line':i+1,'code':line})
    oldnames=re.findall(r'"(OneBossFight\.[^"]+)"',old)
    newnames=re.findall(r'"(OneBossFight\.[^"]+)"',new)
    assert oldnames==newnames,('automation names changed',rel)
(here/'full.diff').write_text(''.join(diff),encoding='utf-8')
(here/'live_pins_sha256.txt').write_text(''.join(pins),encoding='utf-8')
(here/'post_source_manifest_sha256.txt').write_text(''.join(v+' *'+k+'\n' for k,v in sorted(current.items())),encoding='utf-8')
(here/'assertion_changes.json').write_text(json.dumps(assertions,indent=2),encoding='utf-8')
table=['# Itemised changed assertions (source-only, unrun)\n','Every changed assertion is recorded with its old/new line and complete expression. Sequence replacement blocks are paired in order; new prefix/suffix rows have no old assertion. The full diff remains authoritative for surrounding logic.\n']
for i,row in enumerate(assertions,1):
    table.append(f'\n## {i}. {row["file"]}\n')
    for key in ['old','new']:
        value=row[key]
        table.append(f'\n{key} '+(f'line{value[0]}:\n```cpp\n{value[1]}\n```\n' if value else '(no assertion at this sequence position)\n'))
(here/'ASSERTION_CHANGE_TABLE.md').write_text(''.join(table),encoding='utf-8')
(here/'changed_array_mutations.json').write_text(json.dumps(mutation,indent=2),encoding='utf-8')
checks={'scope':'SOURCE integrity/static review, NOT compiler or Unreal test','source_count':212,'changed':changed,'unchanged':203,'six_independent_literal_lists':literal_checks,'plans':plans,'managed_classes':managed,'CheckPlans_body_unchanged':True,'automation_names_unchanged':True,'assertion_rows':len(assertions),'changed_array_mutations':mutation}
(here/'source_checks.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print('Static source integrity/parity only:',len(changed),'changed,203unchanged;',len(assertions),'assertion rows;',len(mutation),'changed collection mutation lines.')
