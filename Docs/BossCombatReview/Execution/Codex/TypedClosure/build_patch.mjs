// Mechanical staging only: live files are read, never written. Run from project root.
import fs from 'node:fs';
import cp from 'node:child_process';
import crypto from 'node:crypto';
import path from 'node:path';
const dir='Docs/BossCombatReview/Execution/Codex/TypedClosure';
const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
const names=['Source/OneBossFight/Player/RPGCombatCatalog.cpp','Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp'];
let patch='', pins={};
for(const name of names){
 const raw=fs.readFileSync(name); pins[name]=hash(raw);
 let s=raw.toString().replaceAll('\r\n','\n');
 if(name.endsWith('/RPGCombatCatalog.cpp')){
  s='#include "Player/RPGCombatCatalogABI.h"\n'+s;
  const start=s.indexOf('\t\t\t\t// Validate that the item actually references');
  const end=s.indexOf('\t\t\t\tfor (ERPGAttackKind Kind',start);
  if(start<0||end<0)throw Error('production anchors changed');
  s=s.slice(0,start)+'\t\t\t\tFWeaponReferences References; References.Item = Item; References.DeclaredItemBase = ItemBase;\n\t\t\t\tReferences.ActorClass = ActorClass; References.AbilityClass = AbilityClass; References.Style = Style;\n\t\t\t\tFString ABIError;\n\t\t\t\tif (!ValidateWeaponReferences(W, References, E->Leases, ABIError)) return Fail(ABIError);\n\t\t\t\tif (auto* Resolved = E->Weapons.FindByPredicate([&W](const FRPGCatalogWeapon& Value) { return Value.WeaponId == W.WeaponId; })) Resolved->ReferenceProvenance = TEXT("typed ABI/item actor/style ability grant checked; live equip not yet observed");\n'+s.slice(end);
 }else{
  s=s.replace('#include "Player/RPGCombatCatalog.h"','#include "Player/RPGCombatCatalog.h"\n#include "Player/RPGCombatCatalogABI.h"\n#include "GameFramework/Actor.h"\n#include "UObject/UnrealType.h"\n#include "UObject/GarbageCollection.h"\n#include "UObject/Package.h"');
  const at=s.lastIndexOf('\treturn true;\n}'); if(at<0)throw Error('test anchor changed');
  s=s.slice(0,at)+fs.readFileSync(dir+'/resolution_test_addition.cpp.txt','utf8').replaceAll('\r\n','\n')+'\n'+s.slice(at);
 }
 const target=dir+'/'+name; fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,s);
 const r=cp.spawnSync('git',['diff','--no-index','--ignore-cr-at-eol','--',name,target],{encoding:'utf8'});
 if(r.status!==1)throw Error('diff failed '+r.stderr);
 let d=r.stdout; const lines=d.split('\n');
 lines[0]=`diff --git a/${name} b/${name}`;
 d=lines.map(l=>l.startsWith('+++ ')?`+++ b/${name}`:l.startsWith('--- ')?`--- a/${name}`:l).join('\n');patch+=d;
}
for(const name of ['Source/OneBossFight/Player/RPGCombatCatalogABI.h','Source/OneBossFight/Player/RPGCombatCatalogABI.cpp']){
 const s=fs.readFileSync(dir+'/'+name,'utf8').replaceAll('\r\n','\n');const lines=s.trimEnd().split('\n');
 patch+=`diff --git a/${name} b/${name}\nnew file mode 100644\n--- /dev/null\n+++ b/${name}\n@@ -0,0 +1,${lines.length} @@\n`+lines.map(l=>'+'+l).join('\n')+'\n';
}
fs.writeFileSync(dir+'/PROMOTION_STEP1_TYPED_ABI.patch',patch);
fs.writeFileSync(dir+'/PREIMAGE_AND_PATCH_SHA256.json',JSON.stringify({preimages:pins,patch_sha256:hash(patch)},null,2)+'\n');
console.log(JSON.stringify({preimages:pins,patch_sha256:hash(patch)},null,2));
