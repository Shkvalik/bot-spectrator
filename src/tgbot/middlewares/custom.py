from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message


class CustomMiddleware(BaseMiddleware):
    def __init__(self, middleware_object: Any, name: str) -> None:
        self.middleware_object = middleware_object
        self.name = name

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        data[self.name] = self.middleware_object
        return await handler(event, data)
