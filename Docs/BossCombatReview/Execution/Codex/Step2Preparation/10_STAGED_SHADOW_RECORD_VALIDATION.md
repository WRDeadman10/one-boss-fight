# Staged shadow-record schema hardening

2026-10-27 label-only follow-up / X178: dormant driver check now says “diagnostic record schema ... (not parity)” rather than “semantic JSON.” Function behavior unchanged;31/31 offline checks rerun/pass. New draft SHA c0af0dc6066b73bbbd248981244fc231d653cfc9fbd58cfde4c054958caad99c. Earlier6058... hash below belongs to X177 revision. AG07 deeper/nested identity findings remain under review; no full trace or engine proof.

## Current correction — producer wire contract,2026-10-26 / X177

The original24-check revision below contained a Codex-introduced compatibility error: it rejected all string ordinals, although actual staged RPGShadowCompare.cpp:145–146 deliberately serializes observation_ordinal and playback_ordinal as decimal strings because they are uint64. The original acceptance of observation_ordinal='1' was valid wire behavior, not a malformed-input defect. Earlier X175 wording and the original report below are superseded on this point. Tests using a synthetic integer ordinal incorrectly reinforced that assumption;24/24 did not establish producer compatibility.

Current draft accepts only canonical positive ASCII decimal-string observation ordinals up to uint64 maximum, compares after lossless Python int parsing, and rejects fractional/numeric/bool/whitespace/zero/overflow representations. Other count/time/generation/hash/JSON shape hardening remains. New independent valid cases cover9007199254740993 and18446744073709551615. The helper now statically inspects the actual C++ SetStringField/LexToString declaration and reports its source hash; this is source-wire agreement evidence, not execution of C++ JSON serialization or deep trace validation.

Actual rerun:31/31 offline assertions pass. Current driver SHA6058f72f8f73a40acd3364653e678d79e661a0376482977dad5459ccbfce25fe; producer SHAf6a0274c3bad8d5221981fa10dc529a284aa3285eb1220ba3e4f991a07363924. Nothing promoted or run in UE. Playback ordinal/nested semantic identity validation remains part of AG07 independent challenge, not silently claimed complete.

## Historical original24-check revision (superseded ordinal policy)

Codex,2026-10-26. Changed only Codex/Drafts/Scripts/Editor/pie_timeline_shadow.py and added offline shadow_record_validator_checks.py. The script remains an unpromoted step3 draft; no live Scripts/Source file, engine, PIE or gameplay change. All existing approval gates remain.

## Reproduction and correction

Extracted only the actual draft's validate_records function through Python AST; did not import Unreal or execute driver top-level callbacks. Four independently supplied malformed records were accepted before correction: current=True, observation_ordinal='1', observation_ordinal=1.9, generation=True. Python bool is an int subclass and int(...) silently converted the two ordinals.

Draft now requires exact integer count within its existing4096 record cap; exact integer positive increasing ordinals; exact uint32-positive generation; true numeric finite time/rate scalars excluding bool; object-shaped decoded JSON; and string hashes before regex. Malformed JSON rejects without escaping the schema function. Negative playback rate remains permitted as diagnostic input; reverse/inconclusive records are not relabeled MATCH by this change. No new gameplay/visual threshold introduced.

## Actual verification

`python -I Docs/BossCombatReview/Execution/Codex/Step2Preparation/shadow_record_validator_checks.py` passes **24/24 offline assertions** against the function extracted from the staged driver. Includes valid synthetic records, empty/invalid count, bool/NaN/infinity/null values, coerced ordinals, generation overflow, bad hash types, invalid status/action/containers, malformed/non-object JSON, repeated ordinal and valid newer reverse-inconclusive diagnostics.

Current draft SHA256:05c6f55c349dd242e605461e934cce597e140a51f8847400544032d9611200bc. First helper attempt failed to locate the draft because its root calculation used parents[6]; corrected to parents[5], then23/23 passed; after adding a malformed-JSON case24/24 passed. The first failure is not a UE failure and is retained here rather than described as an uninterrupted pass.

These are schema checks, not deep crossing/legacy-snapshot semantic validation, source-hash authenticity, identity association, natural attack coverage or observer off/on parity. Synthetic placeholder identities/hashes are intentional fixture data. Broader world/encounter/key correspondence and trace semantics still need independent review and real engine evidence. Existing promotion packets were not regenerated/applied; before any future promotion compare draft diff/hash and follow current lead approval.
