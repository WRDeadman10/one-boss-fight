# BQ-11..15: Queue BQ batch 3, Greystone and player input

C (implementer), 2026-11-13. Queue: `QUEUE_BQ.md`.

**All C++ is written but NOT compiled or run.** Binary acceptance needs the Lead's C-1155 build and suite. No engine, editor, PIE, tool run, asset change or commit.

| Task | Result | Files |
|---|---|---|
| **BQ-11** montage notify-track C++ helper | **reconciled, already delivered.** C-1275a added the editor-only C++ montage notify rows (class, trigger, duration, track, slot, segment), and commit `f97994a7` (C-1275a with C-1280..C-1282) authored the four `_Fit_Greystone` wrappers (BUILD-297, 506/506). No new code | none |
| **BQ-12** editor script plan using the helper | **reconciled, already delivered** by the same C-1275a/C-1282 work. The remaining wrapper gates (notify readback and save validation in the editor, B5) stay ENG | none |
| **BQ-13** KI-085 latched input after the riposte | **accepted at source-review level** (X-2334; AG A-957). Opt-in `URPGBossStagger::bFlushInputAfterRiposte` (default **off**) and the pure seam `ShouldFlushInputOnRestore`; it calls `APlayerController::FlushPressedKeys` after `EnableInput`, only when the boss and player are both alive. Test `OneBossFight.Riposte.InputFlushOnRestore` | `Player/RPGBossStagger.h/.cpp`, `Tests/RPGRiposteInputFlushTests.cpp` (new) |
| **BQ-14** KI-059 dodge characterization | **accepted at source-review level** (X-2335; AG A-958). The two C++ dodge decisions are extracted verbatim into pure seams `IsNoDirectionInput` (strict `<`) and `IsDoubleTapLongRoll` (inclusive `<=`); behaviour unchanged. Test `OneBossFight.Dodge.DecisionSeams` | `Player/RPGDodgeTiming.h/.cpp`, `Tests/RPGDodgeDecisionTests.cpp` (new) |
| **BQ-15** | this report | |

## What this native coverage does NOT verify (X-2335)

- **KI-059: double stamina payment and the quick-to-full roll restart are pack-Blueprint behaviours.** They live in the pack's dodge gameplay ability, not in this C++. They remain **ENG-gated and unverified**. BQ-14 only characterizes the two decisions URPGDodgeTiming makes in C++.
- **KI-085:** the live latched-key reproduction (a driver holding sprint through an execution) and turning `bFlushInputAfterRiposte` on are ENG and design decisions.

## Gates still open

1. **The Lead's C-1155 build plus suite** for `Riposte.InputFlushOnRestore` and `Dodge.DecisionSeams`.
2. **PIE:** KI-085 latched keys; the KI-059 stamina payment and restart.
3. **Wrapper notify readback and save validation (B5):** ENG.

**Earlier uncommitted edits** in `RPGBossStagger.h/.cpp` and `RPGDodgeTiming.h` were preserved; my edits were insertions or in-place calls to the seams only.
