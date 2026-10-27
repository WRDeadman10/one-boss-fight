# 2b legacy extraction: diff delivery for Codex review (source edit only, NOT built, NOT run)

Order: X-237 / `Codex/ALL83_IMPLEMENTATION_RESTART_2026-10-27.md`. Claim: C-184. Files: `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp` and `.h` only.

## Hashes

| file | preimage (pinned, = HEAD, clean) | new |
|---|---|---|
| cpp | `1b036b03aec269e5b3e906d8adaedac709c33f6a3c15413d0454b9c354523712` (283 lines) | `17bc29c9d9e033de98cf9956c8d0d8e8bd2f7516a80295d96b4c2ff7ef822834` (297 lines, 12416 bytes, CRLF) |
| h | `ab75575c7fcde9e18e7be75f42676f6a0ad0fecfd7bcc32d438cac86c1a9cd02` (33 lines) | `8bc1a655f4e529b2dc4d1e96c098dc2c6c0ec5902529767298f31ac965c97d06` (35 lines, 1403 bytes, CRLF) |

Evidence beside this file: `preimages/` (both preimages, sha256 list, HEAD, source git status), `2b_legacy_extraction.diff` (git diff of the two files), `2b_block_mapping.txt` (mechanical mapping output), `2b_lexical_witness_candidate.txt` (Codex lexical helper, candidate mode). The edit was applied by a script that asserts every anchor line of the preimage first (`scratchpad/apply_2b.py`; two anchor assertions failed on my first attempt because I mis-stated an indentation depth, nothing was written then).

## What changed (the whole change)

`Attach` is split at the one place where the original has a hybrid-sensitive boundary. Nothing else moved.

1. New private const `AttachLegacyBossPrelude(AActor*)`: the body of the original `else if (IsPackBoss(Pawn)) { ... }` (boss `AddFootsteps(Pawn, true)` and the whole music block), moved verbatim, dedented one tab.
2. New private const `AttachLegacyBossBundle(AActor*)`: the original statements 195..282 (all 19 boss registrations Stagger..Legend), moved verbatim, **every `IsPackBoss(Pawn) &&` guard kept per statement, none merged into one outer `if`**.
3. `Attach` keeps: signature, the player branch (`if (IsPackPlayer) AddFootsteps(false)`), the `else if (IsPackBoss(Pawn))` test, and all nine player registrations in place and unchanged. The else-if body is now `AttachLegacyBossPrelude(Pawn);` and the function ends with an unconditional `AttachLegacyBossBundle(Pawn);`.
4. Header: two private declarations beside `Attach`. Nothing public changed.

Not touched: `IsPackPlayer`, `IsPackBoss` (class-name ABI walk), `AddFootsteps`, `StepSound`, the music/footstep defaults and paths, `PostInitialize`/`OnActorSpawned`/`OnWorldBeginPlay`/`Deinitialize`, includes. No coordinator, lookup, adapter, data, balance, config, content, driver or pack change.

## Original-to-new mapping (`2b_block_mapping.txt`, every block found exactly once, byte-equal)

| old lines | new lines | content | change |
|---|---|---|---|
| 1..136 | 1..136 | includes, subsystem lifecycle, `IsPackPlayer`/`IsPackBoss`, anon namespace with `AddFootsteps` | none |
| 137..144 | 251..258 | `Attach` signature, player footsteps branch, `else if (IsPackBoss(Pawn))` + `{` | none (position only) |
| 145..158 | 141..154 | boss `AddFootsteps(true)` + music block | **dedent one tab, now inside `AttachLegacyBossPrelude`** |
| 159..160 | 260..261 | else-if `}` + blank | none; new line 259 (the call) sits between 258 and 260 |
| 161..194 | 262..295 | nine `IsPackPlayer && !Find...` registrations | none |
| 195..282 | 161..248 | 19 boss registrations | **moved verbatim into `AttachLegacyBossBundle`** |
| 283 | 297 | `Attach` `}` | none; new line 296 (the call) before it |

Complete list of new lines with no original counterpart (14): the two function frames (signature + `{` + `}` for each = 6 lines), 2 blank separator lines, 4 comment lines above the frames, `AttachLegacyBossPrelude(Pawn);` (new 259), `AttachLegacyBossBundle(Pawn); // ...` (new 296). All 283 original lines are accounted for, 0 deleted, 0 altered besides the documented dedent.

## Guard / default / trigger mapping

| property | original | new | preserved by |
|---|---|---|---|
| exact `IsPackPlayer` checks | 1 branch test + 9 per-statement | same 10 | untouched text |
| exact `IsPackBoss` checks | 1 else-if test + per-statement (Stagger..Legend, the Death `if (IsPackBoss)` block, the resolver/guard/audit block) | same | else-if test untouched in `Attach`; bundle per-statement guards verbatim |
| plain boss: footsteps, music first | prelude inside else-if, before the player section | prelude called from the same else-if, before the player section | call at the same position |
| hybrid class (player AND boss): boss footsteps/music NOT added | else-if skipped because the player branch wins | else-if skipped, prelude not called | prelude only reachable from the else-if |
| hybrid: player components then boss bundle | player 9 statements, then boss bundle | same order | bundle call is the last statement of `Attach` |
| Death before Look, Legend last | order inside the 19 | same, same relative order | block moved verbatim |
| defaults (music paths, fallback + warning, PhaseTwo `LOAD_NoWarn`, boss footstep pitch/volume/range/speeds) | inline | same text | verbatim |
| triggers: spawn handler and world-begin loop both call `Attach` | `OnActorSpawned`, `OnWorldBeginPlay` | untouched | lines 1..136 byte-equal |
| idempotence of a second `Attach` | each registration guarded by `!FindComponentByClass` (resolver `FindOrAdd`, `URPGBossDeath::Attach` as before) | same statements, same guards | verbatim |
| null Pawn | both class tests false, nothing dereferenced | prelude/bundle: prelude unreachable, bundle guards short-circuit before any `Pawn->` use | guards kept per statement |

The extra helper boundary adds no behavior: the helpers are private const members called once each, with no new state, no new includes and no new virtual or UFUNCTION surface (no UHT-visible change besides two plain private declarations in a UCLASS body).

## Reviewed counterexamples (AG17 / X221)

The two known lexical false accepts are a changed music default and a duplicated spawn `Attach` call. Neither is present here: the music block and every default are byte-equal after the dedent (`2b_block_mapping.txt` shows the prelude body block found with dedent 1 and nothing else), and lines 1..136 including both trigger sites are byte-equal.

## Lexical witness (do not read as acceptance)

`node legacy_attach_witness.mjs --candidate <new cpp>` (read-only; baseline not touched, not regenerated): exit **1**, `orderMatches: false`, `bossEvents: 19`, `sourceHashUnchanged: false`, `triggerTokensUnchanged: true`, 11/11 self tests. Reason, as expected: the baseline lists 21 ordered events (footsteps + music + the 19) and the helper only understands a single `AttachLegacyBossBundle`; my split moves the first two into the prelude. The helper cannot express a split, so it neither proves nor disproves the order here. The proof offered is the byte-level block mapping above plus a planned runtime witness. I did not edit the baseline or the helper.

## NOT done / NOT claimed

Not built, not UHT-checked, no automation, no PIE, no component-order/idempotence runtime witness (all wait for diff acceptance per X-237). Nothing claims compile success. Only my own mechanical comparison supports equivalence; the compile and a runtime witness for both attach triggers are still to be proved.

## Proposed runtime witness after acceptance (for Codex to confirm or change)

Existing scope only: UHT/build, `Automation RunTests OneBossFight` (expect 45), and one planned component-order/idempotence check that records the registered component class order on the boss and player pawn after the spawn trigger and after the world-begin trigger and then forces a second `Attach` equivalent, comparing against the pre-change order captured from the existing 21-step baseline (+ player order). If that needs a new test helper or driver, I will post that as a concrete delta first.
