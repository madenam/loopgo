from db.models import User;

class UserService:

    @staticmethod
    async def create(telegram_id: int, name: str, phone: str) -> User:
        return await User.create(
            telegram_id=telegram_id,
            name=name,
            phone=phone
        ) 
    
    @staticmethod
    async def get_by_telegram_id(telegram_id: int) -> User | None:
        return await User.get_or_none(telegram_id=telegram_id);

    @staticmethod
    async def exists(telegram_id: int) -> bool: 
        return await User.exists(telegram_id=telegram_id);
    
    @staticmethod
    async def update(telegram_id: int, **kwargs) -> None:
        await User.filter(telegram_id=telegram_id).update(**kwargs)

    @staticmethod
    async def delete(telegram_id: int) -> None:
        await User.filter(telegram_id=telegram_id).delete()

    @staticmethod
    async def get_all() -> list[User]:
        return await User.all()
    
