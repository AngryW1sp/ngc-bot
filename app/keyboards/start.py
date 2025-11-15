from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="➕ Ввести игроков", callback_data="players_input"),
        InlineKeyboardButton(
            text="📊 Статистика",    callback_data="stats"), 
        InlineKeyboardButton(
            text="Добавить игру",    callback_data="add_game"),
    ]])
    return kb
