import unittest
from unittest.mock import patch

from remo_line_bot import app as line_bot_app


class LineBotAppTest(unittest.TestCase):
    @patch.object(line_bot_app.app, "run")
    def test_run_server_disables_debugger_and_reloader(self, app_run):
        line_bot_app.run_server()

        app_run.assert_called_once_with(
            port=line_bot_app.PORT,
            debug=False,
            use_reloader=False,
        )


if __name__ == "__main__":
    unittest.main()
