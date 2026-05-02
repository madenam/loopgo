import datetime as dt
from zoneinfo import ZoneInfo
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from db.service.booking_service import BookingService
from db.service.service_service import ServiceService
from db.models import BookingStatus
from helpers.config import configs

ADD_SVC_NAME, ADD_SVC_DURATION, ADD_SVC_PRICE = 20, 21, 22
APP_TIMEZONE = ZoneInfo(configs["TIMEZONE"])


def _is_admin(user_id: int) -> bool:
    return str(user_id) == str(configs.get("ADMIN_CHAT_ID"))


# ── Admin panel inline tugmalari ──────────────────────────────────────────────

async def admin_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(query.from_user.id):
        return

    if query.data == "admin_addservice":
        context.user_data["admin_step"] = ADD_SVC_NAME
        await query.message.reply_text("Yangi xizmat nomi:")

    elif query.data == "admin_services":
        services = await ServiceService.get_all()
        if not services:
            await query.message.reply_text("Hech qanday xizmat yo'q.")
            return
        for s in services:
            kb = InlineKeyboardMarkup([[
                InlineKeyboardButton("🗑 O'chirish", callback_data=f"delsvc_{s.id}")
            ]])
            await query.message.reply_text(
                f"📌 {s.name}\n⏱ {s.duration_min} min  💰 {int(s.price):,} so'm",
                reply_markup=kb,
            )

    elif query.data == "admin_bookings":
        bookings = await BookingService.get_today_bookings()
        if not bookings:
            await query.message.reply_text("Bugun bronlar yo'q.")
            return
        lines = [f"📋 Bugungi bronlar ({len(bookings)} ta):\n"]
        for b in bookings:
            lines.append(
                f"⏰ {b.time.strftime('%H:%M')} — {b.service.name}\n"
                f"   👤 {b.user.name} | 📞 {b.user.phone or '—'}"
            )
        await query.message.reply_text("\n".join(lines))


# ── Xizmat qo'shish: matn qadamlari (user_data orqali) ───────────────────────

async def admin_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inline panel orqali boshlangan xizmat qo'shish oqimini ushlab turadi."""
    if not _is_admin(update.effective_user.id):
        return
    step = context.user_data.get("admin_step")
    if step is None:
        return

    text = update.message.text.strip()

    if step == ADD_SVC_NAME:
        context.user_data["svc_name"] = text
        context.user_data["admin_step"] = ADD_SVC_DURATION
        await update.message.reply_text("Davomiyligi (daqiqada, masalan: 30):")

    elif step == ADD_SVC_DURATION:
        if not text.isdigit():
            await update.message.reply_text("Faqat raqam kiriting (masalan: 30):")
            return
        context.user_data["svc_duration"] = int(text)
        context.user_data["admin_step"] = ADD_SVC_PRICE
        await update.message.reply_text("Narxi (so'mda, masalan: 50000):")

    elif step == ADD_SVC_PRICE:
        if not text.isdigit():
            await update.message.reply_text("Faqat raqam kiriting (masalan: 50000):")
            return
        name     = context.user_data.pop("svc_name")
        duration = context.user_data.pop("svc_duration")
        price    = int(text)
        context.user_data.pop("admin_step", None)
        await ServiceService.create(name=name, duration_min=duration, price=price)
        await update.message.reply_text(
            f"✅ Xizmat qo'shildi!\n\n"
            f"📌 {name}\n"
            f"⏱ {duration} min  💰 {price:,} so'm"
        )


# ── Xizmat qo'shish (ConversationHandler — /addservice buyrug'i uchun) ─────────

async def addservice_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not _is_admin(update.effective_user.id):
        return ConversationHandler.END
    await update.message.reply_text("Yangi xizmat nomi:")
    return ADD_SVC_NAME


async def addservice_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["svc_name"] = update.message.text.strip()
    await update.message.reply_text("Davomiyligi (daqiqada, masalan: 30):")
    return ADD_SVC_DURATION


async def addservice_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("Faqat raqam kiriting (masalan: 30):")
        return ADD_SVC_DURATION
    context.user_data["svc_duration"] = int(text)
    await update.message.reply_text("Narxi (so'mda, masalan: 50000):")
    return ADD_SVC_PRICE


async def addservice_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("Faqat raqam kiriting (masalan: 50000):")
        return ADD_SVC_PRICE
    name = context.user_data["svc_name"]
    duration = context.user_data["svc_duration"]
    price = int(text)
    await ServiceService.create(name=name, duration_min=duration, price=price)
    await update.message.reply_text(
        f"✅ Xizmat qo'shildi!\n\n"
        f"📌 Nomi: {name}\n"
        f"⏱ Davomiyligi: {duration} min\n"
        f"💰 Narxi: {price:,} so'm"
    )
    return ConversationHandler.END


async def addservice_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Bekor qilindi.")
    return ConversationHandler.END


# ── Xizmatlar ro'yxati va o'chirish ───────────────────────────────────────────

async def services_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update.effective_user.id):
        return
    services = await ServiceService.get_all()
    if not services:
        await update.message.reply_text("Hech qanday xizmat yo'q. /addservice orqali qo'shing.")
        return
    for s in services:
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("🗑 O'chirish", callback_data=f"delsvc_{s.id}")
        ]])
        await update.message.reply_text(
            f"📌 {s.name}\n⏱ {s.duration_min} min  💰 {int(s.price):,} so'm",
            reply_markup=kb,
        )


async def delete_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not _is_admin(query.from_user.id):
        return
    service_id = int(query.data.split("_")[1])
    await ServiceService.delete(service_id)
    await query.edit_message_text(query.message.text + "\n\n🗑 O'chirildi")


# ── Bronlarni tasdiqlash / rad etish ──────────────────────────────────────────

async def confirm_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    booking_id = int(query.data.split("_")[1])
    booking = await BookingService.get_by_id(booking_id)
    if not booking:
        await query.edit_message_text("Bron topilmadi.")
        return
    await BookingService.update_status(booking_id, BookingStatus.CONFIRMED)
    await query.edit_message_text(query.message.text + "\n\n✅ Tasdiqlandi")
    await context.bot.send_message(
        chat_id=booking.user.telegram_id,
        text=(
            f"✅ Broningiz tasdiqlandi!\n\n"
            f"✂️ Xizmat: {booking.service.name}\n"
            f"📅 Sana: {booking.date.strftime('%d.%m.%Y')}\n"
            f"⏰ Vaqt: {booking.time.strftime('%H:%M')}"
        ),
    )
    booking_dt = dt.datetime.combine(booking.date, booking.time, tzinfo=APP_TIMEZONE)
    remind_at = booking_dt - dt.timedelta(hours=1)
    now = dt.datetime.now(APP_TIMEZONE)
    if remind_at > now:
        delay = (remind_at - now).total_seconds()
        context.job_queue.run_once(
            _send_reminder,
            when=delay,
            data={"telegram_id": booking.user.telegram_id, "booking": booking},
        )


async def reject_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    booking_id = int(query.data.split("_")[1])
    booking = await BookingService.get_by_id(booking_id)
    if not booking:
        await query.edit_message_text("Bron topilmadi.")
        return
    await BookingService.update_status(booking_id, BookingStatus.CANCELLED)
    await query.edit_message_text(query.message.text + "\n\n❌ Rad etildi")
    await context.bot.send_message(
        chat_id=booking.user.telegram_id,
        text=(
            f"❌ Broningiz rad etildi.\n\n"
            f"✂️ Xizmat: {booking.service.name}\n"
            f"📅 Sana: {booking.date.strftime('%d.%m.%Y')}\n"
            f"⏰ Vaqt: {booking.time.strftime('%H:%M')}"
        ),
    )


async def admin_bookings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update.effective_user.id):
        return
    bookings = await BookingService.get_today_bookings()
    if not bookings:
        await update.message.reply_text("Bugun bronlar yo'q.")
        return
    lines = [f"📋 Bugungi bronlar ({len(bookings)} ta):\n"]
    for b in bookings:
        lines.append(
            f"⏰ {b.time.strftime('%H:%M')} — {b.service.name}\n"
            f"   👤 {b.user.name} | 📞 {b.user.phone or '—'}"
        )
    await update.message.reply_text("\n".join(lines))


async def daily_admin_digest(context: ContextTypes.DEFAULT_TYPE) -> None:
    admin_id = configs.get("ADMIN_CHAT_ID")
    if not admin_id:
        return
    bookings = await BookingService.get_today_bookings()
    if not bookings:
        text = "📋 Bugun bronlar yo'q."
    else:
        lines = [f"🌅 Bugungi bronlar ({len(bookings)} ta):\n"]
        for b in bookings:
            lines.append(
                f"⏰ {b.time.strftime('%H:%M')} — {b.service.name}\n"
                f"   👤 {b.user.name} | 📞 {b.user.phone or '—'}"
            )
        text = "\n".join(lines)
    await context.bot.send_message(chat_id=int(admin_id), text=text)


async def _send_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    data = context.job.data
    booking = data["booking"]
    await context.bot.send_message(
        chat_id=data["telegram_id"],
        text=(
            f"⏰ Eslatma!\n\n"
            f"1 soatdan so'ng broningiz bor:\n"
            f"✂️ {booking.service.name}\n"
            f"🕐 {booking.time.strftime('%H:%M')}"
        ),
    )
