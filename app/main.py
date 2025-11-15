import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.middlewares.access import AccessMiddleware
from app.config import BOT_TOKEN
from app.db import init_db
from app.routers.stats import stats
from app.routers.add_game import create_game
from app.routers.flow import flow

ALLOWED_USERS = {5344749587, 459787851}


async def main():
    init_db()
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware(AccessMiddleware(ALLOWED_USERS))
    dp.callback_query.middleware(AccessMiddleware(ALLOWED_USERS))
    dp.include_router(flow)
    dp.include_router(create_game)
    dp.include_router(stats)
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
