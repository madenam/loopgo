from dotenv import load_dotenv
import os

load_dotenv()

configs = {
    "BOT_TOKEN": os.getenv("BOT_TOKEN"),
    "ADMIN_CHAT_ID": os.getenv("ADMIN_CHAT_ID"),
    "DATABASE_URL": os.getenv("DATABASE_URL", "sqlite://db.sqlite3"),
    "TIMEZONE": os.getenv("TIMEZONE", "Asia/Tashkent"),
}

app_name = "loopgo"
