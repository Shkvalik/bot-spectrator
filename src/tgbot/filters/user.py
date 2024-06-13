from aiogram.filters import BaseFilter
from aiogram.types import Message

from src.tgbot.models.database import DataBase


class UserFilter(BaseFilter):
    is_user: bool = True

    async def __call__(self, obj: Message, db: DataBase) -> bool:
        return (obj.from_user.id in db.get_users_id()) == self.is_user
