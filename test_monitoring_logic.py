#!/usr/bin/env python3
"""
Focused tests for ISDATMonitorBot monitoring target and notification payload.
"""

import unittest
from unittest.mock import patch

from bot import ISDATMonitorBot


class ISDATMonitorBotTests(unittest.TestCase):
    def test_monitors_new_results_page(self):
        bot = ISDATMonitorBot("token", "chat")
        self.assertEqual(
            bot.main_url,
            "https://www.isdat.fr/admission-vie-etudiante/admission-formation-initiale/musique/",
        )

    @patch.object(ISDATMonitorBot, "_save_page_state")
    @patch.object(ISDATMonitorBot, "_load_page_state", return_value={"main_page_hash": "old"})
    @patch.object(ISDATMonitorBot, "_get_page_content_hash", return_value="new")
    def test_change_message_contains_results_link(self, *_mocks):
        bot = ISDATMonitorBot("token", "chat")

        changed, message = bot.check_page_content_change()

        self.assertTrue(changed)
        self.assertIn("https://www.isdat.fr/admission-vie-etudiante/admission-formation-initiale/musique/", message)


if __name__ == "__main__":
    unittest.main()
