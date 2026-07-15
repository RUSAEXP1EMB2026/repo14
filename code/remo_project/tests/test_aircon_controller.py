import unittest
from datetime import datetime, timedelta

from controllers import aircon_controller
from modules import nature_remo


class AirconControllerTest(unittest.TestCase):
    def setUp(self):
        aircon_controller._comfortable_since = None
        self.settings = {
            "wake_time": "07:30",
            "return_time": "19:00",
            "sleep_time": "23:00",
            "comfort_temp_min": 23,
            "comfort_temp_max": 27,
            "comfort_humidity_max": 60,
        }
        self.weather = {
            "weather": "Clear",
            "outside_temp": 22,
        }

    def test_starts_fan_when_comfortable_30_minutes_before_wake(self):
        action = aircon_controller.judge(
            self.settings,
            {"temperature": 25, "humidity": 50},
            self.weather,
            presence=True,
            now=datetime(2026, 7, 12, 7, 0),
        )

        self.assertEqual(action["value"], "wake_preheat")
        self.assertEqual(action["operation_mode"], "blow")
        self.assertEqual(action["air_volume"], "auto")
        self.assertIsNone(action["temperature"])

    def test_wake_preheat_window_does_not_continue_after_wake(self):
        action = aircon_controller.judge(
            self.settings,
            {"temperature": 29, "humidity": 50},
            self.weather,
            presence=True,
            now=datetime(2026, 7, 12, 7, 31),
        )

        self.assertEqual(action["value"], "cooling")

    def test_turns_off_after_comfort_is_continuous_for_10_minutes(self):
        started = datetime(2026, 7, 12, 12, 0)
        sensor_data = {"temperature": 25, "humidity": 50}
        settings = {
            "comfort_temp_min": 23,
            "comfort_temp_max": 27,
            "comfort_humidity_max": 60,
        }

        first = aircon_controller.judge(
            settings, sensor_data, self.weather, presence=True, now=started
        )
        before_ten_minutes = aircon_controller.judge(
            settings,
            sensor_data,
            self.weather,
            presence=True,
            now=started + timedelta(minutes=9, seconds=59),
        )
        after_ten_minutes = aircon_controller.judge(
            settings,
            sensor_data,
            self.weather,
            presence=True,
            now=started + timedelta(minutes=10),
        )

        self.assertIsNone(first)
        self.assertIsNone(before_ten_minutes)
        self.assertEqual(after_ten_minutes["value"], "off")

    def test_temperature_outside_range_resets_comfort_timer(self):
        started = datetime(2026, 7, 12, 12, 0)
        settings = {
            "comfort_temp_min": 23,
            "comfort_temp_max": 27,
            "comfort_humidity_max": 60,
        }
        aircon_controller.judge(
            settings,
            {"temperature": 25, "humidity": 50},
            self.weather,
            presence=True,
            now=started,
        )

        action = aircon_controller.judge(
            settings,
            {"temperature": 29, "humidity": 50},
            self.weather,
            presence=True,
            now=started + timedelta(minutes=5),
        )

        self.assertEqual(action["value"], "cooling")
        self.assertIsNone(aircon_controller._comfortable_since)

    def test_controls_temperature_even_when_presence_is_false(self):
        action = aircon_controller.judge(
            {
                "comfort_temp_min": 20,
                "comfort_temp_max": 24,
                "comfort_humidity_max": 60,
            },
            {"temperature": 25.9, "humidity": 75},
            {"weather": "Clouds", "outside_temp": 29.98},
            presence=False,
            now=datetime(2026, 7, 12, 21, 7),
        )

        self.assertEqual(action["value"], "humidity_cooling")
        self.assertEqual(action["operation_mode"], "cool")

    def test_fan_payload_omits_temperature(self):
        payload = nature_remo._aircon_payload(
            {
                "operation_mode": "blow",
                "temperature": None,
                "air_volume": "auto",
            }
        )

        self.assertEqual(
            payload,
            {"operation_mode": "blow", "air_volume": "auto"},
        )
