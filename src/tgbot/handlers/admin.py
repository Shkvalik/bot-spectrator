from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hcode, hbold

from src.config import Config
from src.tgbot.filters.admin import AdminFilter
from src.tgbot.keyboards import reply, inline
import time

from src.tgbot.misc.states import AddUser, User
from src.tgbot.models.database import DataBase
from src.tgbot.services.utils import get_random_string

router = Router()
router.message.filter(AdminFilter())


@router.message(CommandStart())
async def admin_start(message: Message):
    await message.answer_sticker('CAACAgIAAxkBAAEKFhdk4ynKsLOlS2j7KcuvkjJQDEpvqgACaQADpsrIDONYOer9B49cMAQ')
    await message.reply(
        'Привет, админ👋🏻',
        reply_markup=reply.keyboard_home(is_admin=True)
    )


@router.message(F.text == reply.admin_panel.text)
async def admin_panel(message: Message, state: FSMContext):
    await message.reply('Админ панель⤵️', reply_markup=reply.keyboard_admin)
    await state.set_state()


@router.message(F.text == reply.edit_users.text)
async def edit_users(message: Message, state: FSMContext, db: DataBase):
    users = db.get_users()

    await message.reply('Выберите пользователя', reply_markup=inline.get_menu_of_users(users))

    await state.set_state(User.menu)


@router.callback_query(User.menu)
async def user_menu(call: CallbackQuery, state: FSMContext):
    if call.data == inline.button_back.callback_data:
        return await call.message.delete()

    await state.update_data(user_tg_id=call.data)

    await call.message.edit_text('Удалить пользователя?', reply_markup=inline.keyboard_aprove)

    await call.answer()
    await state.set_state(User.delete)


@router.callback_query(User.delete)
async def roter_name(call: CallbackQuery, state: FSMContext, db: DataBase):
    data = await state.get_data()
    user_tg_id = data.get('user_tg_id')

    if int(user_tg_id) == call.from_user.id:
        await call.answer('Вы не можете удалить сами себя🚫')

    elif call.data == inline.button_yes.callback_data:
        db.delete_user(user_tg_id)

        await call.answer('Пользователь удалён✅')

    users = db.get_users()

    await call.message.edit_text('Выберите пользователя', reply_markup=inline.get_menu_of_users(users))

    await state.set_state(User.menu)


@router.message(F.text == reply.get_access_key.text)
async def get_access_key(message: Message, state: FSMContext):
    calendar_title = 'Выберите дату окончания подписки:'

    await state.update_data(calendar_title=calendar_title)
    await message.reply(calendar_title, reply_markup=inline.create_calendar())

    await state.set_state(AddUser.get_date_of_expiry)


@router.callback_query(AddUser.get_date_of_expiry)
async def get_date_of_expiry(call: CallbackQuery, state: FSMContext):
    if call.data == inline.button_back.callback_data:
        await call.answer('Меню закрыто❌')
        return await call.message.delete()

    await call.answer()

    await state.update_data(date_of_expiry=call.data)

    await call.message.edit_text('Выберите тип пользователя:', reply_markup=inline.keyboard_choice_status)
    await state.set_state(AddUser.choice_type)


@router.callback_query(AddUser.choice_type)
async def get_access_key(call: CallbackQuery, db: DataBase, state: FSMContext):
    data = await state.get_data()

    if call.data == inline.button_back.callback_data:
        calendar_title = data.get('calendar_title')
        await call.message.edit_text(calendar_title, reply_markup=inline.create_calendar())

        return await state.set_state(AddUser.get_date_of_expiry)

    unix_time = str(int(time.time()))
    random_string = get_random_string(4)
    access_key = f'ACKU-{unix_time[:5]}-{random_string}-{unix_time[5:]}'
    status = 'админ' if call.data == 'admin' else 'обычный'
    date_of_expiry = data.get('date_of_expiry')

    db.add_access_key(access_key, date_of_expiry, call.data)

    await call.message.edit_text(f'Ключ доступа, со статусом "{hbold(status)}"!\n'
                                 f'{hcode(access_key)}')
