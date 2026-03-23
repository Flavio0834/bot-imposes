#!/usr/bin/env python3
"""
Focused tests for HEARMonitorBot monitoring target and notification payload.
"""

import unittest
from unittest.mock import patch

from bot import HEARMonitorBot


class HEARMonitorBotTests(unittest.TestCase):
    def test_monitors_new_results_page(self):
        bot = HEARMonitorBot("token", "chat")
        self.assertEqual(
            bot.main_url,
            "https://www.hear.fr/admissions/resultats-admissions/",
        )

    @patch.object(HEARMonitorBot, "_save_page_state")
    @patch.object(HEARMonitorBot, "_load_page_state", return_value={"main_page_hash": "old"})
    @patch.object(HEARMonitorBot, "_get_page_content_hash", return_value="new")
    def test_change_message_contains_results_link(self, *_mocks):
        bot = HEARMonitorBot("token", "chat")

        changed, message = bot.check_page_content_change()

        self.assertTrue(changed)
        self.assertIn("https://www.hear.fr/admissions/resultats-admissions/", message)


if __name__ == "__main__":
    unittest.main()
