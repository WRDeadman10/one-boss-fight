// Offline lexical witness for future 2b review; NOT a C++ AST, engine test or behavioral equivalence proof.
import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
const dir='Docs/BossCombatReview/Execution/Codex/Step2Preparation';
const baselinePath=dir+'/LEGACY_ATTACH_BASELINE_2026-10-26.json';
const live='Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp';
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const expected=['Footsteps','URPGBossMusic','URPGBossStagger','URPGBossPhases','URPGBossEncounter','URPGBossDormantWake','URPGBossPosture','Death.OwnClip','URPGBossLook','URPGBossBleed','URPGAttackTracker','URPGBossCloseClipSwap','URPGBossShockwave','URPGBossLowSweep','URPGBossHealPunish','DamageResolver','URPGTraceGuard','URPGTraceAudit','URPGBossHud','URPGCombatDebug','URPGBossLegend'];
function tokens(s){
 if(s.includes('R"'))throw Error('raw C++ strings unsupported: review parser before use');
 return [...s.matchAll(/\/\/[^\n]*|\/\*[\s\S]*?\*\/|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|[A-Za-z_]\w*|\d+(?:\.\d+)?|[^\s]/g)].filter(m=>!m[0].startsWith('//')&&!m[0].startsWith('/*')).map(m=>({v:m[0],at:m.index}));
}
function body(s,method){
 const start=s.indexOf('URPGPlayerMovesSubsystem::'+method+'(');if(start<0)throw Error('method absent: '+method);
 const t=tokens(s.slice(start));const first=t.findIndex(x=>x.v==='{');if(first<0)throw Error('body absent');
 let depth=0;for(let i=first;i<t.length;i++){if(t[i].v==='{')depth++;if(t[i].v==='}')depth--;if(!depth)return t.slice(first+1,i).map(x=>({...x,at:x.at+start}));}throw Error('unbalanced body');
}
function events(s,method){
 const t=body(s,method),found=[];
 const legacyPlayerClasses=['URPGCameraRig','URPGRiposteInput','URPGDodgeTiming','URPGSwingTracker','URPGHitIntake','URPGBuildLoadout','URPGBuildSelect','URPGFlaskHud','URPGIFrameMonitor'];
 const add=(id,i)=>found.push({id,line:s.slice(0,t[i].at).split('\n').length});
 for(let i=0;i<t.length;i++){
  const v=t.slice(i,i+15).map(x=>x.v).join('');
  if(v.startsWith('AddFootsteps(Pawn,true)'))add('Footsteps',i);
  if(v.startsWith('NewObject<')&&expected.includes(t[i+2]?.v))add(t[i+2].v,i);
  if(v.startsWith('NewObject<')&&!expected.includes(t[i+2]?.v)&&!(method==='Attach'&&legacyPlayerClasses.includes(t[i+2]?.v)))add('Unexpected.'+t[i+2]?.v,i);
  if(v.startsWith('URPGBossDeath::Attach(Pawn,ERPGBossDeathMode::OwnClip)'))add('Death.OwnClip',i);
  if(v.startsWith('URPGDamageResolver::FindOrAdd(Pawn)'))add('DamageResolver',i);
 }return found;
}
function fingerprint(s,method){return hash(body(s,method).map(x=>x.v).join('\u001f'));}
const tests=[];const test=(n,f)=>{f();tests.push(n);};
test('comments ignored',()=>assert.deepEqual(tokens('x; // y\n/* z */ q;').map(x=>x.v),['x',';','q',';']));
test('strings preserve fake comments/braces',()=>assert.equal(tokens('TEXT("//{ }");').filter(x=>x.v.includes('//')).length,1));
test('escaped quotes kept',()=>assert.equal(tokens('TEXT("a\\\"b");')[2].v,'"a\\\"b"'));
test('method braces extracted',()=>assert.equal(body('void URPGPlayerMovesSubsystem::Attach(AActor* Pawn){if(Pawn){x();}}','Attach').filter(x=>x.v==='x').length,1));
test('missing method fails',()=>assert.throws(()=>body('void Other(){}','Attach')));
test('unbalanced body fails',()=>assert.throws(()=>body('void URPGPlayerMovesSubsystem::Attach(){','Attach')));
test('raw string unsupported fails explicitly',()=>assert.throws(()=>tokens('R"(x)"')));
test('OwnClip static factory recorded',()=>assert.deepEqual(events('void URPGPlayerMovesSubsystem::Attach(){URPGBossDeath::Attach(Pawn, ERPGBossDeathMode::OwnClip);}','Attach').map(x=>x.id),['Death.OwnClip']));
test('changed mode not silently counted',()=>assert.equal(events('void URPGPlayerMovesSubsystem::Attach(){URPGBossDeath::Attach(Pawn, ERPGBossDeathMode::PackMontage);}','Attach').length,0));
test('config changes alter fingerprint',()=>assert.notEqual(fingerprint('void URPGPlayerMovesSubsystem::Attach(){x=1;}','Attach'),fingerprint('void URPGPlayerMovesSubsystem::Attach(){x=2;}','Attach')));
test('unexpected new consumer not ignored',()=>assert.deepEqual(events('void URPGPlayerMovesSubsystem::AttachLegacyBossBundle(){NewObject<URPGUnexpected>(Pawn);}','AttachLegacyBossBundle').map(x=>x.id),['Unexpected.URPGUnexpected']));
const args=process.argv.slice(2),sourcePath=args.includes('--candidate')?args[args.indexOf('--candidate')+1]:live;
const raw=fs.readFileSync(sourcePath),s=raw.toString().replaceAll('\r\n','\n');
const method=s.includes('URPGPlayerMovesSubsystem::AttachLegacyBossBundle(')?'AttachLegacyBossBundle':'Attach';
const actual=events(s,method);const ids=actual.map(x=>x.id);
const hooks={spawnCallsAttach:body(s,'OnActorSpawned').map(x=>x.v).join('').includes('Attach(Actor)'),worldBeginCallsAttach:body(s,'OnWorldBeginPlay').map(x=>x.v).join('').includes('Attach(*It)')};
if(args.includes('--capture')){
 if(sourcePath!==live||method!=='Attach')throw Error('capture requires original legacy Attach');
 assert.deepEqual(ids,expected);assert.equal(hooks.spawnCallsAttach&&hooks.worldBeginCallsAttach,true);
 if(fs.existsSync(baselinePath))throw Error('baseline already exists: never overwrite historical witness');
 const baseline={scope:'lexical pre-extraction witness only',source:live,sha256:hash(raw),bodyTokenSHA256:fingerprint(s,'Attach'),triggerTokenSHA256:{spawn:fingerprint(s,'OnActorSpawned'),worldBegin:fingerprint(s,'OnWorldBeginPlay')},bossEvents:actual,expected,playerPathRequiresManualDiff:true,creationGuardsAndDefaultsRequireManualDiff:true};
 fs.writeFileSync(baselinePath,JSON.stringify(baseline,null,2)+'\n');
}
const baseline=JSON.parse(fs.readFileSync(baselinePath));
const report={scope:'lexical order/hooks/config fingerprint only; NOT runtime idempotence or behavior proof',selftests:{passed:tests.length,total:tests.length},source:sourcePath,method,bossEvents:ids.length,orderMatches:JSON.stringify(ids)===JSON.stringify(baseline.expected),hooks,sourceHashUnchanged:hash(raw)===baseline.sha256,triggerTokensUnchanged:fingerprint(s,'OnActorSpawned')===baseline.triggerTokenSHA256.spawn&&fingerprint(s,'OnWorldBeginPlay')===baseline.triggerTokenSHA256.worldBegin,bodyTokenSHA256:fingerprint(s,method),manualReview:['all guards/default values/player branch equivalence','actual register/BeginPlay callbacks','duplicate trigger idempotence','Shipping/disabled observer behavior']};
console.log(JSON.stringify(report,null,2));
if(!report.orderMatches||!hooks.spawnCallsAttach||!hooks.worldBeginCallsAttach||(!args.includes('--candidate')&&!report.sourceHashUnchanged))process.exitCode=1;
