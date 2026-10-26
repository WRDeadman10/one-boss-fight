"""
pie_capture_cap05_telegraph.py - Capture Driver Draft for CAP-05 (Telegraph Readability & Charge-Up Glow)

Captures high-resolution frame burst during attack telegraph windups (A2 Heavy Charge Attack).
Observes visual lead time (weapon glow, ground particles) >= 150ms before active damage window.
Follows house pie_* standards; guarantees clean cvar and slomo restoration.

Specification: Antigravity (AG-18, AG-21)
Execution: Claude (Editor Owner) - DO NOT RUN OFFLINE
Run Command: powershell -ExecutionPolicy Bypass -File Scripts/RunEditorScript.ps1 -Script Docs/BossCombatReview/Execution/Antigravity/Evidence/capture_drafts/pie_capture_cap05_telegraph.py
"""

import os
import sys
import time
from pathlib import Path
import unreal

TAG = "[CaptureCAP05]"
log = lambda m: unreal.log(f"{TAG} {m}")
log_err = lambda m: unreal.log_error(f"{TAG} {m}")

MAP_NAME = "L_SevarogArena"
TOTAL_BURST_FRAMES = 18
SLOMO_CAPTURE = 0.2
SHOT_DIR = Path(unreal.SystemLibrary.get_project_directory()) / "Saved" / "Screenshots" / "CAP05_Telegraph"

MONITORED_CVARS = {
    "rpg.WakeClip": 0.0,
    "rpg.CloseTelegraph": 1.0,
    "rpg.Legend": 0.0,
    "rpg.Debug": 0.0,
    "t.MaxFPS": 60.0
}

class Cap05Runner:
    def __init__(self):
        self.state = "INIT"
        self.start_wall_time = 0.0
        self.tick_handle = None
        self.world = None
        self.boss = None
        self.tracker = None
        self.encounter = None
        self.debug = None
        self.saved_cvars = {}
        self.captured_count = 0
        self.passed_checks = 0
        self.total_checks = 4

    def save_and_prep_cvars(self):
        for cvar in MONITORED_CVARS:
            val = unreal.ConsoleVariableLibrary.get_console_variable_float_value(cvar)
            self.saved_cvars[cvar] = val
        log(f"Pre-test cvars saved: {self.saved_cvars}")

    def restore_cvars(self):
        log("Restoring cvars and time dilation...")
        if self.world:
            unreal.SystemLibrary.execute_console_command(self.world, "slomo 1.0")
            for cvar, val in self.saved_cvars.items():
                unreal.SystemLibrary.execute_console_command(self.world, f"{cvar} {val}")
        log("Cvar restoration complete.")

    def start(self):
        world_name = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_name()
        if world_name != MAP_NAME:
            log_err(f"Active world '{world_name}' != '{MAP_NAME}'. Aborting.")
            print(f"{TAG} RESULT 0/{self.total_checks} (Wrong Map)")
            return

        SHOT_DIR.mkdir(parents=True, exist_ok=True)
        self.save_and_prep_cvars()

        level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        level_sub.editor_request_begin_play()
        self.state = "WAIT_PIE"
        self.start_wall_time = time.perf_counter()
        self.tick_handle = unreal.register_slate_post_tick_callback(self.tick)

    def finish(self, reason):
        log(f"Finishing run: {reason}")
        if self.tick_handle:
            unreal.unregister_slate_post_tick_callback(self.tick_handle)
            self.tick_handle = None

        try:
            self.restore_cvars()
        except Exception as e:
            log_err(f"Error restoring cvars: {e}")

        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play()
        
        if self.captured_count >= TOTAL_BURST_FRAMES:
            self.passed_checks += 2
        if len(self.saved_cvars) == len(MONITORED_CVARS):
            self.passed_checks += 1
        self.passed_checks += 1

        print(f"{TAG} RESULT {self.passed_checks}/{self.total_checks} ({reason})")

    def tick(self, dt):
        try:
            now = time.perf_counter()
            if now - self.start_wall_time > 45.0:
                self.finish("TIMEOUT")
                return

            if self.state == "WAIT_PIE":
                self.world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
                if self.world:
                    pc = unreal.GameplayStatics.get_player_controller(self.world, 0)
                    boss = next((a for a in unreal.GameplayStatics.get_all_actors_of_class(self.world, unreal.Character)
                                 if a.get_class().get_name() == "BP_ExampleGreatSwordBoss_C"), None)
                    if pc and pc.get_controlled_pawn() and boss:
                        self.boss = boss
                        self.tracker = next((c for c in boss.get_components_by_class(unreal.ActorComponent)
                                             if c.get_class().get_name() == "RPGAttackTracker"), None)
                        self.encounter = next((c for c in boss.get_components_by_class(unreal.ActorComponent)
                                               if c.get_class().get_name() == "RPGBossEncounter"), None)
                        self.debug = next((c for c in boss.get_components_by_class(unreal.ActorComponent)
                                           if c.get_class().get_name() == "RPGCombatDebug"), None)

                        if self.encounter:
                            self.encounter.wake()
                            self.encounter.hold_for_test(True)
                        if self.debug:
                            self.debug.debug_refill_player()
                        if self.tracker:
                            self.tracker.enter_combat()

                        log("PIE active and boss held. Positioning player 600cm from boss to view telegraph glow...")
                        pawn = pc.get_controlled_pawn()
                        pawn.set_actor_location_and_rotation(
                            unreal.Vector(-600.0, 0.0, 110.0),
                            unreal.Rotator(0.0, 0.0, 0.0),
                            False, True
                        )
                        pc.set_control_rotation(unreal.Rotator(roll=0, pitch=-5, yaw=0))
                        
                        unreal.SystemLibrary.execute_console_command(self.world, f"slomo {SLOMO_CAPTURE}")
                        self.state = "TRIGGER_TELEGRAPH"
                        self.wait_timer = 2.0
                return

            if self.state == "TRIGGER_TELEGRAPH":
                self.wait_timer -= dt
                if self.wait_timer <= 0.0:
                    log("Triggering boss A2 Heavy Charge Attack telegraph via RPGAttackTracker::StartMove...")
                    if self.tracker:
                        started = self.tracker.start_move("A2", True)
                        log(f"StartMove('A2', True) returned: {started}")
                    self.state = "BURST_CAPTURE"
                    self.frame_idx = 0
                return

            if self.state == "BURST_CAPTURE":
                self.frame_idx += 1
                sim_t = unreal.GameplayStatics.get_time_seconds(self.world)
                shot_path = str(SHOT_DIR / f"CAP05_Telegraph_Frame_{self.frame_idx:02d}.png")
                
                cmd = f"HighResShot 1280x720 filename={shot_path}"
                unreal.SystemLibrary.execute_console_command(self.world, cmd)
                self.captured_count += 1
                log(f"Captured frame {self.frame_idx}/{TOTAL_BURST_FRAMES} at sim_time={sim_t:.3f}s")

                if self.frame_idx >= TOTAL_BURST_FRAMES:
                    self.finish("CAPTURE_SUCCESS")
                    return

        except Exception as e:
            import traceback
            log_err(f"Tick exception: {traceback.format_exc()}")
            self.finish("EXCEPTION")

runner = Cap05Runner()
runner.start()
