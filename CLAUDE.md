# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Telegram barbershop booking bot. Users browse services, pick a time slot, and book — admins confirm/reject and receive daily summaries. Reminders fire automatically 1 hour before appointments.

## Commands

```bash
pip install -r requirements.txt
python main.py
```

## Architecture

```
bot/
  main.py            # Entry point: initialise DB, scheduler, run_polling()
  core/
    config.py        # Loads .env → exposes BOT_TOKEN, ADMIN_CHAT_ID, DATABASE_URL
    app.py           # Builds and returns the Application instance
  handlers/
    start.py         # /start → name → phone → main menu (ConversationHandler)
    booking.py       # Booking flow: service → date → time slot → confirm
    admin.py         # Admin callbacks: approve ✅ / reject ❌, daily list
  db/
    models.py        # Tortoise ORM models: User, Service, Booking (see below)
  scheduler/
    reminders.py     # APScheduler jobs: 1-hour reminder + 08:00 daily admin digest
```

### Data models

**User** — `telegram_id` (unique), `name`, `phone`, `created_at`  
**Service** — `name`, `duration_min`, `price`  
**Booking** — FK→User, FK→Service, `date`, `time`, `status` (pending/confirmed/cancelled), `created_at`

### Key flows

- **User:** `/start` → registration → main menu → book (service → day → free slot → confirm) / view/cancel own bookings  
- **Admin:** receives inline keyboard on each new booking (confirm/reject); daily 08:00 digest of that day's bookings  
- **Slots:** available times are computed by filtering out already-booked slots for the chosen service duration

### Environment variables

```
BOT_TOKEN=
ADMIN_CHAT_ID=
DATABASE_URL=        # sqlite:///db.sqlite3  or  postgres://...
DEBUG=False
```

## Stack

Python 3.12+, python-telegram-bot, Tortoise ORM, APScheduler (async), python-dotenv. SQLite for dev, PostgreSQL for prod.
