# Known Issues

| ID | Area | Description | Workaround | Status |
|---|---|---|---|---|
| KI-001 | Toolchain | UBT warns "Visual Studio 2022 compiler is not a preferred version" (MSVC 14.51, VS 2026). Build succeeds. | Install MSVC 14.38 (17.8) if a later build fails | Open |
| KI-002 | Build | ~68 C4996 deprecation warnings from engine headers (UE 5.5 API deprecations) | Ignore; not project code | Open |
