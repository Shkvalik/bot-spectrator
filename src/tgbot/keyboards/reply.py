from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton
from aiogram.types import ReplyKeyboardRemove

button_back = KeyboardButton(text='Назад↩️')
keyboard_back = ReplyKeyboardBuilder().row(button_back).as_markup(resize_keyboard=True)

admin_panel = KeyboardButton(text='Админ панель🪖')
get_access_key = KeyboardButton(text='Доступ🪪')
edit_users = KeyboardButton(text='Юзеры👨🏻')

keyboard_admin = ReplyKeyboardBuilder().row(
    get_access_key, edit_users,
    button_back, width=2
).as_markup(resize_keyboard=True)

remove_keyboard = ReplyKeyboardRemove()

add_wallet_key = KeyboardButton(text='Добавить кошелек ➕')
delete_wallet_key = KeyboardButton(text='Удалить кошелек ➖')


def keyboard_home(is_admin: bool = False):
    keyboard = ReplyKeyboardBuilder()

    if is_admin:
        keyboard.row(add_wallet_key, delete_wallet_key, admin_panel, width=2)
    else:
        keyboard.row(add_wallet_key, delete_wallet_key, width=2)

    return keyboard.as_markup(resize_keyboard=True)
