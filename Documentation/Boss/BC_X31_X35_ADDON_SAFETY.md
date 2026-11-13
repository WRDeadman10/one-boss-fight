# Queue BC Batch 7: X31–X35 add-on safety and issue refresh

## X31 — disabled-default compatibility

`FRPGBossAreaEffect` and `FRPGBossChannelDrain` are value members on `FRPGBossMoveCardSpec`; both `bEnabled` members default false and their numeric fields have default initialization. `CompileMetadata` copies the full spec into the compiled card, so the values are preserved. Existing BC-X01 tests assert default-off compiled snapshots remain disabled after source mutation. This is source and native-test coverage; the expanded native suite has not been run in this workspace.

## X32 — effect-only validation/compile routes

Validation permits a move with no direct windows only when it has an enabled AreaEffect or ChannelDrain (or is defensive), while rejecting both add-ons together and rejecting either add-on on defensive cards. `CompileMetadata` runs validation before constructing compiled metadata and retains the copied spec. `URPGFrameworkMoveExecutor::Initialize` independently revalidates the compiled card and accepts positive add-on damage/tick damage as a damage source. BC-X01's focused cases cover valid effect-only cards and the add-on conflict; native execution/runtime remains unclaimed.

## X33 — channel lifecycle cleanup

Channel ticks are driven by executor card-local position (`TickChannelDrain`), not a timer. `Abort` clears the area snare, aborts the model, stops owned montage/movement, and disables component ticking; `EndPlay` clears the snare and calls `Abort`. Stagger, death, leash, watchdog, and failure routes call Abort in the character/executor path. Thus no channel timer survives; no tick occurs after executor abort is terminal. No gameplay change made.

## X34 — temporary movement-speed ownership

Area snare captures baseline speed, applies its multiplier, and every 0.05 s compares current speed with the last applied value. If an external policy changes speed, the executor rebases that observed value as the new baseline and reapplies the multiplier. On expiry/abort it restores the baseline only when current speed still equals the executor's applied value, preserving a distinct late external change. Static path audit only; concurrent systems writing the exact applied value or timing interactions have no runtime evidence here.

## X35 — known-issue correction

Refreshed `Documentation/KNOWN_ISSUES.md`: the old X-1784 EndPlay tag-cleanup entry was stale. Current i-frame and parry components transfer failed owned-tag removal to `RPGOwnedTagCleanup`. The narrower encounter-reset i-frame removal and persistent EndPlay stamina-write cases remain test-coverage gaps, not confirmed runtime failures.

## Scope

Static source and existing test review. No code or tests changed/run in this batch; no Unreal/build/PIE/cook/assets. Any earlier focused Python results remain scoped to BC-X26–X30.
