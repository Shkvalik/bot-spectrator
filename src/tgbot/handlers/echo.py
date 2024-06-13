from aiogram import Router
from aiogram.types import Message
from src.tgbot.filters.user import UserFilter
from src.tgbot.keyboards import reply
from src.tgbot.models.database import DataBase

router = Router()
router.message.filter(UserFilter())


@router.message()
async def bot_echo(message: Message, db: DataBase):
    if message.text == reply.button_back.text:
        return await message.answer(
            'Вы вернулись в главное меню↩️',
            reply_markup=reply.keyboard_home(db.user_is_admin(message.from_user.id))
        )

    await message.reply('Не понимаю🫤')
