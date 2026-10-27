// Read-only account-resume evidence preflight. NEVER launches/stops engine, builds, git or processes.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const root=fs.realpathSync('.');
const observations='Docs/BossCombatReview/Execution/Codex/Step2Preparation/SOURCE_OBSERVATIONS.json';
export function checkPins(records,read){
 const errors=[],seen=new Set();if(!Array.isArray(records)||!records.length)return ['pins empty/not array'];
 for(const r of records){
  if(!r||typeof r.path!=='string'||!r.path||r.path.includes('..')||path.isAbsolute(r.path)){errors.push('invalid relative pin path');continue;}
  if(seen.has(r.path)){errors.push('duplicate pin: '+r.path);continue;}seen.add(r.path);
  if(typeof r.sha256!=='string'||!/^\p{ASCII_Hex_Digit}{64}$/u.test(r.sha256)){errors.push('invalid SHA256: '+r.path);continue;}
  try{if(hash(read(r.path))!==r.sha256.toLowerCase())errors.push('HASH DRIFT: '+r.path);}catch(e){errors.push('UNREADABLE: '+r.path+' ('+e.message+')');}
 }return errors;
}
export function countAutomation(text,expected){
 const lines=text.split(/\r?\n/).filter(l=>l.includes('Test Completed.'));
 const passed=lines.filter(l=>/Result=\{Success\}/.test(l)).length;
 const paths=lines.map(l=>l.match(/\bPath=\{([^{}]+)\}/)?.[1]?.trim());
 const missingPaths=paths.filter(p=>!p).length;
 const knownPaths=paths.filter(Boolean),uniquePaths=new Set(knownPaths).size;
 const duplicatePaths=knownPaths.length-uniquePaths;
 return {completed:lines.length,passed,expected,uniquePaths,missingPaths,duplicatePaths,
  matches:Number.isSafeInteger(expected)&&expected>0&&lines.length===expected&&passed===expected&&missingPaths===0&&duplicatePaths===0};
}
const tests=[];function test(name,f){f();tests.push(name);}
const fixture=[{path:'fake.txt',sha256:hash('known')}];
test('matching exact hash',()=>assert.deepEqual(checkPins(fixture,()=>Buffer.from('known')),[]));
test('drift rejected',()=>assert.match(checkPins(fixture,()=>Buffer.from('changed'))[0],/DRIFT/));
test('missing file rejected',()=>assert.match(checkPins(fixture,()=>{throw Error('absent');})[0],/UNREADABLE/));
test('malformed hash rejected',()=>assert.match(checkPins([{path:'x',sha256:'abcd'}],()=>Buffer.from('x'))[0],/invalid SHA/));
test('duplicate record rejected',()=>assert.match(checkPins([...fixture,...fixture],()=>Buffer.from('known'))[0],/duplicate/));
test('traversal rejected',()=>assert.match(checkPins([{path:'../escape',sha256:hash('x')}],()=>Buffer.from('x'))[0],/invalid relative/));
test('empty pin set rejected',()=>assert.match(checkPins([],()=>Buffer.from('x'))[0],/empty/));
const completion=(name='OneBossFight.Fake',result='Success')=>`Test Completed. Result={${result}} Name={Fake} Path={${name}}`;
test('automation count match',()=>assert.equal(countAutomation(completion(),1).matches,true));
test('failed test not counted green',()=>assert.equal(countAutomation(completion('OneBossFight.Fake','Fail'),1).matches,false));
test('missing test not counted green',()=>assert.equal(countAutomation('',1).matches,false));
test('extra/replayed completion rejected',()=>assert.equal(countAutomation(completion()+'\n'+completion(),1).matches,false));
test('same-count duplicate replacing missing test rejected',()=>assert.equal(countAutomation(completion()+'\n'+completion(),2).matches,false));
test('distinct paths accepted even with equal short names',()=>assert.equal(countAutomation(completion('OneBossFight.A.Fake')+'\n'+completion('OneBossFight.B.Fake'),2).matches,true));
test('missing identity rejected despite green count',()=>assert.equal(countAutomation('Test Completed. Result={Success}',1).matches,false));
test('blank identity rejected',()=>assert.equal(countAutomation(completion('  '),1).matches,false));
test('zero expected tests cannot be green',()=>assert.equal(countAutomation('',0).matches,false));
function safeRead(relative){
 const real=fs.realpathSync(path.resolve(root,relative));
 const rel=path.relative(root,real);if(rel.startsWith('..')||path.isAbsolute(rel))throw Error('resolved path outside project');
 return fs.readFileSync(real);
}
const original=safeRead(observations);
const inventory=JSON.parse(original);
const pins=[...inventory.files,
 {path:'Source/OneBossFight/Player/RPGEncounterBinding.h',sha256:'4330f8c416cd75284e829856b5d1cba7001c5ee62f40bdc7b1bf98a8dbf94a80'},
 {path:'Source/OneBossFight/Player/RPGEncounterBinding.cpp',sha256:'2fe63bcb78261b9bdd15be33607ea3c696ae33227989facc5b67e15cd91110dc'},
 {path:'Source/OneBossFight/Tests/RPGEncounterBindingTests.cpp',sha256:'bcdb3b2f40f1795bfd6187523cf98fc8ab2567cae46949065dd3a6908f2d66da'}];
const errors=checkPins(pins,safeRead);
const base='Docs/BossCombatReview/Execution/Claude/Evidence/exports/';
const logs=[['automation_catalogpath_run3.log',43,'c62ab549a70a66341f9939f82c711bebc62a2d45e6170cbac00ef07d7e2584c0'],['automation_diagnostics_run1.log',44,'708ed040f6a1b4c1986917982f48c0e1b8fdd2afeda0db4437c2d61a1c3a78c1'],['automation_step2a_scaffold.log',45,'6704ec5cecc7f4287cedffc119f7a1ea15988f57cf9a24ee98e3d7a32eb16952']].map(([name,count,pin])=>{
 const bytes=safeRead(base+name),actual=hash(bytes),result=countAutomation(bytes.toString(),count);
 if(actual!==pin||!result.matches)errors.push('AUTOMATION EVIDENCE DRIFT: '+name);
 return {path:base+name,sha256:actual,hashMatches:actual===pin,...result};
});
const checkpoint='Docs/BossCombatReview/Execution/Claude/ACCOUNT_HANDOVER_CURRENT.md';
const summary={scope:'read-only evidence consistency, NOT runtime readiness/gate approval or tested-binary provenance',selftests:{passed:tests.length,total:tests.length},sourcePins:pins.length,sourceObservationDigest:hash(original),checkpoint:{path:checkpoint,sha256:hash(safeRead(checkpoint))},automation:logs,errors,runtimeProcessState:'NOT CHECKED; operator must inspect before resuming',liveCvarsAndEditorState:'NOT CHECKED',shippingAndFullGate:'NOT PROVEN BY THIS SCRIPT'};
console.log(JSON.stringify(summary,null,2));if(errors.length)process.exitCode=1;
