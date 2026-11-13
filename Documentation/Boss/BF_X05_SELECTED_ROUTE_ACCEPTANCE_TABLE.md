# BF-X05 selected-route acceptance predicates

This is the machine-checkable form of the lead acceptance sheet in `BF_X01_X05_FRAMEWORK_ROUTE_SUPPORT.md`. It defines a receipt gate only; it cannot establish that the receipt came from a live run. Every accepted row must cite a raw log excerpt in `evidence` and retain the corresponding raw log.

| Row | Required predicate |
|---|---|
| ID-01 | One build ID and map identity are shared by both arms; each arm has a distinct world and route flag. |
| PACK-01 | Default-off arm selects one pack boss, no framework boss or framework binding, with selector flag false. |
| FW-01 | Opt-in arm isolates/destroys the pack boss before the transient framework spawn, then sets `rpg.FrameworkEncounterSelection=1` and selects the same definition path; deferred activation succeeds with exactly one framework boss and no pack boss. Definition SHA-256 is present and read back. |
| PART-01 | Framework boss/player occupy distinct binding participant slots and share one positive generation. |
| HUD-01 | Native health max is positive; current is bounded; HUD owner matches the boss identity and its displayed fraction matches native current/max. |
| TERM-01 | One terminal callback comes from the selected boss at the binding generation; completion and victory count are exactly one. |
| RETRY-01 | Retry is visible after completion; measured delay is finite/nonnegative and matches configured delay within 0.05 s. |
| RESET-01 | Exactly one reset/rebind advances generation; callback from the prior generation is refused. |
| REPLACE-01 | Callback from a different replacement actor is refused. |

`Scripts/Tools/verify_bf_x05_selected_route.py` checks these predicates from a versioned JSON transcription of Lead evidence. It does not infer values from prose, create evidence, or mark a row PASS when a cited excerpt is missing. Synthetic contracts test the verifier; live acceptance remains Lead-owned.
