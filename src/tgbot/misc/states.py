from aiogram.fsm.state import StatesGroup, State


class Settings(StatesGroup):
    add_wallet = State()
    add_nickname = State()
    remove_wallet = State()


class User(StatesGroup):
    menu = State()
    delete = State()


class AddUser(StatesGroup):
    get_date_of_expiry = State()
    choice_type = State()
