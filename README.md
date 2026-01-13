# bot-imposes

Little bot to check when program is published by superior music school (HEAR).

This bot monitors the HEAR (Haute école des arts du Rhin) website for updates about imposed pieces for 2026. It sends Telegram notifications when:

1. The text "Pièces imposées 2026 - Prochainement disponible" is no longer present on the admissions page
2. The imposed pieces pages (pieces-imposees variants) are no longer returning 404 errors

## Features

- 🔍 Monitors multiple URLs for changes
- 📱 Sends Telegram notifications
- 🔄 Designed to run as a cron job
- 📝 Detailed logging
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
2. Pieces pages:
   - https://www.hear.fr/admissions/musique/pieces-imposees
   - https://www.hear.fr/admissions/musique/pieces-imposees-0
   - https://www.hear.fr/admissions/musique/pieces-imposees-1
   - https://www.hear.fr/admissions/musique/pieces-imposees-2
   - https://www.hear.fr/admissions/musique/pieces-imposees-3

## Logging

The bot logs all activities to stdout. To save logs to a file when running as a cron job, redirect the output:

```bash
python bot.py >> bot.log 2>&1
```

## Troubleshooting

### 401 Unauthorized Error

If you encounter a `401 Unauthorized` error when sending Telegram notifications:

```
ERROR - Failed to send Telegram notification: 401 Client Error: Unauthorized
```

**Solution:** This is typically caused by whitespace (spaces, tabs, or newlines) in your Telegram credentials. The bot now automatically strips whitespace from credentials, but ensure your `.env` file doesn't have extra whitespace:

```env
# Correct - no extra whitespace
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=123456789

# Incorrect - has trailing whitespace (can cause 401 errors)
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11  
TELEGRAM_CHAT_ID=123456789
```

Also verify:
- Your bot token is valid and active (check with @BotFather)
- Your bot token is complete and correctly copied
- Your chat ID is correct

## License

MIT
