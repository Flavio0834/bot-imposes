#!/usr/bin/env python3
"""
Test script to verify the bot's web scraping functionality without sending Telegram messages.
"""

from bot import HEARMonitorBot
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_bot():
    """Test the bot's web scraping functionality."""
    print("=" * 60)
    print("Testing HEAR Monitor Bot (Dry Run - No Telegram Messages)")
    print("=" * 60)
    
    # Create bot with dummy credentials (won't send messages)
    bot = HEARMonitorBot('dummy_token', 'dummy_chat_id')
    
    print("\n1. Testing main page check...")
    text_present, message = bot.check_main_page()
    if text_present is not None:
        if text_present:
            print("   ✓ Target text is still present on main page")
        else:
            print("   ✓ Target text is NOT present on main page!")
            print(f"   Message that would be sent:\n{message}")
    else:
        print("   ✗ Error checking main page")
    
    print("\n2. Testing pieces URLs check...")
    available_urls, message = bot.check_pieces_urls()
    if available_urls:
        print(f"   ✓ Found {len(available_urls)} available URL(s)!")
        for url, status in available_urls:
            print(f"     - {url} (Status: {status})")
        print(f"   Message that would be sent:\n{message}")
    else:
        print("   ✓ All pieces URLs still return 404 or contain error text")
    
    print("\n" + "=" * 60)
    print("Test completed successfully")
    print("=" * 60)

if __name__ == "__main__":
    test_bot()
