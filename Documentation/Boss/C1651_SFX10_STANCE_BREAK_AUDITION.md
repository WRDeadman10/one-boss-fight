# C-1651 SFX-10 Stance-Break Audition

**Status:** Candidate preview prepared; no cue selected or wired.
**Date:** 2026-11-18.

**Lead recheck (2026-11-18):** Confirmed the preview and README exist in `D:\FightVideo\SFX_audition\C1651_SFX10\` with the documented hashes; all three source WAVs also exist and match the documented SHA-256 hashes. The separate older `C1651_Batch1_SFX10` WAV/MP3 reel is preserved and is not the preview linked here. This completes BT-109's candidate-preparation scope; Owner selection remains a separate open decision.

## Preview

- Audio: `D:/FightVideo/SFX_audition/C1651_SFX10/SFX10_StanceBreak_OptionsA-C.mp3`
- Length: 9.811633 seconds; size 237,025 bytes.
- SHA-256: `235FD353EAE405618F550C1FF34F8F95CFB45BB1A2363AE397DBFD26BC0171D3`
- Index: `D:/FightVideo/SFX_audition/C1651_SFX10/README.txt` (SHA-256 `BD658C8B3633DB9BB84DFAACE8579DCFDD5CF2DC910D5354B906DA2C21A8C70D`).
- The preview concatenates existing WAV exports in A/B/C order with one second of silence between options. It does not replace or modify any existing audition files.

| Option | Source cue | Existing WAV duration | Preview interval | Character from candidate manifest |
|---|---|---:|---:|---|
| A | `/Game/StarterContent/Audio/Collapse01` | 3.92 s | 0.00–3.92 s | Stone/armor collapse |
| B | `/Game/AdvancedARPGCombat/RangedCombatSystem/DemoAssets/Effects/ArrowSounds/A_Guardian_Impact01` | 0.81 s | 4.92–5.73 s | Resonant heavy impact |
| C | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundWaves/Sevarog_ProfileDizzy_010` | 3.08 s | 6.73–9.81 s | Spectral ringing/disorientation |

Source WAV hashes were preserved and checked before processing:

- A `GAP05_OptionA_StanceBreak_Collapse01.wav`: `C5DCE8C2CE74BB23448CC9AC9571B49308DFC825229830F4D31D088AC3FDE6F3`
- B `GAP05_OptionB_StanceBreak_GuardianImpact.wav`: `4614A403A42D7C0B9DA97194F89B2E0BE8EDF2D6B9B87483E06FCA180F57CB16`
- C `GAP05_OptionC_StanceBreak_SevarogDizzy.wav`: `36BD1F1CC9A32F7CC6B61D373AD15044229C52D7D6C672678A866BC6E081A6B5`

## Limits and next step

The source files have long tails relative to the active transients; this preview leaves them intact so the Owner can hear the full cue. Choose A, B, C, or None. This was offline processing of existing repository audio exports only: no external media, project source/assets/config, Unreal/Editor, tests, build, or PIE. Do not wire the cue until the Owner choice is recorded; later Unreal inspection/authoring requires the project C-1155 process.
