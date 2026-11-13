"""BK-122/123 (C, implementer; X-2012, X-2013): pure adapter that binds a Sevarog executor receipt to its owner mailbox source.

bind_receipt_source(raw_text, receipt, validate_receipt=..., extract_owner_block=...) checks one receipt against the
SAME complete raw mailbox text the executor read:
  1. validate_receipt(receipt) must be valid (validate_sevarog_executor_receipt.validate_receipt; every outcome
     carries a bound source),
  2. extract_owner_block(raw_text, message_id, errors) (bind_owner_approval.extract_owner_block, :82-112) must return
     exactly one `### [<id>] Owner -> ...` body: duplicate, missing, non-owner and empty blocks are refused, and so
     is a final block whose text does not end in a newline. A final block cut cleanly at a line end CANNOT be told
     apart from a complete one; pass the whole mailbox file,
  3. the owner source tuple is derived from that block - sender "Owner", the id, path Documentation/TEAM_MAILBOX.md,
     sha256 of the stripped body (the binder's form, bind_owner_approval.py:141) - and must equal receipt.source exactly.

Dependency boundary (X-2013): this module imports only hashlib and performs no filesystem access, not even at import.
The caller injects both rule functions, so the rules stay the binder's and validator's own and cannot drift.

It proves TEXT BINDING ONLY: that the receipt names an owner message present once and unaltered in the given text.
It does not prove that the text is the real mailbox file, that any runtime event happened, or that a write was
authorized; X-1991 remains the owner gate.
"""
import hashlib

MAILBOX_PATH = "Documentation/TEAM_MAILBOX.md"
SOURCE_KEYS = ("message_id", "sender", "path", "sha256")


def bind_receipt_source(raw_text, receipt, validate_receipt, extract_owner_block):
    """Return {bound, errors, receipt_result, derived_source, proves}; never reads files or authorizes anything."""
    errors = []
    result = {"bound": False, "errors": errors, "receipt_result": None, "derived_source": None,
              "proves": "text-binding-only"}
    if not callable(validate_receipt) or not callable(extract_owner_block):
        errors.append("validate_receipt and extract_owner_block must be injected callables")
        return result
    try:
        receipt_result = validate_receipt(receipt)
    except Exception as exc:
        errors.append("receipt validator raised %s" % type(exc).__name__)
        return result
    result["receipt_result"] = receipt_result
    if not isinstance(receipt_result, dict):
        errors.append("receipt validator returned a non-object result")
        return result
    reported_errors = receipt_result.get("errors")
    if receipt_result.get("valid") is not True or not isinstance(reported_errors, list) or reported_errors:
        if not isinstance(reported_errors, list):
            reported_errors = ["validator returned invalid result"]
        elif receipt_result.get("valid") is True and reported_errors:
            errors.extend("receipt validator marked result valid but reported errors: " + str(e) for e in reported_errors)
            return result
        errors.extend("receipt: " + str(e) for e in reported_errors)
        return result
    if not isinstance(receipt, dict) or not isinstance(receipt.get("source"), dict):
        errors.append("valid receipt result is missing an object source record")
        return result
    claimed = receipt["source"]
    if set(claimed) != set(SOURCE_KEYS) or not isinstance(claimed.get("message_id"), str):
        errors.append("valid receipt result has a malformed source record")
        return result
    try:
        body = extract_owner_block(raw_text, claimed["message_id"], errors)
    except Exception as exc:
        errors.append("owner block extractor raised %s" % type(exc).__name__)
        return result
    if body is None or errors:
        return result
    if not isinstance(body, str):
        errors.append("extract_owner_block returned a non-string body")
        return result
    try:
        body_sha256 = hashlib.sha256(body.encode("utf-8")).hexdigest()
    except UnicodeEncodeError:
        errors.append("owner block body is not valid UTF-8 text")
        return result
    derived = {"message_id": claimed["message_id"], "sender": "Owner", "path": MAILBOX_PATH,
               "sha256": body_sha256}
    result["derived_source"] = derived
    for key in SOURCE_KEYS:
        if claimed.get(key) != derived[key]:
            errors.append("receipt source.%s %r does not match the owner block (%r)" % (key, claimed.get(key), derived[key]))
    result["bound"] = not errors
    return result
