# Opt-in parry sound layer expected sheet (Queue D156)

Status: protocol only. No sound is selected, authored, replaced, or enabled here. Review this protocol and default-off behavior before implementation. Live Editor/packaged audio verification remains Lead-owned; sound asset and mix choices require their normal review.

## Claim and sound boundary

The proposed optional sound layer adds a distinct cue after an accepted parry while preserving existing pack sounds. It must not play on a parry press alone, a missed/failed parry, or unrelated hit. It must not change combat timing, input, grade, damage, stamina, posture, recovery, or existing sound events. Do not replace, mute, or edit pack sound assets. `URPGPlayerParry::NotifyParried` records the grade on accepted notification (`RPGPlayerParry.cpp:138-145`), but that does not establish the current authored audio graph or prove a playable cue exists.

No clip, volume, pitch, spatialization, mixing priority, cooldown, or grade-specific sound mapping is selected here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, raw logs/audio/screens and hashes | **Expected:** unique run IDs; preserve source recordings and hash after capture. **Observed:** pending. |
| Build/map/actors | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, actual player/controller and boss identities. **Observed:** pending. |
| Existing pack audio | **Expected:** identify relevant pack sound events/assets and record their enabled state and playback in baseline. **Observed:** pending; asset graph is not established by this sheet. |
| Feature state | **Expected:** new layer toggle read back off by default, enabled only in paired run; record exact hook/config. **Observed:** pending. |
| Audio capture | **Expected:** fixed output device, volume, sample rate and capture route; record these settings and prevent unrelated audio from masking the cue. **Observed:** pending. |

## Paired cases

Repeat from matching encounter state, input timing, attack/profile identity and seed. Change only the reviewed new-layer toggle.

| Row | Required evidence | Pass condition |
|---|---|---|
| Default-off accepted parry | Real accepted parry; capture gameplay result and existing pack sounds with feature read back off. | Establishes baseline existing audio; no new layer cue is heard. |
| Enabled accepted parry | Repeat the same accepted parry with the optional layer enabled. Capture output audio and event timing, and identify pack and new-layer cues separately where possible. | New cue occurs once at the reviewed accepted-parry event; existing pack sounds remain intact and are not replaced/suppressed. Combat state/outcome matches baseline. |
| Negative no-parry control | Perform a press without accepted contact and a real non-parried contact, with the layer enabled and off. Capture outcomes and audio. | New parry cue is absent from both negative outcomes. Existing pack sounds follow their ordinary behavior unchanged. |
| Repeated event / cleanup | Where safe, exercise repeated callbacks or rapid distinct accepted parries and teardown/reset. | No duplicate playback from one accepted event and no stale sound after reset/end; cadence policy must be reviewed before judging rapid distinct events. |

## Evidence interpretation and limits

- **Measured:** source-tokenized accepted/refused outcome and timing with raw line references; captured audio file, device/settings and event markers; asset/event identity where inspected.
- **Inferred:** cue-to-event attribution only when a distinct source/event marker or controlled recording supports it. Perceived loudness alone does not prove which sound fired.
- **Manual:** audibility, mix balance, masking, localization and whether pack sounds remain recognizable; document reviewer and conditions.
- A source log alone cannot prove audible output, the loaded asset, or absence of replacement. Do not claim asset identity without loaded asset/runtime evidence.

## Failure and stop conditions

Fail if the toggle defaults on, the cue plays without accepted parry, one accepted event triggers duplicates, pack sounds are replaced/suppressed, or combat/resource/timing state changes. Stop if no accepted-parry event can be distinguished, audio capture cannot separate events, or the feature needs unreviewed clip/mix/cooldown choices. Invalid setup or missing capture is inconclusive.

## Verification boundary

Expected protocol only. No audio selection, asset/source/UI changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before review.
