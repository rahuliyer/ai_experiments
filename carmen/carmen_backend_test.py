import os
import unittest
import json

from carmen_backend import *

class CarmenBackendTest(unittest.TestCase):
    GAME_STATE = {
        "case_id": "8d354a22-4ee1-4eb5-a594-aa6a60a2d6c5",
        "suspect_name": "Picasso Peculiar",
        "current_city": "Chennai",
        "stolen_item": "The Louvre's Laughing Mona Lisa",
        "hops": [
            "Paris",
            "Rome",
            "Cairo",
            "Tokyo",
            "New York",
            "Sydney"
        ],
        "next_hop": 3
    }

    @classmethod
    def setUpClass(cls):
        os.environ["GAME_ENVIRONMENT"] = "TEST"

        clear_game_states()
        cls.maxDiff = None

    @classmethod
    def tearDownClass(cls):
        clear_game_states()


    def setUp(self):
        store_game_state(self.GAME_STATE)
        self.game_state = self.GAME_STATE.copy()
        self.case_id = self.game_state["case_id"]

    def tearDown(self):
        clear_game_states()
        self.game_state = None


    def test_empty_state_returns_empty_dict(self):
        clear_game_states()
        ret = get_game_states()

        self.assertEqual(ret, {})

    def test_state_is_loaded_correctly(self):
        ret = get_game_state(self.case_id)

        self.assertEqual(ret, self.GAME_STATE)

    def test_state_is_stored_correctly(self):
        self.game_state["next_hop"] = 32

        store_game_state(self.game_state)

        self.assertEqual(get_game_state(self.case_id), self.game_state)

    def test_get_game_state(self):
        self.assertEqual(get_game_state(self.case_id), self.game_state)

    def test_fetch_game_state_tool(self):
        self.assertEqual(
            fetch_game_state.invoke(
                {
                    "case_id": self.case_id
                }
            ),
            json.dumps(self.game_state)
        )

    def test_set_current_city_tool(self):
        set_current_city.invoke(
            {
                "case_id": self.case_id,
                "current_city": "Bangalore"
            },
        )

        new_game_state = get_game_state(self.case_id)
        self.assertEqual(new_game_state["current_city"], "Bangalore")

    def test_update_game_state_tool(self):
        update_game_state.invoke(
            {
                "case_id": self.case_id,
                "key": "next_hop",
                "value": 46
            },
        )

        new_game_state = get_game_state(self.case_id)
        self.assertEqual(new_game_state["next_hop"], 46)

    def test_generate_new_game(self):
        game_state = json.loads(generate_new_game())

        self.assertIn("case_id", game_state)
        self.assertIn("suspect_name", game_state)
        self.assertIn("hops", game_state)
        self.assertEqual(len(game_state["hops"]), 6)
        self.assertIn("next_hop", game_state)
        self.assertEqual(game_state["next_hop"], 1)

    def test_generate_destinations(self):
        dests_json = generate_destinations.invoke(
            {
                "previous_city": "London",
                "next_city": "Mumbai",
                "current_city": "Tokyo",
                "exclude_list": "Paris,Lima"
            }
        )

        dests = json.loads(dests_json)["destinations"]

        self.assertEqual(len(dests), 4)
        self.assertIn("London", dests)
        self.assertIn("Mumbai", dests)
        self.assertNotIn("Tokyo", dests)
        self.assertNotIn("Paris", dests)
        self.assertNotIn("Lima", dests)

    def test_generate_regular_clues(self):
        clues = json.loads(generate_regular_clues.invoke(
            {
                "city": "Bangalore"
            }
        ))["clues"]

        self.assertEqual(len(clues), 3)
        self.assertIn("location", clues[0])
        self.assertIn("clue", clues[0])
        self.assertIn("location", clues[1])
        self.assertIn("clue", clues[1])
        self.assertIn("location", clues[2])
        self.assertIn("clue", clues[2])

    def test_generate_mistaken_clues(self):
        clues = json.loads(generate_mistaken_clues.invoke({}))["clues"]

        self.assertEqual(len(clues), 3)
        self.assertIn("location", clues[0])
        self.assertIn("clue", clues[0])
        self.assertEqual(clues[0]["clue"], "No one with the suspect's description was seen here")
        self.assertIn("location", clues[1])
        self.assertIn("clue", clues[1])
        self.assertEqual(clues[1]["clue"], "No one with the suspect's description was seen here")
        self.assertIn("location", clues[2])
        self.assertIn("clue", clues[2])
        self.assertEqual(clues[2]["clue"], "No one with the suspect's description was seen here")

    def test_generate_arrest_clues(self):
        suspect_name = "Bobo the Clown"
        clues = json.loads(generate_arrest_clues.invoke(
            {
                "suspect_name": suspect_name
            }
        ))["clues"]

        self.assertEqual(len(clues), 3)
        self.assertIn("location", clues[0])
        self.assertIn("clue", clues[0])
        self.assertIn("location", clues[1])
        self.assertIn("clue", clues[1])
        self.assertIn("location", clues[2])
        self.assertIn("clue", clues[2])

        watch_out_count = 0
        arrest_count = 0
        other_count = 0
        for i in range(0,3):
            if clues[i]["clue"] == "Watch your step. You are getting close":
                watch_out_count += 1
            elif clues[i]["clue"] == f"Congratulations! You have arrested the suspect, {suspect_name}":
                arrest_count += 1
            else:
                other_count += 1

        self.assertEqual(watch_out_count, 2)
        self.assertEqual(arrest_count, 1)
        self.assertEqual(other_count, 0)

    def test_new_game(self):
        res = new_game()

        game_states = get_game_states()

        self.assertIn(res["case_id"], game_states)

        self.assertIn("case_id", res)
        self.assertIn("suspect_name", res)

    def test_get_destinations(self):
        res = get_destinations(self.case_id)
        dests = res["destinations"]

        self.assertEqual(res["city"], "Chennai")
        self.assertIn("Cairo", dests)
        self.assertIn("Tokyo", dests)
        self.assertNotIn("Sydney", dests)
        self.assertNotIn("Paris", dests)
        self.assertNotIn("Rome", dests)
        self.assertNotIn("New York", dests)

    def test_get_destinations_last_city(self):
        update_game_state.invoke(
            {
                "case_id": self.case_id,
                "key": "next_hop",
                "value": MAX_HOPS + 1
            },
        )

        res = get_destinations(self.case_id)
        dests = res["destinations"]

        self.assertEqual(res["city"], "Chennai")
        self.assertEqual(len(dests), 0)

    def test_get_clues_wrong_city(self):
        clues = get_clues(self.case_id)["clues"]

        self.assertEqual(len(clues), 3)
        self.assertEqual(clues[0]["clue"], "No one with the suspect's description was seen here")

    def test_get_clues_right_city(self):
        set_current_city.invoke(
            {
                "case_id": self.case_id,
                "current_city": "Cairo"
            },
        )

        clues = get_clues(self.case_id)["clues"]

        suspect_name = self.game_state["suspect_name"]
        self.assertEqual(len(clues), 3)
        self.assertNotEqual(clues[0]["clue"], "No one with the suspect's description was seen here")
        self.assertNotEqual(clues[0]["clue"], "Watch your step. You are getting close")
        self.assertNotEqual(clues[0]["clue"], f"Congratulations! You have arrested the suspect, {suspect_name}")

    def test_get_clues_final_city(self):
        set_current_city.invoke(
            {
                "case_id": self.case_id,
                "current_city": "Sydney"
            },
        )

        update_game_state.invoke(
            {
                "case_id": self.case_id,
                "key": "next_hop",
                "value": MAX_HOPS + 1
            },
        )

        clues = get_clues(self.case_id)["clues"]

        suspect_name = self.game_state["suspect_name"]
        self.assertEqual(len(clues), 3)
        self.assertIn(
            clues[0]["clue"],
            [
                "Watch your step. You are getting close",
                f"Congratulations! You have arrested the suspect, {suspect_name}"
            ]
        )

    def test_travel_wrong_city(self):
        res = travel(self.case_id, "Bangalore")

        self.assertEqual(res["current_city"], "Bangalore")

        gs = get_game_state(self.case_id)

        self.assertEqual(gs["current_city"], "Bangalore")

        self.assertEqual(
            gs["next_hop"],
            self.game_state["next_hop"])

    def test_travel_back_to_correct_city(self):
        res = travel(self.case_id, "Cairo")

        self.assertEqual(res["current_city"], "Cairo")

        gs = get_game_state(self.case_id)

        self.assertEqual(gs["current_city"], "Cairo")

        self.assertEqual(
            gs["next_hop"],
            self.game_state["next_hop"])

    def test_travel_to_correct_next_city(self):
        set_current_city.invoke(
            {
                "case_id": self.case_id,
                "current_city": "Cairo"
            },
        )

        res = travel(self.case_id, "Tokyo")

        self.assertEqual(res["current_city"], "Tokyo")

        gs = get_game_state(self.case_id)

        self.assertEqual(gs["current_city"], "Tokyo")

        self.assertEqual(
            gs["next_hop"],
            self.game_state["next_hop"] + 1)

    def test_travel_to_future_city(self):
        res = travel(self.case_id, "New York")

        self.assertEqual(res["error"], "You cannot travel to that city")

        gs = get_game_state(self.case_id)

        self.assertEqual(gs["current_city"], "Chennai")

        self.assertEqual(
            gs["next_hop"],
            self.game_state["next_hop"])

if __name__ == "__main__":
    unittest.main()
