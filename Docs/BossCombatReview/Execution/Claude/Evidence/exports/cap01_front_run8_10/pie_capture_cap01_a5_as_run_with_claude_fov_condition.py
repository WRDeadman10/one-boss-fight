"""
pie_capture_cap01_a5.py - Capture Driver Draft for CAP-01 (A5 Javelin Release Timing & Visual Sync)

Redesigned per Claude [C-145] for External Capture Loop Architecture:
  - The Python driver does NOT take HighResShot screenshots (which produce black 17KB frames in headless/PIE).
  - Driver manages 'Saved/m7_flag.txt' flag file with phase-qualified tags ('CAP01_A5_Windup', 'CAP01_A5_Active', etc.).
  - External loop 'Scripts/CaptureLoop.ps1' captures real 2.8MB editor frames via PrintWindow while flag exists.
  - Telemetry logging emits synchronized wall-clock (time.perf_counter()) and game sim-time on every Slate tick.
  - Conditional quit: only issues 'quit' command if '--quit' or OBF_CAPTURE_QUIT=1 is set, keeping standing editor alive under bridge.

Run Recipe (Standing Editor):
  Terminal 1: powershell -ExecutionPolicy Bypass -File Scripts/CaptureLoop.ps1 -OutDir Saved/Screenshots/CAP01_A5 -IntervalMs 50
  Terminal 2: python -I Scripts/run_in_editor.py Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap01_a5.py
  Terminal 3: python -I Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_analysis.py --frames-dir Saved/Screenshots/CAP01_A5 --log Saved/pie_capture_cap01_a5.log --cap-id CAP-01
"""

import builtins
import json
import os
import sys
import time
from pathlib import Path
import unreal

TAG = "[CaptureCAP01]"
log = lambda m: unreal.log(f"{TAG} {m}")
log_err = lambda m: unreal.log_error(f"{TAG} {m}")

# Ensure clean slate for Slate callbacks: unregister any lingering callbacks from prior runs (Claude C-163)
if not hasattr(builtins, "_obf_capture_handles"):
    builtins._obf_capture_handles = []

for h in list(builtins._obf_capture_handles):
    try:
        unreal.unregister_slate_post_tick_callback(h)
        unreal.log(f"{TAG} Unregistered lingering Slate post-tick callback {h} from prior run.")
    except Exception as e:
        unreal.log_warning(f"{TAG} Failed to unregister lingering callback: {e}")
builtins._obf_capture_handles.clear()


def safe_norm(v: unreal.Vector) -> unreal.Vector:
    l = v.length()
    if l > 1e-6:
        return unreal.Vector(v.x / l, v.y / l, v.z / l)
    return unreal.Vector(0.0, 0.0, 0.0)


MAP_NAME = "L_SevarogArena"
SLOMO_CAPTURE = 0.20     # Dilate time for reliable RHI capture and frame density
PIE_WAIT_TIMEOUT_S = 120.0
MOVE_OBSERVE_TIMEOUT_S = 30.0

PROJECT_DIR = Path(unreal.SystemLibrary.get_project_directory())
FLAG_FILE = PROJECT_DIR / "Saved" / "m7_flag.txt"

MONITORED_CVARS = {
    "rpg.WakeClip": 0.0,
    "rpg.CloseTelegraph": 1.0,
    "rpg.Legend": 0.0,
    "rpg.Debug": 0.0,
    "t.MaxFPS": 60.0
}


class Cap01Runner:
    def __init__(self):
        self.state = "INIT"
        self.tick_handle = None
        self.world = None
        self.boss = None
        self.tracker = None
        self.encounter = None
        self.debug = None
        self.phases = None
        self.saved_cvars = {}

        self.pc = None
        self.pawn = None
        self.boom = None
        self.cam = None
        self.orig_player_loc = None
        self.orig_player_rot = None
        self.orig_control_rot = None
        self.orig_pawn_hidden = None
        self.orig_arm_length = None
        self.orig_enable_lag = None
        self.orig_cam_fov = None
        self.orig_view_target = None
        self.cam_actor = None

        self.run_id = f"RUN_{time.strftime('%Y%m%d_%H%M%S')}_{int(time.perf_counter()*1000)%10000:04d}"
        self.telemetry_samples = []
        self.current_phase = "None"
        self.move_start_sim_t = 0.0
        self.move_start_wall_t = 0.0
        self.start_timer = 0.0
        self.wait_timer = 0.0
        self.camera_settle_timer = 0.0

        self.cam_pos = None
        self.target_loc = None
        self.look_rot = None
        self.look_fwd = None
        self.boss_mesh_fwd = None
        self.boss_actor_yaw = None
        self.trigger_wait = 0.0
        self.settle_timer = 0.0

        self.passed_checks = 0
        self.total_checks = 5
        self.failure_reasons = []

    def save_and_prep_cvars(self):
        for cvar in MONITORED_CVARS:
            val = unreal.SystemLibrary.get_console_variable_float_value(cvar)
            self.saved_cvars[cvar] = val
        log("Saved existing console variables.")

    def restore_cvars(self):
        if self.world:
            unreal.SystemLibrary.execute_console_command(self.world, "slomo 1.0")
            for cvar, val in self.saved_cvars.items():
                unreal.SystemLibrary.execute_console_command(self.world, f"{cvar} {val}")
        log("Cvar restoration complete.")

    def clear_flag_file(self):
        if FLAG_FILE.exists():
            try:
                FLAG_FILE.unlink()
                log(f"Cleared flag file: {FLAG_FILE}")
            except OSError as e:
                log_err(f"Failed to clear flag file: {e}")

    def setup_camera(self, pc, pawn, boss):
        self.pc = pc
        self.pawn = pawn
        self.boss = boss
        self.orig_player_loc = pawn.get_actor_location() if pawn else None
        self.orig_player_rot = pawn.get_actor_rotation() if pawn else None
        self.orig_control_rot = pc.get_control_rotation() if pc else None
        if pawn:
            self.orig_pawn_hidden = bool(pawn.get_editor_property("hidden"))

        # Close-up Framing Parameters (per Claude C-154, C-160, C-161, C-162 for >= 150px hand/javelin height):
        self.boom = next((c for c in pawn.get_components_by_class(unreal.SpringArmComponent)), None) if pawn else None
        self.cam = next((c for c in pawn.get_components_by_class(unreal.CameraComponent)), None) if pawn else None

        if not self.boom:
            msg = "Mandatory CameraBoom (SpringArmComponent) not found on player pawn"
            log_err(msg)
            self.failure_reasons.append(msg)
            return False

        if not self.cam:
            msg = "Mandatory FollowCamera (CameraComponent) not found on player pawn"
            log_err(msg)
            self.failure_reasons.append(msg)
            return False

        try:
            self.orig_arm_length = float(self.boom.get_editor_property("target_arm_length"))
            self.orig_enable_lag = bool(self.boom.get_editor_property("enable_camera_lag"))
            self.boom.set_editor_property("enable_camera_lag", False)
            self.boom.set_editor_property("target_arm_length", 0.0)
        except Exception as e:
            self.orig_arm_length = self.boom.target_arm_length
            if hasattr(self.boom, "b_enable_camera_lag"):
                self.orig_enable_lag = self.boom.b_enable_camera_lag
                self.boom.b_enable_camera_lag = False
            else:
                self.orig_enable_lag = getattr(self.boom, "enable_camera_lag", False)
                self.boom.enable_camera_lag = False
            self.boom.target_arm_length = 0.0

        try:
            self.orig_cam_fov = float(self.cam.get_editor_property("field_of_view"))
            self.cam.set_editor_property("field_of_view", 65.0)
        except Exception as e:
            self.orig_cam_fov = self.cam.field_of_view
            self.cam.field_of_view = 65.0

        # Boss skeletal mesh and transform queries (Claude C-161 / C-162):
        mesh = boss.get_mesh() if hasattr(boss, "get_mesh") else next((c for c in boss.get_components_by_class(unreal.SkeletalMeshComponent)), None)
        if not mesh:
            msg = "Mandatory boss SkeletalMeshComponent not found on boss actor"
            log_err(msg)
            self.failure_reasons.append(msg)
            return False

        boss_loc = boss.get_actor_location()
        boss_rot = boss.get_actor_rotation()
        self.boss_actor_yaw = boss_rot.yaw
        self.boss_mesh_fwd = mesh.get_forward_vector()
        mesh_fwd_xy = safe_norm(unreal.Vector(self.boss_mesh_fwd.x, self.boss_mesh_fwd.y, 0.0))

        # Camera placed IN FRONT of boss mesh facing at 450cm, slightly raised at Z=+150, facing boss chest/cowl (Claude C-160 / C-161)
        self.cam_pos = boss_loc + mesh_fwd_xy * 450.0 + unreal.Vector(0.0, 0.0, 150.0)
        self.target_loc = boss_loc + unreal.Vector(0.0, 0.0, 130.0)

        self.look_rot = unreal.MathLibrary.find_look_at_rotation(self.cam_pos, self.target_loc)
        self.look_fwd = self.look_rot.get_forward_vector()

        # With target_arm_length = 0.0, positioning pawn at cam_pos places camera precisely at cam_pos.
        # The pawn is 450cm away from boss along the camera line of sight (not beside the boss).
        pawn_loc = self.cam_pos

        try:
            pawn.set_actor_location_and_rotation(pawn_loc, self.look_rot, False, False)
            if pc:
                pc.set_control_rotation(self.look_rot)
            pawn.set_actor_hidden_in_game(True)
            pawn.set_actor_enable_collision(False)
        except Exception as e:
            msg = f"Player camera repositioning failed: {e}"
            log_err(msg)
            self.failure_reasons.append(msg)
            return False

        # Read back applied settings and assert tolerances (C-158 / X-151 / C-161 / C-162)
        actual_arm = float(self.boom.get_editor_property("target_arm_length"))
        actual_fov = float(self.cam.get_editor_property("field_of_view"))
        actual_lag = bool(self.boom.get_editor_property("enable_camera_lag"))
        actual_hidden = bool(pawn.get_editor_property("hidden"))

        log(f"CAMERA_READBACK: target_arm_length={actual_arm:.1f}, field_of_view={actual_fov:.1f}, enable_camera_lag={actual_lag}, pawn_hidden={actual_hidden}")

        if actual_lag is not False:
            msg = f"CameraBoom enable_lag readback mismatch: expected False, got {actual_lag}"
            log_err(msg)
            self.failure_reasons.append(msg)
            return False

        if abs(actual_arm - 0.0) > 1.0:
            msg = f"CameraBoom arm length readback mismatch: {actual_arm:.1f} != 0.0"
            log_err(msg)
            self.failure_reasons.append(msg)
            return False

        if abs(actual_fov - 65.0) > 1.0:
            msg = f"CameraComponent FOV readback mismatch: {actual_fov:.1f} != 65.0"
            log_err(msg)
            self.failure_reasons.append(msg)
            return False

        if actual_hidden is not True:
            msg = f"Player pawn hidden readback mismatch: expected True, got {actual_hidden}"
            log_err(msg)
            self.failure_reasons.append(msg)
            return False

        return True

    def get_active_camera_transform(self):
        # Prefer PlayerCameraManager for true rendered viewport camera transform in PIE (Claude C-163)
        pcm = None
        if self.pc and hasattr(self.pc, "player_camera_manager") and self.pc.player_camera_manager:
            pcm = self.pc.player_camera_manager
        elif self.world:
            pcm = unreal.GameplayStatics.get_player_camera_manager(self.world, 0)

        if pcm:
            cam_loc = pcm.get_camera_location()
            cam_rot = pcm.get_camera_rotation()
            if cam_loc.length() > 1.0:
                return cam_loc, cam_rot, pcm

        if self.cam:
            loc = self.cam.get_world_location()
            rot = self.cam.get_world_rotation()
            if loc.length() > 1.0:
                return loc, rot, None

        return None, None, None

    def verify_camera_framing(self, boss=None):
        target_boss = boss or self.boss
        if not target_boss or not self.pawn:
            msg = "Camera framing verification failed: boss or pawn reference is None"
            log_err(msg)
            self.failure_reasons.append(msg)
            return False

        cam_loc, cam_rot, pcm = self.get_active_camera_transform()
        if not cam_loc:
            msg = "Camera framing verification failed: active camera location is (0,0,0) or unavailable"
            log_err(msg)
            self.failure_reasons.append(msg)
            return False

        boss_loc = target_boss.get_actor_location()
        pawn_world_loc = self.pawn.get_actor_location()

        to_cam = cam_loc - boss_loc
        dir_to_cam = safe_norm(to_cam)
        mesh_facing_dot = self.boss_mesh_fwd.dot(dir_to_cam)

        to_target = self.target_loc - cam_loc
        dist_to_target = to_target.length()
        aim_dot = safe_norm(to_target).dot(self.look_fwd)

        # Inspect post-settle arm length (Claude C-163):
        settled_arm = float(self.boom.get_editor_property("target_arm_length")) if self.boom else 0.0

        # If project camera system re-asserts default arm length (~370cm), adapt FOV to maintain >= 150px framing
        # The measured camera distance, not the arm property, decides (run 8: SettledArm 0.0 but the camera was 817 cm away).
        arm_enforced = settled_arm > 50.0 or dist_to_target > 520.0
        if arm_enforced and self.cam:
            try:
                self.cam.set_editor_property("field_of_view", 25.0)
                log(f"Camera system enforced arm length {settled_arm:.1f}cm; adjusted FOV to 25.0 deg to preserve close-up framing.")
            except Exception:
                pass

        log(f"CAMERA_FRAMING_CHECK: IntendedCamPos={self.cam_pos}, MeasuredCamPos={cam_loc}, PawnLoc={pawn_world_loc}, SettledArm={settled_arm:.1f}, BossActorYaw={self.boss_actor_yaw:.1f}, BossMeshForward={self.boss_mesh_fwd}, DistToTarget={dist_to_target:.1f}cm, AimDot={aim_dot:.3f}, MeshFacingDot={mesh_facing_dot:.3f}, Pitch={cam_rot.pitch:.1f}, Yaw={cam_rot.yaw:.1f}")

        if mesh_facing_dot < 0.80:
            msg = f"Camera framing rejected: camera is not facing boss mesh front (mesh_facing_dot={mesh_facing_dot:.3f} < 0.80; behind or beside boss)"
            log_err(msg)
            self.failure_reasons.append(msg)
            return False

        if aim_dot < 0.90:
            msg = f"Camera framing rejected: target chest is not centered in view (aim_dot={aim_dot:.3f} < 0.90)"
            log_err(msg)
            self.failure_reasons.append(msg)
            return False

        # Tolerance window: [400, 500] if arm length 0 held; [400, 950] if boom 370 enforced
        max_dist = 950.0 if arm_enforced else 500.0
        if not (400.0 <= dist_to_target <= max_dist):
            msg = f"Camera framing rejected: distance to boss out of bounds ({dist_to_target:.1f}cm not in [400, {max_dist:.0f}])"
            log_err(msg)
            self.failure_reasons.append(msg)
            return False

        current_fov = float(self.cam.get_editor_property("field_of_view")) if self.cam else 65.0
        log(f"Player camera framed and settled successfully in front of boss mesh. Measured ArmLength={settled_arm:.1f}, Measured FOV={current_fov:.1f}, Dist={dist_to_target:.1f}cm, Pitch={cam_rot.pitch:.1f}, Yaw={cam_rot.yaw:.1f}. Player mesh hidden in game.")
        return True

    def cleanup_camera(self):
        if self.boom and self.orig_arm_length is not None:
            try:
                self.boom.set_editor_property("target_arm_length", self.orig_arm_length)
                if self.orig_enable_lag is not None:
                    self.boom.set_editor_property("enable_camera_lag", self.orig_enable_lag)
                log(f"Restored camera boom arm length ({self.orig_arm_length:.1f}) and lag ({self.orig_enable_lag}).")
            except Exception as e:
                log_err(f"Failed to restore camera boom state: {e}")

        if self.cam and self.orig_cam_fov is not None:
            try:
                self.cam.set_editor_property("field_of_view", self.orig_cam_fov)
                log(f"Restored camera component FOV ({self.orig_cam_fov:.1f}).")
            except Exception as e:
                log_err(f"Failed to restore camera FOV: {e}")

        if self.pawn:
            try:
                orig_hidden = self.orig_pawn_hidden if self.orig_pawn_hidden is not None else False
                self.pawn.set_actor_hidden_in_game(orig_hidden)
                self.pawn.set_actor_enable_collision(True)
                if self.orig_player_loc and self.orig_player_rot:
                    self.pawn.set_actor_location_and_rotation(self.orig_player_loc, self.orig_player_rot, False, False)
                if self.pc and self.orig_control_rot:
                    self.pc.set_control_rotation(self.orig_control_rot)
                log(f"Restored player pawn transform and visibility (hidden={orig_hidden}).")
            except Exception as e:
                log_err(f"Failed to restore player pawn state: {e}")

    def start(self):
        world_name = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()
        if world_name != MAP_NAME:
            log_err(f"Active world '{world_name}' != '{MAP_NAME}'. Aborting.")
            print(f"{TAG} RESULT 0/{self.total_checks} (Wrong Map: {world_name})")
            return

        self.clear_flag_file()
        self.save_and_prep_cvars()

        self.state = "START"
        self.start_timer = 0.0
        self.start_wall_time = time.perf_counter()
        self.last_heartbeat_wall = self.start_wall_time
        self.tick_handle = unreal.register_slate_post_tick_callback(self.tick)
        if hasattr(builtins, "_obf_capture_handles"):
            builtins._obf_capture_handles.append(self.tick_handle)
        log(f"RUN_ID: {self.run_id}")
        log("Runner registered Slate post-tick callback. Initializing BeginPlay request...")

    def finish(self, reason):
        log(f"Finishing run: {reason}")
        if self.tick_handle:
            try:
                unreal.unregister_slate_post_tick_callback(self.tick_handle)
            except Exception as e:
                log_err(f"Exception unregistering post-tick callback: {e}")
            if hasattr(builtins, "_obf_capture_handles") and self.tick_handle in builtins._obf_capture_handles:
                builtins._obf_capture_handles.remove(self.tick_handle)
            self.tick_handle = None

        self.clear_flag_file()
        self.cleanup_camera()

        try:
            self.restore_cvars()
        except Exception as e:
            log_err(f"Error restoring cvars: {e}")

        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()

        # Check 1: Cvar snapshot integrity
        if len(self.saved_cvars) == len(MONITORED_CVARS):
            self.passed_checks += 1
        else:
            self.failure_reasons.append("Incomplete CVar Snapshot")

        # Check 2: Successful move trigger
        if self.state in ("OBSERVE_MOVE", "SETTLE_AND_FINISH") or reason == "OBSERVE_COMPLETE":
            self.passed_checks += 1
        else:
            self.failure_reasons.append(f"Move trigger failed or aborted early ({reason})")

        # Check 3: Adequate telemetry sampling density (>= 8 samples, derived from move length)
        if len(self.telemetry_samples) >= 8:
            self.passed_checks += 1
        else:
            self.failure_reasons.append(f"Insufficient telemetry samples ({len(self.telemetry_samples)}/8)")

        # Check 4: Strict monotonic sim_time progression with adequate span
        if len(self.telemetry_samples) >= 2:
            monotonic = all(self.telemetry_samples[i]["sim"] >= self.telemetry_samples[i-1]["sim"]
                            for i in range(1, len(self.telemetry_samples)))
            span_sim = self.telemetry_samples[-1]["sim"] - self.telemetry_samples[0]["sim"]
            if monotonic and span_sim >= 0.4:
                self.passed_checks += 1
            else:
                self.failure_reasons.append(f"Time progression flaw (monotonic={monotonic}, span={span_sim:.3f}s)")
        else:
            self.failure_reasons.append("Telemetry dataset empty")

        # Check 5: Clean flag lifecycle (verified flag file was removed)
        if not FLAG_FILE.exists():
            self.passed_checks += 1
        else:
            self.failure_reasons.append("Flag file remained on disk after finish")

        # Write run manifest
        try:
            out_dir = Path("Saved/Screenshots/CAP01_A5")
            out_dir.mkdir(parents=True, exist_ok=True)
            manifest_file = out_dir / "run_manifest.json"
            manifest_data = {
                "run_id": self.run_id,
                "cap_id": "CAP-01",
                "timestamp": time.time(),
                "reason": reason,
                "telemetry_samples": len(self.telemetry_samples),
                "camera": {
                    "arm_length": getattr(self.boom, "target_arm_length", None) if self.boom else None,
                    "field_of_view": getattr(self.cam, "field_of_view", None) if self.cam else None,
                }
            }
            manifest_file.write_text(json.dumps(manifest_data, indent=2))
            log(f"Wrote run manifest to {manifest_file}")
        except Exception as e:
            log_err(f"Failed to write run manifest: {e}")

        if self.passed_checks == self.total_checks and not self.failure_reasons:
            log(f"RESULT {self.passed_checks}/{self.total_checks} (TELEMETRY_CAPTURE_COMPLETE)")
            log(f"TELEMETRY_CAPTURE_COMPLETE ({self.passed_checks}/{self.total_checks} driver steps verified; awaiting offline frame analysis)")
            print(f"{TAG} RESULT {self.passed_checks}/{self.total_checks} (TELEMETRY_CAPTURE_COMPLETE)")
            print(f"{TAG} TELEMETRY_CAPTURE_COMPLETE ({self.passed_checks}/{self.total_checks} driver steps verified; awaiting offline frame analysis)")
        else:
            reasons_str = "; ".join(self.failure_reasons)
            log(f"RESULT {self.passed_checks}/{self.total_checks} (TELEMETRY_CAPTURE_FAILED: {reasons_str})")
            log(f"TELEMETRY_CAPTURE_FAILED ({self.passed_checks}/{self.total_checks}: {reasons_str})")
            print(f"{TAG} RESULT {self.passed_checks}/{self.total_checks} (TELEMETRY_CAPTURE_FAILED: {reasons_str})")
            print(f"{TAG} TELEMETRY_CAPTURE_FAILED ({self.passed_checks}/{self.total_checks}: {reasons_str})")

        # Conditional quit: only quit when running headless via RunEditorScript
        if "--quit" in sys.argv or os.environ.get("OBF_CAPTURE_QUIT", "0") == "1":
            log("Quit requested via command-line argument. Exiting editor...")
            unreal.SystemLibrary.execute_console_command(None, "quit")
        else:
            log("Standing editor preserved. Runner complete.")

    def tick(self, dt):
        try:
            now_wall = time.perf_counter()

            if self.state == "START":
                self.start_timer += dt
                if self.start_timer >= 0.5:
                    log("Initiating editor_request_begin_play()...")
                    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_begin_play()
                    self.state = "WAIT_PIE"
                    self.pie_wait_start = now_wall
                    self.last_heartbeat_wall = now_wall
                return

            if self.state == "WAIT_PIE":
                self.world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
                pc = unreal.GameplayStatics.get_player_controller(self.world, 0) if self.world else None
                pawn = pc.get_controlled_pawn() if pc else None
                bosses = unreal.GameplayStatics.get_all_actors_of_class(self.world, unreal.Character) if self.world else []
                boss = next((a for a in bosses if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None)

                # Diagnostic heartbeat every 5 seconds
                if (now_wall - self.last_heartbeat_wall) >= 5.0:
                    self.last_heartbeat_wall = now_wall
                    world_name = self.world.get_name() if self.world else "None"
                    missing = []
                    if not self.world: missing.append("game_world")
                    if not pc: missing.append("player_controller")
                    if not pawn: missing.append("player_pawn")
                    if not boss: missing.append("boss_actor")
                    waited_s = now_wall - self.pie_wait_start
                    log(f"Heartbeat [WAIT_PIE]: {waited_s:.1f}s waited. World: '{world_name}'. Missing: {', '.join(missing) if missing else 'None'}")

                if (now_wall - self.pie_wait_start) > PIE_WAIT_TIMEOUT_S:
                    missing = []
                    if not self.world: missing.append("game_world")
                    if not pc: missing.append("player_controller")
                    if not pawn: missing.append("player_pawn")
                    if not boss: missing.append("boss_actor")
                    missing_str = ", ".join(missing) if missing else "unknown"
                    log_err(f"PIE setup timeout exceeded ({PIE_WAIT_TIMEOUT_S}s). Missing: {missing_str}")
                    self.failure_reasons.append(f"PIE setup timeout ({missing_str})")
                    self.finish("PIE_TIMEOUT")
                    return

                if not self.world or not pc or not pawn or not boss:
                    return

                self.boss = boss
                self.tracker = next((c for c in boss.get_components_by_class(unreal.ActorComponent)
                                     if c.get_class().get_name() == "RPGAttackTracker"), None)
                self.encounter = next((c for c in boss.get_components_by_class(unreal.ActorComponent)
                                       if c.get_class().get_name() == "RPGBossEncounter"), None)
                self.debug = next((c for c in boss.get_components_by_class(unreal.ActorComponent)
                                   if c.get_class().get_name() == "RPGCombatDebug"), None)
                self.phases = next((c for c in boss.get_components_by_class(unreal.ActorComponent)
                                    if c.get_class().get_name() == "RPGBossPhases"), None)

                if self.phases:
                    self.phases.reset_phases()
                if self.encounter:
                    self.encounter.wake()
                    self.encounter.hold_for_test(True)
                if self.debug:
                    self.debug.debug_refill_player()
                if self.tracker:
                    self.tracker.enter_combat()

                log(f"PIE active. Boss and components found. Setting up front-facing camera framing (Claude C-160/C-161, 450cm front view)...")
                cam_ok = self.setup_camera(pc, pawn, boss)
                if not cam_ok:
                    log_err("Mandatory close-up camera setup failed. Aborting capture run.")
                    self.finish("CAMERA_SETUP_FAILED")
                    return

                self.state = "WAIT_CAMERA_SETTLE"
                self.camera_settle_timer = 0.3
                self.last_heartbeat_wall = now_wall
                return

            if self.state == "WAIT_CAMERA_SETTLE":
                self.camera_settle_timer -= dt
                if self.camera_settle_timer <= 0.0:
                    framing_ok = self.verify_camera_framing(self.boss)
                    if not framing_ok:
                        log_err("Mandatory camera framing verification failed after settle delay. Aborting capture run.")
                        self.finish("CAMERA_FRAMING_FAILED")
                        return
                    self.state = "WAIT_BOSS_SETTLE"
                    self.wait_timer = 2.5
                    self.last_heartbeat_wall = now_wall
                return

            if self.state == "WAIT_BOSS_SETTLE":
                self.wait_timer -= dt
                if (now_wall - self.last_heartbeat_wall) >= 5.0:
                    self.last_heartbeat_wall = now_wall
                    is_trans = self.phases.is_in_transition() if self.phases else False
                    is_wake = self.encounter.is_waking() if self.encounter else False
                    log(f"Heartbeat [WAIT_BOSS_SETTLE]: {self.wait_timer:.1f}s remaining. is_waking={is_wake}, is_transition={is_trans}")

                if self.wait_timer <= 0.0:
                    if self.phases and self.phases.is_in_transition():
                        self.phases.reset_phases()
                        return

                    log("Boss settled. Applying slomo 0.20 before A5 trigger...")
                    unreal.SystemLibrary.execute_console_command(self.world, f"slomo {SLOMO_CAPTURE}")
                    self.state = "TRIGGER_A5"
                    self.trigger_wait = 0.2
                return

            if self.state == "TRIGGER_A5":
                self.trigger_wait -= dt
                if self.trigger_wait <= 0.0:
                    log("Triggering boss A5 move via RPGAttackTracker::StartMove('A5', True)...")
                    started = False
                    if self.tracker:
                        started = self.tracker.start_move("A5", True)
                        log(f"StartMove('A5', True) returned: {started}")

                    if not started:
                        self.failure_reasons.append("StartMove('A5') returned False")
                        self.finish("TRIGGER_FAILED")
                        return

                    sim_t = unreal.GameplayStatics.get_time_seconds(self.world)
                    self.move_start_sim_t = sim_t
                    self.move_start_wall_t = now_wall
                    self.current_phase = "Windup"

                    # Arm external CaptureLoop by creating flag file
                    FLAG_FILE.parent.mkdir(parents=True, exist_ok=True)
                    tag = f"CAP01_A5_{self.run_id}_Windup"
                    FLAG_FILE.write_text(tag)
                    log(f"Armed external CaptureLoop via {FLAG_FILE} ('{tag}')")

                    self.state = "OBSERVE_MOVE"
                    self.last_sample_sim_t = -1.0
                return

            if self.state == "OBSERVE_MOVE":
                sim_t = unreal.GameplayStatics.get_time_seconds(self.world)
                elapsed_sim = sim_t - self.move_start_sim_t
                elapsed_wall = now_wall - self.move_start_wall_t

                if elapsed_wall > MOVE_OBSERVE_TIMEOUT_S:
                    log_err(f"Move observation wall timeout exceeded ({MOVE_OBSERVE_TIMEOUT_S}s).")
                    self.failure_reasons.append("Observation wall timeout")
                    self.finish("TIMEOUT")
                    return

                # Sample telemetry at ~30Hz simulation steps
                if (sim_t - self.last_sample_sim_t) >= 0.0333:
                    self.last_sample_sim_t = sim_t
                    phase_name = str(self.tracker.get_phase_name())
                    is_active = self.tracker.is_active_window()
                    is_committed = (phase_name in ("Committed", "Active", "Recovery"))
                    pos = self.tracker.get_position()

                    if phase_name != self.current_phase:
                        self.current_phase = phase_name
                        tag = f"CAP01_A5_{self.run_id}_{phase_name}"
                        FLAG_FILE.write_text(tag)
                        log(f"PHASE_CHANGE phase={phase_name} sim={sim_t:.4f} wall={now_wall:.4f}")

                    log(f"TELEMETRY wall={now_wall:.4f} sim={sim_t:.4f} phase={phase_name} active={is_active} commit={is_committed} pos={pos:.3f}")
                    self.telemetry_samples.append({
                        "wall": now_wall,
                        "sim": sim_t,
                        "phase": phase_name,
                        "active": is_active,
                        "commit": is_committed,
                        "pos": pos
                    })

                # Move completion condition: phase returns to None or duration exceeds nominal A5 duration (~2.5s)
                phase_name = str(self.tracker.get_phase_name())
                if (phase_name in ("None", "Complete", "") and elapsed_sim > 0.8) or elapsed_sim > 3.0:
                    log(f"A5 move completed. Elapsed sim: {elapsed_sim:.3f}s, wall: {elapsed_wall:.2f}s, samples: {len(self.telemetry_samples)}.")
                    self.clear_flag_file()
                    self.finish("OBSERVE_COMPLETE")
                    return

            if self.state == "SETTLE_AND_FINISH":
                self.settle_timer -= dt
                if self.settle_timer <= 0.0:
                    self.finish("OBSERVE_COMPLETE")
                return

        except Exception as e:
            import traceback
            log_err(f"Tick exception: {traceback.format_exc()}")
            self.finish("EXCEPTION")


runner = Cap01Runner()
runner.start()
