"""BK-176..180 (C, implementer; X-2038): PROPOSED status receipt v1.2 for C-1155 runners - successor of v1.1
(runner_status_receipt_proposal_v1_1.py) and v1, both left unchanged while Antigravity's read-only audit continues.

v1.2 changes over v1.1 (closing A-844 findings A-D):
  * BK-176 non-PASS `pass_claims` must also be a list of UNIQUE, valid UPPER_SNAKE keys (it may be empty).
  * BK-177 FAIL vs INCOMPLETE are decided by the evidence, not chosen freely:
           INCOMPLETE  <=> a lock was retained, OR a process was killed on timeout or never started, OR no process ran;
           FAIL        <=> otherwise (every process ran to an end, every lock released) but the run is not PASS.
           needs_operator stays true exactly when a lock was retained (so it implies INCOMPLETE).
  * BK-178 log paths are FILE paths (no trailing '/', last segment `name.ext`) and duplicates are detected with
           Windows case-insensitive equivalence (casefold).
  * BK-179 a log that feeds any measured field, and every process log on a PASS, must carry a valid SHA-256;
           an unhashed (null) log is allowed only on FAIL/INCOMPLETE when no measured field relies on it.

v1.1 changes over v1:
  * BK-171 timestamps are PARSED (calendar-valid date and time, UTC 'Z', up to 7 fractional digits) and compared as
           datetimes, never as strings; 2026-02-30T12:00:00Z or 24:00:00 are refused.
  * BK-172 PASS requires a non-empty, receipt-declared `pass_claims` list; every claim must be a MEASURED field
           (plus any caller-required keys). No claims, no PASS.
  * BK-173 process identities are unambiguous: unique roles, unique PIDs among started processes, unique log paths;
           a measured field must name a STARTED process.
  * BK-174 terminal coherence: PASS also requires every created lock released, every process log fresh, and a fresh
           log for any `killed_marker` termination; a retained lock means the run is not PASS.

Disconnected proposal: no runner writes this format and nothing imports this module. Pure Python - no filesystem,
process, network, Unreal, lock or log access; callers pass the receipt (a dict, or JSON text for parse_receipt_text).
A valid receipt is not runtime proof and not write authorization; X-1991 and C-1155 remain the gates.

Schema `onebossfight.runner-status-receipt/v1.2` (v1 rules below, plus the v1.1 and v1.2 changes above) addresses the
BK-141..165 census findings:
  * terminal outcome  - one explicit outcome (PASS / FAIL / INCOMPLETE) + a failure record whenever it is not PASS
                        (BK-158: 1/34 runners had a verdict; 2/34 wrote anything on failure).
  * measured fields   - every field declares kind measured / unmeasured / config; measured fields name their source,
                        unmeasured fields can never satisfy a required claim (BK-156: 23 unmeasured no-save claims).
  * typed values      - str / int / bool / null only; no NaN, no "True" strings, unique UPPER_SNAKE keys
                        (BK-162: duplicate keys, mixed True/1 booleans, empty KEY= values).
  * run identity      - one 32-hex run token shared, exactly and case-sensitively, by the lock record and the receipt;
                        the evidence folder name contains it (BK-153/159: fixed folders, nothing bound).
  * freshness         - every log a measured field relies on must be marked written after its process started and
                        live inside the per-run evidence folder (BK-154/157: stale-log markers).
  * per-lock release  - created / released / retained lists, with retained locks forcing needs_operator
                        (BK-149: 29 false aggregate counts).
"""
import json
import math
import re
from datetime import datetime, timezone

SCHEMA = "onebossfight.runner-status-receipt/v1.2"
LOCK_PATHS = ("ENGINE_LOCK.json", "Docs/BossCombatReview/Execution/ENGINE_LOCK.json")
EVIDENCE_PREFIX = "Docs/BossCombatReview/Execution/"
HEX32 = re.compile(r"[0-9a-f]{32}")
HEX64 = re.compile(r"[0-9a-f]{64}")
UTC = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,7}))?Z")
KEY = re.compile(r"[A-Z][A-Z0-9_]{1,63}")
SCRIPT = re.compile(r"Scripts/Editor/[A-Za-z0-9_]+\.ps1")
OUTCOMES = {"PASS", "FAIL", "INCOMPLETE"}
TERMINATIONS = {"exited", "killed_timeout", "killed_marker", "not_started"}
KINDS = {"measured", "unmeasured", "config"}
BOOLEAN_SPELLINGS = {"true", "false"}  # one boolean encoding only (BK-162: True/False mixed with 1/0)

TOP_KEYS = {"schema", "runner", "run", "lock", "processes", "fields", "pass_claims", "outcome", "failure", "needs_operator"}
RUNNER_KEYS = {"script", "command_id"}
RUN_KEYS = {"run_token", "started_utc", "finished_utc", "evidence_dir"}
LOCK_KEYS = {"token", "policy", "party", "created", "released", "retained"}
PROCESS_KEYS = {"role", "pid", "started_utc", "finished_utc", "termination", "exit_code", "log"}
LOG_KEYS = {"path", "sha256", "written_after_start"}
FIELD_KEYS = {"key", "kind", "value", "source"}
FAILURE_KEYS = {"stage", "message"}


class DuplicateKeyError(ValueError):
    pass


def _no_duplicates(pairs):
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise DuplicateKeyError("duplicate JSON key %r" % key)
        seen[key] = value
    return seen


def parse_receipt_text(text):
    """Parse receipt JSON strictly: duplicate object keys and NaN/Infinity are refused. Returns (receipt, errors)."""
    if not isinstance(text, str):
        return None, ["receipt text must be a string"]

    def no_constants(name):
        raise ValueError("non-finite number %s is not allowed" % name)

    try:
        return json.loads(text, object_pairs_hook=_no_duplicates, parse_constant=no_constants), []
    except (ValueError, TypeError) as exc:  # json.JSONDecodeError and DuplicateKeyError are ValueErrors
        return None, ["receipt JSON rejected: %s" % exc]


def _enum(value, allowed):
    return isinstance(value, str) and value in allowed


def _shape(obj, keys, label, errors):
    if not isinstance(obj, dict):
        errors.append("%s must be an object" % label)
        return False
    if set(obj) != keys:
        errors.append("%s keys must be exactly %s" % (label, ", ".join(sorted(keys))))
        return False
    return True


def parse_utc(value):
    """Calendar-valid UTC timestamp -> (aware datetime, 7th fractional digit) for exact ordering, or None.
    Accepts YYYY-MM-DDTHH:MM:SS[.f{1,7}]Z only; leap seconds (:60), 24:00 and impossible dates are refused."""
    if not isinstance(value, str):
        return None
    match = UTC.fullmatch(value)
    if match is None:
        return None
    try:
        moment = datetime.strptime(match.group(1), "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None
    fraction = match.group(2) or ""
    micro = int((fraction + "000000")[:6]) if fraction else 0
    tenth_micro = int(fraction[6]) if len(fraction) == 7 else 0  # keep 100 ns precision for ordering only
    return moment.replace(microsecond=micro, tzinfo=timezone.utc), tenth_micro


def _utc(value):
    return parse_utc(value) is not None


def _when(value):
    parsed = parse_utc(value)
    return None if parsed is None else parsed


def _int(value):
    return type(value) is int


def _scalar(value):
    if value is None or type(value) in (str, int, bool):
        return True
    return False


LOG_FILE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*\.[A-Za-z0-9]{1,8}")


def _safe_file(value):
    """A safe repo-relative FILE path: no trailing '/', and the last segment is `name.ext`."""
    return isinstance(value, str) and not value.endswith("/") and _safe_dir(value) \
        and LOG_FILE.fullmatch(value.split("/")[-1]) is not None


def _safe_dir(value):
    if not isinstance(value, str) or not value.startswith(EVIDENCE_PREFIX) or "\\" in value or ":" in value:
        return False
    if any(ord(c) < 32 or ord(c) == 127 for c in value):
        return False
    return all(part not in ("", ".", "..") for part in value.rstrip("/").split("/"))


def validate_receipt(receipt, required_measured=()):
    """Return {valid, errors}; never raises. required_measured: a list/tuple/set/frozenset of UPPER_SNAKE keys that
    must be present as MEASURED fields for a PASS. A malformed requirement (X-2037) makes the result invalid."""
    errors = []
    result = {"valid": False, "errors": errors}
    if not (isinstance(required_measured, (list, tuple, set, frozenset))
            and all(isinstance(k, str) and KEY.fullmatch(k) for k in required_measured)):
        errors.append("required_measured must be a list/tuple/set of UPPER_SNAKE keys")
        return result
    required_measured = sorted(set(required_measured))
    if not _shape(receipt, TOP_KEYS, "receipt", errors):
        return result
    if receipt["schema"] != SCHEMA:
        errors.append("receipt.schema must be %s" % SCHEMA)
        return result

    runner = receipt["runner"]
    if _shape(runner, RUNNER_KEYS, "runner", errors):
        if not (isinstance(runner["script"], str) and SCRIPT.fullmatch(runner["script"])):
            errors.append("runner.script must be a Scripts/Editor/<name>.ps1 path")
        if not (isinstance(runner["command_id"], str) and runner["command_id"].strip()):
            errors.append("runner.command_id must be a non-empty string")

    run = receipt["run"]
    token = None
    if _shape(run, RUN_KEYS, "run", errors):
        token = run["run_token"] if isinstance(run["run_token"], str) and HEX32.fullmatch(run["run_token"]) else None
        if token is None:
            errors.append("run.run_token must be 32 lowercase hex")
        if not (_utc(run["started_utc"]) and _utc(run["finished_utc"])):
            errors.append("run.started_utc and run.finished_utc must be calendar-valid UTC ISO-8601 (...Z)")
        elif _when(run["finished_utc"]) < _when(run["started_utc"]):
            errors.append("run.finished_utc is earlier than run.started_utc")
        if not _safe_dir(run["evidence_dir"]):
            errors.append("run.evidence_dir must be a safe path below %s" % EVIDENCE_PREFIX)
        elif token is not None and token not in run["evidence_dir"].rstrip("/").split("/")[-1]:
            errors.append("run.evidence_dir's last segment must contain the run token (a per-run folder)")

    retained = _lock(receipt["lock"], token, errors)

    roles = _processes(receipt["processes"], run if isinstance(run, dict) else {}, errors)
    measured = _fields(receipt["fields"], roles, errors)

    outcome = receipt["outcome"]
    failure = receipt["failure"]
    if not _enum(outcome, OUTCOMES):
        errors.append("outcome must be PASS, FAIL or INCOMPLETE")
    elif outcome == "PASS":
        if failure is not None:
            errors.append("a PASS receipt cannot carry a failure record")
        for role, proc in roles.items():
            if proc.get("termination") in ("killed_timeout", "not_started"):
                errors.append("PASS is impossible when process %r was %s" % (role, proc.get("termination")))
            if proc.get("termination") == "exited" and proc.get("exit_code") != 0:
                errors.append("PASS requires process %r to exit 0" % role)
        claims = receipt["pass_claims"]
        if not (isinstance(claims, list) and claims and all(isinstance(k, str) for k in claims)
                and len(set(claims)) == len(claims)):
            errors.append("PASS requires a non-empty list of unique pass_claims")
            claims = []
        missing = [k for k in list(claims) + [k for k in required_measured if k not in claims] if k not in measured]
        if missing:
            errors.append("PASS requires measured fields: %s" % ", ".join(sorted(missing)))
        if not roles:
            errors.append("PASS requires at least one launched process")
        for role, proc in roles.items():
            log = proc.get("log")
            if isinstance(log, dict) and log.get("written_after_start") is not True:
                errors.append("PASS requires every process log to be proven fresh (%r is not)" % role)
        if retained:
            errors.append("PASS is impossible while a lock is retained; report INCOMPLETE with needs_operator")
        for role, proc in roles.items():
            log = proc.get("log")
            if isinstance(log, dict) and not (isinstance(log.get("sha256"), str) and HEX64.fullmatch(log["sha256"])):
                errors.append("PASS requires every process log to carry a valid sha256 (%r does not)" % role)
    else:
        claims = receipt["pass_claims"]
        if not (isinstance(claims, list) and all(isinstance(k, str) and KEY.fullmatch(k) for k in claims)
                and len(set(claims)) == len(claims)):
            errors.append("pass_claims must be a list of unique UPPER_SNAKE keys")
        incomplete_because = []
        if retained:
            incomplete_because.append("a lock was retained")
        if any(p.get("termination") in ("killed_timeout", "not_started") for p in roles.values()):
            incomplete_because.append("a process timed out or never started")
        if not roles:
            incomplete_because.append("no process ran")
        if outcome == "FAIL" and incomplete_because:
            errors.append("FAIL is not allowed when %s; report INCOMPLETE" % "; ".join(incomplete_because))
        if outcome == "INCOMPLETE" and not incomplete_because:
            errors.append("INCOMPLETE requires a retained lock, a timed-out or unstarted process, or no process; "
                          "every process ended and every lock was released, so report FAIL")
        if _shape(failure, FAILURE_KEYS, "failure", errors):
            if not all(isinstance(failure[k], str) and failure[k].strip() for k in FAILURE_KEYS):
                errors.append("failure.stage and failure.message must be non-empty strings")
            elif any(c in failure["message"] for c in "\r\n"):
                errors.append("failure.message must be a single line")

    if type(receipt["needs_operator"]) is not bool:
        errors.append("needs_operator must be a boolean")
    elif receipt["needs_operator"] != bool(retained):
        errors.append("needs_operator must be true exactly when a lock was retained")

    result["valid"] = not errors
    return result


def _lock(lock, token, errors):
    if not _shape(lock, LOCK_KEYS, "lock", errors):
        return []
    if not (isinstance(lock["token"], str) and token is not None and lock["token"] == token):
        errors.append("lock.token must equal run.run_token exactly (case-sensitive)")
    if lock["policy"] != "C-1155" or not _enum(lock["party"], {"X", "C", "A"}):
        errors.append("lock must be a team C-1155 lock (party X/C/A)")
    lists = [lock[k] for k in ("created", "released", "retained")]
    if not all(isinstance(l, list) and all(isinstance(p, str) for p in l) for l in lists):
        errors.append("lock.created/released/retained must be lists of paths")
        return []
    created, released, retained = lists
    if created != list(LOCK_PATHS[:len(created)]) or not created:
        errors.append("lock.created must list the canonical locks in creation order (root first), at least one")
    if len(set(released)) != len(released) or len(set(retained)) != len(retained) or set(released) & set(retained):
        errors.append("lock.released and lock.retained must be disjoint lists without repeats")
    if sorted(released + retained) != sorted(created):
        errors.append("every created lock must be listed exactly once as released or retained")
    return retained


def _processes(processes, run, errors):
    roles, pids, logs = {}, set(), set()
    if not (isinstance(processes, list) and len(processes) <= 16):
        errors.append("processes must be a list of at most 16 records")
        return roles
    start, finish = run.get("started_utc"), run.get("finished_utc")
    evidence = run.get("evidence_dir") if isinstance(run.get("evidence_dir"), str) else None
    for index, proc in enumerate(processes):
        label = "processes[%d]" % index
        if not _shape(proc, PROCESS_KEYS, label, errors):
            continue
        role = proc["role"]
        if not (isinstance(role, str) and KEY.fullmatch(role.upper()) and role == role.lower()):
            errors.append("%s.role must be a lowercase identifier" % label)
            continue
        if role in roles:
            errors.append("%s.role %r is repeated" % (label, role))
            continue
        roles[role] = proc
        if not _enum(proc["termination"], TERMINATIONS):
            errors.append("%s.termination must be one of %s" % (label, ", ".join(sorted(TERMINATIONS))))
            continue
        started = proc["termination"] != "not_started"
        if started:
            if not (_int(proc["pid"]) and proc["pid"] > 0):
                errors.append("%s.pid must be a positive integer for a started process" % label)
            elif proc["pid"] in pids:
                errors.append("%s.pid %d is already used by another process in this run" % (label, proc["pid"]))
            else:
                pids.add(proc["pid"])
            if not (_utc(proc["started_utc"]) and _utc(proc["finished_utc"])):
                errors.append("%s times must be calendar-valid UTC ISO-8601" % label)
            elif _utc(start) and _utc(finish) and not (
                    _when(start) <= _when(proc["started_utc"]) <= _when(proc["finished_utc"]) <= _when(finish)):
                errors.append("%s must start and finish inside the run window" % label)
        elif any(proc[k] is not None for k in ("pid", "started_utc", "finished_utc", "exit_code", "log")):
            errors.append("%s was not started and cannot claim a pid, times, exit code or log" % label)
        if proc["termination"] == "exited":
            if not _int(proc["exit_code"]):
                errors.append("%s.exit_code must be an integer when the process exited" % label)
        elif proc["exit_code"] is not None:
            errors.append("%s.exit_code must be null unless the process exited" % label)
        log = proc["log"]
        if proc["termination"] == "killed_marker" and not (isinstance(log, dict) and log.get("written_after_start") is True):
            errors.append("%s was killed on a marker, so its log must exist and be proven fresh" % label)
        if log is not None and _shape(log, LOG_KEYS, label + ".log", errors):
            if isinstance(log["path"], str):
                folded = log["path"].casefold()
                if folded in logs:
                    errors.append("%s.log.path is shared with another process (Windows paths compare case-insensitively)" % label)
                logs.add(folded)
            if not (isinstance(log["path"], str) and evidence and log["path"].startswith(evidence.rstrip("/") + "/")
                    and _safe_file(log["path"])):
                errors.append("%s.log.path must be a file (name.ext, no trailing '/') inside run.evidence_dir" % label)
            if log["sha256"] is not None and not (isinstance(log["sha256"], str) and HEX64.fullmatch(log["sha256"])):
                errors.append("%s.log.sha256 must be null or 64 lowercase hex" % label)
            if type(log["written_after_start"]) is not bool:
                errors.append("%s.log.written_after_start must be a boolean" % label)
    return roles


def _fields(fields, roles, errors):
    measured = set()
    if not (isinstance(fields, list) and len(fields) <= 256):
        errors.append("fields must be a list of at most 256 records")
        return measured
    seen = set()
    for index, field in enumerate(fields):
        label = "fields[%d]" % index
        if not _shape(field, FIELD_KEYS, label, errors):
            continue
        key = field["key"]
        if not (isinstance(key, str) and KEY.fullmatch(key)):
            errors.append("%s.key must be UPPER_SNAKE" % label)
            continue
        if key in seen:
            errors.append("%s.key %s is duplicated" % (label, key))
            continue
        seen.add(key)
        value = field["value"]
        if not _scalar(value) or (isinstance(value, str) and any(c in value for c in "\r\n")):
            errors.append("%s.value must be a single-line string, integer, boolean or null" % label)
        elif isinstance(value, str) and value.strip().lower() in BOOLEAN_SPELLINGS:
            errors.append("%s.value spells a boolean as a string; use a JSON boolean" % label)
        if not _enum(field["kind"], KINDS):
            errors.append("%s.kind must be measured, unmeasured or config" % label)
            continue
        if field["kind"] == "measured":
            source = field["source"]
            proc = roles.get(source) if isinstance(source, str) else None
            if proc is None:
                errors.append("%s is measured but its source is not a listed process role" % label)
                continue
            if proc.get("termination") == "not_started":
                errors.append("%s is measured from a process that never started" % label)
                continue
            log = proc.get("log")
            if not (isinstance(log, dict) and log.get("written_after_start") is True):
                errors.append("%s is measured from a log that is missing or not proven fresh" % label)
                continue
            if not (isinstance(log.get("sha256"), str) and HEX64.fullmatch(log["sha256"])):
                errors.append("%s is measured from a log without a valid sha256" % label)
                continue
            if value is None:
                errors.append("%s is measured but has no value" % label)
                continue
            measured.add(key)
        elif field["source"] is not None:
            errors.append("%s.source must be null for an unmeasured or config field" % label)
    return measured
