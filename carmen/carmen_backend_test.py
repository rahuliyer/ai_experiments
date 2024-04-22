import os
import unittest
import json

from carmen_backend import *

class TestGameStateFunctions(unittest.TestCase):
    GAME_STATES = {
        '8d354a22-4ee1-4eb5-a594-aa6a60a2d6c5': {
            'case_id': '8d354a22-4ee1-4eb5-a594-aa6a60a2d6c5',
            'suspect_name': 'Picasso Peculiar',
            'current_city': 'Chennai',
            'stolen_item': "The Louvre's Laughing Mona Lisa",
            'hops': [
                'Paris', 
                'Rome', 
                'Cairo', 
                'Tokyo', 
                'New York', 
                'Sydney'
            ],
            'next_hop': 3
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

        self.case_id, _ = next(iter(get_game_states().items()))

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
        new_game_states = self.GAME_STATES
        new_game_states[self.case_id]["next_hop"] = 77

        store_game_state(new_game_states[self.case_id])

        self.assertEquals(get_game_states(), new_game_states)

    def test_get_game_state(self):
        game_state = self.GAME_STATES[self.case_id]

        self.assertEquals(get_game_state(self.case_id), game_state)
        
if __name__ == "__main__":
    unittest.main()
