import unittest
from datetime import datetime

from controllers import light_controller


class LightControllerTest(unittest.TestCase):
    def setUp(self):
        self.settings = {
            "sleep_time": "23:00",
            "wake_time": "07:00",
            "absence_threshold": 30,
        }
        self.weather = {"weather": "Clear"}

    def test_keeps_light_off_between_sleep_and_wake(self):
        action = light_controller.judge(
            self.settings,
            {},
            self.weather,
            presence=True,
            now=datetime(2026, 7, 12, 1, 0),
        )

        self.assertEqual(action["value"], "off")

    def test_turns_full_light_on_when_presence_is_detected(self):
        action = light_controller.judge(
            self.settings,
            {},
            self.weather,
            presence=True,
            now=datetime(2026, 7, 12, 12, 0),
        )

        self.assertEqual(action["value"], "full_light")

    def test_ignores_missing_presence_outside_sleep_period(self):
        action = light_controller.judge(
            self.settings,
            {"motion": 0, "motion_time": None},
            self.weather,
            presence=False,
            now=datetime(2026, 7, 12, 12, 0),
        )

        self.assertEqual(action["value"], "full_light")


if __name__ == "__main__":
    unittest.main()
