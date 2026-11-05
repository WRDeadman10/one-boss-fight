# Anti-cheese proof expectations (S119)

## What the retained PHS005 run actually configures

`B_PHS005/create_anticheese_content.py` authors the selector band as 110–140 cm, `AntiCheeseKiteRangeCm=150`, streak 2, two cards at base weight 1, and a Kite multiplier of 2 only for `Move_Sevarog_HeavySlam_F7`. It does not set a hug threshold or a non-neutral Hug multiplier. This is a kite-only witness; it cannot establish hug behavior.

The logic counts the current decision in the streak (`RPGFrameworkBossCharacter.cpp:451–452`); the state token is emitted only when the streak gate is met (`:459`). With threshold 150 and streak 2:

- Kite negative/control: obtain two consecutive decision snapshots with range <150 cm; neither may emit `anticheese state=Kiting`.
- Kite positive: obtain two consecutive snapshots at range >=150 cm. The first is streak 1 and must not emit Kiting; the second must emit `state=Kiting streak=2`, with its logged range and threshold, before candidate scores for that decision.
- Reset control: one subsequent decision below 150 cm clears the kite streak; a later single decision >=150 cm must remain streak 1 and not emit Kiting.

The retained `pie_kite/editor_raw.log` shows the transition and response: sequence 2 has scores SwingSlow 0.915334 / HeavySlam 0.739259; sequence 3 logs Kiting streak 2 at 158.467 cm against 150, then scores 0.915334 / 1.47852, selecting HeavySlam. This is an unambiguous selected-card crossover on the observed snapshot. Because the state changes between sequence 2 and 3, it is not a strict same-snapshot multiplier isolation. A stronger A/B keeps the exact range, cooldown/repeat history, card set, and seed fixed, with the gate off vs on; require identical base traces except the configured pattern factor and a changed winner.

## Hug proof still needed

Keep the existing band and cards, author a fresh profile with kite disabled and `AntiCheeseHugRangeCm=100`, streak 2. Set SwingSlow Hug multiplier 2 and HeavySlam Hug multiplier 1 (all base weights 1); keep both Kite multipliers 1. The hug control uses two consecutive decisions >100 cm and must remain neutral. The positive uses two consecutive decisions <=100 cm; only the second logs Hugging streak 2. At an identical fixed selector snapshot, unweighted scores must be computed from each card's range factor, then the Hug multiplier applied; record both traces and selected card. A second run one centimeter above the threshold checks the strict negative boundary. Keep kite/hug thresholds separated if both are enabled (`RPGBossFrameworkProfile.cpp:101–102`).

## Score comparison contract

`RPGBossMoveSelector.cpp:63–66` multiplies base card weight, range factor, repeat factor, and applicable pattern multipliers; kite and hug factors are applied only when their state is active. With no tie band, highest score wins and ties retain the earlier candidate (`:66–67`). Record every eligible candidate's score from the same decision sequence; a cross-sequence comparison alone does not isolate the multiplier. Do not label the current retained kite run as a hug witness or as a fully controlled A/B.

Source and evidence reviewed: `RPGFrameworkBossCharacter.cpp:451–459,521`, `RPGBossFrameworkProfile.h:167–170`, `RPGBossFrameworkProfile.cpp:98–103`, `RPGBossMoveSelector.cpp:63–67`, `B_PHS005/create_anticheese_content.py:102–116`, and `B_PHS005/pie_kite/editor_raw.log` sequences 2–4. Source/evidence review only; no run performed.

## Setup
## Control
## PASS
## FAIL
