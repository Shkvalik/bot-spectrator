import logging
import re
from datetime import datetime

import httpx
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold

from src.loader import config
from src.tgbot.filters.user import UserFilter
from src.tgbot.keyboards import inline, reply
from src.tgbot.misc.states import Settings
from src.tgbot.models.database import DataBase

router = Router()
router.message.filter(UserFilter())
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def start(message: Message):


    await message.answer('Привет! Выберите действие:', reply_markup=keyboard.as_markup(resize_keyboard=True))


def format_timestamp(timestamp):
    dt_object = datetime.utcfromtimestamp(timestamp)

    return dt_object.strftime('%d.%m.%Y %H:%M')


def is_ton_wallet(wallet_address):
    ton_regex = r'^(UQ|EQ)[A-Za-z0-9_-]{46}$'

    return bool(re.match(ton_regex, wallet_address))


async def get_last_event_id(bot, wallet_id):
    async with httpx.AsyncClient(headers={
        'Authorization': 'Bearer AEHYPKO6ZLFR5BQAAAADNPGK7PJU3J6EJ7GF4GRMYOLUZ3EPDLPULBVZ7Z4SLLPCOTGKQYA'}) as ahttpx:
        try:
            response = await ahttpx.get(f'https://tonapi.io/v2/accounts/{wallet_id}/events?limit=10')

            if response.status_code != 200 and response.json().get('events', False):
                await bot.send_message(
                    '1122881379',
                    f'{hbold("Ошибка при проверке")}‼️\n\n'
                    f'{hbold("Кошелек:")} {wallet_id}\n'
                    f'{hbold("Статус Код:")} {response.status_code}\n'
                    f'{hbold("Ошибка:")} {response.text}'
                )
                return {
                    'status': False,
                    'context': 'Произошла ошибка при получении данных кошелька\n\n. Обратитесь к @kkeshikk за помощью'
                }

            return {
                'status': True,
                'context': response.json().get('events')[0].get('event_id')
            }

        except Exception:
            await bot.send_message(
                config.tg_bot.chat_id,
                f'{hbold("Ошибка при проверке")}‼️\n\n'
                f'{hbold("Кошелек:")} {wallet_id}\n'
                f'{hbold("Статус Код:")} {response.status_code}\n'
                f'{hbold("Ошибка:")} {response.text}'
            )

            return {
                'status': False,
                'context': 'Произошла ошибка при получении данных кошелька\n\n. Обратитесь к @kkeshikk за помощью'
            }


@router.message(F.text == 'Добавить кошелек ➕')
async def add_wallet_handler(message: Message, state: FSMContext):
    await message.answer('🔠 Отправьте номер кошелька для добавления')

    await state.set_state(Settings.add_wallet)


@router.message(Settings.add_wallet)
async def add_wallet(message: Message, state: FSMContext, db: DataBase):
    if not is_ton_wallet(message.text):
        await message.answer(
            text=(
                f'❌ {hbold("Не верный формат кошелька")}\n\n'
                f'Используйте кошельки сети {hbold("TON")}'
            ),
            reply_markup=inline.cancel_action()
        )
        return

    existing_wallet = db.get_user_wallet(message.text.strip(), message.from_user.id)

    if existing_wallet:
        return await message.answer(f'🫡 Кошелек уже добавлен')

    await state.update_data(wallet_id=message.text)

    await message.answer('Добавить имя для этого кошелька?', reply_markup=inline.add_nickname())


@router.callback_query(F.data.in_({'yes_nickname', 'no_nickname'}))
async def nickname_callback(bot: Bot, callback_query: CallbackQuery, state: FSMContext, db: DataBase):
    if callback_query.data == 'yes_nickname':
        await callback_query.message.answer('Введите имя для кошелька:')

        return await state.set_state(Settings.add_nickname)

    data = await state.get_data()

    existing_wallet_last_event_id = db.get_existing_wallet_last_event_id(data.get('wallet_id'))

    if existing_wallet_last_event_id:
        db.add_wallet(
            callback_query.from_user.id,
            data.get('wallet_id'),
            '',
            'TON',
            existing_wallet_last_event_id[0]
        )

        await callback_query.message.edit_text(
            f'🤫 {hbold("Имя не будет задано")}\n\n'
            f'📝 {hbold("Кошелек добавлен")}'
        )

        await state.set_state()

    else:
        response = await get_last_event_id(bot, data.get('wallet_id'))

        if response.get('status'):
            db.add_wallet(
                callback_query.from_user.id,
                data.get('wallet_id'),
                '',
                'TON',
                response.get('context')
            )

            await callback_query.message.edit_text(
                f'🤫 {hbold("Имя не будет задано")}\n\n'
                f'📝 {hbold("Кошелек добавлен")}'
            )

            await state.set_state()

        else:
            await callback_query.answer(response.get('context'))

            await state.set_state()


@router.message(Settings.add_nickname)
async def add_nickname(bot: Bot, message: Message, state: FSMContext, db: DataBase):
    data = await state.get_data()

    existing_wallet_last_event_id = db.get_existing_wallet_last_event_id(data.get('wallet_id'))

    if existing_wallet_last_event_id:
        db.add_wallet(
            message.from_user.id,
            data.get('wallet_id'),
            message.text.strip(),
            'TON',
            existing_wallet_last_event_id
        )

        await message.answer(
            f'📝 {hbold("Кошелек c именем")} {message.text.strip()} {hbold("добавлен")}'
        )

        await state.set_state()

    else:
        response = await get_last_event_id(bot, data.get('wallet_id'))

        if response.get('status'):
            db.add_wallet(
                message.from_user.id,
                data.get('wallet_id'),
                message.text.strip(),
                'TON',
                response.get('context')
            )

            await message.answer(
                f'📝 {hbold("Кошелек c именем")} {message.text.strip()} {hbold("добавлен")}'
            )

            await state.set_state()

        else:
            await message.answer(response.get('context'))

            await state.set_state()


@router.message(F.text == 'Удалить кошелек ➖')
async def delete_wallet_handler(message: Message, db: DataBase):
    user_id = message.from_user.id

    wallets = db.get_user_wallets(user_id)

    if not wallets:
        await message.answer("📂 У вас нет кошельков для удаления")
        return

    await message.answer("🗂️ Выберите кошелек для удаления:", reply_markup=inline.get_user_wallets(wallets))


@router.callback_query(F.data.contains('page'))
async def pagination_callback(callback_query: CallbackQuery, db: DataBase):
    user_id = callback_query.from_user.id

    wallets = db.get_user_wallets(user_id)

    current_page = int(callback_query.data.split('_')[-1])

    await callback_query.message.edit_reply_markup(reply_markup=inline.pagination_user_wallets(wallets, current_page))
    await callback_query.answer()


@router.callback_query(F.data.startswith('delete_wallet'))
async def delete_wallet_callback(callback_query: CallbackQuery, db: DataBase):
    wallet_id = callback_query.data.split('__')[-1]
    user_id = callback_query.from_user.id

    db.delete_user_wallet(wallet_id, user_id)

    await callback_query.message.edit_text("Кошелек успешно удален")


@router.callback_query(F.data == 'cancel')
async def cancel(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state()
    await callback_query.message.edit_text('Добавление отменено🚫')
