import logging
from telegram import Update
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, filters, ContextTypes,
)
from tortoise.context import _current_context

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class TortoiseApplication(Application):
    async def process_update(self, update: Update) -> None:
        from db.db import get_db_ctx
        token = _current_context.set(get_db_ctx())
        try:
            await super().process_update(update)
        finally:
            _current_context.reset(token)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Xato:", exc_info=context.error)


from helpers.config import configs
from bot.handlers.commands import start, got_phone, show_contact, help_command, ASK_PHONE
from bot.handlers.booking import (
    start_booking, select_service, select_date, select_time, confirm_booking_user,
)
from bot.handlers.admin import (
    confirm_booking, reject_booking, admin_bookings_command,
    addservice_start, addservice_name, addservice_duration, addservice_price, addservice_cancel,
    ADD_SVC_NAME, ADD_SVC_DURATION, ADD_SVC_PRICE,
    services_list_command, delete_service, admin_panel_callback, admin_text_handler,
)
from bot.handlers.my_bookings import show_my_bookings, cancel_my_booking


def create_app(post_init=None, post_shutdown=None):
    builder = ApplicationBuilder().token(configs["BOT_TOKEN"]).application_class(TortoiseApplication)
    if post_init:
        builder = builder.post_init(post_init)
    if post_shutdown:
        builder = builder.post_shutdown(post_shutdown)
    app = builder.build()

    # Ro'yxatdan o'tish
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_PHONE: [
                MessageHandler(filters.CONTACT, got_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, got_phone),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    ))

    # Xizmat qo'shish (admin)
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("addservice", addservice_start)],
        states={
            ADD_SVC_NAME:     [MessageHandler(filters.TEXT & ~filters.COMMAND, addservice_name)],
            ADD_SVC_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, addservice_duration)],
            ADD_SVC_PRICE:    [MessageHandler(filters.TEXT & ~filters.COMMAND, addservice_price)],
        },
        fallbacks=[CommandHandler("cancel", addservice_cancel)],
    ))

    # Admin matn oqimi (inline paneldan boshlangan holat)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_text_handler), group=1)

    # Menyu tugmalari
    app.add_handler(MessageHandler(filters.Regex(r"^✂️ Bron qilish$"),      start_booking))
    app.add_handler(MessageHandler(filters.Regex(r"^📋 Mening bronlarim$"), show_my_bookings))
    app.add_handler(MessageHandler(filters.Regex(r"^📞 Bog'lanish$"),       show_contact))

    # Booking callback-lar (context.user_data orqali holat)
    app.add_handler(CallbackQueryHandler(select_service,      pattern=r"^svc_"))
    app.add_handler(CallbackQueryHandler(select_date,         pattern=r"^date_"))
    app.add_handler(CallbackQueryHandler(select_time,         pattern=r"^time_"))
    app.add_handler(CallbackQueryHandler(confirm_booking_user, pattern=r"^(ok|no)$"))

    # Admin panel
    app.add_handler(CallbackQueryHandler(admin_panel_callback, pattern=r"^admin_"))

    # Admin callback-lar
    app.add_handler(CallbackQueryHandler(confirm_booking,   pattern=r"^confirm_\d+$"))
    app.add_handler(CallbackQueryHandler(reject_booking,    pattern=r"^cancel_\d+$"))
    app.add_handler(CallbackQueryHandler(cancel_my_booking, pattern=r"^mycancel_\d+$"))
    app.add_handler(CallbackQueryHandler(delete_service,    pattern=r"^delsvc_\d+$"))

    # Buyruqlar
    app.add_handler(CommandHandler("bookings",  admin_bookings_command))
    app.add_handler(CommandHandler("services",  services_list_command))
    app.add_handler(CommandHandler("help",      help_command))
    app.add_error_handler(error_handler)

    return app
