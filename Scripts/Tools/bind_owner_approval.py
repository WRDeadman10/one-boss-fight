"""BK-97 (C, implementer; X-2003): pure binding adapter between a raw owner mailbox message, the approval envelope
validator and the proposal-only repair planner.

Closes the source-binding limitation recorded in X-2003: the planner must not trust a separately supplied
envelope result or owner_source object. bind_owner_approval() takes the RAW mailbox text (one complete owner message
block, or a larger mailbox excerpt containing it), the owner message id, and the envelope; it

  1. finds exactly one `### [<id>] Owner -> ...` block (duplicate, missing, non-owner or unterminated blocks refused),
  2. requires envelope.owner_message to name that id and carry reply_text equal to the block body (stripped) with the
     matching SHA-256 (mismatched id, altered body or hash refused),
  3. runs validate_owner_approval_envelope.validate() on the envelope (no file access; the source check is step 1-2),
  4. derives owner_source INTERNALLY from the bound block (sender, id, body hash, mailbox path) - callers cannot pass one,
  5. reports approval_complete only when the envelope is valid with all 9 fields approved and nothing unresolved/rejected.

plan_from_bound() feeds that bound result to plan_repair(). It is dry-run by default: mode=write is refused unless the
binding is complete AND the caller passes allow_write=True; the adapter itself never authorizes data authoring or a
C-1155 run (write_permitted is always False in the binding). Pure Python: no Unreal, no files, no locks.
"""
import hashlib
import importlib.util
import re
import copy
import weakref
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ENVELOPE = _load("validate_owner_approval_envelope")
PLANNER = _load("plan_sevarog_definition_repair")
OWNER_ID = re.compile(r"(?:O|H)-[0-9]+")
HEADER = re.compile(r"^### \[([^\]]+)\] (\S+) -> [^\n]*$", re.MULTILINE)
MAILBOX_PATH = "Documentation/TEAM_MAILBOX.md"
_BOUND_DATA = weakref.WeakKeyDictionary()


class _BoundApproval:
    """Read-only capability issued only by bind_owner_approval in this process."""
    __slots__ = ("__weakref__",)
    __hash__ = object.__hash__

    def __getitem__(self, key):
        data = _BOUND_DATA.get(self)
        if data is None:
            raise KeyError(key)
        return copy.deepcopy(data[key])

    def __iter__(self):
        data = _BOUND_DATA.get(self)
        return iter(tuple(data)) if data is not None else iter(())

    def __len__(self):
        data = _BOUND_DATA.get(self)
        return len(data) if data is not None else 0

    def keys(self):
        data = _BOUND_DATA.get(self)
        return tuple(data) if data is not None else ()

    def get(self, key, default=None):
        data = _BOUND_DATA.get(self)
        return copy.deepcopy(data.get(key, default)) if data is not None else default


def _issue_binding(data):
    binding = _BoundApproval()
    _BOUND_DATA[binding] = copy.deepcopy(data)
    return binding


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_owner_block(raw_text, message_id, errors):
    """Return the stripped body of the single owner block with this id, or None (errors appended)."""
    if not isinstance(raw_text, str) or not raw_text.strip():
        errors.append("raw mailbox text is required")
        return None
    if not (isinstance(message_id, str) and OWNER_ID.fullmatch(message_id)):
        errors.append("message_id must be an owner id O-<n> or H-<n>, got %r" % (message_id,))
        return None
    headers = list(HEADER.finditer(raw_text))
    matching = [h for h in headers if h.group(1) == message_id]
    if not matching:
        errors.append("no block with id %s in the raw text" % message_id)
        return None
    if len(matching) > 1:
        errors.append("duplicate blocks with id %s (%d) refused" % (message_id, len(matching)))
        return None
    header = matching[0]
    if header.group(2) != "Owner":
        errors.append("block %s is from %r, not Owner" % (message_id, header.group(2)))
        return None
    following = [h for h in headers if h.start() > header.start()]
    end = following[0].start() if following else len(raw_text)
    body_raw = raw_text[header.end():end]
    if not following and not raw_text.endswith("\n"):
        errors.append("block %s is the last block and the text does not end with a newline: possibly truncated" % message_id)
        return None
    body = body_raw.strip()
    if not body:
        errors.append("block %s has an empty body" % message_id)
        return None
    return body


def bind_owner_approval(raw_text, message_id, envelope):
    errors = []
    binding = {"bound": False, "errors": errors, "approval_complete": False, "write_permitted": False,
               "envelope_result": None, "owner_source": None}
    body = extract_owner_block(raw_text, message_id, errors)
    message = envelope.get("owner_message") if isinstance(envelope, dict) else None
    if not isinstance(message, dict):
        errors.append("envelope.owner_message must be an object")
        return _issue_binding(binding)
    if message.get("message_id") != message_id:
        errors.append("envelope names message %r but the bound block is %r" % (message.get("message_id"), message_id))
    if message.get("path") != MAILBOX_PATH:
        errors.append("envelope.owner_message.path must be %s" % MAILBOX_PATH)
    if body is not None:
        reply = message.get("reply_text")
        if reply != body:
            errors.append("envelope reply_text is not exactly the complete owner message body (altered, partial or padded)")
        if message.get("reply_sha256") != _sha(body):
            errors.append("envelope reply_sha256 does not equal the hash of the bound owner message body")
    result = ENVELOPE.validate(envelope)
    binding["envelope_result"] = result
    if not result["valid"]:
        errors.extend("envelope: " + e for e in result["errors"])
    if errors:
        return _issue_binding(binding)
    binding["bound"] = True
    binding["owner_source"] = {"sender": "Owner", "message_id": message_id, "reply_sha256": _sha(body), "path": MAILBOX_PATH}
    approved = {a["field_path"] for a in result["approved_for_review"]}
    binding["approval_complete"] = (not result["unresolved"] and not result["rejected"] and approved == set(ENVELOPE.FIELDS))
    return _issue_binding(binding)


def plan_from_bound(binding, snapshot, context, allow_write=False):
    """Hand a bound result to the planner. Dry-run by default; write only with a complete binding and allow_write=True."""
    issued = _BOUND_DATA.get(binding) if type(binding) is _BoundApproval else None
    if not isinstance(issued, dict) or issued.get("bound") is not True:
        return {"accepted": False, "errors": ["an owner binding from bind_owner_approval() is required"], "steps": [], "writes": []}
    context = dict(context or {})
    if context.get("mode") == "write":
        if not issued.get("approval_complete"):
            return {"accepted": False, "errors": ["write refused: the owner approval is not complete (X-1991 unresolved)"], "steps": [], "writes": []}
        if allow_write is not True:
            return {"accepted": False, "errors": ["write refused: allow_write=True was not given; dry-run is the default"], "steps": [], "writes": []}
    elif "mode" not in context:
        context["mode"] = "dry_run"
    return PLANNER.plan_repair(issued["envelope_result"], snapshot, context, issued["owner_source"])
