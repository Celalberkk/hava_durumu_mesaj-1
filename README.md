# Daily Weather Bot

A Python bot that sends a short weather summary to WhatsApp every morning. It pulls the hourly forecast for the day, checks for rain and extreme temperatures, and sends a Turkish-language alert with the time ranges to watch out for, plus a motivational quote of the day.

## Features

- **Hourly forecast** from the free [Open-Meteo](https://open-meteo.com/) API (no API key needed)
- **Rain alert** for hours with a precipitation probability of 20% or more
- **Heat alert** for hours at or above 35°C
- **Cold alert** for hours at or below 10°C
- **Readable time ranges:** consecutive hours are merged (e.g. `14:00 - 17:00`)
- **Calm-day message** with the day's temperature range when there is nothing to warn about
- **WhatsApp delivery** through the [CallMeBot](https://www.callmebot.com/) API
- **Daily schedule:** runs every morning at 08:30, or once on demand with `--now`

## Example message

```
☀️ Günaydın! Bugünkü hava durumu uyarınız (İstanbul):

☔ Yağmur Riski: 14:00 - 17:00 arasında yağmur ihtimali var (ort. %45, maks. %60). Yanınıza şemsiye almayı unutmayın!

🔵 Düşük Sıcaklık: 22:00 - 00:00 arası sıcaklık 10°C altına düşecek (min. 7.5°C). Kalın giyinmeyi unutmayın!

💬 Günün Sözü:
...
```

## How it works

1. `location.py` returns the coordinates to check.
2. `weather.py` requests today's hourly temperature and precipitation probability from Open-Meteo.
3. `alerts.py` finds the hours that cross each threshold and builds the message.
4. `quotes.py` adds a random quote of the day.
5. `notifier.py` sends the message to WhatsApp through CallMeBot.
6. `main.py` ties the steps together, handles errors and logging, and runs the schedule.

## Project structure

```
├── main.py           # Entry point: workflow, scheduling, logging
├── weather.py        # Open-Meteo API client
├── alerts.py         # Threshold checks and message formatting
├── notifier.py       # WhatsApp delivery via CallMeBot
├── location.py       # Coordinates to check
├── quotes.py         # Quote of the day list
└── requirements.txt
```

## Setup

Requires Python 3.9 or newer.

```bash
git clone https://github.com/Celalberkk/hava_durumu_mesaj-1.git
cd hava_durumu_mesaj-1
pip install -r requirements.txt
```

Get a CallMeBot API key by following the WhatsApp setup steps on the CallMeBot website. Then create a `.env` file in the project folder:

```
CALLMEBOT_PHONE=+905xxxxxxxxx
CALLMEBOT_API_KEY=your_api_key
```

`.env` holds your private credentials, so it is listed in `.gitignore` and never committed.

## Usage

```bash
python main.py --now   # send one message right away (for testing)
python main.py         # keep running and send a message every day at 08:30
```

When running on GitHub Actions, add `CALLMEBOT_PHONE` and `CALLMEBOT_API_KEY` as repository secrets instead of using a `.env` file.

## Tech stack

Python · requests · schedule · python-dotenv · Open-Meteo API · CallMeBot API · GitHub Actions
