# C-1037 PPM black-frame handoff

Lead BUILD-257 is green 485/485. Both-route PIE logged a Perfect-grade parry and `PPM_ParryDistortion` added to the parrying player's `FollowCamera` at weight 1. The legacy pre-press mean gray was 14.7, +0.05 s mean gray 0.1 (nearly black), +0.15 s 34.3 and +0.30 s 38.1. The material is connected but its post-process output is wrong. KI-191 remains partial; the PPM visual gate failed.

Antigravity C-1037 owns the asset repair under `ENGINE_LOCK`: sample `SceneTexture:PostProcessInput0`, use small channel-offset UVs gated by ParryPulse/strength, output the scene color to Emissive, and read back material domain, blendable location and SceneTexture node. The Lead reruns the frame comparison. Codex does not edit this asset or run the Editor.

Codex probe hotfix: removed `legend.get_parry_slow_motion_count()` because the C++ getter lacks a UFUNCTION and Python cannot invoke it. The Development C++ logs already report grade, material, camera target and weight. The four proof frames, camera blendable readout, warmup discard and unique capture folder remain. Run syntax/diff checks before handing to the Lead.
