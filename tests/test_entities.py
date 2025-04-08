from unittest import TestCase
from unittest.mock import patch
import time

import entities


class TestEntities(TestCase):
    def setUp(self):
        entities.entities = []
        entities.projectiles = []
        entities.enemies = []
        entities.enemy_projectiles = []

    def test_create_projectile(self):
        proj = entities.create_projectile(5.0, 5.0, 0.0)

        self.assertEqual(proj["type"], entities.ENTITY_PROJECTILE)
        self.assertEqual(proj["x"], 5.0)
        self.assertEqual(proj["y"], 5.0)
        self.assertEqual(proj["angle"], 0.0)
        self.assertEqual(proj["speed"], 5.0)
        self.assertEqual(proj["damage"], 25)
        self.assertFalse(proj["remove"])

        self.assertIn(proj, entities.entities)
        self.assertIn(proj, entities.projectiles)

    def test_create_projectile_custom_params(self):
        proj = entities.create_projectile(
            10.0, 15.0, 1.5, speed=3.0, lifetime=2.0, damage=30
        )

        self.assertEqual(proj["type"], entities.ENTITY_PROJECTILE)
        self.assertEqual(proj["x"], 10.0)
        self.assertEqual(proj["y"], 15.0)
        self.assertEqual(proj["angle"], 1.5)
        self.assertEqual(proj["speed"], 3.0)
        self.assertEqual(proj["lifetime"], 2.0)
        self.assertEqual(proj["damage"], 30)

    def test_create_enemy_projectile(self):
        proj = entities.create_enemy_projectile(10.0, 8.0, 1.5)

        self.assertEqual(proj["type"], entities.ENTITY_ENEMY_PROJECTILE)
        self.assertEqual(proj["x"], 10.0)
        self.assertEqual(proj["y"], 8.0)
        self.assertEqual(proj["angle"], 1.5)
        self.assertEqual(proj["speed"], 4.0)
        self.assertEqual(proj["damage"], entities.ENEMY_PROJECTILE_DAMAGE)
        self.assertFalse(proj["remove"])

        self.assertIn(proj, entities.entities)
        self.assertIn(proj, entities.enemy_projectiles)

    def test_create_enemy_projectile_custom_params(self):
        proj = entities.create_enemy_projectile(
            7.0, 12.0, 0.5, speed=2.0, lifetime=3.0, damage=10
        )

        self.assertEqual(proj["x"], 7.0)
        self.assertEqual(proj["y"], 12.0)
        self.assertEqual(proj["angle"], 0.5)
        self.assertEqual(proj["speed"], 2.0)
        self.assertEqual(proj["lifetime"], 3.0)
        self.assertEqual(proj["damage"], 10)

    def test_create_enemy(self):
        enemy = entities.create_enemy(5.0, 5.0)

        self.assertEqual(enemy["type"], entities.ENTITY_ENEMY)
        self.assertEqual(enemy["x"], 5.0)
        self.assertEqual(enemy["y"], 5.0)
        self.assertEqual(enemy["health"], 100)
        self.assertEqual(enemy["max_health"], 100)
        self.assertEqual(enemy["state"], "idle")
        self.assertFalse(enemy["remove"])

        self.assertIn(enemy, entities.entities)
        self.assertIn(enemy, entities.enemies)

    def test_create_enemy_custom_health(self):
        enemy = entities.create_enemy(7.0, 8.0, health=150)

        self.assertEqual(enemy["x"], 7.0)
        self.assertEqual(enemy["y"], 8.0)
        self.assertEqual(enemy["health"], 150)
        self.assertEqual(enemy["max_health"], 150)

    def test_create_boss(self):
        boss = entities.create_boss(15.0, 15.0)

        self.assertEqual(boss["type"], entities.ENTITY_ENEMY)
        self.assertEqual(boss["subtype"], "boss")
        self.assertEqual(boss["x"], 15.0)
        self.assertEqual(boss["y"], 15.0)
        self.assertEqual(boss["health"], 500)
        self.assertEqual(boss["max_health"], 500)
        self.assertGreater(boss["detection_range"], 10.0)
        self.assertFalse(boss["remove"])
        self.assertIn("attack_patterns", boss)

        self.assertIn(boss, entities.entities)
        self.assertIn(boss, entities.enemies)

    @patch("time.time")
    def test_update_projectile_movement_lifetime(self, mock_time):
        mock_time.return_value = 100.0
        proj = {
            "x": 5.0,
            "y": 5.0,
            "angle": 0.0,
            "speed": 5.0,
            "creation_time": 98.0,
            "lifetime": 1.5,
            "remove": False,
        }
        world_map = [[0]]

        result = entities._update_projectile_movement(proj, 0.1, world_map, 100.0)

        self.assertTrue(result)
        self.assertTrue(proj["remove"])

    @patch("utils.collision.is_collision")
    def test_update_projectile_movement_collision(self, mock_collision):
        proj = {
            "x": 5.0,
            "y": 5.0,
            "angle": 0.0,
            "speed": 5.0,
            "creation_time": 100.0,
            "lifetime": 10.0,
            "remove": False,
        }
        world_map = [[0]]
        mock_collision.return_value = True

        result = entities._update_projectile_movement(proj, 0.1, world_map, 101.0)

        self.assertTrue(result)
        self.assertTrue(proj["remove"])
        self.assertNotEqual(proj["x"], 5.0)

    @patch("entities._update_projectile_movement")
    def test_update_projectiles_hit_enemy(self, mock_update_movement):
        mock_update_movement.return_value = False
        current_time = time.time()

        proj = {"x": 5.0, "y": 5.0, "damage": 40, "remove": False}
        enemy = {
            "x": 5.0,
            "y": 5.0,
            "health": 100,
            "state": "idle",
            "remove": False,
            "color": entities.ENEMY_COLOR,
        }

        entities.projectiles = [proj]
        entities.enemies = [enemy]

        entities.update_projectiles(0.1, [[0]], current_time)

        self.assertTrue(proj["remove"])
        self.assertEqual(enemy["health"], 60)

    @patch("entities._update_projectile_movement")
    def test_update_projectiles_kill_enemy(self, mock_update_movement):
        mock_update_movement.return_value = False
        current_time = time.time()

        proj = {"x": 5.0, "y": 5.0, "damage": 100, "remove": False}
        enemy = {
            "x": 5.0,
            "y": 5.0,
            "health": 100,
            "state": "idle",
            "remove": False,
            "color": entities.ENEMY_COLOR,
        }

        entities.projectiles = [proj]
        entities.enemies = [enemy]

        entities.update_projectiles(0.1, [[0]], current_time)

        self.assertTrue(proj["remove"])
        self.assertEqual(enemy["health"], 0)
        self.assertEqual(enemy["state"], "dead")
        self.assertEqual(enemy["color"], entities.ENEMY_DEAD_COLOR)
        self.assertFalse(enemy["xp_awarded"])

    @patch("entities._update_projectile_movement")
    def test_update_enemy_projectiles_hit_player(self, mock_update_movement):
        mock_update_movement.return_value = False

        proj = {"x": 5.0, "y": 5.0, "damage": 15, "remove": False}

        player_state = {"health": 100}

        entities.enemy_projectiles = [proj]

        entities.update_enemy_projectiles(
            0.1, [[0]], 5.0, 5.0, player_state, time.time()
        )

        self.assertTrue(proj["remove"])
        self.assertEqual(player_state["health"], 85)

    def test_try_move_entity_x_collision_only(self):
        entity = {"x": 5.0, "y": 5.0}
        world_map = [[0, 0], [0, 0]]

        def mock_collision(x, y, _):
            return x > 5.0 and y == 5.0

        with patch("utils.collision.is_collision", side_effect=mock_collision):
            result = entities.try_move_entity(entity, 0.0, 1.0, world_map)

            self.assertFalse(result)
            self.assertEqual(entity["x"], 5.0)
            self.assertEqual(entity["y"], 5.0)

    def test_cleanup_entities(self):
        entities.entities = [
            {"id": 1, "remove": True},
            {"id": 2, "remove": False},
            {"id": 3, "remove": True, "subtype": "boss", "state": "dead"},
            {"id": 4, "remove": False},
        ]
        entities.projectiles = [
            {"id": "p1", "remove": True},
            {"id": "p2", "remove": False},
        ]
        entities.enemies = [
            {"id": "e1", "remove": True},
            {"id": "e2", "remove": False},
            {"id": "e3", "remove": True, "subtype": "boss", "state": "dead"},
        ]
        entities.enemy_projectiles = [
            {"id": "ep1", "remove": True},
            {"id": "ep2", "remove": False},
        ]

        entities.cleanup_entities()

        self.assertEqual(len(entities.entities), 3)
        self.assertEqual(len(entities.projectiles), 1)
        self.assertEqual(len(entities.enemies), 2)
        self.assertEqual(len(entities.enemy_projectiles), 1)

        self.assertIn(
            {"id": 3, "remove": True, "subtype": "boss", "state": "dead"},
            entities.entities,
        )

    def test_clear_entities(self):
        entities.entities = [{"id": 1}, {"id": 2}]
        entities.projectiles = [{"id": "p1"}, {"id": "p2"}]
        entities.enemies = [{"id": "e1"}, {"id": "e2"}]
        entities.enemy_projectiles = [{"id": "ep1"}, {"id": "ep2"}]

        entities.clear_entities()

        self.assertEqual(len(entities.entities), 0)
        self.assertEqual(len(entities.projectiles), 0)
        self.assertEqual(len(entities.enemies), 0)
        self.assertEqual(len(entities.enemy_projectiles), 0)

    def test_get_enemy_display_text(self):
        enemy = {
            "ascii": ["ABC", "DEF"],
            "death_ascii": ["XXX", "YYY"],
            "state": "idle",
        }

        with patch("entities.distort_text", lambda text, dist: text + "!"):
            result = entities.get_enemy_display_text(enemy, 5.0)
            self.assertEqual(result, ["ABC!", "DEF!"])

        enemy["state"] = "dead"
        with patch("entities.distort_text", lambda text, dist: text + "?"):
            result = entities.get_enemy_display_text(enemy, 10.0)
            self.assertEqual(result, ["XXX?", "YYY?"])

    def test_award_xp_no_player_state(self):
        entities.award_xp(None, 100)

    def test_award_xp_no_level_up(self):
        player_state = {"exp": 0, "exp_to_next": 200}

        entities.award_xp(player_state, 100)

        self.assertEqual(player_state["exp"], 100)

    @patch("ui.add_message")
    def test_award_xp_with_level_up(self, mock_add_message):
        player_state = {
            "exp": 90,
            "exp_to_next": 100,
            "level": 1,
            "max_health": 100,
            "health": 50,
        }

        entities.award_xp(player_state, 20)

        self.assertEqual(player_state["level"], 2)
        self.assertEqual(player_state["exp"], 10)
        self.assertEqual(player_state["exp_to_next"], 150)
        self.assertEqual(player_state["max_health"], 120)
        self.assertEqual(player_state["health"], 120)
        mock_add_message.assert_called_once()
