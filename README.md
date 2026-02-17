# bot-imposes

Little bot to check when program is published by superior music school (HEAR).

This bot monitors the HEAR (Haute école des arts du Rhin) website for updates about imposed pieces for 2026. It sends Telegram notifications when:

1. **The page content changes** - Detects any modification to the main admissions page content
2. The text "Pièces imposées 2026 - Prochainement disponible" is no longer present on the admissions page
3. The imposed pieces pages (pieces-imposees variants) are no longer returning 404 errors

## Features

- 🔍 Monitors multiple URLs for changes
- 🔔 **Detects any content changes on the main page**
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

To run the bot automatically every hour, add this to your crontab:

```bash
# Edit your crontab
crontab -e

# Add this line (adjust the path to your installation):
0 * * * * cd /path/to/bot-imposes && /usr/bin/python3 bot.py >> /var/log/bot-imposes.log 2>&1
```

Example schedules:
- Every hour: `0 * * * *`
- Every 30 minutes: `*/30 * * * *`
- Every day at 8 AM: `0 8 * * *`

## Configuration

The bot uses environment variables for configuration. Create a `.env` file with:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

## Monitored URLs

The bot checks:
1. Main page: https://www.hear.fr/admissions/musique/candidats-en-licencednspmde-2-2/
   - **Monitors for any content changes using hash comparison**
   - Checks if "Pièces imposées 2026 - Prochainement disponible" text is removed
2. Pieces pages:
   - https://www.hear.fr/admissions/musique/pieces-imposees
   - https://www.hear.fr/admissions/musique/pieces-imposees-0
   - https://www.hear.fr/admissions/musique/pieces-imposees-1
   - https://www.hear.fr/admissions/musique/pieces-imposees-2
   - https://www.hear.fr/admissions/musique/pieces-imposees-3

## How It Works

### Page Content Monitoring
The bot saves a hash of the normalized page content on first run. On subsequent runs, it compares the current content hash with the saved hash. If they differ, it sends a notification and updates the saved hash.

The page state is stored in `page_state.json` (automatically created on first run).

## Logging

The bot logs all activities to stdout. To save logs to a file when running as a cron job, redirect the output:

```bash
python bot.py >> bot.log 2>&1
```

## License

MIT
