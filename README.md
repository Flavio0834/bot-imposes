# bot-imposes

Bot to monitor the ISDAT admissions page for content changes.

This bot monitors the ISDAT music admissions page and sends Telegram notifications when any content changes are detected. Perfect for monitoring admission results and important updates.

## Features

- 🔔 **Detects any content changes** on the admissions page
- 📱 Sends Telegram notifications
- 🔄 Designed to run as a cron job
- 📝 Detailed logging
- 💾 Persistent state storage for change detection
- ⚙️ Configurable via environment variables

## Installation

1. Clone this repository:
```bash
git clone https://github.com/Flavio0834/bot-imposes.git
cd bot-imposes
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your Telegram credentials:
   - Create a Telegram bot by talking to [@BotFather](https://t.me/botfather)
   - Get your chat ID by sending a message to your bot, then visit:
     ```
     https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
     ```
   - Copy `.env.example` to `.env` and fill in your credentials:
     ```bash
     cp .env.example .env
     # Edit .env with your actual credentials
     ```

## Usage

### Manual Execution

Run the bot manually:
```bash
python bot.py
```

### Cron Job Setup

To run the bot automatically every 10 minutes, add this to your crontab:

```bash
# Edit your crontab
crontab -e

# Add this line (adjust the path to your installation):
*/10 * * * * cd /path/to/bot-imposes && /usr/bin/python3 bot.py >> /var/log/bot-imposes.log 2>&1
```

Example schedules:
- Every 10 minutes: `*/10 * * * *`
- Every 30 minutes: `*/30 * * * *`
- Every day at 8 AM: `0 8 * * *`

## Configuration

The bot uses environment variables for configuration. Create a `.env` file with:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

## Monitored URL

The bot monitors:
- Main page: https://www.isdat.fr/admission-vie-etudiante/admission-formation-initiale/musique/
  - **Monitors for any content changes using hash comparison**

## How It Works

### Page Content Monitoring
The bot saves a hash of the normalized page content on first run. On subsequent runs, it compares the current content hash with the saved hash. If they differ, it sends a notification and updates the saved hash.

The page state is stored in `page_state.json` (automatically created on first run).

When a change is detected, you'll receive a Telegram notification like:
```
🔔 ISDAT Page Update Detected! 🔔

The content of the page has changed:
https://www.isdat.fr/admission-vie-etudiante/admission-formation-initiale/musique/

Please check the page for updates!
```

## Logging

The bot logs all activities to stdout. To save logs to a file when running as a cron job, redirect the output:

```bash
python bot.py >> bot.log 2>&1
```

## License

MIT
