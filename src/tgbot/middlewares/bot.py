from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message


class BotMiddleware(BaseMiddleware):
    def __init__(self, bot) -> None:
        self.bot = bot

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        data['bot'] = self.bot

        return await handler(event, data)
