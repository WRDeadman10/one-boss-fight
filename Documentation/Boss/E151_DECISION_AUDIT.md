# E151 decision audit: repeat penalty decay

Queue E's D19 reference is stale: D19 is the parry stamina-cost audit. Selector repeat memory/penalty is documented by D6 and route-start updates by D15; Queue E is corrected.

`FRPGBossMoveSelector::Select` applies one constant `RepeatPenalty` factor to any candidate currently in `Recent`. `NoteStarted` appends real starts and trims the oldest entry to `RepeatMemory`; there is no time-based or per-repeat decay. `Reset` clears that memory. Existing D6 coverage maps the memory window and gaps.

No owner decision is needed for the explicit current policy. If design wants a different penalty per repeat age or elapsed time, owner approval is needed because that changes encounter behavior; Lead reviews implementation. Static inspection only; no tests/build/Editor run.
