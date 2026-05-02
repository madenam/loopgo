from enum import StrEnum
from tortoise import fields
from tortoise.models import Model


class BookingStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class User(Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.IntField(unique=True)
    name = fields.CharField(max_length=255)
    phone = fields.CharField(max_length=20, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

class Service(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    price = fields.FloatField()
    duration_min = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)


class Booking(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="bookings")
    service = fields.ForeignKeyField("models.Service", related_name="bookings")
    date = fields.DateField()
    time = fields.TimeField()
    status = fields.CharEnumField(BookingStatus, default=BookingStatus.PENDING)
    created_at = fields.DatetimeField(auto_now_add=True)