# Audio module

The audio folder contains arena ambience, boss music, and footstep components. It owns playback lifecycle and asset references; combat state is observed through the encounter/phases and pack reflection helpers.

## Files

- `RPGArenaAmbience` builds the ambience actor, starts loops, and restarts the wind layer when it finishes (`RPGArenaAmbience.cpp:20-39`).
- `RPGBossMusic` starts/stops tracks, swaps to Phase 2, and coordinates audio components at death/end play (`RPGBossMusic.cpp:20-26,67-113,139`). It reads encounter/phase state rather than owning phase transitions.
- `RPGFootsteps` tracks landing and movement to trigger footstep sounds (`RPGFootsteps.cpp:69-79`).

## Lifecycle guidance

Use component/actor teardown to stop owned audio and clear delegate bindings. The music component may observe the framework/pack phase source, but a phase transition remains owned by the relevant boss phase system. `rpg.Legend` controls the separate hit-stop/shake/music presentation pass in `Player/RPGLegend`; it is not the music asset configuration. Source references are not proof that all audio assets are present or balanced in a packaged build.
