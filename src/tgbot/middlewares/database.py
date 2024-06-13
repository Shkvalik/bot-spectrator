from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message


class DataBaseMiddleware(BaseMiddleware):
    def __init__(self, database) -> None:
        self.database = database

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        data['db'] = self.database
        return await handler(event, data)
