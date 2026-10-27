// Read-only source inventory. Output only this Codex folder. NOT a C++ parser or hydration authorizer.
import fs from 'node:fs';
import crypto from 'node:crypto';
const out='Docs/BossCombatReview/Execution/Codex/Step2Preparation';
const player=['RPGBossStagger','RPGBossPhases','RPGBossEncounter','RPGBossDormantWake','RPGBossPosture','RPGBossDeath','RPGBossLook','RPGBossBleed','RPGAttackTracker','RPGBossCloseClipSwap','RPGBossShockwave','RPGBossLowSweep','RPGBossHealPunish','RPGBossJavelin','RPGPlayerMovesSubsystem','RPGLegend'];
const bases=[...player.map(n=>'Source/OneBossFight/Player/'+n),'Source/OneBossFight/UI/RPGBossHud','Source/OneBossFight/Audio/RPGBossMusic','Source/OneBossFight/Audio/RPGFootsteps'];
const digest=b=>crypto.createHash('sha256').update(b).digest('hex');
const result={version:1,kind:'lexical observation only; no completeness or semantic first-read claim',files:[],components:[]};
for(const base of bases){
 const files=['h','cpp'].map(ext=>{const p=base+'.'+ext;const b=fs.readFileSync(p);const lines=b.toString().replaceAll('\r\n','\n').split('\n');result.files.push({path:p,sha256:digest(b)});return{p,lines};});
 const [h,c]=files, fields=[];let scope='unresolved';
 for(let i=0;i<h.lines.length;i++){
  const line=h.lines[i];
  const type=line.match(/^\s*(?:class\s+(?:ONEBOSSFIGHT_API\s+)?|struct\s+)(\w+)\s*(?::|$)/);if(type)scope=type[1];
  if(!line.includes('UPROPERTY('))continue;
  const annotation=line.trim();let j=i+1;while(j<h.lines.length && !h.lines[j].trim())j++;
  const declaration=h.lines[j]?.trim();if(!declaration)throw Error('missing declaration '+h.p+':'+(i+1));
  const name=declaration.match(/(?:\s|>)(\w+)\s*(?:=|;|\{)/)?.[1];
  if(!name)throw Error('unparsed declaration '+h.p+':'+(j+1)+' '+declaration);
  const occurrences=[];const rx=new RegExp('\\b'+name+'\\b');
  for(let k=0;k<c.lines.length;k++)if(rx.test(c.lines[k]))occurrences.push({line:k+1,text:c.lines[k].trim()});
  fields.push({name,scopeHint:scope,header:h.p,line:j+1,annotation,declaration,metadataClass:annotation.includes('Transient')?'transient':annotation.includes('BlueprintAssignable')?'delegate':annotation.includes('Edit')?'editable':'other',cpp:c.p,lexicalOccurrences:occurrences});
 }
 const pattern= /LoadObject|LoadSynchronous|GetPlayerPawn|GetPlayerCharacter|FindComponentByClass|RegisterComponent|GetDefault|static constexpr|TEXT\("\/Game\//;
 const seams=c.lines.flatMap((text,i)=>pattern.test(text)?[{line:i+1,text:text.trim()}]:[]);
 result.components.push({name:base.split('/').at(-1),fields,seams});
}
const total=result.components.reduce((n,c)=>n+c.fields.length,0);
const md=['# Step2 source observations (generated)','',result.kind+'. No assets/Source changed. All public/private/constructor/default read semantics require manual audit. Widget/struct fields may share a header; scopeHint is lexical, not UHT truth.','',`Input files: ${result.files.length}; header property observations: ${total}; file families: ${result.components.length}.`,'','| Family | Properties | Transient | Editable | Delegates |','|---|---:|---:|---:|---:|'];
for(const c of result.components)md.push(`|${c.name}|${c.fields.length}|${c.fields.filter(f=>f.metadataClass==='transient').length}|${c.fields.filter(f=>f.metadataClass==='editable').length}|${c.fields.filter(f=>f.metadataClass==='delegate').length}|`);
md.push('','Detailed declarations, source hashes, lexical references and dependency seams are in SOURCE_OBSERVATIONS.json. This index supplements, does not replace, WP13/Claude D2D or editor effective-value readbacks.','');
fs.writeFileSync(out+'/SOURCE_OBSERVATIONS.json',JSON.stringify(result,null,2)+'\n');fs.writeFileSync(out+'/SOURCE_OBSERVATIONS.md',md.join('\n'));
console.log(JSON.stringify({files:result.files.length,families:result.components.length,properties:total,sha256:digest(fs.readFileSync(out+'/SOURCE_OBSERVATIONS.json'))}));
