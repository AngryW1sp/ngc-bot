from aiogram import Router, F, types
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, get_user_locale

from app.keyboards.games import build_games_keyboard
from app.keyboards.start import main_menu
from app.utils.parsing import extract_usernames
from app.db import create_visits, get_game_by_id

flow = Router()


class PlayerInput(StatesGroup):
    choice_game = State()
    choice_date = State()
    player_list = State()


@flow.message(CommandStart())
async def on_start(m: types.Message):
    await m.answer("Привет! Выбери действие:", reply_markup=main_menu())

# Шаг 1: выбор игры


@flow.callback_query(F.data == "players_input")
async def ask_game(cb: types.CallbackQuery, state: FSMContext):
    await state.set_state(PlayerInput.choice_game)
    await cb.message.edit_text("Выберите игру:", reply_markup=build_games_keyboard())
    await cb.answer()


@flow.callback_query(StateFilter(PlayerInput.choice_game), F.data.startswith("game:"))
async def on_game_selected(cb: types.CallbackQuery, state: FSMContext):
    game_id = int(cb.data.split(":", 1)[1])
    game_name = get_game_by_id(game_id).name
    await state.update_data(game_id=game_id, game_name=game_name)
    await state.set_state(PlayerInput.choice_date)
    # показываем календарь
    kb = await SimpleCalendar(locale=await get_user_locale(cb.from_user)).start_calendar()
    await cb.message.edit_text("Выберите дату:", reply_markup=kb)
    await cb.answer()

# Шаг 2: выбор даты из календаря


@flow.callback_query(StateFilter(PlayerInput.choice_date), SimpleCalendarCallback.filter())
async def on_calendar(cb: types.CallbackQuery, callback_data: dict, state: FSMContext):
    cal = SimpleCalendar(locale=await get_user_locale(cb.from_user), show_alerts=True)
    selected, picked = await cal.process_selection(cb, callback_data)
    if selected:
        await state.update_data(date=picked)
        await state.set_state(PlayerInput.player_list)
        await cb.message.edit_text(
            f"Дата выбрана: {picked:%d.%m.%Y}\nПришлите список игроков одним сообщением (например, @user1, @user2).",
            reply_markup=None
        )
    await cb.answer()

# Шаг 3: ввод списка игроков


@flow.message(StateFilter(PlayerInput.player_list))
async def on_players_list(m: types.Message, state: FSMContext):
    players = extract_usernames(m.text or "")
    # удаляем пользовательское сообщение ради «иллюзии приложения»
    try:
        await m.delete()
    except Exception:
        pass

    if not players:
        await m.answer("Не нашёл ни одного @username. Пришлите списком ещё раз.")
        return

    data = await state.get_data()
    try:
        create_visits(
            {"game": data["game_id"], "date": data["date"], "player_list": players})
        await m.answer(
            f"Сохранил ✅\nИгра: {data['game_name']}\nДата: {data['date']:%d.%m.%Y}\nИгроки: {', '.join(players)}",
            reply_markup=main_menu()
        )
        await state.clear()
    except Exception as exc:
        await m.answer(f"Ошибка сохранения: {exc}", reply_markup=main_menu())
        await state.clear()
