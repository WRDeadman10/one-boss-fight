# DD25 C281/C284 final source arithmetic audit

Source reasoning only; no runtime reproduction or unrestricted arithmetic proof.
Historical pre-write findings/lead request remain separately preserved in C281_PREWRITE_SOURCE_FINDINGS.md. C284 resolved both findings; nothing below requests a pending contract decision.

| Field/operation | Source reasoning and explicit limits |
|---|---|
| PackPollSeconds | Native cpp:223 adds bounded float to double Now; authored >0,<=1e6. It does not repair arbitrary nonfinite world time, guarantee a real poll interval or validate scheduling. For finite extreme double time a small1e6 offset rounds away, not a float-add overflow. |
| PackEndTimeMultiplier | Native:296/303 injects only when >0, zero/negative/NaN skip injection. Authored finite>=0,<=1e6 with0 OFF. Reflected downstream timing/clip length is external; no montage duration/playback proof. |
| HoldAtSeconds | Native pause comparisons:446/:494; Clamp(float(Age),0,HoldAt):519. Authored finite>0,<=1e6 prevents negative upper bound/inverted authored interval; prior double-to-float Age narrowing and external invalid ages remain residuals. No frame/pose/timing proof. |
| DyingSeconds | Native:419 compares with double Age. Authored finite>0,<=1e6; external clock/age/state semantics not certified. |
| BlendInSeconds | Native:439 passes value to RPGBossClips::Play (Clips.h:52/59); restart with positive StartAt instead selects0. Authored finite>=0,<=1e6; no engine blending/duration capability claim. |
| MaxClipRestarts | C284 amended authored int32 range0..1000000. Native comparison:508 and equality-warning increment:510-512 plus normal increment:517. After zero-initialized per-death counter and normal invariant-preserving flow, legal limit permits at most1000001 at the one-time warning, belowINT32_MAX. This closes that local overflow reasoning, not cumulative ClipRestartCount at518 or lifetime/external counters. Ceiling is AUTHORED CONTRACT, not native guard or tuning value. Zero disables restarts. No native edit/reproduction. |

DeathMode/name/ref/bool fields have no numeric arithmetic. Both required soft paths are uniform authoring policy, while native Preload:160-173 on first Tick:343 loads only the selected mode. Asset-file presence/hashes are not load/class/skeleton/cook/pose proof.

Attach:47-49 returns Existing before allocation WITHOUT Mode assignment. Typed mode remains authoritative on this reuse path. Possible-second-instance claim from C281 is retracted by C284; no reservation/race/activation-order guarantee is inferred. Constructor:31-39 enables tick and assigns soft defaults; no runtime operation is invoked by the adapter/tests. KI-083 pack destruction/remains EndPlay:119-128 remains unexecuted here.
