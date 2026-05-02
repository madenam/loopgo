import datetime as dt
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from db.models import Booking, Service


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [["✂️ Bron qilish"], ["📋 Mening bronlarim"], ["📞 Bog'lanish"]],
        resize_keyboard=True,
    )


def services_keyboard(services: list[Service]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            f"{s.name} — {int(s.price):,} so'm ({s.duration_min} min)",
            callback_data=f"svc_{s.id}",
        )]
        for s in services
    ]
    return InlineKeyboardMarkup(buttons)


def dates_keyboard() -> InlineKeyboardMarkup:
    today = dt.date.today()
    buttons = [
        [InlineKeyboardButton(
            (today + dt.timedelta(days=i)).strftime("%d.%m.%Y (%a)"),
            callback_data=f"date_{(today + dt.timedelta(days=i)).isoformat()}",
        )]
        for i in range(1, 8)
    ]
    return InlineKeyboardMarkup(buttons)


def times_keyboard(slots: list[dt.time]) -> InlineKeyboardMarkup:
    buttons, row = [], []
    for i, slot in enumerate(slots):
        row.append(InlineKeyboardButton(slot.strftime("%H:%M"), callback_data=f"time_{slot.strftime('%H:%M')}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)


def confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Tasdiqlash", callback_data="ok"),
        InlineKeyboardButton("❌ Bekor qilish", callback_data="no"),
    ]])


def admin_booking_keyboard(booking_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm_{booking_id}"),
        InlineKeyboardButton("❌ Rad etish", callback_data=f"cancel_{booking_id}"),
    ]])


def my_bookings_keyboard(bookings: list[Booking]) -> list[InlineKeyboardMarkup]:
    return [
        InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ Bekor qilish", callback_data=f"mycancel_{b.id}")
        ]])
        for b in bookings
    ]
