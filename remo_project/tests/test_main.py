import unittest
from unittest.mock import Mock, patch

import main


class MainTest(unittest.TestCase):
    @patch("main.threading.Thread")
    @patch("remo_line_bot.app.run_server")
    def test_start_line_bot_runs_server_in_daemon_thread(self, run_server, thread_class):
        thread = Mock()
        thread_class.return_value = thread

        result = main.start_line_bot()

        thread_class.assert_called_once_with(
            target=run_server,
            name="line-bot-server",
            daemon=True,
        )
        thread.start.assert_called_once_with()
        self.assertIs(result, thread)


if __name__ == "__main__":
    unittest.main()
