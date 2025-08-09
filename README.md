# YouTube Live Stream Notifier

A Python application that monitors YouTube channels for live streams and sends notifications to Telegram when new live streams are detected.

## Features

- 🔴 **Real-time monitoring** of multiple YouTube channels for live streams
- 📱 **Telegram notifications** with live stream details and direct links
- ⏰ **Configurable active hours** with different schedules for weekdays and weekends
- 🚫 **Duplicate prevention** with TTL-based tracking of notified streams
- 🐳 **Docker support** for easy deployment
- 🌏 **Timezone support** (configured for Asia/Bangkok)

## Prerequisites

Before running this application, you'll need:

1. **YouTube Data API v3 Key**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable YouTube Data API v3
   - Create credentials (API key)

2. **Telegram Bot**
   - Message [@BotFather](https://t.me/BotFather) on Telegram
   - Create a new bot with `/newbot`
   - Get your bot token

3. **Telegram Chat ID**
   - Add your bot to a chat or group
   - Send a message to the bot
   - Visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find your chat ID in the response

## Installation

### Local Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd youtube-live-notify
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your configuration:
```env
YOUTUBE_API_KEY=your_youtube_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
CHANNEL_IDS=UCxxxxxxxxxxxxxx,UCyyyyyyyyyyyyyy
CHECK_INTERVAL=300
TTL_HOURS=24
WEEKDAY_ACTIVE_TIMES=06:00-09:00,18:00-23:59
WEEKEND_ACTIVE_TIMES=10:00-12:00,20:00-22:00
```

4. Run the application:
```bash
python main.py
```

### Docker Setup

#### Option 1: Docker Compose (Recommended)

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file with your actual configuration values

3. Run with Docker Compose:
```bash
docker-compose up -d
```

4. View logs:
```bash
docker-compose logs -f
```

5. Stop the service:
```bash
docker-compose down
```

#### Option 2: Docker Run

1. Build the Docker image:
```bash
docker build -t youtube-live-notify .
```

2. Run the container with your environment file:
```bash
docker run -d --name youtube-live-notify --env-file .env youtube-live-notify
```

## Configuration

### Environment Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `YOUTUBE_API_KEY` | Your YouTube Data API v3 key | `AIzaSyXXXXXXXXXXXXXXXXXXXXXX` | ✅ |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | `1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ` | ✅ |
| `TELEGRAM_CHAT_ID` | Telegram chat ID to send notifications | `-1001234567890` | ✅ |
| `CHANNEL_IDS` | Comma-separated YouTube channel IDs | `UCxxxxxx,UCyyyyyy` | ✅ |
| `CHECK_INTERVAL` | Check interval in seconds | `300` (5 minutes) | ✅ |
| `WEEKDAY_ACTIVE_TIMES` | Active hours on weekdays (Mon-Fri) | `06:00-09:00,18:00-23:59` | ✅ |
| `WEEKEND_ACTIVE_TIMES` | Active hours on weekends (Sat-Sun) | `10:00-12:00,20:00-22:00` | ✅ |
| `TTL_HOURS` | Hours to remember notified streams | `24` | ❌ |

### Finding YouTube Channel IDs

1. Go to the YouTube channel page
2. View page source and search for `"channelId":"` or `"externalId":"`
3. Alternatively, use online tools like [Comment Picker](https://commentpicker.com/youtube-channel-id.php)

### Time Format

- Use 24-hour format: `HH:MM`
- Multiple ranges separated by commas: `06:00-09:00,18:00-23:59`
- Timezone is set to Asia/Bangkok in the code

## How It Works

1. **Monitoring Loop**: The application runs continuously, checking for live streams at configured intervals
2. **Active Hours**: Only sends notifications during configured active periods (different for weekdays/weekends)
3. **API Calls**: Uses YouTube Data API v3 to search for live videos on specified channels
4. **Duplicate Prevention**: Tracks notified video IDs in `notified.json` with TTL to prevent spam
5. **Telegram Notification**: Sends formatted messages with live stream title, channel, and direct link

## Output Examples

### Console Output
```
🔔 แจ้งเตือน 1 live ใหม่ จาก Channel Name
✅ No new live streams in the last check.
⏳ Not in active time period
```

### Telegram Notification
```
🔴 Live จาก Channel Name:

📺 Stream Title Here ➡️ https://www.youtube.com/watch?v=VIDEO_ID
```

## File Structure

```
youtube-live-notify/
├── main.py              # Main application code
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
├── .env               # Environment variables (not tracked)
├── .env.example       # Example environment file
├── .gitignore         # Git ignore rules
├── notified.json      # Tracks notified streams (auto-generated)
└── README.md          # This file
```

## Troubleshooting

### Common Issues

1. **"quotaExceeded" Error**: YouTube API has daily quota limits. Monitor your usage in Google Cloud Console.

2. **No Notifications**: Check if:
   - You're within active time periods
   - Channel IDs are correct
   - Bot has permissions to send messages to the chat

3. **Bot Not Responding**: Ensure:
   - Bot token is correct
   - Chat ID is correct (including negative sign for groups)
   - Bot is added to the group (if using group chat)

### Logs and Debugging

The application prints status messages to console:
- `🔔` New live stream notifications
- `✅` Normal operation (no new streams)
- `⏳` Outside active hours
- `❌` Errors with details

## API Rate Limits

- **YouTube API**: 10,000 units per day (each search request costs ~100 units)
- **Telegram API**: 30 messages per second to the same chat

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is provided as-is for educational and personal use.

## Disclaimer

This tool is for personal use only. Ensure you comply with:
- YouTube's Terms of Service
- Telegram's Terms of Service  
- Google's API usage policies

Use responsibly and respect rate limits.
