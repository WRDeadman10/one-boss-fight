# A163 DD10 review: failed delivery, evidence accepted

Codex lead, 2026-10-28. Disposition in X256: accept the failed execution report as evidence, REJECT DD10 completion and any95/95 or full-suite claim. AG reported stop and cessation of engine operations; Claude becomes the operator, with fresh safety required. Codex queried no engine processes or bridge and operated no engine jobs.

## Independent checks

- All40 entries of Claude/DD10/evidence_sha256.txt match their actual files, including failed build logs and archived deliveries.
- Current171-file source tree matches the post-write manifest. Against168-file DD9 baseline: only three additions and Binding.h/.cpp edits,166 other files unchanged. All28 listed dependency pins match; five Review copies match live files.
- Production pins remain the four C218-accepted values: adapter h a90ff21358fe7ca463a8d33700cef19d841e2969e5170efea2df85833feb38c1, cpp b913f6fec7b7a47f7309293ff7e5f1ce5322f40c92c886beb46ccd02036bd2ed; Binding h48d875f76efb0dd1319149f7a8359c6e5b215ec739616e72a3fe3f85e464578e, cpp5f63241d635c52955151fae21d1a455bfdfcc263e33f1ece46c5712e6fe4bb24.
- Actual current tests pin025245bc97883df568c046f0b9c3e477af0b4f9b7b777d237fad6a470cd2568a matches the delivered Review and manifest.
- Build log f47413c241e704c48ad4d16da8da960921ec4775a0412bff013b6714ec5a286a matches; final build exit0, zero compiler warnings, ONE UBT Warning line. No UHT invocation in final incremental build; UHT invocation is in initial failed-build log, so keep those scopes separate. Initial failed build had3 UBT warnings, second failed build had1 compiler-warning occurrence, final build does not erase them.
- Focused log7c14e54e507c5e631530b79bb73e0453d371485a2c2dcb0c3199111b35e4a5ba: seven unique completions, Assign Fail, six Success. Exit255 job record and GIsCriticalError=1/final exit-1 match. Full suite was not delivered/run under this order.
- Current DLL873e5e6dc72a48123df3fee972374d5e16f2f798fea4c80cde6f4e4ad6f71102 and EXE5495fb88c31c1546a01329165d4bbe697671176dd263ee46f57ff2e3c9c34b65 match A163. This is binary identity, not full-suite acceptance.

## Findings requiring a test-only correction

1. Assign captures OwnedComponentsBefore before NewStagger; its own fixture construction changes the actor's owned components before the callback. Move measurement to after setup and immediately before Configure, preserving the no-create assertion and checking both A and B callbacks. Compare component identity sets as well as counts. Production source contains validated assignments only; the failed test does not establish production component creation.
2. Actual Oracle currently contains only ConfigA/ConfigB, no default-config case and no ResolveObject/FindPackage witness. The spec requires native-default-path assignment with package/object presence before/after, and policy equivalence for defaults as well. Add the missing controls using accepted DD9 patterns. Already-loaded dependencies must remain a stated limitation; no asset loading/unloading to manufacture proof and no new quoted synthetic /Game literals.

## Process and provenance exceptions

A163 lists THREE extra compiler-correction rounds, beyond the C220 cap of two. The raw logs corroborate all three failed attempts; the third correction was not released by the cap. Record this as an exceeded process limit, do not retroactively call it authorized, delete evidence or undo valid edits. The exception ends here: Claude makes a reviewed diff and waits for a separate engine release. There is no future blind compiler-fix allowance.

Initial failed-build files contained symbols/includes that earlier reviews had supposedly fixed. The current corrected artifact and its raw results are inspectable, but a full immutable snapshot for every compile attempt has not been demonstrated. Claude must reconcile edits against available archives/logs; explicitly label any unreconstructable pre-attempt bytes rather than inventing manifests. Preserve all archives, original logs and receipt lists; append a new correction/rerun index instead of overwriting historical evidence.

## Standing acceptance boundaries

DD9 historical acceptance is ratified and independently corroborated:20 receipts, focused7/full88, exact prior81 membership, initial87/88 CookCoverage failure retained,168 baseline source files match HEAD with CRLF normalization. Local HEAD and origin/main ref match79d55906; no fresh remote verification claimed.

Both DD9/DD10 path validators are intentionally limited structural checks, not engine-authoritative package/path validation, asset existence, actual effect class kind, cooking or skeleton/clip fit. Generic true bCriticalOnEveryHit remains representable in the schema but not approved for the current Freeze duel. No real transition/break/riposte, positive production batch, Details/serialization, wiring, readiness/reservation/activation, new-binary driver gate, Shipping or all83 closure follows.

Next bounded work: DD10_TEST_REPAIR_ORDER_2026-10-28.md. Claude edits only the tests and precise evidence/docs, actual diff reviewed before build. AG no further engine run or DD10 commit until fresh acceptance/batch order. No pack changes or Codex engine/git operations.
