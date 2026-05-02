import datetime as dt
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from db.service.service_service import ServiceService
from db.service.booking_service import BookingService
from db.service.user_service import UserService
from bot.keyboards import (
    services_keyboard, dates_keyboard, times_keyboard,
    confirm_keyboard, main_menu_keyboard, admin_booking_keyboard,
)
from helpers.config import configs

STEP_SERVICE  = "service"
STEP_DATE     = "date"
STEP_TIME     = "time"
STEP_CONFIRM  = "confirm"


async def start_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = await ServiceService.get_all()
    if not services:
        await update.message.reply_text(
            "Hozircha xizmatlar yo'q. Admin qo'shishi kerak."
        )
        return
    context.user_data["booking"] = {"step": STEP_SERVICE}
    await update.message.reply_text(
        "Xizmatni tanlang:",
        reply_markup=services_keyboard(services),
    )


async def select_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    booking = context.user_data.get("booking", {})
    if booking.get("step") != STEP_SERVICE:
        return
    query = update.callback_query
    await query.answer()
    service_id = int(query.data.split("_")[1])
    service = await ServiceService.get_by_id(service_id)
    booking.update({
        "step": STEP_DATE,
        "service_id": service_id,
        "service_name": service.name,
        "service_duration": service.duration_min,
    })
    await query.edit_message_text(
        f"✂️ Xizmat: {service.name}\n\nSanani tanlang:",
        reply_markup=dates_keyboard(),
    )


async def select_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    booking = context.user_data.get("booking", {})
    if booking.get("step") != STEP_DATE:
        return
    query = update.callback_query
    await query.answer()
    date_str = query.data.split("_", 1)[1]
    booking_date = dt.date.fromisoformat(date_str)
    service = await ServiceService.get_by_id(booking["service_id"])
    slots = await BookingService.get_available_slots(service, booking_date)
    if not slots:
        await query.edit_message_text(
            "Bu kunda bo'sh vaqt yo'q. Boshqa kun tanlang:",
            reply_markup=dates_keyboard(),
        )
        return
    booking.update({"step": STEP_TIME, "date": date_str})
    await query.edit_message_text(
        f"✂️ Xizmat: {booking['service_name']}\n"
        f"📅 Sana: {booking_date.strftime('%d.%m.%Y')}\n\n"
        f"Vaqtni tanlang:",
        reply_markup=times_keyboard(slots),
    )


async def select_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    booking = context.user_data.get("booking", {})
    if booking.get("step") != STEP_TIME:
        return
    query = update.callback_query
    await query.answer()
    time_str = query.data.split("_", 1)[1]
    booking_date = dt.date.fromisoformat(booking["date"])
    booking.update({"step": STEP_CONFIRM, "time": time_str})
    await query.edit_message_text(
        f"📋 Bron ma'lumotlari:\n\n"
        f"✂️ Xizmat: {booking['service_name']}\n"
        f"📅 Sana: {booking_date.strftime('%d.%m.%Y')}\n"
        f"⏰ Vaqt: {time_str}\n\n"
        f"Tasdiqlaysizmi?",
        reply_markup=confirm_keyboard(),
    )


async def confirm_booking_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    booking = context.user_data.get("booking", {})
    if booking.get("step") != STEP_CONFIRM:
        await query.edit_message_text("Muammo yuz berdi. Iltimos, qaytadan boshlang.")
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text="Asosiy menyu:",
            reply_markup=main_menu_keyboard(),
        )
        return

    if query.data == "no":
        context.user_data.pop("booking", None)
        await query.edit_message_text("Bron bekor qilindi.")
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text="Asosiy menyu:",
            reply_markup=main_menu_keyboard(),
        )
        return

    user = await UserService.get_by_telegram_id(query.from_user.id)
    if user is None:
        await query.edit_message_text("Foydalanuvchi topilmadi. /start bosing.")
        return

    h, m = map(int, booking["time"].split(":"))
    new_booking = await BookingService.create(
        user_id=user.id,
        service_id=booking["service_id"],
        booking_date=dt.date.fromisoformat(booking["date"]),
        booking_time=dt.time(h, m),
    )
    context.user_data.pop("booking", None)
    await query.edit_message_text("✅ Bron qabul qilindi! Admin tasdiqlashini kuting.")
    await context.bot.send_message(
        chat_id=query.from_user.id,
        text="Asosiy menyu:",
        reply_markup=main_menu_keyboard(),
    )
    booking_full = await BookingService.get_by_id(new_booking.id)
    await _notify_admin(context.bot, booking_full)


async def _notify_admin(bot, booking) -> None:
    admin_id = configs.get("ADMIN_CHAT_ID")
    if not admin_id:
        return
    text = (
        f"📅 Yangi bron!\n\n"
        f"👤 Ism: {booking.user.name}\n"
        f"📞 Tel: {booking.user.phone or 'Kiritilmagan'}\n"
        f"✂️ Xizmat: {booking.service.name}\n"
        f"📅 Sana: {booking.date.strftime('%d.%m.%Y')}\n"
        f"⏰ Vaqt: {booking.time.strftime('%H:%M')}"
    )
    await bot.send_message(
        chat_id=int(admin_id),
        text=text,
        reply_markup=admin_booking_keyboard(booking.id),
    )
