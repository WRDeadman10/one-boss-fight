"""
M6 content setup: puts a benchmark runner into L_Greybox so the real boss fight can be benchmarked
(-RPGBenchmark -RPGBenchmarkFight). The runner does nothing without the command-line switch. Idempotent.

Run headless (editor closed):
  UnrealEditor-Cmd.exe OneBossFight.uproject -run=pythonscript -script=Scripts/Editor/setup_m6_content.py -unattended -nullrhi
"""
import unreal

LEVEL = "/Game/OneBossFight/Levels/L_Greybox"

unreal.EditorLevelLibrary.load_level(LEVEL)
for actor in unreal.EditorLevelLibrary.get_all_level_actors():
    if actor.get_actor_label() == "BenchmarkRunner":
        actor.destroy_actor()

runner = unreal.EditorLevelLibrary.spawn_actor_from_class(
    unreal.load_class(None, "/Script/OneBossFight.RPGBenchmarkRunner"), unreal.Vector(0.0, 0.0, 150.0))
runner.set_actor_label("BenchmarkRunner")
runner.set_editor_property("run_label", "fight")
runner.set_editor_property("orbit_radius", 1500.0)
runner.set_editor_property("orbit_height", 450.0)
unreal.EditorLevelLibrary.save_current_level()
unreal.log("[M6Setup] BenchmarkRunner placed in L_Greybox.")
