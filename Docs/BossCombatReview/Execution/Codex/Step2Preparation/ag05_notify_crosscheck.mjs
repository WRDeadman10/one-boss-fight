// Read-only comparison of like-named montage metadata/windows. Does NOT prove runtime behavior.
import fs from 'node:fs';
const root='Docs/BossCombatReview/Execution/';
const raw=fs.readFileSync(root+'Claude/Evidence/exports/montage_notifies_2026-10-25.txt','utf8');
const inv=JSON.parse(fs.readFileSync(root+'Antigravity/P1_CUE_SOURCE_INVENTORY.json','utf8'));
const dumps=new Map();let current;
for(const line of raw.split(/\r?\n/)){
 const h=line.match(/== (\S+) \(AnimMontage\) length=([\d.e+-]+)/);if(h){current={length:Number(h[2]),traces:[]};dumps.set(h[1],current);}
 const w=line.match(/ANS_CollisionTrace_C at ([\d.-]+) s for ([\d.]+) s/);if(w&&current)current.traces.push({start:Number(w[1]),duration:Number(w[2])});
}
let comparisons=0;const issues=[];const unavailable=[];
const compare=(id,field,actual,expected)=>{if(actual===undefined||expected===undefined)return;comparisons++;if(typeof actual!=='number'||Math.abs(actual-expected)>.0006)issues.push({id,field,inventory:actual,raw:expected});};
for(const r of inv.routes){
 const leaf=r.montage_path.split('/').at(-1).split('.')[0],d=dumps.get(leaf),t=r.raw_timing_coordinates;
 if(!d){unavailable.push(r.audit_id);continue;}
 compare(r.audit_id,'total_duration',t.total_duration,d.length);
 for(const [prefix,i] of [['',0],['first_',0],['second_',1]]){
  compare(r.audit_id,prefix+'active_start',t[prefix+'active_start'],d.traces[i]?.start);
  compare(r.audit_id,prefix+'active_duration',t[prefix+'active_duration'],d.traces[i]?.duration);
  compare(r.audit_id,prefix+'active_end',t[prefix+'active_end'],d.traces[i]?d.traces[i].start+d.traces[i].duration:undefined);
 }
}
console.log(JSON.stringify({scope:'same-montage local raw export comparisons; tolerance0.6ms for decimal export rounding, NOT gameplay tolerance',comparisons,issues,unavailable},null,2));
