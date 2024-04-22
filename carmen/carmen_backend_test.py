import os
import unittest
import json

from carmen_backend import *

class TestGameStateFunctions(unittest.TestCase):
    GAME_STATES = {
        "8d354a22-4ee1-4eb5-a594-aa6a60a2d6c5": {
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
    }

    @classmethod
    def remove_game_state_file(cls):
        if os.path.exists(GAME_STATE_FILE):
            os.remove(GAME_STATE_FILE)

    @classmethod
    def setUpClass(cls):
        cls.remove_game_state_file()

        cls.maxDiff = None

    @classmethod
    def tearDownClass(cls):
        cls.remove_game_state_file()


    def setUp(self):
        with open(GAME_STATE_FILE, "w") as f:
            json.dump(self.GAME_STATES, f)

        self.game_states = self.GAME_STATES
        self.case_id, _ = next(iter(self.game_states.items()))

    def tearDown(self):
        self.remove_game_state_file()


    def test_missing_file_returns_empty_dict(self):
        os.remove(GAME_STATE_FILE)
        ret = get_game_states()

        self.assertEqual(ret, {})

    def test_state_is_loaded_correctly(self):
        ret = get_game_states()

        self.assertEqual(ret, self.GAME_STATES)

    def test_state_is_stored_correctly(self):

        self.game_states[self.case_id]["next_hop"] = 77

        store_game_state(self.game_states[self.case_id])

        self.assertEqual(get_game_states(), self.game_states)

    def test_get_game_state(self):
        game_state = self.game_states[self.case_id]

        self.assertEqual(get_game_state(self.case_id), game_state)

    def test_fetch_game_state_tool(self):
        self.assertEqual(
            fetch_game_state.invoke(
                {
                    "case_id": self.case_id
                }
            ),
            json.dumps(self.game_states[self.case_id])
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
                "value": 77
            },
        )

        new_game_state = get_game_state(self.case_id)
        self.assertEqual(new_game_state["next_hop"], 77)

if __name__ == "__main__":
    unittest.main()
