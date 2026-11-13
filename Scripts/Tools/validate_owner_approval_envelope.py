"""BK-86..89 (C, implementer; X-1999): read-only validator for a SYNTHETIC owner approval envelope.

An approval envelope records the owner's explicit answer to a decision request (for Sevarog: X-1991) for every
required Stats / Phase_1 field. It is a review record only: the validator emits a validation result and lists of
approved-for-review / rejected / unresolved fields. It never emits a production manifest, never invokes authoring,
never reads assets, and never writes anything. A valid envelope does not authorize authoring or a C-1155 run.

Envelope schema (onebossfight.owner-approval-envelope/v1), all keys required, no others:
  schema                 "onebossfight.owner-approval-envelope/v1"
  envelope_state         "OWNER_DECISION_RECORD"
  production_manifest    false
  authoring_authorized   false
  request_reference      "X-1991"                      (the decision request being answered)
  owner_message          {message_id, sender, path, reply_text, reply_sha256}
                           message_id  owner mailbox id, O-<n> or H-<n> (agent ids X-/C-/A- are refused)
                           sender      exactly "Owner"
                           path        repo-relative source of the reply (Documentation/TEAM_MAILBOX.md)
                           reply_text  the owner's exact reply text
                           reply_sha256  sha256(reply_text), 64 lowercase hex
  decisions              one entry per required field, exactly the 9 fields, no duplicates or extras:
                           {field_path, decision, value, quote}
                           decision  APPROVE_CANDIDATE | APPROVE_VALUE | REJECT | UNRESOLVED
                           value     the explicit value for APPROVE_*; null for REJECT and UNRESOLVED
                           quote     exact complete non-empty line from reply_text; null only for UNRESOLVED

Decision rules (never infer a default; anything not explicit stays UNRESOLVED):
  APPROVE_CANDIDATE  value must equal the X-1991 candidate for that field.
  APPROVE_VALUE      value is an owner alternative; it must differ from the candidate (otherwise use APPROVE_CANDIDATE).
  APPROVE_*          value finite and in the native range (RPGBossStatsAdapters.cpp ValidateStats, RPGBossPhaseAdapters.cpp);
                     the quote must name the field (alias list), contain the value as a number (or the name for PhaseId),
                     contain no other number, and carry no ambiguity, rejection, or conditional marker.
  REJECT             value null; the quote names the field and contains a rejection word (no / reject / not / don't).
  UNRESOLVED         value null and quote null.
With --verify-source, reply_text must exactly match the complete body in Documentation/TEAM_MAILBOX.md under the cited
owner message header; the resolved path must remain inside the selected repository root.
Exit 0 = valid envelope, 1 = invalid.
"""
import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

SCHEMA = "onebossfight.owner-approval-envelope/v1"
TOP_KEYS = {"schema", "envelope_state", "production_manifest", "authoring_authorized", "request_reference", "owner_message", "decisions"}
MESSAGE_KEYS = {"message_id", "sender", "path", "reply_text", "reply_sha256"}
DECISION_KEYS = {"field_path", "decision", "value", "quote"}
DECISIONS = {"APPROVE_CANDIDATE", "APPROVE_VALUE", "REJECT", "UNRESOLVED"}
REQUEST = "X-1991"
HEX64 = re.compile(r"[0-9a-f]{64}")
OWNER_ID = re.compile(r"(O|H)-\d+")
NUMBER = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?(?![\w.])")
AMBIGUOUS = re.compile(r"\b(or|either|maybe|perhaps|not sure|unsure|depends)\b|\?", re.IGNORECASE)
CONDITIONAL = re.compile(r"\b(unless|if|pending|provided|assuming)\b|\bsubject to\b", re.IGNORECASE)
REJECTION = re.compile(r"\b(no|reject|rejected|not|don't|dont|never)\b", re.IGNORECASE)
DEFAULT_ROOT = Path(__file__).resolve().parents[2]
OWNER_MAILBOX_PATH = "Documentation/TEAM_MAILBOX.md"

# X-1991 candidates and native ranges; (kind, candidate, low, low_inclusive, high) where high None = unbounded.
FIELDS = {
    "Stats.MaxHealth": ("float", 1500.0, 1.0, False, None, ("health", "hp")),
    "Stats.MaxPosture": ("float", 100.0, 0.0, False, None, ("posture", "poise")),
    "Stats.PostureRegenDelay": ("float", 6.0, 0.0, True, None, ("delay", "regen delay")),
    "Stats.PostureRegenRate": ("float", 13.0, 0.0, True, None, ("rate", "per s", "per second", "regen rate")),
    "Phases[Phase_1].PhaseId": ("name", "Phase_1", None, None, None, ("phase_1", "phase 1", "phase id")),
    "Phases[Phase_1].EntryHealthFraction": ("float", 0.6, 0.0, False, 1.0, ("threshold", "fraction", "phase two", "phase 2")),
    "Phases[Phase_1].SpeedMultiplier": ("float", 1.0, 0.0, False, None, ("speed",)),
    "Phases[Phase_1].RateMultiplier": ("float", 1.0, 0.0, False, None, ("rate multiplier", "attack rate", "rate")),
    "Phases[Phase_1].AttackMultiplier": ("float", 1.0, 0.0, False, None, ("attack",)),
}


class DuplicateKey(ValueError):
    pass


def no_duplicate_pairs(pairs):
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise DuplicateKey("duplicate JSON key: %s" % key)
        seen[key] = value
    return seen


def loads_strict(text):
    """JSON with duplicate keys and NaN/Infinity refused."""
    def bad_constant(name):
        raise ValueError("non-finite JSON constant refused: %s" % name)
    return json.loads(text, object_pairs_hook=no_duplicate_pairs, parse_constant=bad_constant)


def in_range(value, low, low_inclusive, high):
    if low is not None and (value < low or (value == low and not low_inclusive)):
        return False
    return high is None or value <= high


def finite_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except (OverflowError, TypeError, ValueError):
        return False


def numbers_in(text):
    text = re.sub(r"[.!?;,:]+\s*$", "", text)
    return {float(match) for match in NUMBER.findall(text)}


def mentions_alias(text, aliases):
    return any(re.search(r"(?<![a-z0-9_])%s(?![a-z0-9_])" % re.escape(alias), text, re.IGNORECASE)
               for alias in aliases)


def check_decision(entry, reply, errors):
    field = entry.get("field_path")
    where = "decision %s" % field
    kind, candidate, low, low_inclusive, high, aliases = FIELDS[field]
    decision, value, quote = entry.get("decision"), entry.get("value"), entry.get("quote")
    if not isinstance(decision, str) or decision not in DECISIONS:
        errors.append("%s: decision %r refused (allowed: %s)" % (where, decision, ", ".join(sorted(DECISIONS))))
        return None
    if decision == "UNRESOLVED":
        if value is not None or quote is not None:
            errors.append("%s: UNRESOLVED must have value null and quote null (never infer)" % where)
        return decision
    if not isinstance(quote, str) or not quote.strip():
        errors.append("%s: %s needs a quote from the owner's reply" % (where, decision))
        return None
    reply_lines = {line.strip() for line in reply.splitlines() if line.strip()}
    if quote.strip() not in reply_lines:
        errors.append("%s: quote must exactly match a complete non-empty reply line" % where)
        return None
    lowered = quote.lower()
    if not mentions_alias(lowered, aliases):
        errors.append("%s: quote does not name the field (expected one of %s)" % (where, ", ".join(aliases)))
    if decision == "REJECT":
        if value is not None:
            errors.append("%s: REJECT must have value null" % where)
        if not REJECTION.search(quote):
            errors.append("%s: REJECT quote carries no rejection word" % where)
        return decision
    # APPROVE_CANDIDATE / APPROVE_VALUE
    if AMBIGUOUS.search(quote) or CONDITIONAL.search(quote):
        errors.append("%s: ambiguous quote cannot approve (mark UNRESOLVED): %r" % (where, quote))
    if REJECTION.search(quote):
        errors.append("%s: quote contains a rejection word; conflicting approval refused" % where)
    if kind == "name":
        if value != candidate:
            errors.append("%s: name value must be %r" % (where, candidate))
        elif not re.search(r"(?<![a-z0-9_])%s(?![a-z0-9_])" % r"[ _]".join(re.escape(p) for p in candidate.lower().split("_")),
                           lowered):
            # X-2058 / A-854 BUG-3: token-bounded identity, so Phase_1 is not approved by "Phase_10" (or "Phase 12").
            errors.append("%s: quote does not contain %r as a whole token" % (where, candidate))
        if decision == "APPROVE_VALUE":
            errors.append("%s: PhaseId has no alternatives; use APPROVE_CANDIDATE" % where)
        return decision
    if not finite_number(value):
        errors.append("%s: value must be a finite number, got %r" % (where, value))
        return None
    if not in_range(float(value), low, low_inclusive, high):
        errors.append("%s: value %r outside the native range" % (where, value))
    found = numbers_in(quote)
    if float(value) not in found:
        errors.append("%s: value %r does not appear in the quote" % (where, value))
    elif len(found) > 1:
        errors.append("%s: quote contains several numbers %s; split the quote or mark UNRESOLVED" % (where, sorted(found)))
    if decision == "APPROVE_CANDIDATE" and float(value) != float(candidate):
        errors.append("%s: APPROVE_CANDIDATE value %r differs from the X-1991 candidate %r" % (where, value, candidate))
    if decision == "APPROVE_VALUE" and float(value) == float(candidate):
        errors.append("%s: APPROVE_VALUE equals the candidate; use APPROVE_CANDIDATE" % where)
    return decision


def validate(envelope, root=DEFAULT_ROOT, verify_source=False):
    errors = []
    result = {"valid": False, "errors": errors, "approved_for_review": [], "rejected": [], "unresolved": []}
    if not isinstance(envelope, dict):
        errors.append("envelope must be a JSON object")
        return result
    missing, extra = TOP_KEYS - set(envelope), set(envelope) - TOP_KEYS
    if missing:
        errors.append("missing top-level keys: %s" % ", ".join(sorted(missing)))
    if extra:
        errors.append("unknown top-level keys refused: %s" % ", ".join(sorted(extra)))
    if envelope.get("schema") != SCHEMA:
        errors.append("schema must be %s" % SCHEMA)
    if envelope.get("envelope_state") != "OWNER_DECISION_RECORD":
        errors.append("envelope_state must be OWNER_DECISION_RECORD")
    if envelope.get("production_manifest") is not False:
        errors.append("production_manifest must be false: an envelope is never a production manifest")
    if envelope.get("authoring_authorized") is not False:
        errors.append("authoring_authorized must be false: an envelope never authorizes authoring")
    if envelope.get("request_reference") != REQUEST:
        errors.append("request_reference must be %s" % REQUEST)
    message = envelope.get("owner_message")
    reply = ""
    if not isinstance(message, dict):
        errors.append("owner_message must be an object")
    else:
        m_missing, m_extra = MESSAGE_KEYS - set(message), set(message) - MESSAGE_KEYS
        if m_missing or m_extra:
            errors.append("owner_message keys must be exactly %s" % ", ".join(sorted(MESSAGE_KEYS)))
        if message.get("sender") != "Owner":
            errors.append("owner_message.sender must be exactly 'Owner', got %r" % message.get("sender"))
        if not (isinstance(message.get("message_id"), str) and OWNER_ID.fullmatch(message["message_id"])):
            errors.append("owner_message.message_id must be an owner id O-<n> or H-<n>, got %r" % message.get("message_id"))
        path = message.get("path")
        if path != OWNER_MAILBOX_PATH:
            errors.append("owner_message.path must be %s, got %r" % (OWNER_MAILBOX_PATH, path))
            path = None
        reply = message.get("reply_text") if isinstance(message.get("reply_text"), str) else ""
        if not reply.strip():
            errors.append("owner_message.reply_text must be the owner's non-empty reply")
        digest = message.get("reply_sha256")
        if not (isinstance(digest, str) and HEX64.fullmatch(digest)):
            errors.append("owner_message.reply_sha256 must be 64 lowercase hex")
        elif hashlib.sha256(reply.encode("utf-8")).hexdigest() != digest:
            errors.append("owner_message.reply_sha256 does not match reply_text (tampered or stale)")
        if verify_source and path and reply:
            root = root.resolve()
            target = (root / path).resolve()
            if not target.is_relative_to(root):
                errors.append("owner_message.path resolves outside the repository root: %s" % path)
                target = None
            if target is None:
                pass
            elif not target.is_file():
                errors.append("owner_message.path does not exist: %s" % path)
            else:
                text = target.read_text(encoding="utf-8", errors="replace")
                id_pattern = r"^### \[%s\] " % re.escape(str(message.get("message_id")))
                headers = list(re.finditer(id_pattern + r"Owner -> [^\n]*$", text, re.MULTILINE))
                same_id = list(re.finditer(id_pattern + r"[^\n]*$", text, re.MULTILINE))
                header = headers[0] if headers else None
                if not header:
                    errors.append("no '### [%s] Owner -> ...' header in %s" % (message.get("message_id"), path))
                elif len(same_id) > 1:
                    # X-2058 / A-854 BUG-5: match bind_owner_approval - a repeated message id is ambiguous; refuse.
                    errors.append("message id %s appears in %d headers in %s; duplicate owner message refused"
                                  % (message.get("message_id"), len(same_id), path))
                else:
                    following = re.search(r"^### \[", text[header.end():], re.MULTILINE)
                    body = text[header.end(): header.end() + following.start()] if following else text[header.end():]
                    # X-2058 parity: reply_text must BE the canonical (stripped) body, exactly as hashed - the same
                    # semantics as bind_owner_approval; padded reply text is refused even when its hash matches.
                    if reply != body.strip():
                        errors.append("reply_text does not exactly match the complete owner message %s "
                                      "(it must equal the stripped body; no padding)" % message.get("message_id"))
    decisions = envelope.get("decisions")
    if not isinstance(decisions, list):
        errors.append("decisions must be a list")
        return result
    seen = set()
    for index, entry in enumerate(decisions):
        if not isinstance(entry, dict) or set(entry) != DECISION_KEYS:
            errors.append("decision %d keys must be exactly %s" % (index, ", ".join(sorted(DECISION_KEYS))))
            continue
        field = entry.get("field_path")
        if not isinstance(field, str) or field not in FIELDS:
            errors.append("decision %d: extra/unknown field refused: %r" % (index, field))
            continue
        if field in seen:
            errors.append("decision %s: duplicate decision refused" % field)
            continue
        seen.add(field)
        outcome = check_decision(entry, reply, errors)
        if outcome in ("APPROVE_CANDIDATE", "APPROVE_VALUE"):
            result["approved_for_review"].append({"field_path": field, "value": entry["value"], "decision": outcome})
        elif outcome == "REJECT":
            result["rejected"].append(field)
        elif outcome == "UNRESOLVED":
            result["unresolved"].append(field)
    # X-2058 / A-854 BUG-4: one owner line may approve at most one field. Shared aliases (e.g. bare "rate" for both
    # Stats.PostureRegenRate and Phases[Phase_1].RateMultiplier) would otherwise let "Rate 1.0." approve two fields.
    approved_quotes = {}
    for entry in decisions:
        if isinstance(entry, dict) and entry.get("decision") in ("APPROVE_CANDIDATE", "APPROVE_VALUE") \
                and isinstance(entry.get("quote"), str) and isinstance(entry.get("field_path"), str) \
                and entry.get("field_path") in FIELDS:
            approved_quotes.setdefault(entry["quote"].strip().lower(), []).append(entry["field_path"])
    for quote, fields in sorted(approved_quotes.items()):
        if len(set(fields)) > 1:
            errors.append("one quote approves several fields %s; each approval needs its own owner line: %r"
                          % (sorted(set(fields)), quote))
    absent = sorted(set(FIELDS) - seen)
    if absent:
        errors.append("partial envelope refused; every field needs an explicit entry (UNRESOLVED if unanswered): %s" % ", ".join(absent))
    result["valid"] = not errors
    if not result["valid"]:
        result["approved_for_review"] = []
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("envelope")
    parser.add_argument("--verify-source", action="store_true")
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    args = parser.parse_args(argv)
    try:
        envelope = loads_strict(Path(args.envelope).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        print(json.dumps({"valid": False, "errors": ["cannot read envelope: %s" % error], "approved_for_review": [], "rejected": [], "unresolved": []}, indent=2))
        return 1
    result = validate(envelope, Path(args.root), args.verify_source)
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
