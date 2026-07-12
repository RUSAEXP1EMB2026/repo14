import unittest
import sys
from datetime import datetime
from unittest.mock import Mock, patch

from controllers import audio_controller


class AudioControllerTest(unittest.TestCase):
    def setUp(self):
        audio_controller._last_wake_announcement_key = None

    def test_builds_wake_announcement_at_configured_time(self):
        action = audio_controller.judge_wake(
            {"wake_time": "07:30"},
            {"temperature": 24.5, "humidity": 51},
            {"description": "晴れ", "rain_probability": 0},
            now=datetime(2026, 7, 12, 7, 30),
        )

        self.assertEqual(action["value"], "announce_wake")
        self.assertEqual(
            action["text"],
            "おはようございます、現在は07時30分天気は晴れ、室温24.5度、湿度51パーです",
        )

    def test_does_not_announce_before_wake_time(self):
        action = audio_controller.judge_wake(
            {"wake_time": "07:30"},
            {"temperature": 24.5, "humidity": 51},
            {"description": "晴れ", "rain_probability": 0},
            now=datetime(2026, 7, 12, 7, 29),
        )

        self.assertIsNone(action)

    def test_does_not_repeat_completed_wake_announcement(self):
        now = datetime(2026, 7, 12, 7, 30)
        settings = {"wake_time": "07:30"}
        sensor_data = {"temperature": 24.5, "humidity": 51}
        weather_data = {"description": "晴れ", "rain_probability": 0}
        action = audio_controller.judge_wake(settings, sensor_data, weather_data, now=now)

        audio_controller._mark_wake_announcement(action)

        self.assertIsNone(
            audio_controller.judge_wake(settings, sensor_data, weather_data, now=now)
        )

    def test_unloads_previous_audio_before_saving_unique_announcement_file(self):
        events = []
        music = Mock()
        music.get_busy.side_effect = [True, False]
        music.stop.side_effect = lambda: events.append("stop")
        music.unload.side_effect = lambda: events.append("unload")
        music.load.side_effect = lambda path: events.append(("load", path))
        music.play.side_effect = lambda: events.append("play")
        mixer = Mock()
        mixer.music = music
        fake_pygame = Mock(mixer=mixer)

        tts = Mock()
        tts.save.side_effect = lambda path: events.append(("save", path))
        fake_gtts = Mock()
        fake_gtts.gTTS.return_value = tts

        with (
            patch.object(audio_controller, "AUDIO_ENABLED", True),
            patch.dict(sys.modules, {"pygame": fake_pygame, "gtts": fake_gtts}),
        ):
            result = audio_controller.play({"value": "announce_wake", "text": "test"})

        save_event = next(event for event in events if isinstance(event, tuple) and event[0] == "save")
        load_event = next(event for event in events if isinstance(event, tuple) and event[0] == "load")
        self.assertEqual(result["status"], "ok")
        self.assertLess(events.index("unload"), events.index(save_event))
        self.assertEqual(save_event[1], load_event[1])
        self.assertNotEqual(save_event[1], audio_controller.ANNOUNCE_FILE)


if __name__ == "__main__":
    unittest.main()
