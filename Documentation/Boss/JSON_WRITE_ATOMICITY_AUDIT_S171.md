# JSON write atomicity audit (S171)

Static review of JSON/manifests/profile-related outputs in `Scripts/Tools`, with changes to prevent a failed serialization or publish from truncating an existing valid tool output. A failure-injection fixture was added but not run. No Unreal Editor/build/runtime was used.

## Changes

- `Scripts/Tools/atomic_io.py:16-35` serializes complete bytes to a temporary sibling, flushes and `fsync`s the file, then uses same-directory `os.replace`; an error before publish cleans the temp and leaves the old target intact.
- `atomic_io.py:38-74` provides atomic create helpers using a temporary sibling plus `os.link`, which publishes complete content and fails if the destination already exists. The copy helper likewise copies to a temp before linking it into place.
- `evidence_pack.py:63,66-68` now atomically copies evidence and atomically creates the hash list and JSON manifest. Existing output refusal remains; the manifest is published last as the bundle commit marker.
- `token_coverage.py:69`, `evidence_summary.py:83`, and `make_source_manifest.py:23` now serialize before atomic replacement, so interruption does not expose a partial replacement.
- `new_rule_scaffold.py:69` atomically creates each new scaffold file and refuses an existing destination.
- `profile_dump.py:24-31` is read-only; no profile JSON writer was found in `Scripts/Tools`.
- `test_atomic_io_s171.py:15-37` injects an `os.replace` failure and checks preservation of an existing manifest and cleanup of the temp, then checks that atomic-create will not replace an existing valid file. The fixture was not run.

## Remaining JSON writers outside the offline tools

The repository-wide static scan also found one-off or editor-side writes outside `Scripts/Tools`: `Scripts/CollectBalanceRuns.py:87-88` writes a run record with mode `w`; `Scripts/Editor/move_grey_abps.py:24`, `resolve_retarget_map.py:64`, and `retarget_pack_to_greystone.py:92` rewrite `Saved/greystone_retarget_map.json`; `survey_pack_anims.py:16` rewrites `Saved/pack_anim_survey.json`; and `inspect_assets.py:189-190` opens its report destination in `w`. These are not the offline tool manifest/profile outputs changed here, and remain candidates for a separate editor-artifact atomic-save pass. `pie_build_fight.py:1415-1416` uses exclusive mode `x`, so it refuses an existing run JSON instead of replacing it, though an interrupted first write may leave an incomplete new file.

## Disposition

The offline tool manifests and reports that replace existing destinations now publish complete content atomically; evidence bundles and new scaffolds keep no-overwrite behavior. The separate Editor/run JSON artifacts listed above remain outside this change. No tests/build/Editor/runtime were run; Lead should run `test_atomic_io_s171.py` before accepting the failure behavior.
