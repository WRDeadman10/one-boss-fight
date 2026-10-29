# DD17 follow-up to C245 (Codex Codex/C245_RETAINED_MEMBER_IDENTITY_FOLLOWUP.md): retained member identity. SOURCE ONLY (Claude, 2026-10-28)

Nothing was built, no UHT, no automation, no engine process, no git operation. Only `Player/RPGBossWorldInputCompiler.cpp` changed; the header and the tests file are byte-identical to the bytes delivered in C-245 (`cmp` equal).

## Preserved
`Review/RPGBossWorldInputCompiler.h.delivered_C245` (343d74db...), `Review/RPGBossWorldInputCompiler.cpp.delivered_C245` (9451d166...), `Review/RPGBossWorldInputCompilerTests.cpp.delivered_C245` (c6062437...). The earlier `*.reviewed_by_codex_X284` and `*.before_independent_review` states are kept as well.

## New bytes
- `Player/RPGBossWorldInputCompiler.cpp` 618 lines sha256 `1a99ba054dc606c6514973e6423723bd3a3701ce40ea8c87f2c432d30e457f58` (was 9451d166...); CRLF, 0 bare LF/CR.
- header `343d74db59c3f8fa6f28a16fbeb7bf58fab4193580c25fea4960b77d67141c0e` and tests `c606437268c80824cec95a376b999a8f903421035dd1919f4cfac4c7df8f7f02` unchanged.
Exact delta `revision_C245_followup_cpp.diff` (37 lines) sha256 `37833802f2e6c93781d5437e6823717e7aa47628a9a7b5469973ae24b7331437`; full three-file diff `three_file_c245_followup.diff` `3246d42bae7fb1e447cd14544c932d5648b91e355e7b5fffbfdb55c177fc5d19`. DD17-era manifest (185 files): `manifest_c245_followup_diff.txt` is exactly one removed and one added line (the cpp); 24/24 pins and 14/14 candidates OK; HEAD 79d55906 and both binaries unchanged (the full tree is 191 files now that the DD18 files exist; DD18 files are untouched).

## The change (two spots in the cpp)
1. `Checkpoint`: the member loop no longer calls `ActorProblems` on the saved RAW `FMember::Actor`. For each member it first bounds-checks `Snapshot.IsValidIndex(Member.Index)`, resolves the retained WEAK `Snapshot[Member.Index].Actor` and `.Definition`, requires both non-null and EXACTLY equal to the member's original identities (a cleared, collected or replaced actor or definition is `WorldInput.BindingDrift`), and only then calls `ActorProblems` on the RESOLVED actor (valid, not destroying, in the world, not begun). The saved raw pointers are not dereferenced before that.
2. The candidate request takes the retained weak actor (`Request.Actor = Snapshot[Member.Index].Actor`) instead of re-wrapping the raw pointer, so candidate actor reuse happens only after the check above.
Ordinary foreign/destroyed/begun diagnostics and every existing test are unchanged (the initial validation still uses `ActorProblems` with the same messages); the tests file did not change. A mid-load clearing of a weak identity cannot be provoked without a callback, cvar or injection framework: this is a source-confirmed safety gap closed in source, not a reproduced runtime crash, and stays source-only qualified.

## Open
Not compiled, not run. Every limit of `17_DELIVERY.md` and `17_REVISION_X284.md` still applies. The reconstructed pre-change manifest slip of DD17 stays on record. Nothing committed.
