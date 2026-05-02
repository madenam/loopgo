from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from db.service.user_service import UserService
from bot.keyboards import main_menu_keyboard
from helpers.config import configs

ASK_PHONE = 0


def _phone_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Telefon raqamni ulashish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    tg_user = update.effective_user
    is_exists = await UserService.exists(tg_user.id)

    if not is_exists:
        await UserService.create(telegram_id=tg_user.id, name=tg_user.first_name, phone=None)
        await update.message.reply_text(
            f"Salom, {tg_user.first_name}! 👋\n\n"
            f"Botdan foydalanish uchun telefon raqamingizni yuboring:",
            reply_markup=_phone_keyboard(),
        )
        return ASK_PHONE

    await update.message.reply_text(
        f"Xush kelibsiz, {tg_user.first_name}! 👋",
        reply_markup=main_menu_keyboard(),
    )

    if str(tg_user.id) == str(configs.get("ADMIN_CHAT_ID")):
        await update.message.reply_text(
            "⚙️ Admin panel:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Xizmat qo'shish", callback_data="admin_addservice")],
                [InlineKeyboardButton("📋 Xizmatlar ro'yxati", callback_data="admin_services")],
                [InlineKeyboardButton("📅 Bugungi bronlar", callback_data="admin_bookings")],
            ]),
        )

    return ConversationHandler.END


async def got_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text.strip()

    await UserService.update(update.effective_user.id, phone=phone)
    await update.message.reply_text(
        "Ro'yxatdan o'tdingiz! ✅",
        reply_markup=main_menu_keyboard(),
    )
    return ConversationHandler.END


async def show_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📞 Bog'lanish uchun:\n\n"
        "📱 Tel: +998901234567\n"
        "🕐 Ish vaqti: 09:00 — 18:00"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Mavjud buyruqlar:\n\n"
        "/start    — Botni boshlash\n"
        "/bookings — Bugungi bronlar (admin)\n"
        "/help     — Yordam"
    )
