# A7-B residual risk register

Snapshot based on C-876, C-878, C-872, P15, and the Queue S handover. This register tracks remaining release evidence; it does not change the owner's delayed-retirement decision (A7-B). Legacy remains the safe fallback until the relevant gates close.

| Risk / gate | Known evidence | Remaining gap | Release consequence / next evidence |
|---|---|---|---|
| Selected-route performance on target hardware | Round 4 kit and owner prompt prepared; kit dependency patch supplied after the first run failure (C-885); owner approved RTX 3060 as an RTX 2060 Super stand-in (`BENCHKIT_README.md`) | Comparable packaged 1920×1080 legacy/data measurements on the approved physical GPU, including averages and p99 frame time, are not recorded here | Keep performance gate open until retained runs meet average >=60 FPS, p99 <=16.67 ms, and selected p99 <= legacy +0.5 ms with comparable setup; use S41 report template |
| Shipping selector proof | J049 policy A approved; selected route has no current caller, so legacy startup remains the default (C-876) | First-caller packaged proof and opt-in selected-route smoke evidence | Do not retire legacy; capture selector startup, chosen definition, and fallback behavior in owner package evidence |
| Cook and content compatibility | Three G044 roots are present in the Lead's cooked-tree census; 78 of 156 uncooked closure entries were classified editor-only skeleton references (C-878) | Authoritative cook manifest for the owner package and save/content compatibility evidence for the selected route | Keep cook gate open until the package's manifest is checked against the reviewed allowlist and the supported content version |
| Missing/invalid definition recovery | G2 refusal driver passes 13/13 checks; it requests screenshots for both refusals | Owner visual confirmation and packaged recovery behavior | Keep recovery gate open until refusal text is visible and a package run demonstrates fail-closed behavior without legacy component activation |
| Player definition feature leaves | D5 audit: 214/424 MATCH, 0 mismatch, 210 player leaves NOT-COMPARABLE because the player role receives no BossCore plan | Role/schema policy or explicit acceptance of those leaves as out of scope | Do not call NOT-COMPARABLE a match; retain the limitation in any parity or release report |
| Full gate after recent changes | BUILD-222 is 463/463 and the A5 parity matrix is 31/31 under its accepted comparator rules | Fresh owner package run after current packaging and selector state | Keep build/test completion separate from packaged play-test and release readiness |

## Exit rule

Close each row only with its named evidence and Lead/owner disposition. A5 parity or a green automation suite alone does not close packaged performance, first-caller, cook compatibility, or visual recovery gates.
