# Punish limiter boundary audit (Queue D100)

**Scope:** static source/test map for the bounded use counter and adjacent defensive-card cooldown gate. No tests run; the pure limiter is documented unwired.

`RPGBossPunishLimiterRules.h:8-18` permits a use only when `MaxUses` is 1..100 and `Uses` is in [0, MaxUses); `RecordUse` increments only after that check, and `Reset` sets count to zero. There is no time field or time-based cooldown in this helper. The related defensive-card rule is `RPGBossDefenseRules.h:16,22`: minimum cooldown is 3 seconds and equality passes (`>=`).

`RPGBossPunishLimiterRulesTests.cpp:9-16` tests first availability, exactly three allowed uses, cap equality, refused over-cap use without increment, reset, negative corrupt count, and zero max. It does not cover max 1/100/101, adjacent `Uses` values around the cap, or maximum-int count. `RPGBossDefenseTests.cpp:19-20` checks exactly 3 seconds and 10 pass while 2.9 and NaN fail; no adjacent representable values around 3 or infinities are asserted.

The pure counter has no clock or cooldown state, so repeat timing is not part of its API. The time boundary resides in `CooldownOk`; callers/config validation and any actual use of this opt-in counter are separate. Do not infer runtime rate limiting from these standalone rules/tests.
