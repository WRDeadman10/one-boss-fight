# Role swap addendum to Codex/TEAM_PIPELINE.json (owner order 2026-10-29, lead Claude, post C-251/C-252)

TEAM_PIPELINE.json is NOT rewritten (Codex file, SHA-pinned in TEAM_PIPELINE_SHA256.txt). Read it with this mapping:
- Cards with `owner: Claude` (C00..C18) are now IMPLEMENTER cards owned by CODEX (source, tests, builds and automation on an exact lead release). Statuses, dependencies and acceptance text are unchanged; C00-C02 stay ACCEPTED_BOUNDED_X292.
- Cards with `owner: Antigravity` (A00..A20) are unchanged (content/offline; only committer on an exact approved batch). A00 (toolkit corrections, X-291) is the active card.
- The review/accept/orders/pipeline-maintenance lane that Codex held as lead (Codex/CURRENT_TASK.md, evidence tooling Codex/Mail693Evidence, C248Evidence, C250Evidence, XW00/XW02) passes to CLAUDE. Codex's evidence scripts stay where they are and may be used read-only by the lead.
- Every execution gate stays closed unless a lead work order releases it exactly: all `execution_released` / `git_released` are False.

## What each member was planned to do (read from X-288..X-293, CURRENT_TASK.md, TEAM_PIPELINE.json) and who does it now
| Planned item | Planned owner | Now |
|---|---|---|
| DD19 typed Bleed profile (X-293, source only, 5 files) | Claude | Source WRITTEN by Claude before the swap (not compiled); Codex takes over as implementer (C-251/1), lead reviews the final diff before any build |
| Frozen verification of DD17/DD18 | Claude | done and accepted (X-292) |
| Next implementer cards (C03 preview after A01/A02, C04 remaining consumers after A04) | Claude | Codex, only on a lead work order; none released yet |
| Independent review of A180 / the next AG revision, evidence capture, native-contract checks | Codex | Claude |
| Review of Codex's DD19 final diff, builds release, acceptance docs | Codex (as lead) | Claude |
| AG-CONTENT04 frozen toolkit revision (X-291) | Antigravity | unchanged; delivers to the lead (Claude) |
| Pipeline/status docs (CURRENT_TASK.md, milestone progress) | Codex | Claude, starting with this addendum |

## Remaining consumers with NO typed profile yet (candidate implementer queue, one package at a time after DD19 is accepted)
URPGBossCloseClipSwap (5 editable props), URPGBossLook (5), URPGBossLowSweep (8), URPGBossShockwave (8), URPGBossDeath (12), URPGBossHealPunish (14); plus the non-URPGBoss attack components if the lead names them. Source-confirmed by a property count of Player/RPGBoss*.h; a package's exact field list comes from its work order, not from this count.
