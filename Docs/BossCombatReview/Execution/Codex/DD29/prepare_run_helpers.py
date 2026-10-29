"""Adapt the accepted C315 file-only gates to C319's exact new scope; no Source write."""
from pathlib import Path
import ast
H=Path(__file__).resolve().parent;OLD=H.parent/'DD28';R=H/'run_2026-10-29'
t=(OLD/'check_gate.py').read_text(encoding='utf-8')
t=t.replace('C315','C319').replace('==213','==216').replace('build_dd28','build_dd29').replace("tag=='full_dd28'","tag=='full_dd29'").replace('n=177','n=182')
t=t.replace("changes={'Source/OneBossFight/Player/RPGBossHydrationPreparation.h','Source/OneBossFight/Player/RPGBossHydrationPreparation.cpp'}","changes=set()")
old_map=next(s for s in t.splitlines() if s.strip().startswith('map_file='))
t=t.replace(old_map,"    map_file={'activation_world':('ActivationWorld','RPGBossActivationWorldTests.cpp',5),'activation':('Activation','RPGBossActivationTests.cpp',6),'world_preparation':('WorldPreparation','RPGBossWorldPreparationTests.cpp',4),'registry':('PreparationRegistry','RPGBossPreparationRegistryTests.cpp',3)}")
t=t.replace("DD26/run_2026-10-29/automation_full_dd26.log","DD28/run_2026-10-29/automation_full_dd28.log")
line=next(s for s in t.splitlines() if s.strip().startswith('new=set('))
t=t.replace(line,line.replace('Activation\\.','ActivationWorld\\.').replace('RPGBossActivationTests.cpp','RPGBossActivationWorldTests.cpp'))
t=t.replace('len(new)==6','len(new)==5')
ast.parse(t);(H/'check_gate.py').write_text(t,encoding='utf-8')
t=(OLD/'finish_capture.py').read_text(encoding='utf-8')
t=t.replace('C315','C319').replace('==213','==216').replace("'full_dd28'","'full_dd29'").replace('automation_full_dd28.log','automation_full_dd29.log')
t=t.replace("changed={'Source/OneBossFight/Player/RPGBossHydrationPreparation.h','Source/OneBossFight/Player/RPGBossHydrationPreparation.cpp'}","changed=set()")
t=t.replace("tags=('activation','preparation','registry','world_preparation','production_preparation','full_dd29')","tags=('activation_world','activation','world_preparation','registry','full_dd29')")
t=t.replace('==22','==18').replace("'focused_unique':22","'focused_unique':18").replace("'source_count':213","'source_count':216")
t=t.replace("DD26/run_2026-10-29/automation_full_dd26.log","DD28/run_2026-10-29/automation_full_dd28.log").replace('warning_delta_vs_DD26','warning_delta_vs_DD28')
ast.parse(t);(H/'finish_capture.py').write_text(t,encoding='utf-8')
for name in ('run_build.ps1','run_focused.ps1','build_dd28.cmd'):
    t=(OLD/'run_2026-10-29'/name).read_text(encoding='utf-8').replace('DD28','DD29').replace('dd28','dd29').replace('C315','C319')
    (R/name.replace('dd28','dd29')).write_text(t,encoding='utf-8')
print('C319 helpers prepared; exact18 focused / full182 scope; no engine launch')
