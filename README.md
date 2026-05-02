# ✂️ LoopGo Barbershop Bot

Telegram orqali sartaroshxona xizmatlarini oson bron qilish uchun yaratilgan bot.

---

## 🚀 Xususiyatlar

* 📅 Xizmatlarni bron qilish
* ⏰ Avtomatik eslatmalar (1 soat oldin)
* 👨‍💼 Admin panel (xizmat qo‘shish/o‘chirish)
* 📋 Kunlik bronlar hisoboti
* 🌍 Timezone qo‘llab-quvvatlash

---

## 📦 Talablar

* Python **3.12+**
* Telegram Bot Token
* Admin Telegram Chat ID

---

## ⚙️ O‘rnatish

### 1. Loyihani yuklab oling

```powershell
cd C:\Users\toxfi\Desktop\loopgo
```

### 2. Virtual environment yarating

```powershell
python -m venv venv
```

### 3. Virtual environment’ni yoqing

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Paketlarni o‘rnating

```powershell
pip install -r requirements.txt
```

---

## 🔐 Sozlash

`.env` fayl yarating:

```powershell
Copy-Item .env.example .env
```

`.env` ichiga quyidagilarni yozing:

```env
BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
ADMIN_CHAT_ID="YOUR_TELEGRAM_ID"
DATABASE_URL="sqlite:///barbershop.db"
TIMEZONE="Asia/Tashkent"
```

### 📌 Izohlar

* `BOT_TOKEN` → BotFather orqali olinadi
* `ADMIN_CHAT_ID` → Telegram user ID
* `DATABASE_URL` → SQLite yoki boshqa DB ulanishi
* `TIMEZONE` → Bot ishlaydigan vaqt zonasi

---

## ▶️ Ishga tushirish

```powershell
.\venv\Scripts\python.exe .\src\server.py
```

Agar hammasi to‘g‘ri bo‘lsa:

```text
Bot ishga tushdi...
```

---

## 🛑 To‘xtatish

```powershell
Ctrl + C
```

---

## 📊 Muhim eslatmalar

* 🗄 SQLite baza avtomatik yaratiladi
* 🌅 Har kuni **08:00** da admin’ga bronlar ro‘yxati yuboriladi
* 🔔 Tasdiqlangan bronlar uchun **1 soat oldin eslatma** yuboriladi
* 🌍 Barcha vaqtlar `TIMEZONE` ga asoslanadi

---

## 🧠 Arxitektura tavsiyasi

* Backend’da vaqtni **UTC** da saqlang
* Foydalanuvchiga ko‘rsatishda `TIMEZONE` ga o‘giring
* Bu kelajakda xatolarni kamaytiradi

---

## 💡 Kelajakdagi yaxshilanishlar

* Persistent job queue (restartdan keyin ham eslatmalar ishlashi)
* Web panel (admin uchun)
* Online to‘lov integratsiyasi
* Multi-branch qo‘llab-quvvatlash

---

## 👨‍💻 Muallif

LoopGo loyihasi uchun ishlab chiqilgan 🚀
> Made_nam tomonidan yaratildi ❤️