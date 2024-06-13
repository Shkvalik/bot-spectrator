from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message


class CasheMiddleware(BaseMiddleware):
    def __init__(self, cashe) -> None:
        self.cashe = cashe

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        data['cashe'] = self.cashe

        return await handler(event, data)
