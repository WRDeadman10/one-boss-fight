# Known Issues

| ID | Area | Description | Workaround | Status |
|---|---|---|---|---|
| KI-001 | Toolchain | UBT warns "Visual Studio 2022 compiler is not a preferred version" (MSVC 14.51, VS 2026). Build succeeds. | Install MSVC 14.38 (17.8) if a later build fails | Open |
| KI-003 | Performance | Benchmark PC has an RTX 3060, not the target RTX 2060 Super; baselines are not target-hardware results | Re-measure on a 2060 Super if available | Open |
| KI-004 | Performance | Project defaults (Lumen, VSM) give 94-97 FPS avg and unstable p99 at 1080p in the empty arena | Use the `gi_off` settings via config in M6 | Open |
| KI-005 | Input | Look direction/sensitivity not yet playtested (`bEnableLegacyInputScales=False`, raw mouse, `LookSensitivity=1`) | Tune `LookSensitivity` or flip sign in IMC | Open |
| KI-006 | Content | Player uses the engine tutorial mannequin as a placeholder mesh and anim BP | Replace in asset pipeline milestone | Open |
| KI-002 | Build | ~68 C4996 deprecation warnings from engine headers (UE 5.5 API deprecations) | Ignore; not project code | Open |
