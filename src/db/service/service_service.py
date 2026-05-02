from db.models import Service


class ServiceService:

    @staticmethod
    async def get_all() -> list[Service]:
        return await Service.all()

    @staticmethod
    async def get_by_id(service_id: int) -> Service | None:
        return await Service.get_or_none(id=service_id)

    @staticmethod
    async def create(name: str, duration_min: int, price: float) -> Service:
        return await Service.create(name=name, duration_min=duration_min, price=price)

    @staticmethod
    async def delete(service_id: int) -> None:
        await Service.filter(id=service_id).delete()
