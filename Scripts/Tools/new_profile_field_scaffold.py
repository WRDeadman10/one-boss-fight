"""Print the project's eight review sites for adding an opt-in profile field."""
import argparse
import re
from pathlib import Path


FIELD_RE = re.compile(r"^[A-Z][A-Za-z0-9]*$")
TOKEN_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.]*$")


def checklist_lines(field, error_token_arg=None, log_token_arg=None, test_control=False) -> list:
    """BP-34: the checklist lines main() prints, as a pure function (moved verbatim from main())."""
    lines = []
    f = field
    error_token = error_token_arg or "Framework.Profile.<choose-token-for-" + f + ">"
    log_token = log_token_arg or "<optional: choose-emission-token-or-none>"
    steps = [
        ("Profile declaration", "Source/OneBossFight/Player/RPGBossFrameworkProfile.h",
         "add UPROPERTY with disabled default, units/semantics comment; inspect " + f),
        ("Validation and stable failure", "Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp",
         "validate finite/domain/scope; choose and test " + error_token),
        ("Proof-log schema", "Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py",
         "if emitting " + log_token + ", add a regex matching the literal UE_LOG payload types"),
        ("Validation and wiring tests", "Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp",
         "cover default-off, endpoints, invalid values, scope, token, and wiring behavior as applicable"),
        ("Feature documentation and evidence", "Documentation/TASKS.md; Documentation/TEST_PLAN.md; Docs/BossCombatReview/Execution/Codex/Proofs/*_EXPECTED.md",
         "record units/defaults, enable/control setup, expected relation, source, and proof limits"),
        ("Emission and token indexes", "Source/OneBossFight/<owning feature>; Documentation/Boss/LOG_TOKENS.md",
         "if emitting " + log_token + ", log the measured values and add semantic/source rows; synchronize its schema"),
        ("Runtime state lifecycle", "Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp; RPGFrameworkMoveExecutor.cpp",
         "trace initialization/Rearm, Die, Fail, abort/interruption, and EndPlay; add clears only for owned state"),
        ("Test-control documentation", "Documentation/Boss/TEST_HOOKS.md",
         "include only when adding a CVar/test hook; otherwise no edit is needed"),
    ]

    lines.append("Eight edit/review sites for profile field %s (disabled default required):" % f)
    for index, (label, paths, action) in enumerate(steps, 1):
        if index == 8 and not test_control:
            action = "not applicable unless this change adds a CVar/test hook"
        lines.append("%d. %s | %s: %s" % (index, label, paths, action))
    lines.append("Chosen error token: %s" % error_token)
    lines.append("Chosen emission token: %s" % log_token)
    lines.append("This is a checklist only; verify exact ownership, reset paths, and tests in the current source.")
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--field", required=True,
                        help="PascalCase URPGBossFrameworkProfile member name")
    parser.add_argument("--error-token",
                        help="stable Framework.Profile.* token, if already chosen")
    parser.add_argument("--log-token",
                        help="FrameworkProof payload token, if this field emits one")
    parser.add_argument("--test-control", action="store_true",
                        help="include TEST_HOOKS.md only when adding a new CVar/test hook")
    args = parser.parse_args()
    if not FIELD_RE.fullmatch(args.field):
        parser.error("--field must be PascalCase alphanumeric")
    for option, value in (("--error-token", args.error_token), ("--log-token", args.log_token)):
        if value and not TOKEN_RE.fullmatch(value):
            parser.error(option + " must contain only letters, digits, underscores, and dots")

    for line in checklist_lines(args.field, args.error_token, args.log_token, args.test_control):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
