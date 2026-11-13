# BN-31..35: manual check of the heuristic-O KIs (lane BN, batch 7 of 10, per X-2213)

C (implementer), 2026-11-12. The lead's KI-067 reclassification to O (in the BN-26..30 report) is carried forward, so the running total entering this batch is 2.

**Not done:** no code, asset, engine, build, PIE or test work. No KNOWN_ISSUES status changes and no commits.

| Task | KI | Row | Evidence checked | Manual class | Offline follow-up? |
|---|---|---|---|---|---|
| BN-31 | KI-078 | `KNOWN_ISSUES.md:145`: camera shake, hit stop, slow motion and the music swap are proven in logic (`LEG-01`) but never felt or heard (`-nosound`); each music loop dips to silence for about 3 s; Phase 2 starts with a quiet intro of about 37 s | Tuning needs the `LEG-02` hand test. Trimming the tails is offline audio work, but the row makes it conditional ("if the dip is unwanted"), which is a feel decision | **E** (hand test) + D (whether to trim) | No: the trim is conditional on a listening decision |
| BN-32 | KI-079 | `:146`: the music assets are 19.2 MB and 36.7 MB (LFS) because the Phase 1 OGG import returned nothing. The action is to import the OGG "if the size matters" | Optional, and a re-import is an Editor asset operation | **L** (accepted size) + E (re-import) | No |
| BN-33 | KI-080 | `:147`: two pack textures are missing on the second machine, and some pack material shader compiles fail; the cause was not checked | Machine-specific. The fix is a file copy from the first machine plus an Editor shader recheck; the pack is git-ignored with 92 local edits | **E** (second-machine environment + Editor) | No |
| BN-34 | KI-087 | `:154`: the death clip pelvis is 17 cm higher than idle; the kneel holds for about 1.4 s before the pack destroys the boss; `PackMontage` mode of `URPGBossDeath` does not work and is unused. "Open (cosmetic)" | The visual parts need the LEG hand test. Removing the dead `PackMontage` mode would be a code cleanup, but it changes production source and needs a build, so it is a lead decision. **Not proposed as O** | **E** (visual) + L (cosmetic) | No (a mode cleanup would be a code change needing a build) |
| BN-35 | KI-103 | `:164`: `pie_legend` L1 failed 4/5 once and passed 22/22 in reruns; same family as KI-101. The action is "Watch; no change" | Intermittent PIE timing | **E** (intermittent PIE) + L (watch) | No |

**Batch 7 result:** 0 new O. Running total: 2 O (KI-026, KI-067) out of 34.

**Limits:** row reads only. `URPGBossDeath` was not re-read to confirm the `PackMontage` mode is still unused.
