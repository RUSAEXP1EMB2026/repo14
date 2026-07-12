import unittest
from unittest.mock import patch

import main


class MainRunOnceTest(unittest.TestCase):
    def setUp(self):
        main._last_wake_light_key = None
        main._LAST_CONTROL_SIGNATURES.clear()

    @patch("main.audio_controller.play", return_value={"status": "ok"})
    @patch("main.audio_controller.judge_non_wake", return_value=None)
    @patch(
        "main.audio_controller.judge_wake",
        return_value={
            "value": "announce_wake",
            "text": "wake announcement",
            "wake_announcement_key": "2026-07-12:07:30",
        },
    )
    @patch("main.bgm_controller.stop", return_value={"status": "idle"})
    @patch("main.light_controller.judge", return_value={"value": "daylight"})
    @patch("main.nature_remo.control_light", side_effect=RuntimeError("Nature Remo light error"))
    @patch("main.aircon_controller.judge", return_value=None)
    @patch("main.presence_controller.judge", return_value=True)
    @patch("main.weather.get_weather", return_value={"description": "晴れ"})
    @patch("main.nature_remo.get_sensor_data", return_value={"temperature": 25, "humidity": 50})
    @patch("main.command_handler.process_line_commands")
    @patch("main.spreadsheet")
    def test_wake_announcement_runs_before_light_control_error(
        self,
        spreadsheet,
        process_line_commands,
        get_sensor_data,
        get_weather,
        presence_judge,
        aircon_judge,
        control_light,
        light_judge,
        bgm_stop,
        judge_wake,
        judge_non_wake,
        audio_play,
    ):
        spreadsheet.get_settings.return_value = {"wake_time": "07:30", "bgm_flag": "OFF"}

        main.run_once()

        audio_play.assert_called_once()
        light_log = [
            call
            for call in spreadsheet.save_control_log.call_args_list
            if call.args and call.args[0] == "light"
        ][0]
        self.assertEqual(light_log.args[2]["status"], "error")

    @patch("main._handle_wake_announcement")
    @patch("main._handle_wake_light")
    @patch("main.weather.get_weather", return_value={"description": "晴れ"})
    @patch("main.nature_remo.get_sensor_data", return_value={"temperature": 25, "humidity": 50})
    @patch("main.audio_controller.is_wake_announcement_due", return_value=True)
    @patch("main.audio_controller.get_wake_event_key", return_value="2026-07-12:07:30")
    @patch("main.spreadsheet")
    def test_wake_check_reads_sheet_and_runs_light_and_announcement(
        self,
        spreadsheet,
        get_wake_event_key,
        is_due,
        get_sensor_data,
        get_weather,
        handle_wake_light,
        handle_wake_announcement,
    ):
        settings = {"wake_time": "07:30"}
        spreadsheet.get_settings.return_value = settings

        main.check_wake_actions()

        spreadsheet.get_settings.assert_called_once_with()
        get_wake_event_key.assert_called_once_with(settings)
        handle_wake_light.assert_called_once_with("2026-07-12:07:30")
        is_due.assert_called_once_with(settings)
        handle_wake_announcement.assert_called_once_with(
            settings,
            get_sensor_data.return_value,
            get_weather.return_value,
        )

    @patch("main._execute_control", return_value={"status": "ok"})
    def test_wake_light_turns_on_only_once_per_wake_event(self, execute_control):
        wake_key = "2026-07-12:07:30"

        main._handle_wake_light(wake_key)
        main._handle_wake_light(wake_key)

        execute_control.assert_called_once()
        target, action, control = execute_control.call_args.args
        self.assertEqual(target, "wake_light")
        self.assertEqual(action["value"], "full_light")
        self.assertIs(control, main.nature_remo.control_light)


if __name__ == "__main__":
    unittest.main()
