import sqlite3
import datetime as dt
from tortoise import Tortoise
from tortoise.context import TortoiseContext, _current_context
from helpers.config import configs

# SQLite datetime.time uchun adapter (tortoise-orm 1.x + aiosqlite)
sqlite3.register_adapter(dt.time, lambda t: t.isoformat())
sqlite3.register_adapter(dt.date, lambda d: d.isoformat())

_db_ctx: TortoiseContext | None = None


async def init_db() -> None:
    global _db_ctx
    _db_ctx = TortoiseContext()
    await _db_ctx.__aenter__()          # _current_context → _db_ctx
    await Tortoise.init(                # config _db_ctx.connections ichiga yoziladi
        db_url=configs["DATABASE_URL"],
        modules={"models": ["db.models"]},
    )
    await Tortoise.generate_schemas()


async def close_db() -> None:
    global _db_ctx
    if _db_ctx is not None:
        await _db_ctx.__aexit__(None, None, None)
        _db_ctx = None
    await Tortoise.close_connections()


def get_db_ctx() -> TortoiseContext:
    if _db_ctx is None:
        raise RuntimeError("init_db() hali chaqirilmagan")
    return _db_ctx
