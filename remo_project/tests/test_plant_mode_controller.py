import unittest
from datetime import datetime, timedelta, timezone

from controllers import plant_mode_controller, presence_controller
from modules import nature_remo


class PlantModeControllerTest(unittest.TestCase):
    def test_uses_full_light_after_30_minutes_without_motion(self):
        motion_time = datetime.now(timezone.utc) - timedelta(minutes=31)
        sensor_data = {
            "motion": 1,
            "motion_time": motion_time.isoformat(),
        }
        settings = {"absence_threshold": 30}

        presence = presence_controller.judge(sensor_data, settings)
        action = plant_mode_controller.judge(
            settings,
            sensor_data,
            {"weather": "Clear"},
            presence,
        )

        self.assertFalse(presence)
        self.assertEqual(action["value"], "plant_mode")
        self.assertEqual(nature_remo.LIGHT_BUTTONS["plant_mode"], "on-100")


if __name__ == "__main__":
    unittest.main()
