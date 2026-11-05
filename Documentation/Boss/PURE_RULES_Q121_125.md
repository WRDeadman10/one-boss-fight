# Pure Rules Q121–Q125

These opt-in rules are unit-tested but intentionally unwired. Any runtime use needs an explicit owner/lead integration decision and live proof.

- **Parry feedback (NEXT_IDEAS #1):** emit authored response feedback only for the first resolved `Parried` outcome; duplicate notifications are suppressed.
- **Strafe resume (NEXT_IDEAS #5):** restart a neutral-strafe budget after an interruption only when budget remains and the one restart has not already been spent.
- **Bake freshness (NEXT_IDEAS #7):** a baked blade path is fresh only when both nonzero source fingerprints match; this rule does not compute or attest to a fingerprint.
- **Death and phase presentation (NEXT_IDEAS #8):** death presentation is one-shot after death; a phase roar is one-shot on a live phase change and is suppressed after death.
- **Stuck recovery (NEXT_IDEAS #9):** allow one direction-change recovery only for blocked motion and below a bounded attempt cap.
