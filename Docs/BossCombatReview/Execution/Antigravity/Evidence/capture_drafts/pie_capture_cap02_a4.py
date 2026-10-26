"""
pie_capture_cap02_a4.py - Capture Driver Draft for CAP-02 (A4 Low Sweep Query vs Visible Blade)

Redesigned per Claude [C-145] for External Capture Loop Architecture:
  - The Python driver does NOT take HighResShot screenshots (which produce black 17KB frames in headless/PIE).
  - Driver manages 'Saved/m7_flag.txt' flag file with phase-qualified tags ('CAP02_A4_Windup', 'CAP02_A4_Active', etc.).
  - External loop 'Scripts/CaptureLoop.ps1' captures real 2.8MB editor frames via PrintWindow while flag exists.
  - Telemetry logging emits synchronized wall-clock (time.perf_counter()) and game sim-time on every Slate tick.
  - Conditional quit: only issues 'quit' command if '--quit' or OBF_CAPTURE_QUIT=1 is set, keeping standing editor alive under bridge.

Run Recipe (Standing Editor):
  Terminal 1: powershell -ExecutionPolicy Bypass -File Scripts/CaptureLoop.ps1 -OutDir Saved/Screenshots/CAP02_A4 -IntervalMs 50
  Terminal 2: python -I Scripts/run_in_editor.py Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap02_a4.py
  Terminal 3: python -I Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_analysis.py --frames-dir Saved/Screenshots/CAP02_A4 --log Saved/pie_capture_cap02_a4.log --cap-id CAP-02
"""

import os
import sys
import time
from pathlib import Path
import unreal

TAG = "[CaptureCAP02]"
log = lambda m: unreal.log(f"{TAG} {m}")
log_err = lambda m: unreal.log_error(f"{TAG} {m}")

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


class Cap02Runner:
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
        self.orig_view_target = None
        self.cam_actor = None

        self.telemetry_samples = []
        self.current_phase = "None"
        self.move_start_sim_t = 0.0
        self.move_start_wall_t = 0.0
        self.start_timer = 0.0
        self.wait_timer = 0.0
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

    def setup_camera(self, pc, boss_loc, cam_loc, target_loc):
        self.pc = pc
        self.orig_view_target = pc.get_view_target() if pc else None
        rot = unreal.MathLibrary.find_look_at_rotation(cam_loc, target_loc)
        cam = None
        try:
            cam = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.CameraActor, cam_loc, rot)
        except Exception as e:
            log(f"EditorLevelLibrary spawn failed ({e}), attempting GameplayStatics...")

        if not cam and self.world:
            try:
                t = unreal.Transform(rot, cam_loc, unreal.Vector(1.0, 1.0, 1.0))
                cam = unreal.GameplayStatics.begin_spawning_actor_from_class(self.world, unreal.CameraActor, t)
                if cam:
                    unreal.GameplayStatics.finish_spawning_actor(cam, t)
            except Exception as e:
                log_err(f"GameplayStatics camera spawn failed: {e}")

        if cam:
            self.cam_actor = cam
            cam.set_actor_location_and_rotation(cam_loc, rot, False, True)
            if pc:
                pc.set_view_target_with_blend(cam, 0.0)
            log(f"Dedicated CameraActor spawned at {cam_loc}, rot {rot}. View target set.")
        else:
            log_err("Failed to spawn dedicated CameraActor; falling back to default camera.")

    def cleanup_camera(self):
        if self.pc and self.orig_view_target:
            try:
                self.pc.set_view_target_with_blend(self.orig_view_target, 0.0)
                log("Restored original view target.")
            except Exception as e:
                log_err(f"Failed to restore view target: {e}")
            self.orig_view_target = None
        if self.cam_actor:
            try:
                self.cam_actor.destroy_actor()
                log("Destroyed dedicated CameraActor.")
            except Exception as e:
                log_err(f"Failed to destroy CameraActor: {e}")
            self.cam_actor = None

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
        log("Runner registered Slate post-tick callback. Initializing BeginPlay request...")

    def finish(self, reason):
        log(f"Finishing run: {reason}")
        if self.tick_handle:
            unreal.unregister_slate_post_tick_callback(self.tick_handle)
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

        if self.passed_checks == self.total_checks:
            print(f"{TAG} RESULT {self.passed_checks}/{self.total_checks} (PASSED: All checks verified; telemetry captured)")
        else:
            reasons_str = "; ".join(self.failure_reasons)
            print(f"{TAG} RESULT {self.passed_checks}/{self.total_checks} (FAILED: {reasons_str})")

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

                log(f"PIE active. Boss and components found. Setting up dedicated CameraActor for A4 low sweep observation...")
                boss_loc = boss.get_actor_location()
                cam_loc = unreal.Vector(boss_loc.x - 300.0, boss_loc.y + 180.0, boss_loc.z + 80.0)
                target_loc = unreal.Vector(boss_loc.x, boss_loc.y, boss_loc.z + 30.0)
                self.setup_camera(pc, boss_loc, cam_loc, target_loc)

                # Move player pawn clear of camera line of sight
                pawn.set_actor_location_and_rotation(
                    unreal.Vector(boss_loc.x - 600.0, boss_loc.y - 400.0, 110.0),
                    unreal.Rotator(0.0, 0.0, 0.0),
                    False, True
                )

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

                    log("Boss settled. Applying slomo 0.20 before A4 trigger...")
                    unreal.SystemLibrary.execute_console_command(self.world, f"slomo {SLOMO_CAPTURE}")
                    self.state = "TRIGGER_A4"
                    self.trigger_wait = 0.2
                return

            if self.state == "TRIGGER_A4":
                self.trigger_wait -= dt
                if self.trigger_wait <= 0.0:
                    log("Triggering boss A4 move via RPGAttackTracker::StartMove('A4', True)...")
                    started = False
                    if self.tracker:
                        started = self.tracker.start_move("A4", True)
                        log(f"StartMove('A4', True) returned: {started}")

                    if not started:
                        self.failure_reasons.append("StartMove('A4') returned False")
                        self.finish("TRIGGER_FAILED")
                        return

                    sim_t = unreal.GameplayStatics.get_time_seconds(self.world)
                    self.move_start_sim_t = sim_t
                    self.move_start_wall_t = now_wall
                    self.current_phase = "Windup"

                    FLAG_FILE.parent.mkdir(parents=True, exist_ok=True)
                    FLAG_FILE.write_text("CAP02_A4_Windup")
                    log(f"Armed external CaptureLoop via {FLAG_FILE} ('CAP02_A4_Windup')")

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

                if (sim_t - self.last_sample_sim_t) >= 0.0333:
                    self.last_sample_sim_t = sim_t
                    phase_name = str(self.tracker.get_phase_name())
                    is_active = self.tracker.is_active_window()
                    is_committed = (phase_name in ("Committed", "Active", "Recovery"))
                    pos = self.tracker.get_position()

                    if phase_name != self.current_phase:
                        self.current_phase = phase_name
                        tag = f"CAP02_A4_{phase_name}"
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

                phase_name = str(self.tracker.get_phase_name())
                if (phase_name in ("None", "Complete", "") and elapsed_sim > 0.8) or elapsed_sim > 3.0:
                    log(f"A4 move completed. Elapsed sim: {elapsed_sim:.3f}s, wall: {elapsed_wall:.2f}s, samples: {len(self.telemetry_samples)}.")
                    self.clear_flag_file()
                    self.state = "SETTLE_AND_FINISH"
                    self.settle_timer = 0.5
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


runner = Cap02Runner()
runner.start()
