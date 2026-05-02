# Barbershop Booking Bot

Telegram orqali sartaroshxona xizmatlarini bron qilish imkonini beruvchi bot.

---

## Loyiha maqsadi

Foydalanuvchilar Telegram orqali sartaroshxona xizmatlarini ko'rib, qulay vaqtni tanlab bron qila oladi. Admin esa bronlarni tasdiqlaydi, rad etadi va eslatmalar avtomatik yuboriladi.

---

## Texnologiyalar

- **Til:** Python 3.12+
- **Bot framework:** python-telegram-bot
- **ORM:** Tortoise ORM
- **Ma'lumotlar bazasi:** SQLite (dev) / PostgreSQL (prod)
- **Scheduler:** APScheduler (async)
- **Config:** python-dotenv

---

## Folder structure

```
bot/
├── main.py
├── .env
├── .gitignore
├── requirements.txt
├── CLAUDE.md
│
├── core/
│   ├── __init__.py
│   ├── config.py        # .env o'qish
│   └── app.py           # bot instance yaratish
│
├── handlers/
│   ├── __init__.py
│   ├── start.py         # /start, ro'yxatdan o'tish
│   ├── booking.py       # bron qilish flow
│   └── admin.py         # admin panel
│
├── db/
│   ├── __init__.py
│   └── models.py        # User, Service, Booking
│
└── scheduler/
    ├── __init__.py
    └── reminders.py     # avtomatik eslatmalar
```

---

## Ma'lumotlar bazasi modellari

### User
| Maydon | Tur | Izoh |
|---|---|---|
| id | int | primary key |
| telegram_id | int | unique |
| name | str | ism |
| phone | str | telefon raqam |
| created_at | datetime | yaratilgan vaqt |

### Service
| Maydon | Tur | Izoh |
|---|---|---|
| id | int | primary key |
| name | str | xizmat nomi |
| duration_min | int | davomiyligi (daqiqa) |
| price | int | narxi (so'm) |

### Booking
| Maydon | Tur | Izoh |
|---|---|---|
| id | int | primary key |
| user_id | FK | User |
| service_id | FK | Service |
| date | date | sana |
| time | time | vaqt |
| status | enum | pending / confirmed / cancelled |
| created_at | datetime | yaratilgan vaqt |

---

## Xizmatlar (MVP)

| Xizmat | Davomiyligi | Narxi |
|---|---|---|
| Soch olish | 30 min | 50,000 so'm |
| Soqol olish | 20 min | 30,000 so'm |
| Soch + Soqol | 45 min | 70,000 so'm |

---

## Foydalanuvchi flow

```
/start
  └── Ism so'rash
        └── Telefon so'rash
              └── Bosh menyu

Bosh menyu
  ├── ✂️ Bron qilish
  │     ├── Xizmat tanlash
  │     ├── Kun tanlash
  │     ├── Vaqt tanlash (bo'sh slotlar)
  │     └── Tasdiqlash
  │
  ├── 📋 Mening bronlarim
  │     └── Bekor qilish
  │
  └── 📞 Bog'lanish
```

---

## Admin flow

```
Yangi bron kelganda admin ga xabar:
  └── Tasdiqlash ✅
  └── Rad etish ❌

Bronlar ro'yxati:
  └── Bugungi bronlar
  └── Ertangi bronlar
```

---

## Eslatmalar

- Bron vaqtidan **1 soat oldin** foydalanuvchiga avtomatik xabar
- Admin ga har kuni **08:00 da** bugungi bronlar ro'yxati

---

## Environment variables

```env
BOT_TOKEN=
ADMIN_CHAT_ID=
DATABASE_URL=
DEBUG=False
```

---

## Buyruqlar

```bash
# O'rnatish
pip install -r requirements.txt

# Ishga tushirish
python main.py
```

---

## Keyingi bosqich (V2)

- To'lov tizimi (Payme / Click)
- Reyting va sharhlar
- Web admin dashboard
- Ko'p filial qo'llab-quvvatlash