# E155 decision audit: strafe interruption reset

Queue E's D40 reference is arena-leash boundary coverage; this question concerns strafe-stuck recovery and should point to the D36/D37 detector and geometry audits. Queue E is corrected.

The framework boss resets `StrafeStuck` at fresh proof initialization, when strafe starts, after a tick gap greater than `.5` seconds (logged as `reason=Interrupted`), and when an eligible card ends the strafe. The code comment says stagger or phase hold pauses strafe and the budget counts strafing time only. D36/D37 cover stuck geometry and detector edges; neither substitutes for live actor interruption evidence.

The current `.5`-second gap reset is explicit, so no new policy is needed for the implemented behavior. Whether target loss or leash correction should reset the detector is not established by this static path; owner decision is needed only if those cases become a shipped contract. Lead owns runtime proof. Static inspection only; no tests/build/Editor run.
