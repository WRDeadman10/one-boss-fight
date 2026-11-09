# AX-C16–C20 — KI-169–173 source and gate audit

Date: 2026-11-09. Read-only source inspection. No scripts executed, assets loaded/saved, tests run, or production code changed.

| Task | Finding | Evidence and limit |
|---|---|---|
| AX-C16 / KI-169 | The authoring script passes the literal `Damage Gampelay Effect` to `set_editor_property`; source inspection cannot establish whether the target Blueprint exposes that exact reflected property. | `Scripts/Editor/sevarog_pack_07_bolt_impact.py:32-35`. Retain the existing reflection/readback gate; do not correct by guess. |
| AX-C17 / KI-170 | The affected function docstring contains unusual Unicode separators in the source line already identified as the AST parse failure. | `Scripts/author_brief13_anims.py:140-142`. No parser or Unreal script was run; repair and parse-check remain prerequisites. |
| AX-C18 / KI-171 | The affected block has an over-indented save call immediately following an unindented compile call. | `Scripts/Editor/sevarog_pack_02_montages_abilities.py:212-216`. No script was run; parse repair and reflected property verification remain prerequisites. |
| AX-C19 / KI-172 | Native hit records are queued and scheduled for next-tick finalization without an encounter-generation field in `FPending`. Encounter reset advances participant generation and aborts stagger but has no `URPGHitIntake::ResetCounters` call; that method would clear `Pending`, but `rg` found no call site. | `RPGHitIntake.h:155-166`; `RPGHitIntake.cpp:461-478,509-518,522-527,683-695`; `RPGBossEncounter.cpp:347-365`. This confirms the source path only; stale post-reset application is explicitly unreproduced and the reset-order test is still required before any production change. |
| AX-C20 / KI-173 | Riposte queues `StartRiposteClips` with a next-tick UObject delegate and no retained request ID/generation or timer handle. Dispatch checks current `bRiposteRunning`, player/boss validity, and `Phase == Down`; `AbortStagger` resets the present state, but an old callback could observe later state that satisfies the guard. | `RPGBossStagger.cpp:567-584,825-840`; declarations `RPGBossStagger.h:244,250,287`. This remains a possible ordering hazard, not a reproduced defect; required reset/new-request ordering tests and intent remain open. |

No item was repaired or promoted to runtime-confirmed status. KI-169–171 retain their editor/script safety gates; KI-172–173 retain their reproduction-before-change gates.
