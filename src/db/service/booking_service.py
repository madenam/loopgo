import datetime as dt
from db.models import Booking, BookingStatus, User, Service


class BookingService:

    @staticmethod
    async def create(
        user_id: int,
        service_id: int,
        booking_date: dt.date,
        booking_time: dt.time,
    ) -> Booking:
        return await Booking.create(
            user_id=user_id,
            service_id=service_id,
            date=booking_date,
            time=booking_time,
        )

    @staticmethod
    async def get_user_bookings(telegram_id: int) -> list[Booking]:
        user = await User.get_or_none(telegram_id=telegram_id)
        if not user:
            return []
        return await (
            Booking.filter(
                user=user,
                status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
            )
            .prefetch_related("service")
            .order_by("date", "time")
        )

    @staticmethod
    async def get_by_id(booking_id: int) -> Booking | None:
        booking = await Booking.get_or_none(id=booking_id)
        if booking:
            await booking.fetch_related("user", "service")
        return booking

    @staticmethod
    async def update_status(booking_id: int, status: BookingStatus) -> None:
        await Booking.filter(id=booking_id).update(status=status)

    @staticmethod
    async def get_today_bookings() -> list[Booking]:
        return await (
            Booking.filter(date=dt.date.today(), status=BookingStatus.CONFIRMED)
            .prefetch_related("user", "service")
            .order_by("time")
        )

    @staticmethod
    async def get_booked_times(service_id: int, booking_date: dt.date) -> list[dt.time]:
        bookings = await Booking.filter(
            service_id=service_id,
            date=booking_date,
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
        )
        return [b.time for b in bookings]

    @staticmethod
    async def get_available_slots(service: Service, booking_date: dt.date) -> list[dt.time]:
        booked = await BookingService.get_booked_times(service.id, booking_date)
        slots = []
        current = dt.datetime.combine(booking_date, dt.time(9, 0))
        end = dt.datetime.combine(booking_date, dt.time(18, 0))
        step = dt.timedelta(minutes=service.duration_min)
        while current + step <= end:
            t = current.time()
            if t not in booked:
                slots.append(t)
            current += step
        return slots

    @staticmethod
    async def cancel(booking_id: int) -> None:
        await Booking.filter(id=booking_id).update(status=BookingStatus.CANCELLED)
