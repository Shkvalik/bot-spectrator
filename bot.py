import asyncio
import logging

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault

from src.loader import config
from src.tgbot.handlers import routers_list
from src.tgbot.middlewares import CustomMiddleware
from src.tgbot.models.database import DataBase
from src.tgbot.services import broadcaster
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.tgbot.services.utils import check_wallets


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command='start', description='🔰Главное меню'),
    ]

    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())


async def on_startup(bot: Bot, admin_ids: list[int]):
    await broadcaster.broadcast(bot, admin_ids, 'Бот запущен')


def register_global_middlewares(dp: Dispatcher, bot: Bot, database: DataBase, scheduler: AsyncIOScheduler):
    middleware_types = [
        CustomMiddleware(bot, 'bot'),
        CustomMiddleware(database, 'db'),
        CustomMiddleware(config, 'config'),
        CustomMiddleware(scheduler, 'scheduler'),
    ]

    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)


def setup_logging():
    log_level = logging.DEBUG
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger = logging.getLogger(__name__)
    logger.info('Starting bot')


async def main():
    setup_logging()

    storage = MemoryStorage()
    database = DataBase('db.db')

    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode='HTML'))

    dp = Dispatcher(storage=storage)
    dp.include_routers(*routers_list)

    scheduler = AsyncIOScheduler()
    await check_wallets(bot, database)
    scheduler.add_job(check_wallets, 'interval', args=[bot, database], minutes=10)
    scheduler.start()

    register_global_middlewares(dp, bot, database, scheduler)
    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())

    except (KeyboardInterrupt, SystemExit):
        logging.error('Error! Bot has turned off')
