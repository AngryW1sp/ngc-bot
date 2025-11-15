from aiogram.fsm.state import StatesGroup, State
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, get_user_locale

from app.db import get_visits_stats



stats = Router()


class StatsFlow(StatesGroup):
    date_from = State()
    date_to = State()


@stats.callback_query(F.data == "stats")
async def start_stats(cb: types.CallbackQuery, state: FSMContext):
    await state.set_state(StatsFlow.date_from)
    kb = await SimpleCalendar(locale=await get_user_locale(cb.from_user)).start_calendar()
    await cb.message.edit_text("Выберите *начальную* дату:", reply_markup=kb, parse_mode="Markdown")
    await cb.answer()


@stats.callback_query(
    StateFilter(StatsFlow.date_from), SimpleCalendarCallback.filter()
)
async def set_date_from(cb: types.CallbackQuery, callback_data: dict, state: FSMContext):
    cal = SimpleCalendar(locale=await get_user_locale(cb.from_user), show_alerts=True)
    selected, picked = await cal.process_selection(cb, callback_data)
    if not selected:
        return
    await state.update_data(date_from=picked)
    await state.set_state(StatsFlow.date_to)
    kb = await SimpleCalendar(locale=await get_user_locale(cb.from_user)).start_calendar()
    await cb.message.edit_text(f"Начало: {picked:%d.%m.%Y}\nТеперь выберите *конечную* дату:", reply_markup=kb, parse_mode="Markdown")
    await cb.answer()


@stats.callback_query(
    StateFilter(StatsFlow.date_to), SimpleCalendarCallback.filter()
)
async def set_date_to(cb: types.CallbackQuery, callback_data: dict, state: FSMContext):
    cal = SimpleCalendar(locale=await get_user_locale(cb.from_user), show_alerts=True)
    selected, picked = await cal.process_selection(cb, callback_data)
    if not selected:
        return

    data = await state.get_data()
    date_from = data["date_from"]
    date_to = picked
    if date_to < date_from:
        date_from, date_to = date_to, date_from  # на всякий случай

    rows = get_visits_stats(date_from, date_to)  # [(name, count), ...]

    lines = [f"📊 Статистика {date_from:%d.%m.%Y}–{date_to:%d.%m.%Y}", ""]
    if rows:
        lines += [f"{i+1:>2}. {name} — {cnt}" for i,
                  (name, cnt) in enumerate(rows)]
    else:
        lines += ["Нет данных за выбранный период."]

    await cb.message.edit_text("\n".join(lines))
    await state.clear()
    await cb.answer()
