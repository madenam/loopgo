from telegram import Update
from telegram.ext import ContextTypes

from db.service.booking_service import BookingService
from db.models import BookingStatus
from bot.keyboards import my_bookings_keyboard

STATUS_LABELS = {
    BookingStatus.PENDING: "⏳ Kutilmoqda",
    BookingStatus.CONFIRMED: "✅ Tasdiqlangan",
    BookingStatus.CANCELLED: "❌ Bekor qilingan",
}


async def show_my_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bookings = await BookingService.get_user_bookings(update.effective_user.id)
    if not bookings:
        await update.message.reply_text("Sizda hech qanday aktiv bron yo'q.")
        return
    keyboards = my_bookings_keyboard(bookings)
    for b, kb in zip(bookings, keyboards):
        text = (
            f"✂️ {b.service.name}\n"
            f"📅 {b.date.strftime('%d.%m.%Y')}  ⏰ {b.time.strftime('%H:%M')}\n"
            f"Status: {STATUS_LABELS.get(b.status, b.status)}"
        )
        await update.message.reply_text(text, reply_markup=kb)


async def cancel_my_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    booking_id = int(query.data.split("_")[1])
    await BookingService.cancel(booking_id)
    await query.edit_message_text(query.message.text + "\n\n❌ Bron bekor qilindi")
