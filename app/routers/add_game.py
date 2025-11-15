from aiogram.fsm.state import StatesGroup, State
from aiogram import Router, F, types
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from app.db import add_game
from app.keyboards.start import main_menu

create_game = Router()


class GameInput(StatesGroup):
    add_game = State()


@create_game.callback_query(F.data == 'add_game')
async def create_games(cb: CallbackQuery, state: FSMContext):
    await state.set_state(GameInput.add_game)
    await cb.message.edit_text('Введите название мероприятия: ')
    await cb.answer()


@create_game.message(StateFilter(GameInput.add_game))
async def complete_create(message: Message, state: FSMContext):
    try:
        await message.delete()
        name = message.text.capitalize()
        add_game(name=name)
        await message.answer(f'Игра {name} - успешно сохранена', reply_markup=main_menu())
        await state.clear()

    except Exception as exc:
        await message.answer(f"Ошибка сохранения: {exc}", reply_markup=main_menu())
        await state.clear()
