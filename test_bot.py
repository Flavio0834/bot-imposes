#!/usr/bin/env python3
"""
Test script to verify the bot's page monitoring functionality without sending Telegram messages.
"""

from bot import HEARMonitorBot
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_bot():
    """Test the bot's page monitoring functionality."""
    print("=" * 60)
    print("Testing HEAR Monitor Bot (Dry Run - No Telegram Messages)")
    print("=" * 60)
    
    # Create bot with dummy credentials (won't send messages)
    bot = HEARMonitorBot('dummy_token', 'dummy_chat_id', state_file='test_page_state.json')
    
    print("\nTesting page content change detection...")
    content_changed, message = bot.check_page_content_change()
    if content_changed is not None:
        if content_changed:
            print("   ✓ Page content has changed!")
            print(f"   Message that would be sent:\n{message}")
        else:
            print("   ✓ Page content unchanged (or first run - state initialized)")
    else:
        print("   ✗ Error checking page content")
    
    print("\n" + "=" * 60)
    print("Test completed successfully")
    print("=" * 60)

if __name__ == "__main__":
    test_bot()
