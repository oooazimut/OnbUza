import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import ErrorEvent
from aiogram_dialog import DialogManager, StartMode, setup_dialogs
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import settings
from custom.media_storage import MediaIdStorage
from middlewares import DbSessionMiddleware
from states import MainSG
from routers import start_router


async def ui_error_handler(event: ErrorEvent, dialog_manager: DialogManager):
    logging.warning("Сброс ошибки: {event}")
    await dialog_manager.start(state=MainSG.main, mode=StartMode.RESET_STACK)


async def main():
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    engine = create_async_engine(settings.sqlite_async_dsn, echo=False)
    db_pool = async_sessionmaker(engine, expire_on_commit=False)
    bot = Bot(
        token=settings.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    storage = RedisStorage(
        Redis(),
        key_builder=DefaultKeyBuilder(
            with_destiny=True,
            with_bot_id=True,
        ),
    )
    dp = Dispatcher(storage=storage)
    dp.include_routers(start_router)
    setup_dialogs(dp, media_id_storage=MediaIdStorage())
    dp.update.outer_middleware(DbSessionMiddleware(db_pool))
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
