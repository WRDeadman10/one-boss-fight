# Queue BC Batch 8: X36–X40 reflected surface, locks, and read-only driver safety

## X36 — reflected test-hook inventory

In named target classes, `URPGDamageResolver::ResolveForTest` and `NoteOverlapForTest` are unconditionally declared `UFUNCTION`s in `RPGDamageResolver.h:189–193`; implementations are Shipping no-op/refusal bodies (`RPGDamageResolver.cpp:248–272`). `ARPGFrameworkBossCharacter` test bridge declarations wrap `UFUNCTION` in `WITH_EDITORONLY_DATA` (`RPGFrameworkBossCharacter.h:24–39`), with Shipping refusal bodies. `URPGDodgeTiming` has three BlueprintCallable Development guard-counter helpers (`RPGDodgeTiming.h:123–131`, `RPGDodgeTiming.cpp`); their metadata and Shipping behavior do not alone prove reflected-symbol absence. This is a source inventory, not a Shipping UHT/binary surface result.

## X37 — Shipping-safe guard options

Keep test-only Blueprint entry points behind the project's established editor-only reflection guard where callable reflection is needed for transient Editor proof; compile safe native declarations separately when tests need a C++ seam. Alternatively expose a deliberately harmless Shipping stub only if retaining the node is intentional and documented. For `RPGDamageResolver`, current stubs prevent execution but leave the UFUNCTION declarations unguarded, so a Shipping surface audit must decide whether node visibility is acceptable. Do not claim symbols are stripped without UHT/Shipping evidence. No code changed.

## X38 — lock protocol consistency

`PROJECT_STATE.md` assigns editor/build/PIE ownership to Claude and permits Codex builds/suites only under C-1155. The recent task-specific runner `run_c1254a_transient_profile_check.ps1` checks both locks and matching project Editor process, creates both lock files with `CreateNew` and owner token, passes task-specific evidence, and removes only owned locks in `finally`. The generic `Scripts/Rebuild.ps1` is a convenience wrapper and does not itself acquire C-1155 locks. No lock was created, removed, or queried for ownership by this static audit.

## X39 — command documentation correction

`NEW_AGENT_ONBOARDING.md` and `FULL_SUITE_EVIDENCE_HOWTO.md` showed direct `Rebuild.ps1` invocations that could be misread as the current engine-run protocol. Added a warning: those commands describe shape only; actual runs must use the task-specific runner with both C-1155 locks, owner token, pinned DD27j hash, and ownership-safe release. This preserves the generic wrapper's build/test documentation while making the lock requirement explicit.

## X40 — read-only driver source contract

Added `Scripts/Tools/test_greystone_wrapper_readback_readonly.py`, an AST contract for `Scripts/Editor/verify_greystone_wrapper_readback.py` that rejects asset creation, save, delete, rename, duplicate, and `set_editor_property` calls. It permits only readback logic and the script's documented quit behavior. This check tests source shape only; it cannot prove runtime side effects of opaque Editor APIs.

## Verification and limits

Focused AST contract: **1/1 passed**. Documentation link scan is recorded in the batch handoff after the doc edits. No Unreal/UHT/Shipping/build/test-suite/PIE execution; no lock operations, content asset operations, commit, or push.
