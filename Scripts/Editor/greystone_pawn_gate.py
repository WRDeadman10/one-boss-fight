"""BQ-52/53 (Queue BQ batch 11; B6): shared Greystone pawn gate for the combat-trace and parry confirmation drivers.

Today only pie_greystone_root_motion.py can run on the Greystone child (C1257_PLAYER_TARGET plus the Development CVar
rpg.GreystonePlayerTestPawn). The hit and parry drivers (pie_er_default_wiring_hits.py, pie_tier2_parry.py) always run on
the default mannequin, so "Greystone combat traces and parry work" is unproven. This module is the pure, Unreal-free
piece those drivers can opt into: read the same env switch, produce the console command, and verify that the pawn
actually possessed is the one requested before any trial counts. Default (unset env) = mannequin, unchanged behaviour.

Wiring into the existing drivers is a Lead decision (they are Lead-run C-1155 drivers); see BQ_51_55_BATCH11.md.
"""
ENV_NAME = "C1257_PLAYER_TARGET"
CVAR = "rpg.GreystonePlayerTestPawn"
GREYSTONE_CLASS = "BP_GreystoneERPlayer_C"
MANNEQUIN_CLASS = "BP_CombatPlayerCharacter_C"
TARGETS = ("mannequin", "greystone")


def target_from_env(value):
    """'greystone' / 'mannequin' (case and spaces ignored); unset or empty = 'mannequin'; anything else = None (refuse)."""
    text = (value or "").strip().lower()
    if not text:
        return "mannequin"
    return text if text in TARGETS else None


def cvar_command(target):
    """Console command to set before PIE; None for an invalid target."""
    if target not in TARGETS:
        return None
    return "%s %d" % (CVAR, 1 if target == "greystone" else 0)


def restore_command():
    """Always restore the mannequin default on exit, as pie_greystone_root_motion.py does."""
    return "%s 0" % CVAR


def possession_ok(target, possessed_class_name):
    """A trial counts only for the exact requested pawn class; unrelated non-Greystone classes are not the mannequin."""
    if target == "greystone":
        return possessed_class_name == GREYSTONE_CLASS
    if target == "mannequin":
        return possessed_class_name == MANNEQUIN_CLASS
    return False


def result_tag(target):
    """Suffix for RESULT lines and receipt folders, so mannequin and Greystone runs are never mixed up."""
    return "target=%s" % (target if target in TARGETS else "invalid")
