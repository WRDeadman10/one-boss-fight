# C191 stats adapter source review

Read actual header, cpp, all536 test lines, delivery and actual source manifests. Receipt/live-review-copy hashes match;147 original source entries unchanged, exactly3 new files. No build/test result is claimed. **One bounded lifecycle correction required before build release.**

Typed assignment, complete Stats validation before field writes, finite/sign checks, native health<=1 named capability rejection, exact instance/class plan identity, unregistered/component/owner-begun checks and five focused test groups fit DD3 package01. Existing components, compiler domain and native defaults remain unchanged. Exact native classes are appropriate for this initial native plan ABI; no subclass capability claimed. First failure/public validator/inline constants are acceptable.

## Answer: posture maximum remains positive (>0)

Keep0.5 accepted at this assignment layer as ordered. Generic Stats compiler is positive-only; native BeginPlay/ResetPool use PostureMax directly and current arithmetic supports a positive float. Editor ClampMin1 is authoring metadata, not independent proof of a runtime backend limitation. Do not silently impose >=1 or change native metadata/defaults. The metadata/runtime-domain mismatch belongs to later consistent authoring validation, and eventual effective value still needs real-world evidence. Health's <=1 backend override limitation is a separate demonstrated native guard, not a justification to give posture the same floor.

## Required correction: reject dead component before inspecting/configuring it

CheckConfigurable rejects wrong type and registered/begun component/invalid owner, but never tests component validity or `IsBeingDestroyed`. Installed ActorComponent.cpp DestroyComponent1558+ sets destruction flag, ends play (EndPlay clears bHasBegunPlay), unregisters and marks garbage. A destroyed-but-not-collected component can therefore present false registered/begun flags, retain a valid owner and satisfy the current checks. Source-confirmed acceptance path, not an executed Unreal reproduction. Configuring it would violate a valid unregistered configuration-target contract.

Add an initial named InvalidComponent check using `IsValid(&Component)` and public `Component.IsBeingDestroyed()` before class/member configuration logic; do not dereference freed objects or call IsValidLowLevel as a workaround. Add focused cases for both adapters after DestroyComponent on a fresh component whose actor remains valid. Preserve allocation during the immediate no-GC check with the test's lifetime mechanism, verify destroyed/invalid precondition, snapshot public state around the rejected call and assert no write. No destructive callback/GC tricks or production seam needed. This remains a narrow change to the3 new files; no existing source allowed.

## Precision qualifications (do not expand package)

Public-state snapshots cover selected accessible state, not every private cache. The statement that existing CreateConfigureRegister destroys pending components after callback failure is not a general rollback/owned-resource cleanup guarantee; retain Step2Preparation08's pre-BeginPlay cleanup limitations. Per-callback validation cannot guarantee a whole future cluster has no other failure after an earlier callback succeeded.

Both callbacks validate all4 typed fields, but current per-plan RequiredFields lists describe assignment destinations (1+3) rather than every validation dependency. Document that distinction and ensure the future full-cluster preflight requires the union4; no claim that manifest presence proves actual values/derivation. Do not change existing binding/compiler behavior or grow into provenance enforcement here.

Deliver revised actual3-file hashes/diff and test, then Codex will release focused build/tests. No separate owner permission or repeat design document required; this is correction within the current implementation claim. No runtime activation/pack edits/AG work.
