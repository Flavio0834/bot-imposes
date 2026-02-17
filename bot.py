#!/usr/bin/env python3
"""
Bot to monitor HEAR website for changes in imposed pieces information.

This bot checks:
1. If the page content has changed (using hash comparison)
2. If the text "Pièces imposées 2026 - Prochainement disponible" is no longer present
   on https://www.hear.fr/admissions/musique/candidats-en-licencednspmde-2-2/
3. If any of the URLs (pieces-imposees, pieces-imposees-0, pieces-imposees-1,
   pieces-imposees-2, pieces-imposees-3) no longer return "error 404"

When any condition is met, it sends a Telegram notification.
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import logging
import hashlib
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HEARMonitorBot:
    """Monitor HEAR website for changes and send Telegram notifications."""
    
    # Configuration constants
    REQUEST_TIMEOUT = 15  # seconds
    TELEGRAM_TIMEOUT = 10  # seconds

    def __init__(self, telegram_bot_token, telegram_chat_id, state_file='page_state.json'):
        """
        Initialize the bot.

        Args:
            telegram_bot_token: Telegram bot API token
            telegram_chat_id: Telegram chat ID to send notifications to
            state_file: Path to file storing page state (default: page_state.json)
        """
        self.telegram_bot_token = telegram_bot_token
        self.telegram_chat_id = telegram_chat_id
        self.main_url = "https://www.hear.fr/admissions/musique/candidats-en-licencednspmde-2-2/"
        self.base_pieces_url = "https://www.hear.fr/admissions/musique/pieces-imposees"
        self.target_text = "Pièces imposées 2026 - Prochainement disponible"
        self.state_file = Path(state_file)
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
            response = requests.post(url, data=data, timeout=self.TELEGRAM_TIMEOUT)
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
            response = self.session.get(self.main_url, timeout=self.REQUEST_TIMEOUT)
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
                response = self.session.get(url, timeout=self.REQUEST_TIMEOUT)
                
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

    def _get_page_content_hash(self, url):
        """
        Get normalized content hash of a webpage.
        
        Args:
            url: URL to fetch and hash
            
        Returns:
            str: SHA256 hash of normalized page content, or None on error
        """
        try:
            response = self.session.get(url, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            # Parse HTML and get text content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text and normalize whitespace
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Create hash
            return hashlib.sha256(text.encode('utf-8')).hexdigest()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching page for hash: {e}")
            return None

    def _load_page_state(self):
        """
        Load saved page state from file.
        
        Returns:
            dict: Page state data or empty dict if file doesn't exist
        """
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading page state: {e}")
                return {}
        return {}

    def _save_page_state(self, state):
        """
        Save page state to file.
        
        Args:
            state: Dictionary containing page state data
        """
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            logger.info(f"Page state saved to {self.state_file}")
        except IOError as e:
            logger.error(f"Error saving page state: {e}")

    def check_page_content_change(self):
        """
        Check if the main page content has changed since last check.
        
        Returns:
            tuple: (bool, str) - (has_changed, message)
        """
        logger.info(f"Checking for page content changes: {self.main_url}")
        
        # Get current page hash
        current_hash = self._get_page_content_hash(self.main_url)
        if current_hash is None:
            logger.error("Failed to get current page hash")
            return None, None
        
        # Load previous state
        state = self._load_page_state()
        previous_hash = state.get('main_page_hash')
        
        # If no previous state, save current and don't notify
        if previous_hash is None:
            logger.info("No previous page state found - initializing")
            state['main_page_hash'] = current_hash
            self._save_page_state(state)
            return False, None
        
        # Check if content has changed
        if current_hash != previous_hash:
            logger.info("Page content has changed!")
            message = (
                f"🔔 <b>HEAR Page Update Detected!</b> 🔔\n\n"
                f"The content of the page has changed:\n"
                f"{self.main_url}\n\n"
                f"Please check the page for updates!"
            )
            
            # Update saved state
            state['main_page_hash'] = current_hash
            self._save_page_state(state)
            
            return True, message
        else:
            logger.info("Page content unchanged")
            return False, None

    def run(self):
        """
        Run the monitoring check.

        Returns:
            bool: True if any notification was sent
        """
        notification_sent = False
        
        # Check for page content changes
        content_changed, content_message = self.check_page_content_change()
        if content_changed and content_message:
            self.send_telegram_notification(content_message)
            notification_sent = True
        
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
