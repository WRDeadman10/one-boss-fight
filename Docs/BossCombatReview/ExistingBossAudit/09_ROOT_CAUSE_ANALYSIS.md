# Root-cause analysis

## Confirmed causes versus hypotheses

| Gap | Category | Confirmed mechanism/evidence | Hypothesis or unresolved outcome | Discriminator |
|---|---|---|---|---|
| G01 wave cue | Missing presentation integration | Only wave ring drawing is non-Shipping debug; KI-065 records absent visual. [Wave:164](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.cpp:164) | No independently wired current ring effect established | Debug-off packaged capture synchronized with wave radius |
| G02 skipped release | Animation timing/state transitions | Tracker can skip Active; specials require Active equality. [Tracker:465](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:465), [Heal:255](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossHealPunish.cpp:255) | How often real frame hitches produce omission | Controlled position jumps across.45–.50, then real frame-hitch test |
| G02 ring tunneling | Collision implementation | Current band only; passing inner radius resolves without contact. [Wave:73](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.cpp:73) | Frequency under ordinary gameplay | Stationary target with known previous/new radius; moving target cases |
| G03 fallback mismatch | Incorrect configuration/data coupling | FallbackMontageName selects authored row. [Tracker:105](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:105) | Visible early damage when swap unavailable | Force approved test fallback without editing source assets; log notify/commit |
| G04 defense divergence | Architectural coupling/missing functionality | Own HP-only resolver bypasses guard/parry/reactions; pack separate. [DamageH:25](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGDamageResolver.h:25) | Which specials should block/parry/knock down | Owner policy + actual pack resolver graph U05/U08 |
| G04 splash priority | Damage attribution | Any HP loss since launch treated as central damage. [Wave:106](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossShockwave.cpp:106) | False suppression/double-dip under healing, timing, other loss | Correlated direct/wave event test, not manual health loss only |
| G05 late identity | Architecture/state transitions | Native allocation after playback, index-based recognition. [Tracker:234](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:234), [Tracker:389](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:389) | First-notify or same-index restart causes actual misattribution | Zero-time notify and restart-without-empty-frame scenario |
| G05 recovery | Timing/AI coupling | RecoveryEndTime not an enforced native deadline. [Tracker:251](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp:251) | Pack may enforce sufficient recovery; not all openings are false | Current ability callbacks + earliest-retaliation measurement |
| G06 A4 availability | Missing selection integration | Native start exists but only test initiation found; KI-067 says not BT-selected. [Issues:71](C:/UnrealProject/OneBossFight/Documentation/KNOWN_ISSUES.md:71) | Current unseen BP override could add a call | Read current BT/call references and autonomous selection log |
| G07 sword trace | Collision/art integration | Hidden pack weapon queries, visible NoCollision sword. [Look:76](C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossLook.cpp:76) | Size/position mismatch actually unacceptable | Overlay socket segments and visible blade across active poses |
| G08 low FPS | Rendering/configuration | Valid Shipping baseline GPU-bound; later fire-light tests improve same-block results. [Perf:23](C:/UnrealProject/OneBossFight/Documentation/PERFORMANCE_LOG.md:23), [Perf:39](C:/UnrealProject/OneBossFight/Documentation/PERFORMANCE_LOG.md:39) | Early/late experiment difference due machine state or persisted settings | Interleaved repeated baselines, logged config/GPU clocks |
| Selection quality | Unknown runtime/AI | Historical random-index/last-index chooser; current high-level BT not read | Repeats caused by weights, cooldown, pool size or fallback | Candidate eligibility/choice reasons and seeded frequency run |
| KI-085 latch | Player input integration | DisableInput/EnableInput around riposte; no delivered release during disabled input | Sprint/guard persists after release; explicitly not reproduced | Hold->riposte->release->restore on keyboard/controller |
| KI-106 close reach | Test setup/unknown runtime | Contradictory driver setups; C-84 clean montage list and successful real-denial recovery | Heading/setup affects effective socket travel | Same actual transforms, ability, pose time and trace samples in both drivers |

## What not to infer

- Adding attack animations cannot fix missing selection wiring, missed active-state polling or uncorrelated damage.
- A sampled active flag is not equivalent to observing every crossed montage event.
- Reset generation rejects old encounters, not every stale event within the same encounter.
- A no-tunneling result for one historical A1 path does not establish all authored weapons/ring/projectile paths.
- Source enforcement of yaw does not prove exclusive root-motion/nav authority.
- Attack count, win time and a finite combo array do not prove useful punish windows or well-shaped pressure.
- No utility component in C++ does not prove no contextual selection in the pack's Blueprints.

## Causal priority

First prove the active graph/data and repair presentation/contact timing. Then establish execution and damage provenance. Measure actual geometry and recovery. Only afterward tune selection frequency, spacing and pacing. This order avoids tuning around invisible hits, missing projectiles or misleading test setups.

All proposed fixes are in document10; no implementation occurred. For each hypothesis, its test can either promote it to a confirmed issue or close it without changing gameplay.

