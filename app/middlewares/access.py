from aiogram import BaseMiddleware, types
from typing import Callable, Awaitable, Any


class AccessMiddleware(BaseMiddleware):
    def __init__(self, allowed_ids: set[int]):
        super().__init__()
        self.allowed_ids = allowed_ids

    async def __call__(
        self,
        handler: Callable[[types.TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: types.TelegramObject,
        data: dict[str, Any]
    ) -> Any:

        user = getattr(event, "from_user", None)

        if user and user.id not in self.allowed_ids:
            # простейший отклик при запрете
            if isinstance(event, types.Message):
                await event.answer("⛔ У вас нет доступа к этому боту.")
            if isinstance(event, types.CallbackQuery):
                await event.answer("⛔ У вас нет доступа.", show_alert=True)
            return  # НИЧЕГО не пропускаем дальше

        # если доступ есть → продолжаем цепочку
        return await handler(event, data)
