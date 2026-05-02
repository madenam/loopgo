import warnings
import datetime
from zoneinfo import ZoneInfo
from telegram.warnings import PTBUserWarning
warnings.filterwarnings("ignore", category=PTBUserWarning)
from bot.bot import create_app
from db.db import init_db, close_db
from bot.handlers.admin import daily_admin_digest
from helpers.config import configs


async def post_init(app):
    await init_db()
    app_timezone = ZoneInfo(configs["TIMEZONE"])
    app.job_queue.run_daily(daily_admin_digest, time=datetime.time(8, 0, tzinfo=app_timezone))


async def post_shutdown(app):
    await close_db()


if __name__ == "__main__":
    app = create_app(post_init=post_init, post_shutdown=post_shutdown)
    print("Bot ishga tushdi...")
    app.run_polling()
