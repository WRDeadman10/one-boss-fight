// EXECUTABLE DESIGN MODEL ONLY. No Unreal API, production code, asset loading or performance proof.
import assert from 'node:assert/strict';
export class CoordinatorModel {
 constructor(world,{enabled=true}={}){this.world=world;this.enabled=enabled;this.encounters=new Map();this.actors=new Map();this.retired=new Map();this.retiredEncounters=new Map();this.registering=false;this.disposed=false;}
 reserve(id,participants,hash='pinned'){
  if(this.disposed)throw Error('disposed');if(this.registering)throw Error('registration active');if(!this.enabled||!participants.length)return 'Legacy';
  if(!id||!hash)throw Error('identity');
  const signature=JSON.stringify(participants);
  const old=this.encounters.get(id);if(old){if(old.signature===signature&&old.hash===hash)return 'Idempotent';throw Error('duplicate encounter');}
  const slots=new Set(),actors=new Set();
  for(const p of participants){if(!p.slot||slots.has(p.slot)||!p.actor||actors.has(p.actor)||this.actors.has(p.actor)||p.world!==this.world||p.begun||!Number.isSafeInteger(p.generation)||p.generation<1||p.generation>0xffffffff||p.generation!==participants[0].generation||p.generation<=(this.retired.get(p.actor)??0)||p.generation<=(this.retiredEncounters.get(id)??0))throw Error('participant');slots.add(p.slot);actors.add(p.actor);}
  for(const p of participants)if(!slots.has(p.target)||p.target===p.slot)throw Error('target');
  const e={id,signature,hash,state:'Reserved',version:0,participants:structuredClone(participants),created:0,registered:0,busy:false};
  this.encounters.set(id,e);for(const p of e.participants){this.retired.delete(p.actor);this.actors.set(p.actor,e);}return 'Reserved';
 }
 route(actor){if(this.disposed)return 'Reject';const e=this.actors.get(actor);if(!e)return this.retired.has(actor)?'Reject':'Legacy';return e.state==='Ready'?'Handled':e.state==='Poisoned'?'Reject':'Pending';}
 prepare(id,plans,{fail=false}={}){
  const e=this.encounters.get(id);if(this.registering||!e||e.state!=='Reserved'||e.busy)throw Error('prepare state');
  const actors=new Set(plans.map(p=>p.actor));if(plans.length!==e.participants.length||actors.size!==plans.length)throw Error('whole batch');
  for(const p of e.participants){const plan=plans.find(x=>x.actor===p.actor);if(!plan||!plan.classes.length||new Set(plan.classes).size!==plan.classes.length||plan.preexisting)throw Error('invalid plan');}
  e.busy=true;e.state='Preparing';e.created=plans.reduce((n,p)=>n+p.classes.length,0);
  if(fail){e.created=0;e.state='Reserved';e.busy=false;return false;}
  e.plans=structuredClone(plans);e.state='Prepared';e.busy=false;return true;
 }
 register(id,onRegister=()=>{}){
  const e=this.encounters.get(id);if(this.registering||!e||e.state!=='Prepared'||e.busy)throw Error('register state');
  this.registering=true;e.busy=true;e.state='Registering';const version=e.version;
  try{for(const p of e.plans)for(const cls of p.classes){
   if(this.disposed||e.version!==version||e.state!=='Registering')throw Error('invalidated');
   onRegister(p.actor,cls,this);e.registered++;
   if(this.disposed||e.version!==version||e.state!=='Registering')throw Error('invalidated');
  }e.state='Ready';return true;}catch{e.state='Poisoned';return false;}finally{e.busy=false;this.registering=false;}
 }
 key(actor){const e=this.actors.get(actor);if(!e||e.state!=='Ready')return null;const p=e.participants.find(x=>x.actor===actor);return Object.freeze({world:this.world,encounter:e.id,slot:p.slot,generation:p.generation});}
 resolve(key){if(!key||key.world!==this.world||this.disposed)return null;const e=this.encounters.get(key.encounter);if(!e||e.state!=='Ready')return null;const p=e.participants.find(x=>x.slot===key.slot&&x.generation===key.generation);return p?e.participants.find(x=>x.slot===p.target&&x.generation===key.generation)?.actor??null:null;}
 advance(id,generation){const e=this.encounters.get(id);if(this.registering||!e||e.busy||e.state!=='Ready'||!Number.isSafeInteger(generation)||generation>0xffffffff||e.participants.some(p=>generation<=p.generation))return false;for(const p of e.participants)p.generation=generation;e.version++;return true;}
 invalidate(id){const e=this.encounters.get(id);if(e){e.version++;e.state='Poisoned';}}
 unbind(actor){const e=this.actors.get(actor);if(!e)return;this.invalidate(e.id);for(const p of e.participants){this.retired.set(p.actor,p.generation);this.actors.delete(p.actor);}this.retiredEncounters.set(e.id,e.participants[0].generation);this.encounters.delete(e.id);}
 dispose(){this.disposed=true;for(const e of this.encounters.values()){e.version++;e.state='Poisoned';}this.actors.clear();this.encounters.clear();this.retired.clear();this.retiredEncounters.clear();}
}
const people=(world='W',suffix='')=>[{slot:'Boss',actor:'boss'+suffix,world,target:'Player',generation:1},{slot:'Player',actor:'player'+suffix,world,target:'Boss',generation:1}];
const plans=(suffix='')=>[{actor:'boss'+suffix,classes:['Encounter','Phases','Legend']},{actor:'player'+suffix,classes:['Participant']}];
const reserved=()=>{const c=new CoordinatorModel('W');c.reserve('E',people());return c;};
const ready=()=>{const c=reserved();c.prepare('E',plans());c.register('E');return c;};
const tests=[];const test=(name,f)=>{f();tests.push(name);};
test('empty records choose legacy',()=>assert.equal(new CoordinatorModel('W').reserve('E',[]),'Legacy'));
test('feature disabled chooses legacy',()=>assert.equal(new CoordinatorModel('W',{enabled:false}).reserve('E',people()),'Legacy'));
test('foreign world rejected atomically',()=>{const c=new CoordinatorModel('W');assert.throws(()=>c.reserve('E',people('X')));assert.equal(c.actors.size,0);});
test('duplicate slot rejected',()=>{const p=people();p[1].slot='Boss';assert.throws(()=>new CoordinatorModel('W').reserve('E',p));});
test('duplicate actor rejected',()=>{const p=people();p[1].actor=p[0].actor;assert.throws(()=>new CoordinatorModel('W').reserve('E',p));});
test('missing target rejected',()=>{const p=people();p[0].target='Other';assert.throws(()=>new CoordinatorModel('W').reserve('E',p));});
test('self target rejected',()=>{const p=people();p[0].target='Boss';assert.throws(()=>new CoordinatorModel('W').reserve('E',p));});
test('already begun actor rejected',()=>{const p=people();p[0].begun=true;assert.throws(()=>new CoordinatorModel('W').reserve('E',p));});
test('generation must be positive integer',()=>{const p=people();p[0].generation=NaN;assert.throws(()=>new CoordinatorModel('W').reserve('E',p));});
test('double trigger idempotent',()=>{const c=reserved();assert.equal(c.reserve('E',people()),'Idempotent');assert.equal(c.actors.size,2);});
test('same id changed manifest rejected',()=>assert.throws(()=>reserved().reserve('E',people(),'changed')));
test('explicit pending actor never falls to legacy',()=>assert.equal(reserved().route('boss'),'Pending'));
test('unknown actor remains legacy',()=>assert.equal(reserved().route('unbound'),'Legacy'));
test('partial component plan rejected before creation',()=>{const c=reserved();assert.throws(()=>c.prepare('E',plans().slice(0,1)));assert.equal(c.encounters.get('E').created,0);});
test('duplicate component class rejected',()=>{const c=reserved();const p=plans();p[0].classes.push('Encounter');assert.throws(()=>c.prepare('E',p));});
test('preexisting consumer rejects',()=>{const c=reserved();const p=plans();p[0].preexisting=true;assert.throws(()=>c.prepare('E',p));});
test('configure failure leaves no pending components',()=>{const c=reserved();assert.equal(c.prepare('E',plans(),{fail:true}),false);assert.equal(c.encounters.get('E').created,0);});
test('no resolution until whole batch ready',()=>{const c=reserved();c.prepare('E',plans());assert.equal(c.key('boss'),null);});
test('registration order explicit and ready together',()=>{const c=reserved();c.prepare('E',plans());const seen=[];c.register('E',(a,k)=>{seen.push(k);assert.equal(c.key(a),null);});assert.deepEqual(seen,['Encounter','Phases','Legend','Participant']);assert.equal(c.route('boss'),'Handled');});
test('registration callback error poisons rather than fallback',()=>{const c=reserved();c.prepare('E',plans());assert.equal(c.register('E',()=>{throw Error('callback');}),false);assert.equal(c.route('boss'),'Reject');});
test('invalidation during registration stops remaining callbacks',()=>{const c=reserved();c.prepare('E',plans());let n=0;assert.equal(c.register('E',()=>{n++;c.invalidate('E');}),false);assert.equal(n,1);});
test('reentrant registration rejected',()=>{const c=reserved();c.prepare('E',plans());assert.equal(c.register('E',()=>c.register('E')),false);});
test('two encounters resolve only associated target',()=>{const c=ready();c.reserve('F',people('W','2'));c.prepare('F',plans('2'));c.register('F');assert.equal(c.resolve(c.key('boss')),'player');assert.equal(c.resolve(c.key('boss2')),'player2');});
test('foreign-world key cannot resolve',()=>{const a=ready(),b=new CoordinatorModel('X');b.reserve('E',people('X'));b.prepare('E',plans());b.register('E');assert.equal(b.resolve(a.key('boss')),null);});
test('generation changes invalidate copied old key',()=>{const c=ready(),old=c.key('boss');assert.equal(c.advance('E',2),true);assert.equal(c.resolve(old),null);assert.equal(c.resolve(c.key('boss')),'player');});
test('nonmonotonic generation refused',()=>assert.equal(ready().advance('E',1),false));
test('unbind member invalidates whole encounter, not another',()=>{const c=ready();c.reserve('F',people('W','2'));c.prepare('F',plans('2'));c.register('F');const old=c.key('boss');c.unbind('player');assert.equal(c.resolve(old),null);assert.equal(c.resolve(c.key('boss2')),'player2');});
test('world teardown invalidates all copied keys',()=>{const c=ready(),old=c.key('boss');c.dispose();assert.equal(c.resolve(old),null);assert.throws(()=>c.reserve('new',people()));});
test('world teardown cannot route back to legacy',()=>{const c=ready();c.dispose();assert.equal(c.route('boss'),'Reject');});
test('mixed generation in one encounter rejected',()=>{const p=people();p[1].generation=2;assert.throws(()=>new CoordinatorModel('W').reserve('E',p));});
test('uint32 generation overflow rejected',()=>{const p=people();p[0].generation=0x100000000;assert.throws(()=>new CoordinatorModel('W').reserve('E',p));assert.equal(ready().advance('E',0x100000000),false);});
test('mid-registration unbind cannot restore legacy for surviving members',()=>{const c=reserved();c.prepare('E',plans());let n=0;assert.equal(c.register('E',()=>{n++;c.unbind('boss');}),false);assert.equal(n,1);assert.equal(c.route('boss'),'Reject');assert.equal(c.route('player'),'Reject');assert.equal(c.key('boss'),null);assert.equal(c.route('unbound'),'Legacy');});
test('retired actors cannot rebind with the same generation',()=>{const c=ready();c.unbind('boss');assert.throws(()=>c.reserve('F',people()));assert.equal(c.route('player'),'Reject');});
test('failed rebind validates whole batch before releasing quarantine',()=>{const c=ready();c.unbind('boss');const p=people();p.forEach(x=>x.generation=2);p[1].target='Missing';assert.throws(()=>c.reserve('E',p));assert.equal(c.actors.size,0);assert.equal(c.route('boss'),'Reject');assert.equal(c.route('player'),'Reject');});
test('explicit newer-generation rebind preserves old-key invalidation',()=>{const c=ready(),old=c.key('boss');c.unbind('player');const p=people();p.forEach(x=>x.generation=2);c.reserve('E',p);assert.equal(c.route('boss'),'Pending');c.prepare('E',plans());c.register('E');assert.equal(c.resolve(old),null);assert.equal(c.resolve(c.key('boss')),'player');});
test('reused encounter identity cannot revive old key through different actors',()=>{const c=ready(),old=c.key('boss');c.unbind('boss');assert.throws(()=>c.reserve('E',people('W','2')));const p=people('W','2');p.forEach(x=>x.generation=2);c.reserve('E',p);c.prepare('E',plans('2'));c.register('E');assert.equal(c.resolve(old),null);assert.equal(c.resolve(c.key('boss2')),'player2');});
test('registration blocks cross-encounter registration without poisoning other batch',()=>{const c=reserved();c.reserve('F',people('W','2'));c.prepare('E',plans());c.prepare('F',plans('2'));assert.equal(c.register('E',()=>c.register('F')),false);assert.equal(c.encounters.get('F').state,'Prepared');assert.equal(c.register('F'),true);assert.equal(c.registering,false);});
test('registration blocks cross-encounter preparation and reservation',()=>{const c=reserved();c.reserve('F',people('W','2'));c.prepare('E',plans());assert.equal(c.register('E',()=>{assert.throws(()=>c.prepare('F',plans('2')));assert.throws(()=>c.reserve('G',people('W','3')));}),true);assert.equal(c.encounters.get('F').state,'Reserved');assert.equal(c.encounters.has('G'),false);});
test('registration blocks generation mutation in another encounter',()=>{const c=ready();c.reserve('F',people('W','2'));c.prepare('F',plans('2'));const old=c.key('boss');assert.equal(c.register('F',()=>assert.equal(c.advance('E',2),false)),true);assert.equal(c.resolve(old),'player');});
test('disposal during registration stops callbacks and releases guard',()=>{const c=reserved();c.prepare('E',plans());let n=0;assert.equal(c.register('E',()=>{n++;c.dispose();}),false);assert.equal(n,1);assert.equal(c.registering,false);assert.equal(c.route('player'),'Reject');assert.equal(c.encounters.size,0);});
test('unbind quarantine isolates another encounter and is idempotent',()=>{const c=ready();c.reserve('F',people('W','2'));c.prepare('F',plans('2'));c.register('F');c.unbind('boss');c.unbind('boss');assert.equal(c.route('player'),'Reject');assert.equal(c.resolve(c.key('boss2')),'player2');});
console.log(JSON.stringify({scope:'abstract design-model checks, NOT Unreal automation/runtime proof',passed:tests.length,total:tests.length,tests},null,2));
