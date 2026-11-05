# Player parry

`URPGPlayerParry` is the project's short timed parry window. The pack input action opens it; `URPGDamageResolver` asks whether the window is open at the instant of a boss contact. A parried contact deals no damage and is spent. The component does not edit pack assets; it also mirrors the window into the pack-owned `Status.ParryActive` tag (`RPGPlayerParry.h:13-16,55-60`).

## Input and timing

`BeginPlay` tries to bind the action and component tick retries binding if the pawn input component is late (`RPGPlayerParry.cpp:20-58`). `Press` refuses while a stamina charge/refund is pending, checks optional stamina, then uses the pure `RPGParry::Press` window/cooldown state transition. A successful open sets the gameplay tag; failed paid attempts schedule cost rollback (`:65-99`). `IsWindowOpen` and `GradeNow` query current game time rather than a timer callback (`:101-109`).

## Contact and cleanup

The resolver calls `NotifyParried` on an actual parried contact, incrementing the parry count and marking an optional pending stamina cost as earned (`RPGPlayerParry.cpp:122-135`). Once the window closes, `FinishStaminaCost` commits a successful parry charge or refunds a failed attempt; failed rollback remains pending for retry (`:137-170`). Tick also clears the active tag when the window closes (`:26-38`). `EndPlay` makes bounded retries for pending cost cleanup and tag removal before base teardown (`:172-176`).

Window duration, cooldown, and optional stamina cost are editable properties; zero stamina cost preserves the cost-free default (`RPGPlayerParry.h:25-34`). The tag only coordinates pack hit handling; resolver `Parried` outcomes are the proof that framework boss contacts used the window.
