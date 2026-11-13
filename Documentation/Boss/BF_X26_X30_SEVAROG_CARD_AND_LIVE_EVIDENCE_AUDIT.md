# Queue BF Batch 6 — Sevarog card and live evidence audit (X26–X30)

Date: 2026-11-11  
Status: source/documentation reconciliation complete; saved-asset and live acceptance remain Lead-owned. No raw run outputs were opened.

## X26 — approved S1/S2 ranges

`BE_X26_X30_S1_S2_RANGE.md` records C-1274's approval for exactly `Move_Sevarog_Swing1_Medium` and `Move_Sevarog_Swing2_Medium`: inclusive `MinRangeCm=90`, `MaxRangeCm=120`. The approved transient dry-run scope leaves other cards, S1/S2 timing, and active/recovery windows unchanged. Its reported C-1269 baseline is `0.703333 - 0.350337 - 0.000000 = 0.352996 s`, which exceeds the `0.300000 s` requirement by `0.052996 s`. This is the stated distance model (`max(0, 120 - 150) = 0 cm`), not proof of saved values or live S2 reach.

## X27 — phase pools and effect budgets

`C1280_X26_PHASE_ELIGIBILITY.md` and the C-1278 acceptance table agree on phase assignment: S1–S5 and S7 are eligible in Phase 1 and Phase 2; S6 and S8 are Phase 2 only. The profile uses `PhaseTwoFraction=0.6`, `PhaseTwoId=Phase_2`, and no duplicate `_P2` cards. Source validation totals direct damage plus enabled area and channel damage for profile budgets. C-1278's live table separately specifies S6's single 65-damage hit, S7's 35-damage area hit and 2.5-second snare, and S8's five 8-damage ticks with at most 4 healing per accepted tick. These are configured/acceptance values; live behavior is not inferred from source.

## X28 — ChannelDrain counterplay exemptions

The profile recovery walk-in exemption is limited to ChannelDrain-only cards with either a cone narrower than 180 degrees or fixed facing. `C1280` records the accepted S8 case as 45-degree half-angle and fixed facing (`trackFacing=0`); `C1278` requires the locked heading and allows escape by leaving that cone. A full-cone tracking channel remains subject to the recovery gate. This confirms the exemption predicate and the documented S8 design; no live escape result is claimed.

## X29 — Lead evidence inventory (mailbox/metadata only)

| Evidence item | Recorded reference/status | Scope limit |
|---|---|---|
| S1/S2 transient range validation | `BE_X26_X30_S1_S2_RANGE.md`; receipt `Docs/BossCombatReview/Execution/Codex/BE_X26_X30_S1_S2_RANGE/Run_20261110_182845/`; X-1871 | Build/dry-run/suite receipt as reported; no saved-asset or live reach proof |
| Phase/add-on source validation | `C1280_X26_PHASE_ELIGIBILITY.md`; receipt `Docs/BossCombatReview/Execution/Codex/C1280_X26_PHASE_ELIGIBILITY/Run_20261110_165108/` | Source/transient validation only; no PIE |
| Live acceptance definition | `C1278_X26_LIVE_CHECK_ACCEPTANCE_TABLE.md` | Acceptance criteria, not a result |
| Latest Lead verdict/status | Mailbox through A-791 and X-1888; no newer C-1286 verdict in inspected history | Raw run outputs intentionally not opened; saved asset and PIE status remain pending |

## X30 — refreshed S1–S8 live acceptance questions

Keep these as separate Lead observations; a transient validation or a candidate trace does not answer them:

1. **Reach/contact (S1/S2):** do saved rows contain only the approved 90–120 cm range, and does S2 make/resolve contact at the required live distances? Record actor/card, measured range, hit result, and source run/build identity.
2. **Phase selection (all cards):** above 60% HP, are S6/S8 refused as `MoveModel.Phase`; at/below 60%, is there one Phase 1→2 transition and a non-starved Phase 2 pool?
3. **S6 direct hit:** at 90–150 cm, does the continuous window produce exactly one 65-damage hit per activation, with no hit beyond 150 cm?
4. **S7 area/snare:** does release snapshot the target-ground point at 0.800 s, resolve no earlier than 1.550 s within radius plus target capsule, and apply/restore the 0.55 speed scale only after accepted damage and valid status?
5. **S8 cadence/counterplay/heal:** with locked 45-degree facing, do the five ticks occur at 0.467/0.667/0.867/1.067/1.267 s; do accepted ticks deal 8 and heal at most 4 each; do misses/out-of-cone ticks deal/heal zero?
6. **Recovery/interruption:** for S7/S8, do stagger, death, watchdog, leash, reset, and EndPlay stop later effects and restore any owned speed change? Record each tested interruption independently.

The authoritative per-row signatures and fail conditions remain in `C1278_X26_LIVE_CHECK_ACCEPTANCE_TABLE.md`. No new runtime evidence was created in this batch.

## Disposition

BF-X26 through BF-X30 are complete as a static/source and mailbox-metadata audit. No test, build, Editor, PIE, asset, commit, or push operation was performed. Live S1/S2 reach, S6/S7/S8 behavior, saved card readback, and Lead/Owner acceptance remain open.
