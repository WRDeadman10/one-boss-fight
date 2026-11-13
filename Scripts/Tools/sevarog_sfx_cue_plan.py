"""BQ-86 (Queue BQ batch 18; E1): SFX wiring scaffold for the Sevarog move cards, staged for owner decision O2 (SFX picks).

The engine side already exists: every move card carries FRPGBossCue entries with a TSoftObjectPtr<USoundBase> Sound slot
(Player/RPGBossMoveCard.h), and the executor fires them at TimeSeconds. What is missing is the plan of WHICH cue slots
each card gets and a safe way to fill them once the owner picks sounds. This library provides:
  - cue_slots(rows): the proposed slots per card, derived from the card's own timings (windup at commit, swing at active
    start, impact at active start for hit cards; release for area effects; channel start for drains). Sound = None.
  - validate_picks(slots, picks): checks an owner pick table {(move_id, cue_id): "/Game/...Sound"} before anything is
    authored: every key must be a planned slot, every value a /Game/ object path, no pack (/Game/AdvancedARPGCombat) or
    Ref content path, and no slot silently left out (missing picks are reported, not filled).
It authors nothing and touches no asset. Applying picks to the cards is O2 (owner) then ENG (author script, C-1155).
"""
from __future__ import annotations

import re

_OBJECT_PATH = re.compile(r"^/Game/[A-Za-z0-9_/]+\.[A-Za-z0-9_]+$")
FORBIDDEN_ROOTS = ("/Game/AdvancedARPGCombat/", "/Game/Ref/")


def cue_slots(rows) -> list[dict]:
    """Planned cue slots for authored card rows (dicts as author_sevarog_draft_cards.build_candidate_specs returns)."""
    slots = []
    for row in rows:
        move = row["move_id"]
        commit, active = float(row["commit_seconds"]), float(row["active_start_seconds"])
        slots.append({"move_id": move, "cue_id": "Cue_Windup", "time_seconds": commit, "visual": "None"})
        if row.get("windows"):
            slots.append({"move_id": move, "cue_id": "Cue_Swing", "time_seconds": active, "visual": "None"})
        area = row.get("area_effect")
        if area:
            slots.append({"move_id": move, "cue_id": "Cue_AreaRelease", "time_seconds": float(area["release_seconds"]), "visual": "None"})
            slots.append({"move_id": move, "cue_id": "Cue_AreaResolve",
                          "time_seconds": float(area["release_seconds"]) + float(area["delay_seconds"]), "visual": "None"})
        drain = row.get("channel_drain")
        if drain:
            slots.append({"move_id": move, "cue_id": "Cue_ChannelStart", "time_seconds": float(drain["start_seconds"]), "visual": "None"})
    for slot in slots:
        slot["sound"] = None  # O2: owner picks
    return slots


def validate_picks(slots, picks: dict) -> dict:
    """Returns {'errors': [...], 'missing': [(move, cue), ...]}; an empty errors list means the table may be authored."""
    planned = {(s["move_id"], s["cue_id"]) for s in slots}
    errors = []
    for key, path in picks.items():
        if key not in planned:
            errors.append("unplanned slot: %s/%s" % key if isinstance(key, tuple) and len(key) == 2 else "bad key: %r" % (key,))
            continue
        if not isinstance(path, str) or not _OBJECT_PATH.match(path):
            errors.append("not a /Game object path for %s/%s: %r" % (key[0], key[1], path))
        elif path.startswith(FORBIDDEN_ROOTS):
            errors.append("forbidden source root for %s/%s: %s" % (key[0], key[1], path))
    missing = sorted(planned - set(picks))
    return {"errors": errors, "missing": missing}
