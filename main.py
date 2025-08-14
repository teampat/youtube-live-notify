import os
import time
import json
import requests
from datetime import datetime, timedelta, time as dt_time, timezone
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHANNEL_IDS = os.getenv("CHANNEL_IDS", "").split(",")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL"))
TTL_HOURS = int(os.getenv("TTL_HOURS", 24))
NOTIFIED_FILE = "data/notified.json"
TH_TIMEZONE = ZoneInfo("Asia/Bangkok")


def parse_time_range(range_str):
    start_str, end_str = range_str.split("-")
    return (dt_time.fromisoformat(start_str), dt_time.fromisoformat(end_str))


def parse_multiple_ranges(raw: str):
    return [parse_time_range(r.strip()) for r in raw.split(",") if r]


WEEKDAY_ACTIVE_TIMES = os.getenv("WEEKDAY_ACTIVE_TIMES")
WEEKEND_ACTIVE_TIMES = os.getenv("WEEKEND_ACTIVE_TIMES")
WEEKDAY_SEARCH_QUERY = os.getenv("WEEKDAY_SEARCH_QUERY", "เรื่องเล่าเช้านี้")
WEEKEND_SEARCH_QUERY = os.getenv("WEEKEND_SEARCH_QUERY", "เรื่องเล่าเสาร์-อาทิตย์")

WEEKDAY_PERIODS = parse_multiple_ranges(WEEKDAY_ACTIVE_TIMES)
WEEKEND_PERIODS = parse_multiple_ranges(WEEKEND_ACTIVE_TIMES)
EXCLUDE_KEYWORDS = [
    kw.strip() for kw in os.getenv("EXCLUDE_KEYWORDS", "").split(",") if kw.strip()
]


def is_in_active_period():
    now_th = datetime.now(TH_TIMEZONE)
    current_time = now_th.time()
    current_day = now_th.weekday()
    active_periods = WEEKDAY_PERIODS if current_day < 5 else WEEKEND_PERIODS
    return any(start <= current_time <= end for start, end in active_periods)


def load_notified_video_ids():
    # Ensure the directory exists
    os.makedirs(os.path.dirname(NOTIFIED_FILE), exist_ok=True)

    if os.path.exists(NOTIFIED_FILE):
        with open(NOTIFIED_FILE, "r") as f:
            data = json.load(f)
            now = datetime.now(timezone.utc)
            return {
                vid: ts
                for vid, ts in data.items()
                if datetime.fromisoformat(ts) > now - timedelta(hours=TTL_HOURS)
            }
    return {}


def save_notified_video_ids(data):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(NOTIFIED_FILE), exist_ok=True)
    with open(NOTIFIED_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_search_query():
    now_th = datetime.now(TH_TIMEZONE)
    current_day = now_th.weekday()

    # วันจันทร์-ศุกร์ (0-4) ใช้คำค้นหาจาก WEEKDAY_SEARCH_QUERY
    # วันเสาร์-อาทิตย์ (5-6) ใช้คำค้นหาจาก WEEKEND_SEARCH_QUERY
    if current_day < 5:  # วันธรรมดา
        return WEEKDAY_SEARCH_QUERY
    else:  # วันหยุด
        return WEEKEND_SEARCH_QUERY


def get_live_videos(channel_id):
    search_query = get_search_query()
    encoded_query = quote(search_query)
    url = (
        "https://www.googleapis.com/youtube/v3/search?"
        f"part=snippet&channelId={channel_id}&type=video&eventType=live&maxResults=5"
        f"&q={encoded_query}&key={YOUTUBE_API_KEY}"
    )
    response = requests.get(url)
    data = response.json()
    items = data.get("items", [])

    def is_excluded(title):
        return any(ex_kw in title for ex_kw in EXCLUDE_KEYWORDS)

    return [
        (
            item["id"]["videoId"],
            item["snippet"]["title"],
            item["snippet"]["channelTitle"],
        )
        for item in items
        if not is_excluded(item["snippet"]["title"])
    ]


def send_telegram_notification(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, data=payload)


def main():
    while True:
        try:
            if not is_in_active_period():
                print("⏳ Not in active time period")
                time.sleep(CHECK_INTERVAL)
                continue

            search_query = get_search_query()
            print(f"🔍 ค้นหาด้วยคำว่า: '{search_query}'")

            notified = load_notified_video_ids()
            updated = False

            for channel_id in CHANNEL_IDS:
                channel_id = channel_id.strip()
                live_videos = get_live_videos(channel_id)
                new_videos = []

                for video_id, title, channel_title in live_videos:
                    if video_id not in notified:
                        new_videos.append((video_id, title))
                        notified[video_id] = datetime.now(timezone.utc).isoformat()
                        updated = True

                if new_videos:
                    message_lines = [f"🔴 <b>Live จาก {channel_title}</b>:"]
                    for video_id, title in new_videos:
                        url = f"https://www.youtube.com/watch?v={video_id}"
                        message_lines.append(f"📺 <b>{title}</b> ➡️ {url}")
                    send_telegram_notification("\n\n".join(message_lines))
                    print(f"🔔 แจ้งเตือน {len(new_videos)} live ใหม่ จาก {channel_title}")

            if updated:
                save_notified_video_ids(notified)
            else:
                print("✅ No new live streams in the last check.")
        except Exception as e:
            print(f"❌ Error: {e}")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
