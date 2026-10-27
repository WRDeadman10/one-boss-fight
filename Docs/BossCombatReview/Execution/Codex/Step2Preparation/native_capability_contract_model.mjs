// PROPOSED selected-scalar contract model only. Not Unreal, a production compiler,
// an approved schema/domain policy, a component mutation API or a runtime parity test.
import assert from 'node:assert/strict';

export function selectedScalarPlan(input) {
  const errors = [];
  const health = input?.Stats?.MaxHealth;
  const damage = input?.Transition?.AttackMultiplier;
  const positive = value => typeof value === 'number' && Number.isFinite(value) && value > 0;
  // Selected existing generic scalar domains only, not complete definition validation.
  if (!positive(health)) errors.push({field:'Stats.MaxHealth', reason:'InvalidGenericScalar'});
  if (!positive(damage)) errors.push({field:'Transition.AttackMultiplier', reason:'InvalidGenericScalar'});
  if (errors.length) return Object.freeze({disposition:'GenericInvalid', errors:Object.freeze(errors)});
  if (input.HealthIntent !== 'ApplyConfiguredMaximum') {
    errors.push({field:'HealthIntent', reason:'ExplicitSupportedHealthIntentRequired'});
  } else if (health <= 1) {
    errors.push({field:'Stats.MaxHealth', reason:'NativeHealthBypassDomain'});
  }
  if (input.DamageCapability !== 'ProposedLegacyInverse') {
    errors.push({field:'DamageCapability', reason:'ExplicitSupportedDamageCapabilityRequired'});
  } else if (damage < 1) {
    errors.push({field:'Transition.AttackMultiplier', reason:'SignedDeltaReversalUnspecified'});
  }
  if (errors.length) return Object.freeze({disposition:'UnsupportedNativeCapability', errors:Object.freeze(errors)});
  return Object.freeze({disposition:'SupportedSelectedScalarPlan',
    assignments:Object.freeze({BossMaxHealth:health, DamageScale:damage}),
    evidenceScope:'value-plan only; registration, loaded dependencies and actual pack readback NOT PROVEN'});
}

const fixture = () => ({Stats:{MaxHealth:2000}, Transition:{AttackMultiplier:1.25},
  HealthIntent:'ApplyConfiguredMaximum', DamageCapability:'ProposedLegacyInverse'});
const checks=[];
function test(name, body) { body(); checks.push(name); }
function verdict(edit) { const value=fixture(); edit(value); return selectedScalarPlan(value); }
test('explicit baseline assignments preserve values without mutation',()=>{
  const value=fixture(), before=JSON.stringify(value), plan=selectedScalarPlan(value);
  assert.equal(plan.disposition,'SupportedSelectedScalarPlan');
  assert.deepEqual(plan.assignments,{BossMaxHealth:2000,DamageScale:1.25});
  assert.equal(JSON.stringify(value),before);
});
test('positive half-health generic scalar is native-unsupported, never clamped',()=>{
  const result=verdict(v=>v.Stats.MaxHealth=.5);
  assert.equal(result.disposition,'UnsupportedNativeCapability'); assert.equal('assignments' in result,false);
});
test('health exactly one remains native-unsupported',()=>assert.equal(verdict(v=>v.Stats.MaxHealth=1).disposition,'UnsupportedNativeCapability'));
test('health zero fails generic layer',()=>assert.equal(verdict(v=>v.Stats.MaxHealth=0).disposition,'GenericInvalid'));
test('negative health fails generic layer',()=>assert.equal(verdict(v=>v.Stats.MaxHealth=-1).disposition,'GenericInvalid'));
test('nonfinite scalar fails generic layer',()=>assert.equal(verdict(v=>v.Transition.AttackMultiplier=Infinity).disposition,'GenericInvalid'));
test('bool is not numeric health',()=>assert.equal(verdict(v=>v.Stats.MaxHealth=true).disposition,'GenericInvalid'));
test('positive subunit damage remains generic-valid but unsupported by this candidate profile',()=>assert.equal(verdict(v=>v.Transition.AttackMultiplier=.5).disposition,'UnsupportedNativeCapability'));
test('neutral damage one is supported by selected candidate scalar profile',()=>assert.equal(verdict(v=>v.Transition.AttackMultiplier=1).disposition,'SupportedSelectedScalarPlan'));
test('missing health intent cannot infer preserve mode',()=>assert.equal(verdict(v=>delete v.HealthIntent).disposition,'UnsupportedNativeCapability'));
test('preserve mode is not silently implemented as omitted assignment',()=>{
  const result=verdict(v=>v.HealthIntent='PreserveLegacyMaximum');
  assert.equal(result.disposition,'UnsupportedNativeCapability'); assert.equal('assignments' in result,false);
});
test('unknown damage capability cannot infer native profile',()=>assert.equal(verdict(v=>v.DamageCapability='Unknown').disposition,'UnsupportedNativeCapability'));
test('unsupported inputs remain unchanged and report both domain errors',()=>{
  const value=fixture(); value.Stats.MaxHealth=.5; value.Transition.AttackMultiplier=.5;
  const before=JSON.stringify(value), result=selectedScalarPlan(value);
  assert.equal(result.errors.length,2); assert.equal(JSON.stringify(value),before);
});
test('successful plan does not alias mutable input values or claim runtime readiness',()=>{
  const value=fixture(), result=selectedScalarPlan(value); value.Stats.MaxHealth=999;
  assert.equal(result.assignments.BossMaxHealth,2000); assert.equal(Object.isFrozen(result.assignments),true);
  assert.equal('ready' in result,false); assert.equal('content_hash_verified' in result,false);
});
console.log(JSON.stringify({scope:'PROPOSED selected-scalar abstract model, not UE tests/complete compiler/policy approval',
  passed:checks.length, total:checks.length, tests:checks},null,2));
