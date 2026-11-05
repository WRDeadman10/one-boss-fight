# Designer reference: card-local turn-rate ramp

`RPGBossTurnRateRamp::Rate` returns a smoothly interpolated turn-rate limit at an elapsed point in a move card. It is unwired; the caller must apply the returned limit to turning behavior.

| Input | Unit | Default | Valid domain |
|---|---|---:|---|
| `ElapsedSeconds` | seconds since card start | none | finite and non-negative |
| `RampSeconds` | seconds | none | finite and greater than 0 |
| `StartDegPerSecond` | degrees/second | none | finite, 0 to 720 inclusive |
| `EndDegPerSecond` | degrees/second | none | finite, 0 to 720 inclusive |
| Return value | degrees/second | 0 for invalid input | between start and end limits |

The rule clamps normalized time `ElapsedSeconds / RampSeconds` to 0–1, applies smoothstep `t²(3−2t)`, then interpolates between the two rates. It returns the start rate at time 0 and the end rate at or after the ramp duration.

Invalid inputs return 0. Rates may rise or fall; both endpoints must independently remain within 0–720 degrees/second. Source: [`RPGBossTurnRateRamp.h`](../../Source/OneBossFight/Player/RPGBossTurnRateRamp.h:7), unit tests: [`RPGBossTurnRateRampTests.cpp`](../../Source/OneBossFight/Tests/RPGBossTurnRateRampTests.cpp:6).
