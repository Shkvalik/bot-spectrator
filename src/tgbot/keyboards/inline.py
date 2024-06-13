import calendar
from datetime import datetime

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.tgbot.services.utils import encoder

button_back = InlineKeyboardButton(text='Назад↩️', callback_data='back')
keyboard_back = InlineKeyboardBuilder().row(button_back, width=1).as_markup()

choice_user = InlineKeyboardButton(text='Обычный', callback_data='buyer')
choice_admin = InlineKeyboardButton(text='Админ(фулл доступ)⚠️', callback_data='admin')
keyboard_choice_status = InlineKeyboardBuilder().row(choice_user, choice_admin, button_back, width=1).as_markup()


def get_menu_of_users(users: list[list]):
    keyboard = InlineKeyboardBuilder()

    for user_tg_id, user_name, status in users:
        keyboard.row(InlineKeyboardButton(text=f'{user_tg_id} | {user_name} - {status}', callback_data=f'{user_tg_id}'))

    return keyboard.row(button_back).as_markup()


def contact_us(link: str):
    my_link = InlineKeyboardButton(text='Получить доступ🚪', url=link)
    return InlineKeyboardBuilder().row(my_link).as_markup()


def create_calendar(month: str | int | None = None, year: str | int | None = None) -> InlineKeyboardMarkup:
    month = datetime.now().month if month is None else month
    year = datetime.now().year if year is None else year

    months = ['Пусто', 'Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        InlineKeyboardButton(text='<', callback_data=encoder('prev_month', month, year)),
        InlineKeyboardButton(text=f'{months[month]} {year}', callback_data='none'),
        InlineKeyboardButton(text='>', callback_data=encoder('next_month', month, year))
    )

    day_of_week = []
    for day in ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']:
        day_of_week.append(InlineKeyboardButton(text=day, callback_data='none'))
    keyboard.row(*day_of_week)

    day_of_week = []
    for day in calendar.TextCalendar().itermonthdays(year, month):
        if day != 0:
            if day == datetime.now().day and month == datetime.now().month and year == datetime.now().year:
                text, callback = (f'|{day}|', f'{day:0>2}')

            else:
                text, callback = (f'{day}', f'{day:0>2}')

        else:
            text, callback = (' ', 'none')

        day_of_week.append(InlineKeyboardButton(text=text, callback_data=encoder(callback, f'{month:0>2}', year)))

    keyboard.row(*day_of_week, width=7)

    keyboard.row(InlineKeyboardButton(text='Доступ на 30 минут️⏳', callback_data='30-minut'))
    keyboard.row(InlineKeyboardButton(text='Доступ на всегда🚀', callback_data=encoder('19', '01', '2038')))
    keyboard.row(InlineKeyboardButton(text='Назад↩️', callback_data='back'))

    return keyboard.as_markup()


def cancel_action():
    cancel = InlineKeyboardButton(text='Отменить добавление?', callback_data='cancel')
    return InlineKeyboardBuilder().row(cancel).as_markup()


def add_nickname():
    button_yes = InlineKeyboardButton(text='Да', callback_data='yes_nickname')
    button_no = InlineKeyboardButton(text='Нет', callback_data='no_nickname')
    return InlineKeyboardBuilder().row(button_yes, button_no).as_markup()


def get_user_wallets(wallets: list):
    keyboard_markup = InlineKeyboardBuilder()

    for wallet_id, wallet_name in wallets[:5]:
        wallet_text = wallet_name if wallet_name else f"{wallet_id[:3]}...{wallet_id[-3:]}"
        keyboard_markup.row(InlineKeyboardButton(
            text=wallet_text,
            callback_data=f"delete_wallet__{wallet_id}",
            width=1
        ))

    if len(wallets) > 5:
        keyboard_markup.row(
            InlineKeyboardButton(text="⬅️", callback_data="empty"),
            InlineKeyboardButton(text=f"{1}", callback_data="empty"),
            InlineKeyboardButton(text="➡️", callback_data="next_page_1")
        )

    return keyboard_markup.as_markup()


def pagination_user_wallets(wallets: list, current_page: int):
    total_pages = (len(wallets) + 4) // 5

    start_index = current_page * 5
    end_index = min(start_index + 5, len(wallets))

    keyboard_markup = InlineKeyboardBuilder()

    for wallet_id, wallet_name in wallets[start_index:end_index]:
        wallet_text = wallet_name if wallet_name else f"{wallet_id[:3]}...{wallet_id[-3:]}"
        keyboard_markup.row(InlineKeyboardButton(text=wallet_text, callback_data=f"delete_wallet__{wallet_id}"))

    if total_pages > 1:
        keyboard_markup.row(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"prev_page_{current_page - 1}" if current_page > 0 else "empty"
            ),
            InlineKeyboardButton(
                text=f"{current_page + 1}",
                callback_data="empty"
            ),
            InlineKeyboardButton(
                text="➡️",
                callback_data=f"next_page_{current_page + 1}" if current_page < total_pages - 1 else "empty"
            )
        )

    return keyboard_markup.as_markup(width=1)
