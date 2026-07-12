import unittest
from datetime import datetime, timedelta, timezone

from controllers import light_controller
from modules import nature_remo


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

    def test_turns_light_off_after_presence_is_lost(self):
        motion_time = datetime.now(timezone.utc) - timedelta(minutes=10)
        action = light_controller.judge(
            self.settings,
            {"motion_time": motion_time.isoformat()},
            self.weather,
            presence=False,
            now=datetime(2026, 7, 12, 12, 0),
        )

        self.assertEqual(action["value"], "off")

    def test_uses_plant_mode_after_30_minutes_without_presence(self):
        motion_time = datetime.now(timezone.utc) - timedelta(minutes=31)
        action = light_controller.judge(
            self.settings,
            {"motion_time": motion_time.isoformat()},
            self.weather,
            presence=False,
            now=datetime(2026, 7, 12, 12, 0),
        )

        self.assertEqual(action["value"], "plant_mode")

    def test_plant_mode_sends_full_light_then_cold_color_ten_times(self):
        sequence = nature_remo.LIGHT_BUTTON_SEQUENCES["plant_mode"]

        self.assertEqual(sequence[0], nature_remo.LIGHT_BUTTONS["full_light"])
        self.assertEqual(
            sequence[1:],
            [nature_remo.LIGHT_BUTTONS["daylight"]] * 10,
        )


if __name__ == "__main__":
    unittest.main()
