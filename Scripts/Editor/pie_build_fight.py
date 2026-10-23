"""
Gate 3, M14 (G3-6): the balance run. A scripted PLAYER BOT fights the REAL boss (not held: no hold_for_test, the pack's behaviour tree runs) with the build named in Saved/build_fight_build.txt (Starter, Strength or Dex,
default Strength), from the boss's wake to the boss's death, the player's death or 240 s of fight time, and logs balance metrics. The checks are SANITY only (it ran, the build was equipped, the fight started, the metrics were
logged): balance is read by a human from the [BuildFight] METRIC lines. RESULT n/m passed counts the same m checks (10) however the fight ends.
Read Documentation/M14_FIGHT_NOTES.md first: it lists every API the bot uses, what is NOT verified and where the bot is weak. Written without running the editor: the first run is a debugging run.

WHAT THE BOT DOES (one decision per frame, in this order; every decision is logged with its reason, prefix [BuildFight]):
  1 DODGE     the boss's attack tracker (RPGAttackTracker) says a tracked attack is in Windup, Committed or the first 0.12 s of Active: the dodge key goes down so that the dodge's i-frames (0.16 to 0.46 s after the key
              goes down, measured by pie_iframes.py) cover the start of the attack's active window. One dodge per attack instance, at least 0.45 s between presses (a closer second press is the full roll: RPGDodgeTiming).
              Direction per move in PLAN (sideways for the quick swings, forward through the A2 slam, backward for the A6 wave). A boss montage the tracker does not know (the pack's mid range and sprint attacks) is dodged
              0.2 s into the montage (a guess) and its name is logged so the owner can add it to the tracker.
  2 RIPOSTE   the boss is down (stance break) and RPGBossStagger.is_riposte_available(pawn): Light Attack press. While it is not available the bot walks round to the boss's front (within 130 cm, 55 degrees).
  3 PUNISH    a boss opening (the Recovery phase of a tracked attack, the stance break after the riposte, the phase two roar) that is long enough: close in to the strike range and throw the build's opener:
              Strength: strong (jump heavy in a long stagger), Dex: light chain of three taps, Starter: light (two taps), strong in a stagger. Stamina must stay above the swing cost plus a dodge reserve.
  4 SPACING   while the boss is neutral: approach beyond 380 cm, back off inside 230 cm; after 14 s without any boss attack or opening the bot walks up and throws one bait light attack.
The bot never heals, never refills (one refill BEFORE the wake, to start from a defined state), never touches the boss's health, posture or components. The pawn is turned to the boss with set_actor_rotation when no
montage plays (the stand-in for the lock-on, as pie_pack_fight.py does) and the control rotation looks at the boss (so the IA_Move stick axes are boss relative). Only real input goes in: inject_action and set_key_down.

SETUP: rpg.Build is set before the PIE starts (and again if the loadout has no choice), the boss is reset (dormant), the driver waits for the loadout (style and state Idle) while the boss sleeps, refills once, enters
combat mode, places the player 800 cm in front of the boss and lets the boss wake by itself (the gate is 1200 cm; wake() only if it does not within 6 s).
OUTCOMES: boss_dead (boss health 0, death component dying/dead, or the HUD's Victory), player_dead (player health 0 or a new pawn: the encounter resets, the run stops), timeout (240 s of world time since the wake),
or setup_failed / boss_missing (sanity failures). Run pie_debug_overlay.py once after an editor start first; the warm-up of RunDrivers.ps1 (no_throttle.py, legend_off.py, build_off.py) must have run.
Log prefix [BuildFight]; the metric lines are also written to Saved/build_fight_result_<Build>.txt; ends with RESULT n/m passed.
"""
import math
import os
import re
import datetime
import hashlib
import json
import uuid
import unreal

log = lambda m: unreal.log("[BuildFight] " + m)

# ===================================================================================================================================================================================================
# 0. SCENARIO FILE AND TABLES
# ===================================================================================================================================================================================================
SAVED = os.path.join(unreal.SystemLibrary.get_project_directory(), "Saved")
BUILDS = ("Starter", "Strength", "Dex")
POLICY = "close-recovery-v3"
RUN_ID = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S") + "_" + uuid.uuid4().hex[:8]
SCRIPT_PATH = os.path.join(unreal.SystemLibrary.get_project_directory(), "Scripts", "Editor", "pie_build_fight.py")
with open(SCRIPT_PATH, "rb") as source_file:
    SOURCE_HASH = hashlib.sha256(source_file.read()).hexdigest()


def read_build():
    """The build of this run from Saved/build_fight_build.txt (read at import; a BOM from PowerShell is fine). Returns (build, where it came from)."""
    path = os.path.join(SAVED, "build_fight_build.txt")
    try:
        if os.path.exists(path):
            with open(path, encoding="utf-8-sig") as f:
                words = f.read().split()
            text = words[0] if words else ""
            hit = next((b for b in BUILDS if b.lower() == text.lower()), None) if len(words) == 1 else None
            if hit:
                return hit, "Saved/build_fight_build.txt"
            return "Invalid", "the scenario file does not name Starter, Strength or Dex"
    except Exception as e:
        return "Invalid", "the scenario file is unreadable: %s" % type(e).__name__
    return "Invalid", "the scenario file is missing"


BUILD, BUILD_NOTE = read_build()

IA = "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/"
DODGE_KEY = "Gamepad_FaceButton_Right"   # pie_iframes.py, pie_dodge.py
JUMP_KEY = "Gamepad_FaceButton_Bottom"   # pie_builds.py, pie_hyperarmor.py

# From pie_builds.py (the loadout's own names).
STYLE = {"Starter": "SwordCombatStyle", "Strength": "ClaymoreCombatStyle", "Dex": "DualSwordCombatStyle"}
ABILITY = {"Starter": "GA_Sword_Melee_C", "Strength": "GA_Claymore_Melee_C", "Dex": "GA_DuaSword_Melee_C"}
ACTOR = {"Starter": "BP_ToughSword_C", "Strength": "BP_KwangSword_C", "Dex": "BP_DualSteelSwords_C"}

KINDS = ("Light", "Strong", "Charged", "JumpLight", "JumpHeavy")
# Stamina of one swing of (build, kind): the weapon attack table (RPGWeaponAttackTable::FillDefaults, as ROWS in pie_builds.py); the starter sword keeps the pack's 15 (M13_BUILDS_PLAN.md section 3.1).
COST = {
    "Starter": {"Light": 15.0, "Strong": 15.0, "Charged": 15.0, "JumpLight": 15.0, "JumpHeavy": 15.0},
    "Strength": {"Light": 15.0, "Strong": 35.0, "Charged": 35.0, "JumpLight": 15.0, "JumpHeavy": 35.0},
    "Dex": {"Light": 10.0, "Strong": 10.0, "Charged": 10.0, "JumpLight": 10.0, "JumpHeavy": 10.0},
}
# Which kinds a weapon has (CAPS of pie_builds.py; the starter sword is assumed to have all five: the claymore shares its strong, charged and falling montages).
CAPS = {
    "Starter": {"Light": True, "Strong": True, "Charged": True, "JumpLight": True, "JumpHeavy": True},
    "Strength": {"Light": True, "Strong": True, "Charged": True, "JumpLight": True, "JumpHeavy": True},
    "Dex": {"Light": True, "Strong": True, "Charged": False, "JumpLight": True, "JumpHeavy": True},
}
# kind -> (input action, seconds held, jump first): ACTIONS of pie_builds.py.
ACTIONS = {
    "Light": ("IA_NormalAttack", 0.12, False),
    "Strong": ("IA_StrongAttack", 0.12, False),
    "Charged": ("IA_ChargedAttack", 1.6, False),
    "JumpLight": ("IA_NormalAttack", 0.12, True),
    "JumpHeavy": ("IA_StrongAttack", 0.12, True),
}
# GUESSES (nothing measured): seconds from the press to the first hit. The log prints the measured delay of every swing; replace these numbers with the medians.
HIT_DELAY = {"Light": 0.34, "Strong": 0.69, "Charged": 1.9, "JumpLight": 0.55, "JumpHeavy": 0.85}
# The opener of each build by kind of opening: first one that fits the time left and the stamina wins.
OPENERS = {
    "Strength": {"stagger": ["JumpHeavy", "Strong", "Light"], "recovery": ["Strong", "Light"], "roar": ["Strong", "Light"]},
    "Dex": {"stagger": ["Light"], "recovery": ["Light"], "roar": ["Light"]},
    "Starter": {"stagger": ["Strong", "Light"], "recovery": ["Strong", "Light"], "roar": ["Strong", "Light"]},
}
CHAIN = {"Strength": 1, "Dex": 3, "Starter": 2}   # taps of a Light opener (pie_builds.py B6 taps three times, 0.5 s apart)
TAP_SPACING = 0.5
HEAVY_KINDS = ("Strong", "Charged", "JumpHeavy")
HEAVY_OPENER_BUILDS = ("Starter", "Strength")

# ===================================================================================================================================================================================================
# 1. KNOBS OF THE BOT (all guesses until a run says otherwise; each is named in the notes)
# ===================================================================================================================================================================================================
LIMIT_FIGHT_S = 420.0          # world seconds from the wake (the first run, Strength, left the boss at 51 of 500 health after 240 s)
LIMIT_RUN_S = 720.0            # real seconds from the first frame with a pawn and a boss, whatever the world clock does (a paused world must not hang the editor)
SETTLE_S = 9.0                 # the pack needs this long after the PIE start (pie_builds.py)
START_DIST = 800.0             # cm in front of the boss at the wake (inside the 1200 cm gate)
RESET_DIST = 1600.0            # cm during reset: outside the 1200 cm wake gate
BASE_BOSS_HEALTH = 500.0       # encounter contract; verified before a balance run starts
BASE_POSTURE = 100.0           # own posture-pool contract; verified before a balance run starts
REFILL_BEFORE_FIGHT = True     # one debug_refill_player() before the wake; the bot is never healed afterwards
STRIKE_RANGE0 = 125.0
STRIKE_MIN = 110.0
WALK_SPEED = 450.0             # cm/s, a guess used only to decide whether a closing walk fits an opening (measured speed is logged)
SPACING_MIN = 170.0
SPACING_MAX = 260.0
RETREAT = False
WALL_RADIUS = 1000.0           # cm from the boss's home beyond which the bot does not back off any further (the arena radius is not read)
BAIT_AFTER_S = 1.0
DODGE_PRESS_S = 0.08           # the key stays down this long (pie_iframes.py); the pack dodges when it is released
DODGE_MIN_GAP = 0.45           # two presses closer than RPGDodgeTiming.DoubleTapWindow (0.30 s) would be the full roll
DODGE_STAMINA_MIN = 12.0       # below this the bot does not even press (the cost of a dodge is not known: the log samples it)
DODGE_RESERVE = 20.0           # a swing is only thrown when stamina stays above its cost plus this
IFRAME_FIRST = 0.162           # s after the key goes down: first i-frame (montage 0.107 s at rate 1.3 plus the 0.08 s press), pie_iframes.py QUICK_WINDOW
IFRAME_LAST = 0.457            # last i-frame
CLOSE_DODGE = "flank"
FLANK = (0.5, 0.866)
UNTRACKED_DODGE_AT = 0.20      # montage seconds at which an unknown boss attack montage is dodged
UNTRACKED_REACH = 700.0
OPENING_MIN = 0.45             # an opening shorter than this (real seconds) is logged but not counted as usable
RIPOSTE_GO = 130.0             # distance at which the bot stops walking for the riposte (the rule is 150 cm centre to centre)
RIPOSTE_CONE = 55.0            # degrees off the boss's front allowed for the riposte (the rule is 60)
RIPOSTE_WAIT_S = 1.6           # seconds after the start of the stance break the bot keeps trying for the riposte; then it hits the kneeling boss instead
LOW_STAMINA = 15.0

# Tracked moves: move -> (dodge direction, seconds before the active window at which the key goes down, reach in cm beyond which the bot does not dodge).
#   aim 0.30: the i-frames (0.16 to 0.46 s after the key) cover 0.14 s before to 0.16 s after the start of the active window. aim 0.25 for the A2 slam: its hurting window opens at 1.93 s and the measured hit was at 2.00.
#   aim 0.15 for the A6 wave: the wave starts at the active start and reaches a player 350 to 450 cm away 0.15 to 0.35 s later.
#   "close" = sideways or flank (CLOSE_DODGE), "in" = stick forward (the roll ends at the boss's feet, ready for the A2 recovery), "back" = no stick (the dodge turns away from the camera: RPGDodgeTiming).
PLAN = {
    "A1": ("close", 0.30, 330.0), "A1b": ("close", 0.30, 330.0), "A3a": ("close", 0.30, 330.0), "A3b": ("close", 0.30, 330.0),
    "A2": ("in", 0.25, 450.0),
    "A6": ("jump", 0.15, 1200.0),
    "A4": ("back", 0.25, 450.0),
    "A5": ("close", 0.20, 1100.0),
}
# Built-in copy of the tracker's table (RPGAttackTracker.cpp constructor); the live table is read at the start and replaces it. (commit, active start, active end, recovery end), pack montage name.
DEFAULT_TIMING = {
    "A2": (1.68, 1.93, 2.11, 3.14, "GS_ChargedAttack_Montage"),
    "A1": (0.08, 0.12, 0.42, 1.04, "GS_Attack03_Montage"), "A1b": (0.12, 0.16, 0.46, 1.25, "GS_Attack04_Montage"),
    "A3a": (0.13, 0.17, 0.47, 0.54, "GS_Attack01_Montage"), "A3b": (0.10, 0.14, 0.44, 1.20, "GS_Attack02_Montage"),
    "A6": (0.16, 0.75, 1.17, 1.80, "GS_LeapAttack_Montage"),
    "A4": (0.40, 0.60, 0.90, 1.75, "AN_Boss01_A4_LowSweep"), "A5": (0.45, 0.45, 0.50, 0.95, "AN_Boss01_A5_JavelinThrow"),
}
TIMING = {k: {"commit": v[0], "active_start": v[1], "active_end": v[2], "recovery_end": v[3], "montage": v[4]} for k, v in DEFAULT_TIMING.items()}
TRACKED_NAMES = set(v["montage"] for v in TIMING.values())
# Boss montages the tracker does not know that look like attacks (the pack's mid range and sprint attacks): the words are guesses, every new montage name is logged.
ATTACK_WORDS = ("attack", "slash", "swing", "slam", "mid", "sprint", "lunge", "charge", "leap", "smash", "combo", "strike", "retaliation", "overhead", "sweep")
IGNORE_WORDS = ("knockdown", "getup", "intro", "death", "hitreact", "hit_react", "stun", "equip", "draw", "enter", "exit", "turn", "an_boss01_", "an_riposte", "roar", "dormant", "wake", "stagger", "kneel")

# ===================================================================================================================================================================================================
# 2. STATE
# ===================================================================================================================================================================================================
S = {"phase": "start", "t": 0.0, "run_t": 0.0, "now": 0.0, "w": None, "gen": None, "hb": 0.0, "P": None, "O": None, "C": {}, "finished": False, "errors": 0,
     "inject": {}, "keys_until": {}, "key_state": {}, "stick": None, "stick_until": 0.0, "face": False, "ia": {}, "inject_warned": False,
     "pawn_name": None, "gone": 0.0, "nopawn": 0.0, "home": None, "style0": None,
     "last_dodge_t": -99.0, "dodged_inst": -1, "dodged_bm": -1, "side": 1.0, "strike": STRIKE_RANGE0, "event_t": 0.0,
     "rip_done": {}, "rip_presses": {}, "stag_n_seen": 0, "stag_t0": 0.0, "roar_n": 0, "roar_t0": 0.0, "was_transition": False,
     "bm_last": None, "bm_last_pos": 0.0, "bm_serial": 0, "mode": None, "last_skip": "", "decision_t": -1.0}
handle = None
TAGS = {}
WARNED = set()
CMAPS = {}


def new_metrics():
    return {"outcome": None, "why": "", "error": None, "flags": {"parts": False, "slept": False, "build_ok": False, "intake_bound": False},
            "fight_on": False, "t0": None, "fight_t": 0.0, "last_t": 0.0, "end_t": None, "woke_by": "distance",
            "boss_hp0": None, "boss_hp_last": None, "boss_hp_max": None, "pl_hp0": None, "pl_hp_last": None, "pl_hp_min": None, "pl_st0": None,
            "st_min": None, "st_min_t": 0.0, "st_low_s": 0.0, "st_dips": 0, "st_dip": False,
            "hp_hit": 0.0, "hp_bleed": 0.0, "hp_rip": 0.0, "hp_unmatched": 0.0, "hp_by_kind": {}, "pend_drops": [], "pend_recs": [], "rec_no_drop": 0, "drop_no_rec": 0,
            "hits": 0, "hits_seen": 0, "hits_kind": {}, "swings_seen": 0, "swings_kind": {}, "presses": {}, "presses_total": 0, "whiffs": 0, "ignored": 0, "swing_delays": {}, "cuts": 0,
            "procs_seen": 0, "rip_imp_seen": 0, "base": {}, "rip_press": 0, "rip_accepted": 0, "rip_rejected": 0,
    "dodge_presses": 0, "dodge_montages": 0, "dodge_quick": 0, "dodge_full": 0, "dodge_refused": 0, "dodge_late": 0, "dodge_costs": [], "wave_jumps": 0, "was_dodging": False,
            "taken": [], "taken_total": 0.0, "pl_regen": 0.0, "inst": {}, "cur_inst": None, "inst_seen_t": 0.0, "attacks": {}, "untracked": {},
            "brain_inactive_s": 0.0, "neutral_inactive_s": 0.0, "move_blocked_s": 0.0,
            "openings": [], "open_cur": None, "p2_t": None, "p2_hp": None, "style_changes": 0, "walk_sum": 0.0, "walk_n": 0, "last_pos": None, "metrics_lines": 0}


M = new_metrics()
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append(bool(ok))
    log("%s %s %s" % ("PASS" if ok else "FAIL", name, detail))


# ===================================================================================================================================================================================================
# 3. SMALL HELPERS (P(), comp(), attr(), console(): as in pie_builds.py)
# ===================================================================================================================================================================================================
def safe(key, fn, default=None):
    """Calls fn; the FIRST failure of each key is logged ('API PROBLEM key'), later ones are silent. A name that does not exist in this engine build ends up here, not as a crash."""
    try:
        return fn()
    except Exception as e:
        if key not in WARNED:
            WARNED.add(key)
            log("API PROBLEM %s: %s: %s" % (key, type(e).__name__, str(e)[:180]))
        return default


def tag_obj(name):
    t = TAGS.get(name)
    if t is None:
        t = unreal.GameplayTag()
        t.import_text('(TagName="%s")' % name)
        TAGS[name] = t
    return t


def tags(*names):
    c = unreal.GameplayTagContainer()
    c.import_text("(GameplayTags=(%s))" % ",".join('(TagName="%s")' % n for n in names))
    return c


def cmap(actor):
    """class name -> first component of the actor (plus '__mesh' = first skeletal mesh, '__move' = character movement), refreshed every 3 real seconds."""
    if actor is None:
        return {}
    key = actor.get_name()
    ent = CMAPS.get(key)
    if ent is None or S["t"] - ent[0] > 3.0:
        m = {}
        for c in actor.get_components_by_class(unreal.ActorComponent):
            m.setdefault(c.get_class().get_name(), c)
        # the boss look adds follower meshes (RPGLook...) that have no animation instance: the pack mesh is the one that plays the montages
        meshes = [c for c in actor.get_components_by_class(unreal.SkeletalMeshComponent) if not c.get_name().startswith("RPGLook")]
        moves = actor.get_components_by_class(unreal.CharacterMovementComponent)
        m["__mesh"] = meshes[0] if meshes else None
        m["__move"] = moves[0] if moves else None
        ent = (S["t"], m)
        CMAPS[key] = ent
    return ent[1]


def comp(actor, name):
    return cmap(actor).get(name)


def attr(actor, tag):
    c = comp(actor, "BP_AttributesComponent_C")
    if c is None:
        return None
    try:
        return c.call_method("Get Current Attribute Value", args=(tag_obj(tag),))
    except Exception:
        return None


def world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()


def actors():
    w = world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0) if w else None
    pawn = pc.get_controlled_pawn() if pc else None
    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Character) if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None) if w else None
    return w, pc, pawn, boss


def console(cmd):
    """A console command in the game world, or the editor world before the PIE starts: rpg.Build is process wide."""
    try:
        w = world()
        if w is None:
            w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
        unreal.SystemLibrary.execute_console_command(w, cmd)
    except Exception as e:
        log("console command '%s' failed: %s" % (cmd, e))


def parts():
    return S["C"]


def ia(name):
    a = S["ia"].get(name)
    if a is None:
        a = unreal.load_asset(IA + name)
        S["ia"][name] = a
    return a


def ang_diff(a, b):
    """Signed difference a - b in degrees, -180 to 180."""
    return (a - b + 180.0) % 360.0 - 180.0


def montage_of(actor):
    """(name, position) of the actor's active montage, or (None, 0.0): the calls of pie_pack_fight.py."""
    mesh = comp(actor, "__mesh")
    inst = mesh.get_anim_instance() if mesh else None
    m = inst.get_current_active_montage() if inst else None
    if m is None:
        return None, 0.0
    return m.get_name(), float(inst.montage_get_position(m))


def attack_like(name):
    low = name.lower()
    if any(w in low for w in IGNORE_WORDS):
        return False
    return any(w in low for w in ATTACK_WORDS)


def avg(xs):
    return sum(xs) / len(xs) if xs else 0.0


def counts_text(d):
    return ", ".join("%s %d" % (k, v) for k, v in sorted(d.items())) or "none"


# ===================================================================================================================================================================================================
# 4. OBSERVATION: one dict per frame (every read of the world is here; the bot's decisions read only this dict)
# ===================================================================================================================================================================================================
def observe(p):
    pawn, boss = p["pawn"], p["boss"]
    cb, cp = cmap(boss), cmap(pawn)
    C = {"tr": cb.get("RPGAttackTracker"), "stg": cb.get("RPGBossStagger"), "post": cb.get("RPGBossPosture"), "ph": cb.get("RPGBossPhases"), "enc": cb.get("RPGBossEncounter"),
         "death": cb.get("RPGBossDeath"), "hud": cb.get("RPGBossHud"), "bleed": cb.get("RPGBossBleed"), "dbg": cb.get("RPGCombatDebug"),
         "swing": cp.get("RPGSwingTracker"), "intake": cp.get("RPGHitIntake"), "ld": cp.get("RPGBuildLoadout"), "dodge": cp.get("RPGDodgeTiming"), "mon": cp.get("RPGIFrameMonitor")}
    S["C"] = C
    tr, stg, post, ph, enc, death, hud, bleed = (C[k] for k in ("tr", "stg", "post", "ph", "enc", "death", "hud", "bleed"))
    swing, intake, ld, dodge, mon = (C[k] for k in ("swing", "intake", "ld", "dodge", "mon"))
    O = {"t": S["now"]}
    pl, bl = pawn.get_actor_location(), boss.get_actor_location()
    dx, dy = bl.x - pl.x, bl.y - pl.y
    O["px"], O["py"], O["bx"], O["by"] = pl.x, pl.y, bl.x, bl.y
    O["dist"] = math.hypot(dx, dy)
    O["yaw_to_boss"] = math.degrees(math.atan2(dy, dx))
    O["boss_yaw"] = boss.get_actor_rotation().yaw
    # where the player stands round the boss: 0 = straight in front of it (the riposte cone is measured from here)
    O["polar"] = ang_diff(math.degrees(math.atan2(-dy, -dx)), O["boss_yaw"])
    O["off_front"] = abs(O["polar"])
    home = S["home"]
    O["home_dist"] = math.hypot(pl.x - home[0], pl.y - home[1]) if home else 0.0
    controller = boss.get_controller()
    brains = controller.get_components_by_class(unreal.BrainComponent) if controller else []
    O["brain_running"] = bool(brains[0].is_running()) if brains else None
    O["move_ignored"] = p["pc"].is_move_input_ignored()
    O["test_freeze"] = bool(safe("enc.test_freeze", lambda: enc.get_editor_property("test_freeze"), False)) if enc else None
    player_velocity, boss_velocity = pawn.get_velocity(), boss.get_velocity()
    O["player_speed"] = math.hypot(player_velocity.x, player_velocity.y)
    O["boss_speed"] = math.hypot(boss_velocity.x, boss_velocity.y)
    # attributes
    O["boss_hp"] = attr(boss, "Attribute.Health")
    O["pl_hp"] = attr(pawn, "Attribute.Health")
    O["pl_st"] = attr(pawn, "Attribute.Stamina")
    # montages
    pm, ppos = montage_of(pawn)
    bm, bpos = montage_of(boss)
    low = (pm or "").lower()
    O["pmontage"], O["ppos"] = pm, ppos
    O["dodging"] = bool(pm) and ("dodge" in low or "roll" in low)
    O["bmontage"], O["bpos"] = bm, bpos
    mv = cmap(pawn).get("__move")
    O["falling"] = bool(safe("move.is_falling", lambda: mv.is_falling(), False)) if mv else False
    # the boss's tracker (names of RPGAttackTracker.h)
    O["move"] = str(safe("tr.get_current_move", lambda: tr.get_current_move(), "None")) if tr else "None"
    O["phase"] = safe("tr.get_phase_name", lambda: tr.get_phase_name(), "None") if tr else "None"
    O["pos"] = float(safe("tr.get_position", lambda: tr.get_position(), 0.0)) if tr else 0.0
    O["inst"] = int(safe("tr.get_attack_instance", lambda: tr.get_attack_instance(), 0)) if tr else 0
    # stagger and riposte (RPGBossStagger.h)
    O["stag"] = bool(safe("stg.is_staggered", lambda: stg.is_staggered(), False)) if stg else False
    O["stage"] = safe("stg.get_clip_stage_name", lambda: stg.get_clip_stage_name(), "none") if stg else "none"
    O["rip_avail"] = bool(safe("stg.is_riposte_available", lambda: stg.is_riposte_available(pawn), False)) if stg else False
    O["rip_exec"] = bool(safe("stg.is_riposte_executing", lambda: stg.is_riposte_executing(), False)) if stg else False
    O["riposting"] = O["rip_exec"]
    O["stag_n"] = int(safe("stg.get_stagger_count", lambda: stg.get_stagger_count(), 0)) if stg else 0
    O["rip_count"] = int(safe("stg.get_riposte_count", lambda: stg.get_riposte_count(), 0)) if stg else 0
    O["rip_imp"] = int(safe("stg.get_riposte_impact_count", lambda: stg.get_riposte_impact_count(), 0)) if stg else 0
    O["rip_rej"] = int(safe("stg.get_riposte_reject_count", lambda: stg.get_riposte_reject_count(), 0)) if stg else 0
    O["posture"] = float(safe("post.get_posture", lambda: post.get_posture(), -1.0)) if post else -1.0
    # phases, encounter, death
    O["phase2"] = bool(safe("ph.is_phase_two", lambda: ph.is_phase_two(), False)) if ph else False
    O["transition"] = bool(safe("ph.is_in_transition", lambda: ph.is_in_transition(), False)) if ph else False
    O["rate"] = S.get("attack_rate", 1.2) if O["phase2"] else 1.0
    O["dormant"] = bool(safe("enc.is_dormant", lambda: enc.is_dormant(), False)) if enc else False
    O["death_state"] = safe("death.get_death_state_name", lambda: death.get_death_state_name(), "alive") if death else "alive"
    O["hud_state"] = safe("hud.get_state_name", lambda: hud.get_state_name(), "") if hud else ""
    # bleed, hit intake, swing tracker, dodge component
    O["procs"] = int(safe("bleed.get_proc_count", lambda: bleed.get_proc_count(), 0)) if bleed else 0
    O["proc_dmg"] = float(safe("bleed.get_last_proc_damage", lambda: bleed.get_last_proc_damage(), 0.0)) if bleed else 0.0
    O["hits"] = int(safe("intake.get_boss_hit_count", lambda: intake.get_boss_hit_count(), 0)) if intake else 0
    O["swings"] = int(safe("swing.get_attack_swing_count", lambda: swing.get_attack_swing_count(), 0)) if swing else 0
    O["dodge_presses"] = int(safe("dodge.get_press_count", lambda: dodge.get_press_count(), 0)) if dodge else 0
    O["invuln"] = bool(safe("mon.is_invulnerable_now", lambda: mon.is_invulnerable_now(), False)) if mon else False
    O["style"] = safe("ld.get_actual_style_name", lambda: ld.get_actual_style_name(), "") if ld else ""
    # stance break and roar clocks (the opening estimate needs the start)
    if O["stag_n"] != S["stag_n_seen"]:
        S["stag_n_seen"] = O["stag_n"]
        S["stag_t0"] = O["t"]
    if O["transition"] and not S["was_transition"]:
        S["roar_n"] += 1
        S["roar_t0"] = O["t"]
    S["was_transition"] = O["transition"]
    O["roar_n"] = S["roar_n"]
    # a boss montage the tracker does not know
    if bm != S["bm_last"] or bpos < S["bm_last_pos"] - 0.05:
        S["bm_serial"] += 1
    S["bm_last"], S["bm_last_pos"] = bm, bpos
    O["bserial"] = S["bm_serial"]
    O["bm_untracked"] = bm is not None and O["move"] == "None" and not O["stag"] and not O["transition"] and bm not in TRACKED_NAMES and attack_like(bm)
    # neutral = the boss is between attacks: a looping or non-attack montage (wake, hit reaction, turn) does not make it busy, only an attack-like one does
    O["neutral"] = O["move"] == "None" and not O["stag"] and not O["transition"] and not O["dormant"] and not (bm is not None and attack_like(bm))
    return O


def opening(O):
    """The opening the boss gives now: (kind, key, real seconds left) or None. Recovery of a tracked attack, the stance break (until the get-up starts), the phase two roar."""
    if O["transition"]:
        length = S.get("roar_len", 1.8)
        return ("roar", ("roar", S["roar_n"]), length - (O["t"] - S["roar_t0"]))
    if O["stag"] and O["stage"] != "getup":
        length = S.get("stag_len", 2.5)
        return ("stagger", ("stagger", O["stag_n"]), length - (O["t"] - S["stag_t0"]))
    if O["phase"] == "Recovery" and O["move"] != "None":
        tm = TIMING.get(O["move"])
        left = max(0.0, (tm["recovery_end"] - O["pos"]) / O["rate"]) if tm else 0.4
        return ("rec:" + O["move"], ("rec", O["inst"]), left)
    return None


# ===================================================================================================================================================================================================
# 5. ACCOUNTING: every frame of the fight, counts what happened (the metrics of the report)
# ===================================================================================================================================================================================================
def end_fight(outcome, why):
    if M["outcome"] is None:
        M["outcome"], M["why"], M["end_t"] = outcome, why, S["now"]
        log("FIGHT END: %s after %.1f s: %s" % (outcome, M["fight_t"], why))


def begin_fight(O):
    """The boss is awake: the clock starts and every counter that persists in a component gets its baseline."""
    M["fight_on"] = True
    M["t0"] = M["last_t"] = O["t"]
    M["boss_hp0"] = M["boss_hp_last"] = M["boss_hp_max"] = O["boss_hp"]
    M["pl_hp0"] = M["pl_hp_last"] = M["pl_hp_min"] = O["pl_hp"]
    M["pl_st0"] = O["pl_st"]
    M["hits_seen"], M["swings_seen"], M["procs_seen"], M["rip_imp_seen"] = O["hits"], O["swings"], O["procs"], O["rip_imp"]
    M["base"] = {"hits": O["hits"], "swings": O["swings"], "procs": O["procs"], "stagger": O["stag_n"], "rip_count": O["rip_count"], "rip_imp": O["rip_imp"], "rip_rej": O["rip_rej"], "dodge_presses": O["dodge_presses"]}
    M["last_pos"] = (O["px"], O["py"])
    S["event_t"] = O["t"]
    log("FIGHT START: the boss is awake (woke by %s); boss health %s, player health %s stamina %s, dist %.0f cm, build %s (style %s)" % (M["woke_by"], O["boss_hp"], O["pl_hp"], O["pl_st"], O["dist"], BUILD, O["style"]))


def finalize_instance(iid, O):
    rec = M["inst"].get(iid)
    if rec is None or rec.get("done"):
        return
    rec["done"] = True
    a = M["attacks"].setdefault(rec["move"], {"seen": 0, "hit_me": 0, "avoided": 0, "missed": 0})
    if rec["hit"]:
        a["hit_me"] += 1
        verdict = "HIT ME"
    elif rec["dodged"]:
        a["avoided"] += 1
        verdict = "avoided (dodged)"
    else:
        a["missed"] += 1
        verdict = "missed me (not dodged: range or heading)"
    log("BOSS ATTACK %s #%d ended after %.2f s: %s" % (rec["move"], iid, O["t"] - rec["t0"], verdict))


def close_opening(O):
    cur = M["open_cur"]
    M["open_cur"] = None
    if cur is None:
        return
    hits_in = O["hits"] - cur["hits0"]
    imp_in = O["rip_imp"] - cur["rip0"]
    swings_in = O["swings"] - cur["swings0"]
    presses_in = (M["presses_total"] + M["rip_press"]) - cur["press0"]
    cur["used"] = hits_in >= 1 or imp_in >= 1
    cur["attempted"] = swings_in >= 1 or presses_in >= 1
    cur["len"] = O["t"] - cur["t0"]
    M["openings"].append(cur)
    log("OPENING %s ended after %.2f s (estimated %.2f s at its start, %s): bot threw %d swing(s)/press(es), %d hit(s), %d riposte impact(s) -> %s%s" % (
        cur["kind"], cur["len"], cur["left0"], "usable" if cur["usable"] else "too short to use", max(swings_in, presses_in), hits_in, imp_in, "USED" if cur["used"] else "not used",
        "" if (cur["used"] or cur["attempted"]) else " (the bot did not try: %s)" % (cur.get("skip") or S["last_skip"] or "no reason recorded")))
    S["event_t"] = O["t"]


def track_opening(O):
    op = opening(O)
    cur = M["open_cur"]
    key = op[1] if op else None
    if cur is not None and key != cur["key"]:
        close_opening(O)
    if op is not None and M["open_cur"] is None:
        M["open_cur"] = {"key": op[1], "kind": op[0], "t0": O["t"], "left0": op[2], "dist0": O["dist"], "hits0": O["hits"], "swings0": O["swings"], "rip0": O["rip_imp"],
                         "press0": M["presses_total"] + M["rip_press"], "usable": op[2] >= OPENING_MIN, "skip": ""}
        S["last_skip"] = ""
        log("OPENING %s begins: about %.2f s, bot at %.0f cm (stamina %s, boss posture %.0f)" % (op[0], op[2], O["dist"], ("%.0f" % O["pl_st"]) if O["pl_st"] is not None else "?", O["posture"]))
        S["event_t"] = O["t"]


def match_drops(t):
    """Pairs the boss's health drops with the hit intake's records in order (a record arrives one frame after the pack's hit event, so a drop and its record are less than 0.4 s apart)."""
    recs, drops = M["pend_recs"], M["pend_drops"]
    while recs and drops:
        rt, kind = recs[0]
        drop_t, amount = drops[0]
        if abs(rt - drop_t) <= 0.4:
            M["hp_by_kind"].setdefault(kind, []).append(amount)
            recs.pop(0)
            drops.pop(0)
        elif rt < drop_t:
            M["rec_no_drop"] += 1
            recs.pop(0)
        else:
            M["drop_no_rec"] += 1
            M["hp_unmatched"] += amount
            drops.pop(0)
    while recs and t - recs[0][0] > 0.6:
        M["rec_no_drop"] += 1
        recs.pop(0)
    while drops and t - drops[0][0] > 0.6:
        M["drop_no_rec"] += 1
        M["hp_unmatched"] += drops[0][1]
        drops.pop(0)


def account(O):
    if not M["fight_on"]:
        return
    t = O["t"]
    C = parts()
    dt = max(0.0, t - M["last_t"])
    M["last_t"] = t
    M["fight_t"] = t - M["t0"]
    if O["brain_running"] is False:
        M["brain_inactive_s"] += dt
    if O["move_ignored"]:
        M["move_blocked_s"] += dt
    M["neutral_inactive_s"] = M["neutral_inactive_s"] + dt if O["neutral"] and O["brain_running"] is False else 0.0
    if M["neutral_inactive_s"] >= 10.0 or O["test_freeze"]:
        end_fight("ai_inactive", "boss AI inactive while neutral for %.1f s; test freeze %s" % (M["neutral_inactive_s"], O["test_freeze"]))
    # ---- boss health: every drop is a weapon hit, a bleed proc or the riposte impact
    hp = O["boss_hp"]
    if hp is not None:
        last = M["boss_hp_last"]
        if last is not None and hp < last - 0.01:
            drop = last - hp
            part_bleed = min(drop, max(0.0, O["proc_dmg"])) if O["procs"] > M["procs_seen"] else 0.0
            rest = drop - part_bleed
            part_rip = 0.0
            if O["rip_imp"] > M["rip_imp_seen"]:
                part_rip, rest = rest, 0.0
            M["hp_bleed"] += part_bleed
            M["hp_rip"] += part_rip
            if rest > 0.01:
                M["hp_hit"] += rest
                M["pend_drops"].append((t, rest))
            log("BOSS HEALTH -%.1f (%s) -> %.0f (%.0f%%)%s" % (drop, ("bleed proc %.1f" % part_bleed if part_bleed else "") + (" riposte %.1f" % part_rip if part_rip else "") + (" weapon hit %.1f" % rest if rest > 0.01 else ""),
                                                                 hp, 100.0 * hp / max(M["boss_hp0"] or 1.0, 1.0), " [phase two]" if O["phase2"] else ""))
        M["boss_hp_last"] = hp
    M["procs_seen"] = max(M["procs_seen"], O["procs"])
    M["rip_imp_seen"] = max(M["rip_imp_seen"], O["rip_imp"])
    # ---- hit records of the intake (kind of each hit)
    n_new = O["hits"] - M["hits_seen"]
    if n_new > 0:
        intake = C.get("intake")
        lines = safe("intake.get_record_lines", lambda: list(intake.get_record_lines()), [])
        for line in lines[-n_new:]:
            m = re.search(r"kind (\w+)", line)
            kind = m.group(1) if m else "Unknown"
            M["hits_kind"][kind] = M["hits_kind"].get(kind, 0) + 1
            M["pend_recs"].append((t, kind))
        M["hits_seen"] = O["hits"]
        M["hits"] = O["hits"] - M["base"]["hits"]
    match_drops(t)
    # ---- swings of the swing tracker (kind of each)
    n_sw = O["swings"] - M["swings_seen"]
    if n_sw > 0:
        swing = C.get("swing")
        text = safe("swing.get_last_swing_text", lambda: swing.get_last_swing_text(), "")
        m = re.search(r"kind (\w+),", text)
        kind = m.group(1) if m else "Unknown"
        M["swings_kind"][kind] = M["swings_kind"].get(kind, 0) + n_sw
        M["swings_seen"] = O["swings"]
    # ---- boss attack instances (tracked moves); before the player's health so that a hit in the first frame of an attack is attributed to it
    if O["phase"] != "None" and O["move"] != "None":
        iid = O["inst"]
        if iid != M["cur_inst"]:
            if M["cur_inst"] is not None:
                finalize_instance(M["cur_inst"], O)
            M["inst"][iid] = {"move": O["move"], "t0": t, "dist0": O["dist"], "dodged": False, "hit": False}
            M["attacks"].setdefault(O["move"], {"seen": 0, "hit_me": 0, "avoided": 0, "missed": 0})["seen"] += 1
            M["cur_inst"] = iid
            S["event_t"] = t
            log("BOSS ATTACK %s #%d begins (%s, montage position %.2f s%s): bot at %.0f cm, %.0f deg off the boss's front, stamina %s" % (
                O["move"], iid, O["phase"], O["pos"], ", phase two rate x%.1f" % O["rate"] if O["phase2"] else "", O["dist"], O["off_front"], ("%.0f" % O["pl_st"]) if O["pl_st"] is not None else "?"))
        M["inst_seen_t"] = t
    elif M["cur_inst"] is not None and t - M["inst_seen_t"] > 0.4:
        finalize_instance(M["cur_inst"], O)
        M["cur_inst"] = None
    # ---- player health
    php = O["pl_hp"]
    if php is not None:
        if M["pl_hp_last"] is not None and php < M["pl_hp_last"] - 0.01:
            amount = M["pl_hp_last"] - php
            iid = O["inst"] if (O["phase"] != "None" and O["move"] != "None") else M["cur_inst"]
            who = "%s/%s at %.2f s" % (O["move"], O["phase"], O["pos"]) if O["move"] != "None" else "no tracked move (boss montage %s)" % O["bmontage"]
            rec = {"t": t, "amount": amount, "who": who, "dist": O["dist"], "invuln": O["invuln"], "dodging": O["dodging"], "since_dodge": t - S["last_dodge_t"], "pmontage": O["pmontage"]}
            M["taken"].append(rec)
            M["taken_total"] += amount
            if iid is not None and iid in M["inst"]:
                M["inst"][iid]["hit"] = True
            log("HIT TAKEN -%.1f -> player health %.0f: boss %s at %.0f cm, player montage %s, i-frames %s, last dodge %.2f s ago, stamina %s" % (
                amount, php, who, O["dist"], O["pmontage"], "ON (damage during i-frames: look at this)" if O["invuln"] else "off", t - S["last_dodge_t"], ("%.0f" % O["pl_st"]) if O["pl_st"] is not None else "?"))
        elif M["pl_hp_last"] is not None and php > M["pl_hp_last"] + 0.01:
            M["pl_regen"] += php - M["pl_hp_last"]
        M["pl_hp_last"] = php
        M["pl_hp_min"] = php if M["pl_hp_min"] is None else min(M["pl_hp_min"], php)
    # ---- stamina
    st = O["pl_st"]
    if st is not None:
        if M["st_min"] is None or st < M["st_min"]:
            M["st_min"], M["st_min_t"] = st, M["fight_t"]
        if st < LOW_STAMINA:
            M["st_low_s"] += dt
        low = st < 20.0
        if low and not M["st_dip"]:
            M["st_dips"] += 1
            if M["st_dips"] <= 8:
                log("STAMINA dipped below 20 (%.0f) at %.1f s, mode %s" % (st, M["fight_t"], S["mode"]))
        M["st_dip"] = low
    # ---- boss montages the tracker does not know
    bm = O["bmontage"]
    if bm is not None and O["move"] == "None" and bm not in TRACKED_NAMES and bm not in M["untracked"] and not O["stag"] and not O["transition"]:
        M["untracked"][bm] = {"n": 0, "attack_like": attack_like(bm)}
        log("UNTRACKED boss montage '%s' (position %.2f s, %.0f cm): %s" % (bm, O["bpos"], O["dist"], "looks like an attack: the bot dodges it %.2f s in" % UNTRACKED_DODGE_AT if attack_like(bm) else "ignored (not attack-like by name)"))
    if bm is not None and bm in M["untracked"] and O["bserial"] != M["untracked"][bm].get("serial"):
        M["untracked"][bm]["serial"] = O["bserial"]
        M["untracked"][bm]["n"] += 1
    # ---- dodge montages seen (the bot's presses are counted when it presses)
    if O["dodging"] and not M["was_dodging"]:
        M["dodge_montages"] += 1
        low = (O["pmontage"] or "").lower()
        if "small" in low or "quick" in low:
            M["dodge_quick"] += 1
        else:
            M["dodge_full"] += 1
    M["was_dodging"] = O["dodging"]
    # ---- phase two, weapon, walking speed
    if O["phase2"] and M["p2_t"] is None:
        M["p2_t"], M["p2_hp"] = M["fight_t"], hp
        log("PHASE TWO at %.1f s (boss health %s): attack montages x%.1f from now on, the bot's timing uses that rate" % (M["fight_t"], hp, O["rate"]))
    if O["style"] and S["style0"] and O["style"] != S["style0"]:
        M["style_changes"] += 1
        log("WEAPON CHANGED during the fight: %s -> %s (the lock did not hold)" % (S["style0"], O["style"]))
        S["style0"] = O["style"]
    if M["last_pos"] is not None and dt > 0.0 and S["stick"] is not None and S["now"] < S["stick_until"] and O["pmontage"] is None:
        step = math.hypot(O["px"] - M["last_pos"][0], O["py"] - M["last_pos"][1])
        if 0.0 < step < 100.0:
            M["walk_sum"] += step / dt
            M["walk_n"] += 1
    M["last_pos"] = (O["px"], O["py"])
    track_opening(O)
    # ---- the end of the fight
    if M["outcome"] is None:
        if (hp is not None and hp <= 0.0) or O["death_state"] in ("dying", "dead") or O["hud_state"] == "Victory":
            end_fight("boss_dead", "boss health %s, death state %s, HUD %s" % (hp, O["death_state"], O["hud_state"]))
        elif php is not None and php <= 0.0:
            end_fight("player_dead", "player health %s" % php)
        elif M["fight_t"] >= LIMIT_FIGHT_S:
            end_fight("timeout", "%.0f s of fight time, boss health %s" % (LIMIT_FIGHT_S, hp))


# ===================================================================================================================================================================================================
# 6. INPUT: the generators only set what is held; the tick applies it every frame after they ran
# ===================================================================================================================================================================================================
def hold(action, seconds, vec=(1.0, 0.0, 0.0)):
    S["inject"][action] = (S["now"] + seconds, vec)


def key_hold(name, seconds):
    S["keys_until"][name] = S["now"] + seconds


def set_stick(x, y, seconds=0.12):
    """IA_Move (x right, y forward) relative to the control rotation, which the tick keeps looking at the boss."""
    S["stick"] = (x, y)
    S["stick_until"] = S["now"] + seconds


def clear_stick():
    S["stick"] = None


def stick_from_world(O, wx, wy):
    """A world direction as the stick (right, forward) of a camera that looks at the boss. UE: the right vector of yaw th is (-sin th, cos th)."""
    th = math.radians(O["yaw_to_boss"])
    n = math.hypot(wx, wy) or 1.0
    wx, wy = wx / n, wy / n
    return (wx * -math.sin(th) + wy * math.cos(th), wx * math.cos(th) + wy * math.sin(th))


def face_now():
    p, O = S["P"], S["O"]
    if p and O:
        p["pc"].set_control_rotation(unreal.Rotator(0, 0, O["yaw_to_boss"]))
        p["pawn"].set_actor_rotation(unreal.Rotator(0, 0, O["yaw_to_boss"]), False)


def apply_inputs(p, O):
    pc, t = p["pc"], S["now"]
    for name in list(S["inject"].keys()):
        until, vec = S["inject"][name]
        if t < until:
            ok = unreal.RPGInputTestUtils.inject_action(pc, ia(name), unreal.Vector(vec[0], vec[1], vec[2]))
            if not ok and not S["inject_warned"]:
                S["inject_warned"] = True
                log("API PROBLEM inject_action returned False: the controller has no Enhanced Input subsystem")
        else:
            del S["inject"][name]
    if S["stick"] is not None:
        if t < S["stick_until"]:
            unreal.RPGInputTestUtils.inject_action(pc, ia("IA_Move"), unreal.Vector(S["stick"][0], S["stick"][1], 0.0))
        else:
            S["stick"] = None
    for k in list(S["keys_until"].keys()):
        down = t < S["keys_until"][k]
        if S["key_state"].get(k, False) != down:
            S["key_state"][k] = down
            unreal.RPGInputTestUtils.set_key_down(pc, k, down)
        if not down:
            del S["keys_until"][k]
    if S["face"] and O is not None:
        pc.set_control_rotation(unreal.Rotator(0, 0, O["yaw_to_boss"]))
        if O["pmontage"] is None and not O["falling"] and not O["riposting"]:
            p["pawn"].set_actor_rotation(unreal.Rotator(0, 0, O["yaw_to_boss"]), False)


def release_all(pc):
    for k, down in list(S["key_state"].items()):
        if down:
            safe("release " + k, lambda: unreal.RPGInputTestUtils.set_key_down(pc, k, False))
            S["key_state"][k] = False


# ===================================================================================================================================================================================================
# 7. THE BOT'S DECISIONS (pure: they read the observation, they change nothing)
# ===================================================================================================================================================================================================
def dodge_due(O):
    """None, or the dodge to press NOW. One per attack instance, 0.45 s apart, never while a dodge or the riposte runs, never below the stamina floor."""
    t = O["t"]
    if O["riposting"] or O["dodging"] or t - S["last_dodge_t"] < DODGE_MIN_GAP:
        return None
    if O["pl_st"] is not None and O["pl_st"] < DODGE_STAMINA_MIN:
        return None
    move, phase = O["move"], O["phase"]
    if move != "None" and phase in ("Windup", "Committed", "Active"):
        plan, tm = PLAN.get(move), TIMING.get(move)
        if plan is None or tm is None or O["inst"] == S["dodged_inst"] or O["dist"] > plan[2]:
            return None
        if phase == "Active":
            if (O["pos"] - tm["active_start"]) / O["rate"] > 0.12:
                return None   # too late: the window is already open, a dodge now does not cover its start
            tta = 0.0
        else:
            tta = max(0.0, (tm["active_start"] - O["pos"]) / O["rate"])
        if tta <= plan[1] + 0.01:
            return {"kind": "tracked", "key": O["inst"], "move": move, "how": plan[0], "tta": tta, "aim": plan[1]}
        return None
    if O["bm_untracked"] and O["bserial"] != S["dodged_bm"] and O["bpos"] >= UNTRACKED_DODGE_AT and O["dist"] <= UNTRACKED_REACH:
        return {"kind": "untracked", "key": O["bserial"], "move": O["bmontage"], "how": "close", "tta": 0.0, "aim": 0.0}
    return None


def riposte_vec(O):
    """None when the bot already stands where a riposte is accepted (within RIPOSTE_GO and the cone), else the stick that walks it there: round the boss to its front first, then up to it."""
    if O["dist"] <= RIPOSTE_GO and O["off_front"] <= RIPOSTE_CONE:
        return None
    if O["off_front"] > RIPOSTE_CONE:
        step = min(35.0, O["off_front"]) * (-1.0 if O["polar"] > 0 else 1.0)   # move the polar angle towards the front
        ang = math.radians(O["boss_yaw"] + O["polar"] + step)
        r = max(O["dist"], 150.0)
        tx, ty = O["bx"] + r * math.cos(ang), O["by"] + r * math.sin(ang)
        return stick_from_world(O, tx - O["px"], ty - O["py"])
    return (0.0, 1.0)


def plan_punish(O, op):
    """The opener for an opening, or the walk that gets the bot into range. Recovery deliberately does not use a fit estimate: a measured attempt is more useful than another skipped opening."""
    kind_open, key, left = op
    cls = "stagger" if kind_open == "stagger" else ("roar" if kind_open == "roar" else "recovery")
    if O["falling"] or O["dodging"]:
        S["last_skip"] = "the bot is in the air"
        return None
    st = O["pl_st"] if O["pl_st"] is not None else 0.0
    gap = max(0.0, O["dist"] - S["strike"])
    if gap > 0.0 and st >= COST[BUILD]["Light"] + DODGE_RESERVE:
        return ("move", (0.0, 1.0), "close during %s (%.0f cm, %.2f s left)" % (kind_open, O["dist"], left))
    why_not = []
    for kind in OPENERS[BUILD][cls]:
        if not CAPS[BUILD][kind]:
            continue
        if st < COST[BUILD][kind] + DODGE_RESERVE:
            why_not.append("%s needs %.0f stamina + %.0f reserve, has %.0f" % (kind, COST[BUILD][kind], DODGE_RESERVE, st))
            continue
        if gap > 0.0:
            return ("move", (0.0, 1.0), "close in for a %s during %s (%.0f cm, %.2f s left; no fit veto)" % (kind, kind_open, O["dist"], left))
        taps = CHAIN.get(BUILD, 1) if kind == "Light" else 1
        return ("chain" if taps > 1 else "swing", kind, "%s opening, %.2f s left, stamina %.0f" % (kind_open, left, st), taps)
    S["last_skip"] = "; ".join(why_not) or "no opener of the build for this opening"
    return None


def decide(O):
    """One action per frame: ('dodge', plan) | ('riposte', key) | ('swing', kind, why, 1) | ('chain', kind, why, taps) | ('move', (x, y), why) | ('wait', why). 'why' starts with a short tag; the mode log uses the tag."""
    if O["riposting"]:
        return ("wait", "riposte execution (input locked)")
    plan = dodge_due(O)
    if plan:
        if plan["how"] == "jump":
            return ("jump", plan)
        return ("dodge", plan)
    if O["dodging"]:
        return ("wait", "dodge running (a swing pressed now is eaten)")
    op = opening(O)
    if op is not None:
        kind_open, key, left = op
        if kind_open == "stagger" and not S["rip_done"].get(key) and S["rip_presses"].get(key, 0) < 3 and left > 0.6:
            if O["rip_avail"]:
                return ("riposte", key)
            if O["t"] - S["stag_t0"] < RIPOSTE_WAIT_S:   # the riposte opens when the 0.7 s fall is over; if it has not opened by RIPOSTE_WAIT_S the bot stops waiting for it and hits the kneeling boss
                vec = riposte_vec(O)
                if vec is not None:
                    return ("move", vec, "walk to the boss's front for the riposte (%.0f cm, %.0f deg off its front)" % (O["dist"], O["off_front"]))
                return ("wait", "riposte not open yet (stage %s)" % O["stage"])
        pun = plan_punish(O, op)
        if pun is not None:
            return pun
        return ("wait", "opening skipped (%s)" % S["last_skip"])
    if O["neutral"] and not O["pmontage"] and not O["falling"]:
        if O["t"] - S["event_t"] > BAIT_AFTER_S:
            if O["pl_st"] is not None and O["pl_st"] >= COST[BUILD]["Light"] + DODGE_RESERVE:
                if O["dist"] > S["strike"] + 10.0:
                    return ("move", (0.0, 1.0), "walk up for a bait swing (no boss attack for %.0f s)" % (O["t"] - S["event_t"]))
                kind = "Strong" if BUILD == "Strength" and O["pl_st"] >= COST[BUILD]["Strong"] + DODGE_RESERVE else "Light"
                return ("swing", kind, "neutral pressure: no boss action for %.1f s" % (O["t"] - S["event_t"]), 1)
        if O["dist"] > SPACING_MAX:
            return ("move", (0.0, 1.0), "approach to %.0f cm (now %.0f)" % (SPACING_MAX, O["dist"]))
        if RETREAT and O["dist"] < SPACING_MIN and O["home_dist"] < WALL_RADIUS:
            return ("move", (0.0, -1.0), "back off to %.0f cm (now %.0f)" % (SPACING_MIN, O["dist"]))
    return ("wait", "hold position")


def note_mode(act):
    tag = act[0] + ": " + (act[-1] if isinstance(act[-1], str) else act[1].get("move", "") if act[0] == "dodge" else "").split(" (")[0].split(":")[0]
    if tag != S["mode"]:
        S["mode"] = tag
        if act[0] not in ("dodge", "swing", "chain", "riposte"):   # those log themselves with more detail
            log("MODE %s" % (act[-1] if isinstance(act[-1], str) else tag))


# ===================================================================================================================================================================================================
# 8. ACTIONS: generators (one frame per yield), they poll for a dodge that has become due and give the hand back
# ===================================================================================================================================================================================================
def until(cond, timeout):
    t0 = S["now"]
    while not cond():
        if S["now"] - t0 > timeout:
            return False
        yield 0.0
    return True


def pause(seconds):
    t0 = S["now"]
    while S["now"] - t0 < seconds:
        yield 0.0


def do_dodge(plan):
    O = S["O"]
    how = plan["how"]
    if how == "back":
        clear_stick()
        direction = "backward (no stick)"
    elif how == "in":
        set_stick(0.0, 1.0, 0.5)
        direction = "forward, towards the boss"
    elif CLOSE_DODGE == "flank":
        set_stick(S["side"] * FLANK[0], FLANK[1], 0.5)
        direction = "flank %s" % ("right" if S["side"] > 0 else "left")
    else:
        set_stick(S["side"], 0.0, 0.5)
        direction = "sideways %s" % ("right" if S["side"] > 0 else "left")
    if how == "close":
        S["side"] = -S["side"]
    S["last_dodge_t"] = O["t"]
    if plan["kind"] == "tracked":
        S["dodged_inst"] = plan["key"]
        if plan["key"] in M["inst"]:
            M["inst"][plan["key"]]["dodged"] = True
    else:
        S["dodged_bm"] = plan["key"]
    M["dodge_presses"] += 1
    late = plan["kind"] == "tracked" and plan["tta"] < IFRAME_FIRST - 0.02
    if late:
        M["dodge_late"] += 1
    key_hold(DODGE_KEY, DODGE_PRESS_S)
    st0 = O["pl_st"]
    log("DODGE %s %s: boss %s %s at montage position %.2f s, the active window opens in %.2f s (aimed %.2f s before it)%s; bot at %.0f cm, stamina %s%s" % (
        direction, "press #%d" % M["dodge_presses"], plan["move"], O["phase"] if plan["kind"] == "tracked" else "(untracked montage)", O["pos"] if plan["kind"] == "tracked" else O["bpos"], plan["tta"], plan["aim"],
        " [LATE: the i-frames start %.2f s after the key, the hit is due sooner]" % IFRAME_FIRST if late else "", O["dist"], ("%.0f" % st0) if st0 is not None else "?", " (cuts the swing in progress)" if O["pmontage"] and not O["dodging"] else ""))
    S["event_t"] = O["t"]
    started = yield from until(lambda: S["O"]["dodging"], 0.5)
    if not started:
        M["dodge_refused"] += 1
        log("DODGE ignored by the pack: no dodge montage within 0.5 s (stamina %s, player montage %s)" % (S["O"]["pl_st"], S["O"]["pmontage"]))
        return "refused"
    yield from pause(0.15)
    st1 = S["O"]["pl_st"]
    if st0 is not None and st1 is not None:
        M["dodge_costs"].append(st0 - st1)
        log("INFO dodge stamina %.1f -> %.1f (cost sample %.1f, the pack's regeneration may be in it)" % (st0, st1, st0 - st1))
    yield from until(lambda: not S["O"]["dodging"], 0.9)
    after = S["O"]
    log("DODGE END: distance %.0f -> %.0f, displacement %.0f cm, off-front %.0f, boss yaw %.0f, mode %s" % (
        O["dist"], after["dist"], math.hypot(after["px"] - O["px"], after["py"] - O["py"]), after["off_front"], after["boss_yaw"], S["mode"]))
    return "ok"


def do_wave_jump(plan):
    """A6's ground wave is jumpable; LEAP-01 proves a jump at wave launch clears it. This is an observed input sequence only when the editor owner runs the bot."""
    O = S["O"]
    S["dodged_inst"] = plan["key"]
    M["wave_jumps"] += 1
    clear_stick()
    key_hold(JUMP_KEY, 0.12)
    log("WAVE JUMP #%d: boss %s %s at montage position %.2f s, wave active starts in %.2f s; bot at %.0f cm" % (
        M["wave_jumps"], plan["move"], O["phase"], O["pos"], plan["tta"], O["dist"]))
    S["event_t"] = O["t"]
    yield from until(lambda: S["O"]["falling"], 0.5)
    yield from until(lambda: not S["O"]["falling"], 1.5)
    after = S["O"]
    log("WAVE JUMP END: distance %.0f -> %.0f, displacement %.0f cm, feet state falling %s, mode %s" % (
        O["dist"], after["dist"], math.hypot(after["px"] - O["px"], after["py"] - O["py"]), after["falling"], S["mode"]))
    return "ok"


def do_riposte(key):
    O = S["O"]
    S["rip_presses"][key] = S["rip_presses"].get(key, 0) + 1
    M["rip_press"] += 1
    rip0 = O["rip_count"]
    face_now()
    log("RIPOSTE press #%d of this break: bot at %.0f cm, %.0f deg off the boss's front, stage %s, boss posture %.0f" % (S["rip_presses"][key], O["dist"], O["off_front"], O["stage"], O["posture"]))
    hold("IA_NormalAttack", 0.12)
    accepted = yield from until(lambda: S["O"]["rip_exec"] or S["O"]["rip_count"] > rip0, 0.6)
    if not accepted:
        M["rip_rejected"] += 1
        reason = safe("stg.get_last_riposte_result", lambda: parts()["stg"].get_last_riposte_result(), "?")
        log("RIPOSTE not accepted: %s" % reason)
        return "rejected"
    M["rip_accepted"] += 1
    S["rip_done"][key] = True
    imp0 = S["O"]["rip_imp"]
    log("RIPOSTE accepted: the execution runs (input locked about 2 s)")
    yield from until(lambda: not S["O"]["rip_exec"], 3.5)
    log("RIPOSTE execution over: impacts %d, boss health %s" % (S["O"]["rip_imp"] - imp0, S["O"]["boss_hp"]))
    S["event_t"] = S["now"]
    return "done"


def do_swing(kind, why, taps=1):
    """One swing (taps > 1: a light chain, TAP_SPACING apart). Returns 'hit', 'whiff', 'ignored', 'cut' (a dodge became due), 'stamina' or 'opening over'."""
    action, seconds, jump = ACTIONS[kind]
    result = "none"
    for tap in range(taps):
        O = S["O"]
        if tap > 0:
            op = opening(O)
            if op is None or op[2] < 0.30:
                return "opening over"
            if O["pl_st"] is not None and O["pl_st"] < COST[BUILD][kind] + DODGE_RESERVE:
                return "stamina"
        n0, h0, d0 = O["swings"], O["hits"], O["dist"]
        face_now()
        M["presses"][kind] = M["presses"].get(kind, 0) + 1
        M["presses_total"] += 1
        S["event_t"] = O["t"]
        log("SWING %s%s: %s; bot at %.0f cm (strike range %.0f), stamina %s, boss %s/%s" % (kind, " tap %d of %d" % (tap + 1, taps) if taps > 1 else "", why, d0, S["strike"], ("%.0f" % O["pl_st"]) if O["pl_st"] is not None else "?", O["move"], O["phase"]))
        if jump:
            key_hold(JUMP_KEY, 0.12)
            t_end = S["now"] + 0.32   # pie_builds.py: key down 0.12 s, the strong press 0.2 s after the release
            while S["now"] < t_end:
                yield 0.0
                if M["outcome"] is not None:
                    return "end"
                if dodge_due(S["O"]):
                    M["cuts"] += 1
                    return "cut"
        hold(action, seconds)
        t_press = S["now"]
        registered, t_hit, result = False, None, "none"
        while True:
            yield 0.0
            O = S["O"]
            if M["outcome"] is not None:
                return "end"
            if O["hits"] > h0 and t_hit is None:
                t_hit = S["now"] - t_press
            if O["swings"] > n0:
                registered = True
            if dodge_due(O):
                M["cuts"] += 1
                log("SWING %s cut by a dodge that became due (%.2f s after the press)" % (kind, S["now"] - t_press))
                return "cut"   # at once: a pause here would delay the dodge and its i-frames
            el = S["now"] - t_press
            if not registered and el > seconds + 0.6:
                result = "ignored"
                break
            if registered and tap < taps - 1 and el >= TAP_SPACING - 0.12:   # the 0.12 s pause below makes the press to press gap TAP_SPACING
                break
            if registered and tap == taps - 1 and O["pmontage"] is None and el > seconds:
                break
            if el > seconds + 1.8:
                break
        yield from pause(0.12)   # the hit record arrives a frame after the pack's event
        O = S["O"]
        gained = O["hits"] - h0
        if result == "ignored":
            M["ignored"] += 1
            log("SWING %s ignored by the pack (no swing registered in %.1f s; player montage %s, falling %s)" % (kind, seconds + 0.6, O["pmontage"], O["falling"]))
        elif gained > 0:
            result = "hit" if result != "cut" else "cut"
            M["swing_delays"].setdefault(kind, []).append(t_hit if t_hit is not None else 0.0)
            log("SWING %s landed %d hit(s), first %.2f s after the press (guess was %.2f s), bot was at %.0f cm" % (kind, gained, t_hit if t_hit is not None else -1.0, HIT_DELAY[kind], d0))
        elif registered and result != "cut":
            result = "whiff"
            M["whiffs"] += 1
            if d0 <= S["strike"] + 15.0 and S["strike"] > STRIKE_MIN:
                S["strike"] = max(STRIKE_MIN, S["strike"] - 12.0)
            log("SWING %s whiffed (no hit within %.2f s of the press, bot was at %.0f cm): strike range now %.0f cm" % (kind, S["now"] - t_press, d0, S["strike"]))
        if result == "cut":
            log("SWING %s cut short: a dodge became due" % kind)
            return "cut"
        if result == "ignored":
            return "ignored"
    return result


def fight():
    """The fight loop: decide, run the action (which polls for a dodge that has become due), repeat until the outcome is set."""
    S["face"] = True
    while M["outcome"] is None:
        O = S["O"]
        act = decide(O)
        if O["move"] != "None" and O["t"] - S["decision_t"] >= 0.5:
            S["decision_t"] = O["t"]
            log("DECIDE %s/%s %.2f: distance %.0f, posture %.0f, stamina %s, action %s" % (
                O["move"], O["phase"], O["pos"], O["dist"], O["posture"], O["pl_st"], act))
        note_mode(act)
        kind = act[0]
        if kind == "dodge":
            yield from do_dodge(act[1])
        elif kind == "jump":
            yield from do_wave_jump(act[1])
        elif kind == "riposte":
            yield from do_riposte(act[1])
        elif kind in ("swing", "chain"):
            clear_stick()
            yield from do_swing(act[1], act[2], act[3])
        elif kind == "move":
            set_stick(act[1][0], act[1][1])
            yield 0.0
        else:
            clear_stick()
            yield 0.0


# ===================================================================================================================================================================================================
# 9. SETUP, THE SCRIPT
# ===================================================================================================================================================================================================
def place_player(dist):
    p = S["P"]
    boss, pawn, pc = p["boss"], p["pawn"], p["pc"]
    bl = boss.get_actor_location()
    r = math.radians(boss.get_actor_rotation().yaw)
    q = unreal.Vector(bl.x + math.cos(r) * dist, bl.y + math.sin(r) * dist, bl.z + 20)
    look = math.degrees(math.atan2(bl.y - q.y, bl.x - q.x))
    pawn.set_actor_location_and_rotation(q, unreal.Rotator(0, 0, look), False, True)
    pc.set_control_rotation(unreal.Rotator(0, 0, look))


def load_timing():
    """The tracker's live Attacks table replaces the built-in copy; differences are logged. Reading a property is harmless (only setting one in PIE is not: KI-083)."""
    tr = parts().get("tr")
    live = {}
    try:
        for a in list(tr.get_editor_property("attacks")):
            mid = str(a.get_editor_property("move_id"))
            live[mid] = {"commit": float(a.get_editor_property("commit_time")), "active_start": float(a.get_editor_property("active_start_time")), "active_end": float(a.get_editor_property("active_end_time")),
                         "recovery_end": float(a.get_editor_property("recovery_end_time")), "montage": str(a.get_editor_property("montage_name"))}
    except Exception as e:
        log("SETUP could not read the tracker's Attacks table (%s: %s): the built-in copy of the C++ defaults is used" % (type(e).__name__, str(e)[:120]))
        return
    for mid, row in live.items():
        old = TIMING.get(mid)
        if old is None or any(abs(old[k] - row[k]) > 0.005 for k in ("commit", "active_start", "active_end", "recovery_end")):
            log("INFO tracker row %s differs from the built-in copy: live %s, copy %s" % (mid, {k: row[k] for k in row if k != "montage"}, {k: old[k] for k in old if k != "montage"} if old else None))
    TIMING.clear()
    TIMING.update(live)
    TRACKED_NAMES.clear()
    TRACKED_NAMES.update(v["montage"] for v in TIMING.values())
    log("SETUP tracker table read: %s" % ", ".join("%s active %.2f-%.2f recovery to %.2f" % (k, v["active_start"], v["active_end"], v["recovery_end"]) for k, v in sorted(TIMING.items())))


def read_boss_numbers():
    """The stagger and roar lengths and the phase two attack rate, read from the components (reading is harmless)."""
    C = parts()
    S["stag_len"] = float(safe("stg.stagger_seconds", lambda: C["stg"].get_editor_property("stagger_seconds"), 2.5))
    S["roar_len"] = float(safe("ph.transition_seconds", lambda: C["ph"].get_editor_property("transition_seconds"), 1.8))
    S["attack_rate"] = float(safe("ph.attack_rate_scale", lambda: C["ph"].get_editor_property("attack_rate_scale"), 1.2))
    thr = safe("ph.phase_two_health_fraction", lambda: C["ph"].get_editor_property("phase_two_health_fraction"), None)
    log("SETUP boss numbers: stance break %.1f s, roar %.1f s, phase two attack rate x%.1f, phase two at health fraction %s (the brief said 55 percent, the header says 0.6)" % (S["stag_len"], S["roar_len"], S["attack_rate"], thr))


def script():
    p = S["P"]
    C = parts()
    need = ("tr", "stg", "post", "ph", "enc", "dbg", "swing", "intake", "ld")
    missing = [k for k in need if C.get(k) is None]
    M["flags"]["parts"] = not missing
    S["pawn_name"] = p["pawn"].get_name()
    log("SETUP build %s (%s); pawn %s, boss %s; components missing: %s; optional (death, hud, bleed, dodge, i-frame monitor): %s" % (
        BUILD, BUILD_NOTE, p["pawn"].get_name(), p["boss"].get_name(), missing or "none", [k for k in ("death", "hud", "bleed", "dodge", "mon") if C.get(k) is None] or "all there"))
    if missing:
        end_fight("setup_failed", "components missing: %s" % missing)
        return
    bl = p["boss"].get_actor_location()
    home = safe("enc.get_home_transform", lambda: C["enc"].get_home_transform().translation, None)
    S["home"] = (home.x, home.y) if home is not None else (bl.x, bl.y)
    load_timing()
    read_boss_numbers()
    # 1 the encounter reset: move outside the wake gate first, then require the full dormant baseline.
    # A prior PIE can leave the pawn near the boss; without this, the encounter wakes again before the build applies.
    place_player(RESET_DIST)
    C["enc"].reset_for_test()
    baseline = yield from until(lambda: parts()["enc"].is_dormant()
                                and (attr(S["P"]["boss"], "Attribute.Health") or 0.0) >= BASE_BOSS_HEALTH - 0.5
                                and parts()["post"].get_posture() >= BASE_POSTURE - 0.5, 3.0)
    C = parts()
    boss_health = attr(S["P"]["boss"], "Attribute.Health")
    posture = C["post"].get_posture()
    M["flags"]["slept"] = bool(baseline)
    M["flags"]["intake_bound"] = bool(safe("intake.is_hit_intake_bound", lambda: C["intake"].is_hit_intake_bound(), False))
    log("SETUP dormant baseline: %s; health %s/%s, posture %s/%s; hit intake bound: %s; generation %s" % (
        M["flags"]["slept"], boss_health, BASE_BOSS_HEALTH, posture, BASE_POSTURE, M["flags"]["intake_bound"], safe("enc.get_generation", lambda: C["enc"].get_generation(), "?")))
    if not baseline:
        end_fight("setup_failed", "reset baseline was not dormant/full (health %s, posture %s)" % (boss_health, posture))
        return
    # 2 the build: rpg.Build was set before the PIE; the loadout equips it while the boss sleeps
    want = STYLE[BUILD]
    ld = C["ld"]
    if not safe("ld.has_choice", lambda: ld.has_choice(), False):
        log("SETUP the loadout has no choice yet: setting rpg.Build \"%s\" again" % BUILD)
        console('rpg.Build "%s"' % BUILD)
        yield from pause(0.5)
    t0 = S["now"]
    ok = yield from until(lambda: parts()["ld"].get_actual_style_name() == want and parts()["ld"].get_state_name() == "Idle", 20.0)
    ld = parts()["ld"]
    detail = "style %s (want %s), state %s, chosen %s, weapon actor %s, ability %s: %s, line '%s', calls %s, last: %s" % (
        ld.get_actual_style_name(), want, ld.get_state_name(), ld.get_chosen_build_name(), ld.get_equipped_actor_class_name(), ABILITY[BUILD], ld.has_weapon_ability_for_test(ABILITY[BUILD]), ld.get_build_line(),
        ld.get_apply_attempt_count(), ld.get_last_result()[:200])
    # the style, the idle loadout and the weapon ability decide; the weapon actor's class is only reported (pie_builds.py proved it after an equip, a fresh Starter sword has not been looked at)
    M["flags"]["build_ok"] = bool(ok) and ld.has_weapon_ability_for_test(ABILITY[BUILD]) and ld.get_chosen_build_name() == BUILD
    log("SETUP build %s %s after %.1f s: %s" % (BUILD, "EQUIPPED" if M["flags"]["build_ok"] else "NOT EQUIPPED", S["now"] - t0, detail))
    if ld.get_equipped_actor_class_name() != ACTOR[BUILD]:
        log("INFO the weapon actor in the slot is '%s', pie_builds.py expects '%s' for this build" % (ld.get_equipped_actor_class_name(), ACTOR[BUILD]))
    if not M["flags"]["build_ok"]:
        end_fight("setup_failed", "the build did not apply: " + detail[:160])
        return
    S["style0"] = want
    # 3 the player: one refill before the fight, combat mode
    if REFILL_BEFORE_FIGHT:
        C["dbg"].debug_refill_player()
    asc = comp(p["pawn"], "BP_AdvancedAbilitySystemComponent_C")
    if asc is not None:
        asc.call_method("Try Activate Abilities By Tag", args=(tags("Ability.EnterCombat"),))
    yield from pause(2.2)
    O = S["O"]
    log("SETUP player ready: health %s, stamina %s (refill before the fight: %s), combat mode %s" % (O["pl_hp"], O["pl_st"], REFILL_BEFORE_FIGHT, safe("ld.is_combat_enabled", lambda: parts()["ld"].is_combat_enabled(), "?")))
    if O["pl_hp"] is None or O["pl_hp"] <= 0.0:
        end_fight("setup_failed", "the player has no health (%s): first PIE after an editor start? run pie_debug_overlay.py as a warm-up" % O["pl_hp"])
        return
    # 4 the wake: the player stands inside the gate and the boss wakes by itself
    place_player(START_DIST)
    S["face"] = True
    log("SETUP player placed %.0f cm in front of the boss, facing it; waiting for the wake (the gate is 1200 cm)" % START_DIST)
    woke = yield from until(lambda: not parts()["enc"].is_dormant(), 6.0)
    if not woke:
        M["woke_by"] = "wake() after 6 s"
        log("SETUP the boss did not wake by distance in 6 s: calling the encounter's wake()")
        parts()["enc"].wake()
        woke = yield from until(lambda: not parts()["enc"].is_dormant(), 3.0)
    if not woke:
        end_fight("setup_failed", "the boss never woke")
        return
    yield 0.0
    begin_fight(S["O"])
    # 5 the fight
    yield from fight()
    # 6 let the last counters settle (the pack destroys a dead boss about 4.4 s after its death: stay well inside that)
    if M["outcome"] == "boss_dead":
        yield from pause(1.2)


# ===================================================================================================================================================================================================
# 10. REPORT, CHECKS, FINISH
# ===================================================================================================================================================================================================
def report():
    lines = []

    def metric(name, text):
        line = "METRIC %s = %s" % (name, text)
        lines.append(line)
        log(line)

    base = M["base"] or {}
    O = S["O"] or {}
    fight_s = M["fight_t"]
    metric("build", "%s (%s); weapon style at the end %s" % (BUILD, BUILD_NOTE, O.get("style", "?")))
    metric("run_id", RUN_ID)
    metric("policy", "%s; source %s" % (POLICY, SOURCE_HASH))
    metric("outcome", "%s (%s)" % (M["outcome"], M["why"] or "-"))
    metric("fight_seconds", "%.1f of %.0f allowed (world time from the wake)" % (fight_s, LIMIT_FIGHT_S))
    lost = (M["boss_hp0"] - M["boss_hp_last"]) if (M["boss_hp0"] is not None and M["boss_hp_last"] is not None) else None
    coverage = []
    if M["outcome"] != "boss_dead":
        coverage.append("no victory")
    if lost is None or lost < 0.4 * (M["boss_hp0"] or 1.0):
        coverage.append("less than 40 percent boss health removed")
    if not base or O.get("stag_n", 0) <= base.get("stagger", 0):
        coverage.append("no posture break")
    if not base or O.get("rip_imp", 0) <= base.get("rip_imp", 0):
        coverage.append("no riposte impact")
    if BUILD == "Strength" and not any(M["hits_kind"].get(kind, 0) for kind in ("Strong", "Charged", "JumpHeavy")):
        coverage.append("no Strength heavy hit")
    heavy_presses = sum(M["presses"].get(kind, 0) for kind in HEAVY_KINDS)
    if BUILD in HEAVY_OPENER_BUILDS and heavy_presses < 3:
        coverage.append("only %d heavy swing(s); need at least 3 to exercise the heavy-opener policy" % heavy_presses)
    if BUILD == "Dex" and (not base or O.get("procs", 0) <= base.get("procs", 0)):
        coverage.append("no Dex bleed proc")
    if M["dodge_late"] > 0:
        coverage.append("%d dodge(s) pressed too late for the i-frames (close attacks are not reactively dodgeable: the run measures the bot)" % M["dodge_late"])
    if M["untracked"]:
        coverage.append("untracked boss moves dodged at a guessed time (%s)" % ", ".join(sorted(str(k) for k in M["untracked"])))
    metric("balance_evidence", "INCONCLUSIVE: " + "; ".join(coverage) if coverage else "mechanics exercised; repeated runs and owner feel test still required")
    if lost is not None:
        metric("boss_health", "%.0f -> %.0f, lost %.1f = %.1f weapon hits + %.1f bleed procs + %.1f riposte impacts + %.1f other" % (M["boss_hp0"], M["boss_hp_last"], lost, M["hp_hit"], M["hp_bleed"], M["hp_rip"], lost - M["hp_hit"] - M["hp_bleed"] - M["hp_rip"]))
    else:
        metric("boss_health", "not read")
    hits = M["hits"]
    metric("hits_landed", "%d (%s); %d hit record(s) without a health drop, %d health drop(s) without a record" % (hits, counts_text(M["hits_kind"]), M["rec_no_drop"], M["drop_no_rec"]))
    kinds = ", ".join("%s %.1f (n=%d)" % (k, avg(v), len(v)) for k, v in sorted(M["hp_by_kind"].items())) or "none matched"
    metric("boss_health_per_hit", "%.1f on average over all hits (weapon damage %.1f / %d hits); by kind: %s" % (M["hp_hit"] / hits if hits else 0.0, M["hp_hit"], hits, kinds))
    swings_seen = (O.get("swings", 0) - base.get("swings", 0)) if base else 0
    metric("swings_thrown", "%d bot presses (%s), %d swings seen by the swing tracker (%s), %d whiffs, %d ignored by the pack, %d cut short by a dodge" % (
        M["presses_total"], counts_text(M["presses"]), swings_seen, counts_text(M["swings_kind"]), M["whiffs"], M["ignored"], M["cuts"]))
    delays = "; ".join("%s median %.2f s (n=%d, guess %.2f)" % (k, sorted(v)[len(v) // 2], len(v), HIT_DELAY[k]) for k, v in sorted(M["swing_delays"].items()) if v) or "no hit landed"
    metric("swing_to_hit_delay", delays)
    metric("posture_breaks", "%d" % ((O.get("stag_n", 0) - base.get("stagger", 0)) if base else 0))
    metric("ripostes", "%d done (impacts), %d presses, %d accepted, %d rejected by the press itself, %d rejected requests counted by the boss" % (
        (O.get("rip_imp", 0) - base.get("rip_imp", 0)) if base else 0, M["rip_press"], M["rip_accepted"], M["rip_rejected"], (O.get("rip_rej", 0) - base.get("rip_rej", 0)) if base else 0))
    metric("bleed_procs", "%d (last proc took %.1f health)" % ((O.get("procs", 0) - base.get("procs", 0)) if base else 0, O.get("proc_dmg", 0.0)))
    metric("dodges", "%d presses, %d dodge montages (%d quick, %d full), %d wave jumps, %d ignored by the pack, %d late (the i-frames start after the hit was due), stamina cost samples %s" % (
        M["dodge_presses"], M["dodge_montages"], M["dodge_quick"], M["dodge_full"], M["wave_jumps"], M["dodge_refused"], M["dodge_late"], ", ".join("%.0f" % c for c in M["dodge_costs"][:8]) or "none"))
    by_move = {}
    for t in M["taken"]:
        key = t["who"].split(" at ")[0]
        by_move[key] = by_move.get(key, 0) + 1
    metric("hits_taken", "%d for %.0f health (%s); player health %s -> %s (lowest %s)" % (len(M["taken"]), M["taken_total"], counts_text(by_move), M["pl_hp0"], M["pl_hp_last"], M["pl_hp_min"]))
    metric("attacks_seen", "; ".join("%s %d (hit me %d, not hit after a dodge %d (NOT a dodge success rate: out of range counts too), missed on its own %d)" % (k, v["seen"], v["hit_me"], v["avoided"], v["missed"]) for k, v in sorted(M["attacks"].items())) or "no tracked attack")
    usable = [o for o in M["openings"] if o["usable"]]
    used = [o for o in usable if o["used"]]
    tried = [o for o in usable if o["attempted"]]
    by_kind = {}
    for o in usable:
        k = by_kind.setdefault(o["kind"], [0, 0])
        k[0] += 1
        k[1] += 1 if o["used"] else 0
    metric("openings", "%d usable (>= %.2f s) seen, %d used (at least one hit), %d tried; %d too short; by kind (seen/used): %s" % (
        len(usable), OPENING_MIN, len(used), len(tried), len(M["openings"]) - len(usable), "; ".join("%s %d/%d" % (k, v[0], v[1]) for k, v in sorted(by_kind.items())) or "none"))
    metric("stamina", "start %s, lowest %s at %.1f s, below %.0f for %.1f s, %d dips below 20" % (M["pl_st0"], M["st_min"], M["st_min_t"], LOW_STAMINA, M["st_low_s"], M["st_dips"]))
    metric("phase_two", "reached at %.1f s (boss health %s)" % (M["p2_t"], M["p2_hp"]) if M["p2_t"] is not None else "not reached")
    metric("untracked_boss_montages", "; ".join("%s x%d (%s)" % (k, v["n"], "attack-like: dodged" if v["attack_like"] else "ignored") for k, v in sorted(M["untracked"].items())) or "none")
    metric("walk_speed", "%.0f cm/s measured over %d frames (the bot assumed %.0f)" % (M["walk_sum"] / M["walk_n"], M["walk_n"], WALK_SPEED) if M["walk_n"] else "not measured")
    metric("strike_range", "%.0f cm at the end (started at %.0f)" % (S["strike"], STRIKE_RANGE0))
    M["metrics_lines"] = len(lines)
    try:
        archive = os.path.join(SAVED, "BalanceRuns")
        os.makedirs(archive, exist_ok=True)
        record = {"run_id": RUN_ID, "policy": POLICY, "source_sha256": SOURCE_HASH, "build": BUILD,
                  "build_source": BUILD_NOTE, "actual_style": O.get("style"), "flags": M["flags"], "outcome": M["outcome"],
                  "fight_seconds": fight_s, "boss_start": M["boss_hp0"], "boss_end": M["boss_hp_last"],
                  "player_start": M["pl_hp0"], "player_end": M["pl_hp_last"], "hits_by_kind": M["hits_kind"],
                  "posture_breaks": O.get("stag_n", 0) - base.get("stagger", 0) if base else 0,
                  "ripostes": O.get("rip_imp", 0) - base.get("rip_imp", 0) if base else 0,
                  "bleed_procs": O.get("procs", 0) - base.get("procs", 0) if base else 0,
                  "hits_taken": len(M["taken"]), "damage_taken": M["taken_total"], "coverage_gaps": coverage,
                  "errors": S["errors"], "error": M["error"], "metrics": lines,
                  "settings": {"spacing_max": SPACING_MAX, "strike_range": STRIKE_RANGE0, "close_dodge": CLOSE_DODGE,
                               "neutral_delay": BAIT_AFTER_S, "fight_limit": LIMIT_FIGHT_S}}
        with open(os.path.join(archive, "%s_%s.json" % (RUN_ID, BUILD)), "x", encoding="utf-8") as output:
            json.dump(record, output, indent=2)
        with open(os.path.join(SAVED, "build_fight_result_%s.txt" % BUILD), "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    except Exception as e:
        S["errors"] += 1
        M["error"] = "could not persist balance metrics"
        log("could not write the metrics file: %s" % e)


def final_checks():
    """Always the same ten checks, however the run ended (RESULT n/m must not shrink when the fight is lost)."""
    f = M["flags"]
    attacks = sum(v["seen"] for v in M["attacks"].values()) + sum(v["n"] for v in M["untracked"].values() if v["attack_like"])
    check("S1 the pawn, the boss and the components of the fight exist (tracker, stagger, posture, phases, encounter, debug, swing tracker, hit intake, loadout)", f["parts"], "")
    check("S2 the boss slept before the fight (dormant after the reset)", f["slept"], "")
    check("S3 the %s build was equipped before the wake (%s, loadout state Idle, weapon ability granted)" % (BUILD, STYLE.get(BUILD, "invalid scenario")), f["build_ok"], "")
    check("S4 the fight started: the boss woke and the clock ran (%.1f s of fight time, woke by %s)" % (M["fight_t"], M["woke_by"]), M["t0"] is not None, "")
    check("S5 the boss attacked at least once (%d tracked or untracked attack(s) seen)" % attacks, attacks >= 1, "")
    check("S6 the bot threw at least one swing (%d presses) and the hit intake was bound" % M["presses_total"], M["presses_total"] >= 1 and f["intake_bound"], "")
    check("S7 the weapon stayed the build's weapon (%d change(s) in the fight, style %s)" % (M["style_changes"], (S["O"] or {}).get("style", "?")), M["style_changes"] == 0 and f["build_ok"], "")
    check("S8 the run ended with a known outcome (%s: boss_dead, player_dead or timeout)" % M["outcome"], M["outcome"] in ("boss_dead", "player_dead", "timeout"), M["why"][:120])
    check("S9 the metrics were logged (%d METRIC lines)" % M["metrics_lines"], M["metrics_lines"] >= 10, "")
    check("S10 no script or tick error (%d)" % S["errors"], S["errors"] == 0 and M["error"] is None, str(M["error"] or "")[:160])


def finish():
    global handle
    if S["finished"]:
        return
    S["finished"] = True
    if handle:
        try:
            unreal.unregister_slate_post_tick_callback(handle)
        except Exception:
            pass
        handle = None
    try:
        console('rpg.Build ""')   # process wide: it must not stay set for the next driver (first, in its own try)
    except Exception:
        pass
    try:
        p = S["P"]
        if p and p.get("pc"):
            release_all(p["pc"])
    except Exception:
        pass
    if M["fight_on"] and M["outcome"] is None:
        end_fight("aborted", M["error"] or "the run ended before an outcome")
    try:
        if M["open_cur"] is not None and S["O"] is not None:
            close_opening(S["O"])   # an opening that was still running when the fight ended
        if M.get("cur_inst") is not None and S["O"] is not None:
            finalize_instance(M["cur_inst"], S["O"])   # the attack that killed the bot (or the last one) counts too
        report()
    except Exception:
        import traceback
        S["errors"] += 1
        log("report error " + traceback.format_exc())
    try:
        final_checks()
    except Exception:
        import traceback
        log("check error " + traceback.format_exc())
        check("final checks raised", False)
    log("RESULT %d/%d passed" % (sum(1 for r in RESULTS if r), len(RESULTS)))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()


# ===================================================================================================================================================================================================
# 11. THE TICK
# ===================================================================================================================================================================================================
def heartbeat(O):
    if O is not None and M["fight_on"]:
        log("AI running %s, test freeze %s, boss speed %.0f; player speed %.0f, move ignored %s" % (
            O["brain_running"], O["test_freeze"], O["boss_speed"], O["player_speed"], O["move_ignored"]))
        log("heartbeat: fight %.0f s | boss health %s%s, posture %.0f | player health %s stamina %s | dist %.0f | boss %s/%s | mode %s | hits %d, presses %d, dodges %d, taken %d, breaks %d, ripostes %d" % (
            M["fight_t"], O["boss_hp"], " (phase two)" if O["phase2"] else "", O["posture"], O["pl_hp"], ("%.0f" % O["pl_st"]) if O["pl_st"] is not None else "?", O["dist"], O["move"], O["phase"], S["mode"],
            M["hits"], M["presses_total"], M["dodge_presses"], len(M["taken"]), O["stag_n"] - M["base"].get("stagger", 0), O["rip_imp"] - M["base"].get("rip_imp", 0)))
    else:
        p = S["P"] or {}
        log("heartbeat: run %.0f s, pawn %s, boss %s, setup %s" % (S["run_t"], p["pawn"].get_name() if p.get("pawn") else None, p["boss"].get_name() if p.get("boss") else None, "running" if S["gen"] else "waiting"))


def _tick(dt):
    s = S
    s["t"] += dt
    if s["phase"] == "start":
        if s["t"] > 0.5:
            if BUILD not in BUILDS:
                M["error"] = BUILD_NOTE
                end_fight("setup_failed", BUILD_NOTE)
                finish()
                return
            console('rpg.Build "%s"' % BUILD)   # before the PIE: the first pawn's loadout reads it at its start (process wide, cleared in finish())
            unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
            s.update(phase="run", t=0.0)
        return
    if s["P"] is not None:
        s["run_t"] += dt   # the run limit counts from the first frame with a pawn and a boss (a cold shader cache can make the PIE start slow: KI-081)
    if s["run_t"] > LIMIT_RUN_S or (s["P"] is None and s["t"] > 300.0):
        M["error"] = "the run limit of %.0f real seconds was reached" % LIMIT_RUN_S if s["P"] is not None else "no pawn and boss 300 s after the PIE began"
        s["errors"] += 1
        finish()
        return
    w, pc, pawn, boss = actors()
    if w is not None:
        s["now"] = unreal.GameplayStatics.get_time_seconds(w)
    if s["run_t"] - s["hb"] > (10.0 if M["fight_on"] else 15.0):
        s["hb"] = s["run_t"]
        heartbeat(s["O"])
    if boss is None:
        s["gone"] += dt
        if M["fight_on"] and s["gone"] > 2.0:
            # the pack destroys a dead boss a few seconds after its death: a boss that vanished after an almost empty health bar is a death
            last, top = M["boss_hp_last"], M["boss_hp0"]
            if last is not None and top and last <= 0.15 * top:
                end_fight("boss_dead", "the boss is gone (destroyed by the pack) after its health fell to %s" % last)
            else:
                end_fight("boss_missing", "the boss actor is gone with health %s" % last)
            finish()
        elif s["gone"] > 15.0 and s["gen"] is not None:
            M["error"] = "the boss is missing for 15 s during the setup"
            finish()
        return
    s["gone"] = 0.0
    if pawn is None:
        s["nopawn"] += dt
        if M["fight_on"] and s["nopawn"] > 1.5:
            end_fight("player_dead", "no player pawn for 1.5 s (the pack respawns it about 4 s after the death)")
            finish()
        elif s["nopawn"] > 40.0 and s["gen"] is not None:
            M["error"] = "the player has no pawn for 40 s"
            finish()
        return
    s["nopawn"] = 0.0
    if s["pawn_name"] is not None and pawn.get_name() != s["pawn_name"]:
        if M["fight_on"]:
            end_fight("player_dead", "the player is a new pawn (%s -> %s): it died and the encounter reset" % (s["pawn_name"], pawn.get_name()))
        else:
            M["error"] = "the player pawn changed during the setup"
        finish()
        return
    s["P"] = {"w": w, "pc": pc, "pawn": pawn, "boss": boss}
    O = observe(s["P"])
    s["O"] = O
    account(O)
    if M["outcome"] is not None and M["outcome"] != "boss_dead" and s["gen"] is not None and M["fight_on"]:
        finish()   # a lost or timed out fight ends now (the boss_dead path waits 1.2 s in the script for the last counters)
        return
    if s["gen"] is None:
        if s["t"] < SETTLE_S:
            return
        s["gen"] = script()
    try:
        next(s["gen"])
    except StopIteration:
        apply_inputs(s["P"], O)
        finish()
        return
    apply_inputs(s["P"], O)


def tick(dt):
    try:
        _tick(dt)
    except Exception:
        import traceback
        S["errors"] += 1
        tb = traceback.format_exc()
        if S["errors"] <= 3:
            log("tick error " + tb)
        if M["error"] is None:
            M["error"] = tb.strip().splitlines()[-1][:200]
        if S["errors"] >= 5:
            log("five tick errors: ending the run")
            finish()


log("loaded: build %s (%s); the fight is not held; limit %.0f s of fight time" % (BUILD, BUILD_NOTE, LIMIT_FIGHT_S))
handle = unreal.register_slate_post_tick_callback(tick)
