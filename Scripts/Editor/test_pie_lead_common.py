"""Offline helper contract tests; no Unreal import or editor required."""
import unittest

import pie_lead_common as common


class Named:
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name


class Component:
    def __init__(self, name):
        self.name = name
        self.calls = []

    def get_class(self):
        return Named(self.name)

    def call_method(self, method, args=()):
        self.calls.append((method, args))
        return 123.0

    def debug_refill_player(self):
        self.calls.append(("refill", ()))


class Actor:
    def __init__(self, name, components=()):
        self.name = name
        self.components = list(components)

    def get_class(self):
        return Named(self.name)

    def get_components_by_class(self, _):
        return self.components


class Tags:
    def import_text(self, value):
        self.text = value


class FakeUE:
    ActorComponent = object()
    Character = object()
    SkeletalMeshComponent = object()
    LevelEditorSubsystem = object()
    GameplayTagContainer = Tags
    GameplayTag = Tags

    class GameplayStatics:
        @staticmethod
        def get_all_actors_of_class(world, _):
            return world.actors

        @staticmethod
        def get_time_seconds(world):
            return world.time

    @staticmethod
    def Vector(*coords):
        return coords

    @staticmethod
    def Rotator(*angles):
        return angles

    def get_editor_subsystem(self, _):
        return self

    def editor_request_end_play(self):
        self.ended = True


class CommonTests(unittest.TestCase):
    def setUp(self):
        self.ue = FakeUE()

    def test_boss_lookup_and_boss_owned_refill(self):
        debug = Component("RPGCombatDebug")
        player = Actor("Player", [])
        boss = Actor("BP_ExampleGreatSwordBoss_C", [debug])
        world = type("World", (), {"actors": [player, boss], "time": 12.5})()
        self.assertIs(common.boss_actor(world, self.ue), boss)
        common.refill_player(boss, self.ue)
        self.assertEqual(debug.calls, [("refill", ())])
        self.assertEqual(common.game_time(world, self.ue), 12.5)
        with self.assertRaisesRegex(RuntimeError, "on boss"):
            common.refill_player(player, self.ue)

    def test_enter_combat_health_and_placement(self):
        asc = Component("BP_AdvancedAbilitySystemComponent_C")
        attrs = Component("BP_AttributesComponent_C")
        player = Actor("Player", [asc, attrs])
        common.enter_combat(player, self.ue)
        self.assertEqual(asc.calls[0][0], "Try Activate Abilities By Tag")
        self.assertIn("Ability.EnterCombat", asc.calls[0][1][0].text)
        self.assertEqual(common.health(player, self.ue), 123.0)
        pc = type("PC", (), {"set_control_rotation": lambda self, value: setattr(self, "rotation", value)})()
        player.set_actor_location_and_rotation = lambda *args: setattr(player, "placement", args)
        common.place_player(pc, player, (1, 2, 3), 180, self.ue)
        self.assertEqual(player.placement[0], (1, 2, 3))
        self.assertEqual(pc.rotation, (0.0, 0.0, 180))

    def test_finished_marker(self):
        lines = []
        common.finished(lines.append, "done", self.ue)
        self.assertEqual(lines, ["SUMMARY finished: done"])
        self.assertTrue(self.ue.ended)

    def test_missing_actors_and_components_fail_closed(self):
        self.assertIsNone(common.boss_actor(None, self.ue))
        self.assertIsNone(common.component(None, "RPGCombatDebug", self.ue))
        self.assertIsNone(common.health(None, self.ue))
        self.assertEqual(common.player_montage(None, self.ue), (None, None))
        player = Actor("Player")
        with self.assertRaisesRegex(RuntimeError, "ability component"):
            common.enter_combat(player, self.ue)

    def test_montage_reads_first_active_mesh(self):
        class Mesh:
            def __init__(self, instance):
                self.instance = instance

            def get_anim_instance(self):
                return self.instance

        class Anim:
            def get_current_active_montage(self):
                return Named("Counter")

            def montage_get_position(self, _):
                return 0.25

        player = Actor("Player", [Mesh(None), Mesh(Anim())])
        self.assertEqual(common.player_montage(player, self.ue), ("Counter", 0.25))


if __name__ == "__main__":
    unittest.main()
