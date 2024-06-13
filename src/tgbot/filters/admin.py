from aiogram.filters import BaseFilter
from aiogram.types import Message

from src.tgbot.models.database import DataBase


class AdminFilter(BaseFilter):
    is_admin: bool = True

    async def __call__(self, obj: Message, db: DataBase) -> bool:
        return (obj.from_user.id in db.get_admins_id()) == self.is_admin
