import unittest
from datetime import datetime

from controllers import audio_controller


class AudioControllerTest(unittest.TestCase):
    def setUp(self):
        audio_controller._last_wake_announcement_key = None

    def test_builds_wake_announcement_at_configured_time(self):
        action = audio_controller.judge(
            {"wake_time": "07:30"},
            {"temperature": 24.5, "humidity": 51},
            {"description": "晴れ", "rain_probability": 0},
            None,
            now=datetime(2026, 7, 12, 7, 30),
        )

        self.assertEqual(action["value"], "announce_wake")
        self.assertEqual(
            action["text"],
            "おはようございます、現在は07時30分天気は晴れ、室温24.5度、湿度51パーです",
        )

    def test_does_not_announce_before_wake_time(self):
        action = audio_controller.judge(
            {"wake_time": "07:30"},
            {"temperature": 24.5, "humidity": 51},
            {"description": "晴れ", "rain_probability": 0},
            None,
            now=datetime(2026, 7, 12, 7, 29),
        )

        self.assertIsNone(action)

    def test_does_not_repeat_completed_wake_announcement(self):
        now = datetime(2026, 7, 12, 7, 30)
        settings = {"wake_time": "07:30"}
        sensor_data = {"temperature": 24.5, "humidity": 51}
        weather_data = {"description": "晴れ", "rain_probability": 0}
        action = audio_controller.judge(settings, sensor_data, weather_data, None, now=now)

        audio_controller._mark_wake_announcement(action)

        self.assertIsNone(
            audio_controller.judge(settings, sensor_data, weather_data, None, now=now)
        )


if __name__ == "__main__":
    unittest.main()
