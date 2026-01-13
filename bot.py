#!/usr/bin/env python3
"""
Bot to monitor HEAR website for changes in imposed pieces information.

This bot checks:
1. If the text "Pièces imposées 2026 - Prochainement disponible" is no longer present
   on https://www.hear.fr/admissions/musique/candidats-en-licencednspmde-2-2/
2. If any of the URLs (pieces-imposees, pieces-imposees-0, pieces-imposees-1,
   pieces-imposees-2, pieces-imposees-3) no longer return "error 404"

When either condition is met, it sends a Telegram notification.
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HEARMonitorBot:
    """Monitor HEAR website for changes and send Telegram notifications."""

    def __init__(self, telegram_bot_token, telegram_chat_id):
        """
        Initialize the bot.

        Args:
            telegram_bot_token: Telegram bot API token
            telegram_chat_id: Telegram chat ID to send notifications to
        """
        self.telegram_bot_token = telegram_bot_token
        self.telegram_chat_id = telegram_chat_id
        self.main_url = "https://www.hear.fr/admissions/musique/candidats-en-licencednspmde-2-2/"
        self.base_pieces_url = "https://www.hear.fr/admissions/musique/pieces-imposees"
        self.target_text = "Pièces imposées 2026 - Prochainement disponible"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def send_telegram_notification(self, message):
        """
        Send a notification via Telegram.

        Args:
            message: Message text to send

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            logger.info(f"Telegram notification sent successfully")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False

    def check_main_page(self):
        """
        Check if the target text is still present on the main page.

        Returns:
            tuple: (bool, str) - (text_still_present, message)
        """
        try:
            logger.info(f"Checking main page: {self.main_url}")
            response = self.session.get(self.main_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text()
            
            text_present = self.target_text in page_text
            
            if not text_present:
                message = (
                    f"🚨 <b>HEAR Update Alert!</b> 🚨\n\n"
                    f"The text '<i>{self.target_text}</i>' is NO LONGER present on:\n"
                    f"{self.main_url}\n\n"
                    f"The imposed pieces for 2026 may now be available!"
                )
                return False, message
            else:
                logger.info(f"Target text still present on main page")
                return True, None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking main page: {e}")
            return None, None

    def check_pieces_urls(self):
        """
        Check if any of the pieces-imposees URLs no longer return 404.

        Returns:
            list: List of tuples (url, status) for URLs that are no longer 404
        """
        available_urls = []
        
        # Check base URL without suffix
        urls_to_check = [self.base_pieces_url]
        
        # Check URLs with suffixes -0, -1, -2, -3
        for i in range(4):
            urls_to_check.append(f"{self.base_pieces_url}-{i}")
        
        for url in urls_to_check:
            try:
                logger.info(f"Checking URL: {url}")
                response = self.session.get(url, timeout=15)
                
                # Check if it's NOT a 404
                if response.status_code != 404:
                    # Also check if the page content doesn't contain "error 404" text
                    soup = BeautifulSoup(response.content, 'html.parser')
                    page_text = soup.get_text().lower()
                    
                    if "error 404" not in page_text and "erreur 404" not in page_text:
                        available_urls.append((url, response.status_code))
                        logger.info(f"URL available: {url} (status: {response.status_code})")
                    else:
                        logger.info(f"URL {url} contains 404 error text")
                else:
                    logger.info(f"URL {url} returns 404")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Error checking URL {url}: {e}")
        
        if available_urls:
            message = (
                f"🚨 <b>HEAR Update Alert!</b> 🚨\n\n"
                f"The following imposed pieces pages are now AVAILABLE:\n\n"
            )
            for url, status in available_urls:
                message += f"• {url}\n  (Status: {status})\n"
            message += "\nThe imposed pieces information may now be published!"
            
            return available_urls, message
        
        return [], None

    def run(self):
        """
        Run the monitoring check.

        Returns:
            bool: True if any notification was sent
        """
        notification_sent = False
        
        # Check main page
        text_present, main_message = self.check_main_page()
        if text_present is False and main_message:
            self.send_telegram_notification(main_message)
            notification_sent = True
        
        # Check pieces URLs
        available_urls, pieces_message = self.check_pieces_urls()
        if available_urls and pieces_message:
            self.send_telegram_notification(pieces_message)
            notification_sent = True
        
        if not notification_sent:
            logger.info("No changes detected - no notifications sent")
        
        return notification_sent


def main():
    """Main entry point for the bot."""
    # Load environment variables
    load_dotenv()
    
    # Get credentials from environment variables
    telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    # Validate credentials
    if not telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
        sys.exit(1)
    
    if not telegram_chat_id:
        logger.error("TELEGRAM_CHAT_ID environment variable not set")
        sys.exit(1)
    
    # Create and run bot
    bot = HEARMonitorBot(telegram_bot_token, telegram_chat_id)
    
    try:
        bot.run()
        logger.info("Bot execution completed successfully")
    except Exception as e:
        logger.error(f"Bot execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
