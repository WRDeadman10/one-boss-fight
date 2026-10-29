"""C287/C289 scoped source wiring. No C++ compilation or UE execution."""
from pathlib import Path
import re,json
here=Path(__file__).resolve().parent
root=here.parents[4]
scope=json.loads((here/'scope_files.json').read_text(encoding='utf-8'))
new=['Bleed','LowSweep','Shockwave','HealPunish','Look','CloseClipSwap','Death']
allnames=['Stagger','Phases','Encounter','DormantWake','Posture']+new
player=root/'Source/OneBossFight/Player'
p=player/'RPGBossHydrationPreflight.cpp'
s=p.read_text(encoding='utf-8')
inc=''.join('#include "Player/RPGBoss'+n+'.h"\n#include "Player/RPGBoss'+n+'Adapters.h"\n' for n in new)
s=s.replace('#include "UObject/StrongObjectPtr.h"',inc+'#include "UObject/StrongObjectPtr.h"')
s=s.replace('constexpr int32 BossCorePlanCount = 5;','constexpr int32 BossCorePlanCount = 12;')
s=s.replace('Plans.Add(RPGBossStatsAdapters::MakePosturePlan());','Plans.Add(RPGBossStatsAdapters::MakePosturePlan());\n'+''.join('\t\t\tPlans.Add(RPGBoss'+n+'Adapters::Make'+n+'Plan());\n' for n in new).rstrip())
old='URPGCombatParticipant::StaticClass()};'
assert s.count(old)==1
s=s.replace(old,'URPGCombatParticipant::StaticClass(), '+', '.join('URPGBoss'+n+'::StaticClass()' for n in new)+'};')
s=s.replace('the five combined native clusters','the twelve accepted native component plans').replace('from the five accepted combined factories and no other','from the twelve accepted factories and no other').replace('Encounter, DormantWake, Posture. The order','Encounter, DormantWake, Posture, Bleed, LowSweep, Shockwave, HealPunish, Look, CloseClipSwap, Death. The order').replace('51 unique paths','110 unique paths')
p.write_text(s,encoding='utf-8')
p=player/'RPGBossHydrationPreflight.h';s=p.read_text(encoding='utf-8')
s=s.replace('the plans of the five accepted combined native clusters','the plans of the twelve accepted native component records')
s=s.replace('and Posture (the three posture stats).','and Posture (the three posture stats), followed by Bleed, LowSweep, Shockwave, HealPunish, Look, CloseClipSwap and Death (59 additional paths).')
s=s.replace('(death, presentation, audio and the other legacy consumers are absent)','(audio, attack tracking and other legacy consumers remain absent; the twelve plans alone are not a playable bundle)')
s=s.replace('receives the five combined native plans: Stagger, Phases, Encounter, DormantWake, Posture','receives twelve plans: Stagger, Phases, Encounter, DormantWake, Posture, Bleed, LowSweep, Shockwave, HealPunish, Look, CloseClipSwap, Death')
s=s.replace('Boss-core: Stagger, Phases, Encounter, DormantWake, Posture in this relative plan order.','Boss-core: Stagger, Phases, Encounter, DormantWake, Posture, Bleed, LowSweep, Shockwave, HealPunish, Look, CloseClipSwap, Death in this relative plan order.')
p.write_text(s,encoding='utf-8')
for rel in scope:
    if '/Tests/' not in rel:continue
    p=root/rel;s=p.read_text(encoding='utf-8')
    # Adjust only count-bearing statements; scalar fixture values and encounter tags stay intact.
    lines=[]
    for line in s.splitlines(keepends=True):
        countbearing=bool(re.search(r'Plans\.Num|ClassLeases\.Num|OwnedComponentCount|GetOwnedComponentCount|OwnedList\.Num|OwnedSet\.Num|Weak\.Num|FirstWeak\.Num|Report\.Destroyed|\.Abort\.Destroyed|\.AlreadyGone|DistinctClasses\.Num|DistinctNames\.Num|Required\.Num|Union\.Num|ExpectedPaths\.Num|SumOfRequired|Prior\.Components\.Num|exactly five plans|one class lease per boss plan',line))
        if countbearing:
            # Whole integer literals, not 0.5f, 1.5f or arbitrary scalar domains.
            line=re.sub(r'(?<![\w.])(51|10|9|5)(?![\w.])',lambda m:{'51':'110','10':'24','9':'23','5':'12'}[m[0]],line)
        if re.search(r'for \(int32 Index = 0; Index < 5;',line):line=line.replace('Index < 5;','Index < 12;')
        # Scope/count prose only, preserving constants in unrelated case fixtures.
        line=re.sub(r'(?<![\w-])five\b','twelve',line)
        line=re.sub(r'(?<![\w-])ten\b','twenty-four',line)
        line=re.sub(r'(?<![\w-])nine\b','twenty-three',line)
        line=line.replace('fifty-one','one hundred ten').replace('51-path','110-path').replace('51 unique','110 unique').replace('51 paths','110 paths').replace('51 required','110 required')
        lines.append(line)
    s=''.join(lines)
    # Independently listed class/name expectations; no callback invoked.
    anchor='{URPGBossPosture::StaticClass(), TEXT("RPGBossPosture")}'
    if anchor in s:
        s=s.replace(anchor,anchor+',\n\t\t\t'+', '.join('{URPGBoss'+n+'::StaticClass(), TEXT("RPGBoss'+n+'")} ' for n in new).rstrip())
    # All expected-class/name arrays whose existing prefix is unchanged gain seven literals.
    s=s.replace('URPGBossPosture::StaticClass()};','URPGBossPosture::StaticClass(), '+', '.join('URPGBoss'+n+'::StaticClass()' for n in new)+'};')
    s=s.replace('FName(TEXT("RPGBossPosture"))};','FName(TEXT("RPGBossPosture")), '+', '.join('FName(TEXT("RPGBoss'+n+'"))' for n in new)+'};')
    s=s.replace('const TCHAR* const PlannedNames[5]','const TCHAR* const PlannedNames[12]').replace('TEXT("RPGBossPosture")};','TEXT("RPGBossPosture"), '+', '.join('TEXT("RPGBoss'+n+'")' for n in new)+'};')
    if p.name=='RPGBossHydrationPreparationTests.cpp':
        # Existing helper was factory-derived already (not one of the six independent literal lists).
        anchor='Plans.Add(RPGBossStatsAdapters::MakePosturePlan());'
        assert s.count(anchor)==1
        s=s.replace(anchor,anchor+'\n'+''.join('\t\tPlans.Add(RPGBoss'+n+'Adapters::Make'+n+'Plan());\n' for n in new).rstrip())
        s=s.replace('const int32 Ordinals[] = {1, 3, 5, 6, 8, 10, 11, 13, 15, 16, 18, 20};','const int32 Ordinals[] = {1, 6, 12, 13, 18, 24, 25, 30, 36, 37, 42, 48};')
        s=s.replace('allocations 1 to 5 are the first boss, 6 to 10 the second boss, configures 11 to 15 the first boss, 16 to 20 the second boss','allocations 1 to 12 are the first boss, 13 to 24 the second boss, configures 25 to 36 the first boss, 37 to 48 the second boss')
        s=s.replace('beyond the twenty real steps','beyond the forty-eight real steps').replace('FFaultInjectionScope Fault(21);','FFaultInjectionScope Fault(49);')
    # Explicit old prefix checks now cover ALL twelve fields at their reviewed indexes.
    for var in ['Boss','BossPlan']:
        for member in ['Class','InstanceName','Configure']:
            if member=='Class':anchor=f'{var}.Plans[4].Class == URPGBossPosture::StaticClass()';extra=''.join(f' && {var}.Plans[{i}].Class == URPGBoss{n}::StaticClass()' for i,n in enumerate(new,5))
            elif member=='InstanceName':anchor=f'{var}.Plans[4].InstanceName == FName(TEXT("RPGBossPosture"))';extra=''.join(f' && {var}.Plans[{i}].InstanceName == FName(TEXT("RPGBoss{n}"))' for i,n in enumerate(new,5))
            else:anchor=f'static_cast<bool>({var}.Plans[4].Configure)';extra=''.join(f' && static_cast<bool>({var}.Plans[{i}].Configure)' for i in range(5,12))
            s=s.replace(anchor,anchor+extra)
    # Old explicit class-lease checks include all new indexes too.
    for var in ['Boss','BossPlan']:
        anchor=f'{var}.ClassLeases[4].Get() == {var}.Plans[4].Class'
        s=s.replace(anchor,anchor+''.join(f' && {var}.ClassLeases[{i}].Get() == {var}.Plans[{i}].Class' for i in range(5,12)))
    # Headers needed only by actual newly referenced native classes/factories.
    includes=''
    for n in new:
        if 'URPGBoss'+n+'::' in s and '#include "Player/RPGBoss'+n+'.h"' not in s:includes+='#include "Player/RPGBoss'+n+'.h"\n'
        if 'RPGBoss'+n+'Adapters::' in s and '#include "Player/RPGBoss'+n+'Adapters.h"' not in s:includes+='#include "Player/RPGBoss'+n+'Adapters.h"\n'
    if includes:
        first=s.index('#include "')
        s=s[:first]+includes+s[first:]
    p.write_text(s,encoding='utf-8')
print('Initial nine-file DD26 wiring/count update written SOURCE ONLY; remaining special cases/self-review pending, no build.')
