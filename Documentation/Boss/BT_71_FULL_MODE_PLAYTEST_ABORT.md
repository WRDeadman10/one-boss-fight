# BT-71 — Full-mode playtest attempt aborted safely

Date: 2026-11-17 00:21 UTC
Status: not accepted; no boss-death result.

The Full-mode C-1619 runner launched Unreal Editor and waited for a normal-combat defeat. Computer Use could list the window, but input/capture failed with `GetCursorPos failed: Access is denied (0x80070005)`, so the fight could not be controlled. No `[FrameworkProof] RESULT outcome=BossDefeated` or acceptance receipt was produced. The log contains `Framework.Boss.TargetLifeOrHealthChanged bossInactive=1`.

The runner process was interrupted after the UI retries failed. Its cleanup did not finish, so Codex completed recovery only after confirming the Editor process was absent and both lock files still carried this run's exact owner token. `DefaultGame.ini` was restored byte-for-byte from `DefaultGame.ini.original`; both owned locks were released. Final verification: no UnrealEditor process, no C-1155 locks, config SHA-256 equals the original backup (`5DE691FCA4E0FA375F6F262FA6BA402FEFA7AB9A0B567AE2146E6823F69EDEC8`). Recovery status is `Saved/SevarogArenaRoute/Run_20261116_233212_e01fc5f9/status.txt`.

No asset was saved. BT-71 remains pending for an Owner-operated RDC playtest or restored UI input access. BT-62 remains in Review because raw BehaviorTree ticks are unresolved and there is no Full-mode boss-death evidence. No playable-build acceptance is claimed.

## Follow-up retry after Owner authorization (2026-11-18)

After Owner message H-17 authorized proceeding without waiting, Codex retried Computer Use desktop access before launching another Full-mode run. `cua.getState()` again failed immediately with `GetCursorPos failed: Access is denied (0x80070005)`. No Editor launch, C-1155 lock acquisition, config write, or combat input occurred. BT-71 remains unaccepted; there is still no BossDefeated result/receipt. An active desktop-input session or another explicitly supported acceptance path is still required; do not bypass the Windows access barrier with shell/UI automation.
