import datetime

from aiogram import Router, F, Bot
from aiogram.types import Message

from src.config import Config
from src.tgbot.keyboards import inline, reply
from src.tgbot.models.database import DataBase

import pytz

from src.tgbot.services.utils import decoder

router = Router()


@router.message(F.text[:4].in_(['ACKU', 'ACKD']))
async def access_key(message: Message, db: DataBase):
    code_info = db.check_access_key(message.text)
    if not code_info.status and not code_info.is_use:
        return await message.answer('Вы ввели не верный код доступа😔')

    if not code_info.status and code_info.is_use:
        return await message.answer('Код уже использован ранее❌')

    if code_info.status and not code_info.is_use:
        status = db.get_status_user_by_access_key(message.text)

        if code_info.date_of_expiry == '30-minut':
            time_of_expiry = datetime.datetime.now().timestamp() + (30 * 60)
        else:
            day, month, year = decoder(code_info.date_of_expiry)
            time_of_expiry = datetime.datetime.strptime(f'{day}.{month}.{year}', '%d.%m.%Y').timestamp()

        human_time = datetime.datetime.fromtimestamp(
            time_of_expiry
        ).astimezone(
            pytz.timezone("Europe/Kiev")
        ).strftime(
            '%d.%m.%Y %H:%M'
        )

        db.add_user(message.from_user.id, message.from_user.username, status, int(time_of_expiry))
        db.update_status_access_key(message.text, 1)

        return await message.answer(
            'Вам предоставлен доступ к функционалу бота✅\n'
            f'Дата окончания - {human_time}(GMT+2)',
            reply_markup=reply.keyboard_home(True if status == 'admin' else False)
        )


@router.message()
async def user_start(message: Message, config: Config, db: DataBase, bot: Bot):
    user = message.from_user

    await bot.send_message(
        chat_id=config.tg_bot.chat_id,
        text=f'🔮 Пользователь @{user.username} ({user.full_name} - {user.id}) #запустил бота.\n'
    )

    await message.answer_sticker(
        'CAACAgIAAxkBAAEKEklk4NxP8-ozNRyXynSebz46bIOa8AAChgADpsrIDHXx4J9fCSUCMAQ',
        reply_markup=reply.remove_keyboard
    )
    await message.reply(
        'У Вас нет прав чтобы пользоваться этим ботом❌',
        reply_markup=inline.contact_us(config.tg_bot.admin_link)
    )

    db.delete_user(message.from_user.id)
