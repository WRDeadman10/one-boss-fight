# BT-85: C-1155 gate audit for Greystone visual smoke

Date: 2026-11-17 21:36 Asia/Kolkata
Scope: source-only review of `Scripts/Editor/run_greystone_visual_smoke.ps1` against the established C-1155 route runner pattern. No approval receipt was issued and no build, test, Unreal Editor, or PIE execution occurred.

## Required safe sequence

1. Obtain a fresh owner/lead approval receipt tied to the exact final source hashes, `/Game/OneBossFight/Maps/L_SevarogArena`, and a unique run token. The smoke wrapper currently requires `status=APPROVED`, `result=PASS`, `accepted=true`, `map`, `run_token`, and SHA-256 values for `runner`, `driver`, `retarget_cpp`, and `moves_cpp`; the emitted receipt must echo the token, map, all four hashes, criteria, and verified CVar readback.
2. Confirm Unreal Editor is closed and both `ENGINE_LOCK.json` paths are absent. Acquire both atomically with one token, verify the complete lock identity, then recheck the Editor and all bound hashes.
3. Run only after those gates pass. Do not change the map, player defaults, assets, or config. Close the owned Editor gracefully; do not force-kill it.
4. Release only locks matching the exact owner token after confirming no Editor process remains. If an Editor remains alive, retain the locks and request explicit recovery. Validate the resulting receipt only after cleanup and config-integrity checks.

## Audit findings

The first A-1099 wrapper revision now declares both C-1155 lock paths, refuses pre-existing lock files, creates each lock through a temporary file and atomic move, checks owner token/policy, rechecks Editor state after lock acquisition, rechecks four hashes, and attempts graceful shutdown/owned-token release. Its file hash matches the reported value `EBABA8514B2667DC58207761EA3BB122EA7507A760EDE61623E64A810155BE4E`.

The A-1100 revision matches the reported hash `B7E551BEBBD90F86C4C071EEBD15562B1D6B6B63CE62AD2A1545E9BA689482A3` and corrects both initial findings: lock acquisition/pre-run setup now sits inside `try/finally`, and readback checks token, policy, party, agent, task, and command ID. A-1101 moved config integrity verification ahead of lock release and retains locks on mismatch. A-1102 then replaced terminating errors in cleanup with warnings/failure collection, traps config hash-read errors, and clears environment variables before surfacing cleanup failures. Its reported hash `D485ED22A78DD84DE6F22941294D6D7C5208585CB9343A75B1BCB7DB6AEE5887` matches the workspace. Lead source review confirmed the cleanup gates, all requested C-1155 lock identity fields, and PowerShell parser reports zero syntax errors. BT-79 source implementation is accepted; this does not authorize runtime execution.

The existing route runner uses the same two lock paths and a broad `try/finally`, verifies approval-bound runtime hashes before and after acquiring locks, backs up config byte-for-byte before temporary modification, and retains locks/config when recovery is unsafe. Its current lock readback itself checks only owner token/policy; BT-79's requested complete identity check is an explicit hardening requirement from the lead review.

## State

BT-79 and BT-82 source reviews are complete. BT-84 source-hash preflight is now active with Antigravity. BT-83 runtime smoke remains blocked until a fresh source-hash-bound C-1155 approval is supplied; no approval receipt was created and no runtime operation was performed.
