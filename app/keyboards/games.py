from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.db import get_games


def build_games_keyboard() -> InlineKeyboardMarkup:
    games = get_games()
    if not games:
        # fallback — одна кнопка с подсказкой
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="Нет игр. Добавьте сначала.", callback_data="noop")
        ]])

    b = InlineKeyboardBuilder()
    for g in games:
        b.button(text=g.name, callback_data=f"game:{g.id}")
    b.adjust(2)  # по 2 в ряд
    return b.as_markup()
