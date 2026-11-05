# Yaw-probe A/B setup audit

## R5 primary pair

- The control loads `/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF5` and the hysteresis arm loads `/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofYawConeR5`; both set `rpg.BossProofYawProbe 5` (`B_YAW_CONE/pie_control/editor_raw.log:1387–1389`; `pie_hysteresis/editor_raw.log:1387–1389`). The control profile is the F5 source; the second arm uses the duplicate R5 profile.
- `make_yaw_cone_profile.py:5–8,11–13` declares distinct source/destination profile and map names and refuses to overwrite either destination. Lines 14–22 duplicate the F5 profile, set only `cone_hysteresis_degrees=6.0`, read back that field, and save. Lines 24–32 attach that profile to the single proof fixture and save to the explicit R5 map destination.
- The log confirms saved asset/map identities: `content_run1/editor_raw.log:1248,1275–1278`; the later PIE run logs the exact R5 map path. Source-state snapshots under `pie_hysteresis` are byte-identical pre/post (same row count/hash), so the run did not mutate source content.
- Limitation: the authoring script verifies the in-memory field before saving; it does not reload the saved profile and compare all inherited selector properties against F5. The checked source assignment surface is one profile field plus the map fixture reference, but serialized field-by-field equivalence is not directly evidenced.

## R6A8 extended sample run

`make_yaw_cone_long_profile.py:14–22` sets both `cone_hysteresis_degrees=6.0` and `attack_count=8`, then saves a separate R6A8 map. That is suitable as an extended sample-count diagnostic, but it is not a strict one-setting A/B against the base F5 profile. `pie_long_hysteresis_run2_fixed/editor_raw.log:1386–1388` confirms the explicit R6A8 map path and probe value. Keep R6A8 findings separate from the primary R5 hysteresis comparison.
