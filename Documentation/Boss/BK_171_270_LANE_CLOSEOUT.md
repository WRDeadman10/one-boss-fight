# BK-171..270: 100-task implementer lane closeout (20 batches of 5)

Written by C (implementer) for X-2116 task 270, 2026-11-12. The lane was set by Codex (lead): 20 batches of 5 tasks, one update after each batch, without waiting for AG review.

**How to read the review columns:**
- **Lead**: Codex's disposition, as recorded in `TASKS.md` and the X- posts.
- **AG**: Antigravity's independent read-only review (AG-Rnn, A- posts), only where one is recorded.
- "Queued" means the review was requested but its result is not cited in TASKS for that batch.

This is a reconciliation of existing records, not a new verification.

| # | Batch | Report | Source change | Lead | AG |
|---|---|---|---|---|---|
| 1 | BK-171..175 | `BK_171_175_RUNNER_STATUS_RECEIPT_V1_1.md` | proposal / validator only | accepted | see report |
| 2 | BK-176..180 | `BK_176_180_RUNNER_STATUS_RECEIPT_V1_2.md` | proposal / validator only | accepted | see report |
| 3 | BK-181..185 | `BK_181_185_C1155_FULL_INVENTORY.md` | none (audit) | accepted after correction | independent review |
| 4 | BK-186..190 | `BK_186_190_C1155_LOCK_SCOPE.md` | none (audit + hotfix tests) | accepted after X-2043 correction | AG-R31..R36 (A-849/A-850) |
| 5 | BK-191..195 | `BK_191_195_VALIDATOR_HOTFIXES.md` | validators (A-848 edges) | accepted | AG verified parity |
| 6 | BK-196..200 | `BK_196_200_PYTHON_LOCK_MUTATORS.md` | none (audit) | accepted | AG-R48..R50 (A-852) |
| 7 | BK-201..205 | `BK_201_205_LOCK_MUTATOR_REMEDIATION.md` | none (X-2052 test hotfix) | accepted | AG-R51..R53 |
| 8 | BK-206..210 | `BK_206_210_MUTATOR_FAILURE_PATHS.md` | none (audit) | accepted | AG-R61..R65 (A-855) |
| 9 | BK-211..215 | `BK_211_215_VERIFIER_STAGE_EVIDENCE.md` | verifier stage evidence | accepted | AG-R66..R70 (A-856) |
| 10 | BK-216..220 | `BK_216_220_EVIDENCE_MANIFEST_AUDIT.md` | `verify_evidence_manifest.py` (E1-E8; lead added `label`) | accepted | AG-R71..R75 (A-857) |
| 11 | BK-221..225 | `BK_216_220_EVIDENCE_MANIFEST_AUDIT.md` §BK-221..225 | `verify_evidence_manifest.py` (lead E1-E8 hotfixes) | accepted | AG-R76..R80 (A-858) |
| 12 | BK-226..230 | `BK_226_230_EVIDENCE_PACK_AUDIT.md` | none (audit, P1-P3) | accepted | AG-R81..R82 (A-859) |
| 13 | BK-231..235 | `BK_231_235_EVIDENCE_PACK_HOTFIX.md` | `evidence_pack.py` (**lead** patch) | lead-implemented | AG-R83..R85 (A-859) |
| 14 | BK-236..240 | `BK_236_240_ATOMIC_IO_AUDIT.md` | none (audit, T1-T3; AG found T4) | accepted | AG-R86..R90 |
| 15 | BK-241..245 | same report §241 | `atomic_io.py` T1-T4 (+ lead warnings-as-errors edge) | accepted | AG-R91..R95 |
| 16 | BK-246..250 | `BK_246_250_ATOMIC_IO_CALLERS.md` | none | accepted | AG-R96..R100 |
| 17 | BK-251..255 | `BK_251_255_ATOMIC_IO_PATHS.md` | `atomic_io.py` J1 (+ lead PermissionError edge) | accepted | AG-R101..R105 (A-863) |
| 18 | BK-256..260 | `BK_256_260_ATOMIC_IO_MULTIPROCESS.md` | none | accepted | AG-R106..R110 (A-864) |
| 19 | BK-261..265 | `BK_261_265_ATOMIC_IO_METADATA.md` | `atomic_io.py` M1 (+ lead warnings test) | accepted | AG-R111..R115 (A-865) |
| 20 | BK-266..270 | `BK_266_270_ATOMIC_IO_COPY_REFUSALS.md` + this file | none | lead accepted | AG-R116..R120 (A-866) |

**Out-of-lane work:** the BK-131..140 v2 hotfix and X-2058/2062/2064 validator notes were interleaved in the mailbox timeline but are not part of this BK-171..270 100-task count. Rows now map one-to-one to each five-task range; AG reviews of out-of-lane work are not included in the lane review count.

## Platform and host coverage (whole lane)

- **Host:** Windows 11, NTFS, Python 3.10, a single machine. **No POSIX run.** POSIX-only assertions (`0o600` mode, unlink of read-only files, rename never failing) are written but unverified.
- **Symlinks:** unavailable (WinError 1314, no privilege). Every symlink test **skips**. Junctions and hard links were exercised.
- **Host-dependent skip:** the BK-251 junction `O_EXCL` observation test skips on hosts where J1 does not reproduce (seen by AG).

## Standing limits (all batches)

- No production caller was executed. No real project output, lock, evidence pack, asset, Unreal, build or PIE was touched. All fixtures were OS temp directories.
- Faults were injected by patching unless a report says otherwise. Real-condition reproductions were J1 (junction), M1 (read-only source) and R1 (Windows replace contention).
- Commits: none by C. Antigravity commits on the owner's word.
- X-1991 (the owner's Sevarog stats decision) remains open throughout.

## Recorded limits and remaining follow-up

- **O5 (closed by lead disposition):** an injected failure to add write permission can leave a read-only orphan temp on Windows (BK-269c). This is accepted as best-effort cleanup: the failing `chmod` prevents making the temp deletable, while the original exception is preserved; no runtime change is warranted for an injected-only failure.
- **R1:** losers of a Windows concurrent replace get `PermissionError`; whether callers should retry is a policy decision.
- **BK-246 O1-O4:** caller-side wording and exit-code notes (non-blocking).
